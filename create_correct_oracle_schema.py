#!/usr/bin/env python3
"""
Create the correct Oracle schema that matches the Oracle adapter expectations
Based on the review request requirements:
- WORKSPACES table for workspace operations
- DATASETS table with WORKSPACE_ID foreign key
- DATASET_BLOBS table for file storage
"""
import cx_Oracle
import os

def create_correct_oracle_schema():
    """Create the correct Oracle schema"""
    
    # Initialize Oracle client
    try:
        cx_Oracle.init_oracle_client(lib_dir='/opt/oracle/instantclient_19_23')
        print("✅ Oracle Client initialized")
    except Exception as e:
        print(f"⚠️  Oracle Client: {e}")
    
    # Connect to Oracle
    dsn = cx_Oracle.makedsn(
        'promise-ai-test-oracle.cgxf9inhpsec.us-east-1.rds.amazonaws.com',
        '1521',
        service_name='ORCL'
    )
    conn = cx_Oracle.connect(user='testuser', password='DbPasswordTest', dsn=dsn)
    cursor = conn.cursor()
    
    print("✅ Connected to Oracle database")
    
    # Drop existing tables in correct order (respecting foreign keys)
    print("\n🗑️  Dropping existing tables (if any)...")
    tables_to_drop = [
        'PREDICTION_FEEDBACK',
        'TRAINING_METADATA', 
        'DATASET_BLOBS',
        'DATASETS',
        'WORKSPACES',
        'SAVED_STATES',
        'WORKSPACE_STATES',
        'FILE_STORAGE'
    ]
    
    for table in tables_to_drop:
        try:
            cursor.execute(f"DROP TABLE {table} CASCADE CONSTRAINTS")
            print(f"  ✓ Dropped {table}")
        except:
            pass
    
    # Drop sequences
    try:
        cursor.execute("DROP SEQUENCE file_storage_seq")
    except:
        pass
    
    conn.commit()
    
    print("\n🔧 Creating correct schema for Oracle adapter...")
    
    # 1. Create WORKSPACES table (primary table)
    print("\n1. Creating WORKSPACES table...")
    cursor.execute("""
    CREATE TABLE WORKSPACES (
        ID VARCHAR2(36) PRIMARY KEY,
        NAME VARCHAR2(500) NOT NULL,
        DESCRIPTION CLOB,
        TAGS CLOB CHECK (TAGS IS JSON),
        CREATED_AT TIMESTAMP DEFAULT SYSTIMESTAMP,
        UPDATED_AT TIMESTAMP DEFAULT SYSTIMESTAMP,
        DATASET_COUNT NUMBER(6) DEFAULT 0,
        TRAINING_COUNT NUMBER(6) DEFAULT 0
    )
    """)
    cursor.execute("CREATE INDEX idx_workspaces_created ON WORKSPACES(CREATED_AT DESC)")
    cursor.execute("CREATE INDEX idx_workspaces_name ON WORKSPACES(NAME)")
    print("✅ WORKSPACES table created")
    
    # 2. Create DATASETS table with WORKSPACE_ID foreign key
    print("\n2. Creating DATASETS table with WORKSPACE_ID...")
    cursor.execute("""
    CREATE TABLE DATASETS (
        ID VARCHAR2(36) PRIMARY KEY,
        WORKSPACE_ID VARCHAR2(36),
        NAME VARCHAR2(500) NOT NULL,
        ROW_COUNT NUMBER(12) DEFAULT 0,
        COLUMN_COUNT NUMBER(6) DEFAULT 0,
        COLUMNS CLOB CHECK (COLUMNS IS JSON),
        DTYPES CLOB CHECK (DTYPES IS JSON),
        DATA_PREVIEW CLOB CHECK (DATA_PREVIEW IS JSON),
        FILE_SIZE NUMBER(15) DEFAULT 0,
        SOURCE_TYPE VARCHAR2(50) DEFAULT 'file_upload',
        STORAGE_TYPE VARCHAR2(20) DEFAULT 'direct',
        GRIDFS_FILE_ID VARCHAR2(36),
        TRAINING_COUNT NUMBER(6) DEFAULT 0,
        CREATED_AT TIMESTAMP DEFAULT SYSTIMESTAMP,
        UPDATED_AT TIMESTAMP DEFAULT SYSTIMESTAMP,
        LAST_TRAINED_AT TIMESTAMP,
        CONSTRAINT FK_DATASET_WORKSPACE FOREIGN KEY (WORKSPACE_ID) 
            REFERENCES WORKSPACES(ID) ON DELETE SET NULL
    )
    """)
    cursor.execute("CREATE INDEX idx_datasets_workspace ON DATASETS(WORKSPACE_ID)")
    cursor.execute("CREATE INDEX idx_datasets_created ON DATASETS(CREATED_AT DESC)")
    cursor.execute("CREATE INDEX idx_datasets_name ON DATASETS(NAME)")
    print("✅ DATASETS table created with WORKSPACE_ID foreign key")
    
    # 3. Create DATASET_BLOBS table for file storage
    print("\n3. Creating DATASET_BLOBS table...")
    cursor.execute("""
    CREATE TABLE DATASET_BLOBS (
        ID VARCHAR2(36) PRIMARY KEY,
        DATASET_ID VARCHAR2(36),
        FILENAME VARCHAR2(500) NOT NULL,
        CONTENT_TYPE VARCHAR2(100) DEFAULT 'application/octet-stream',
        FILE_DATA BLOB,
        CREATED_AT TIMESTAMP DEFAULT SYSTIMESTAMP,
        CONSTRAINT FK_BLOB_DATASET FOREIGN KEY (DATASET_ID) 
            REFERENCES DATASETS(ID) ON DELETE CASCADE
    )
    """)
    cursor.execute("CREATE INDEX idx_dataset_blobs_dataset ON DATASET_BLOBS(DATASET_ID)")
    cursor.execute("CREATE INDEX idx_dataset_blobs_created ON DATASET_BLOBS(CREATED_AT DESC)")
    print("✅ DATASET_BLOBS table created")
    
    # 4. Create SAVED_STATES table (for workspace states)
    print("\n4. Creating SAVED_STATES table...")
    cursor.execute("""
    CREATE TABLE SAVED_STATES (
        ID VARCHAR2(36) PRIMARY KEY,
        WORKSPACE_NAME VARCHAR2(500) NOT NULL,
        DATASET_ID VARCHAR2(36) NOT NULL,
        ANALYSIS_RESULTS CLOB CHECK (ANALYSIS_RESULTS IS JSON),
        CREATED_AT TIMESTAMP DEFAULT SYSTIMESTAMP,
        CONSTRAINT FK_SAVED_STATE_DATASET FOREIGN KEY (DATASET_ID) 
            REFERENCES DATASETS(ID) ON DELETE CASCADE
    )
    """)
    cursor.execute("CREATE INDEX idx_saved_states_dataset ON SAVED_STATES(DATASET_ID)")
    cursor.execute("CREATE INDEX idx_saved_states_created ON SAVED_STATES(CREATED_AT DESC)")
    print("✅ SAVED_STATES table created")
    
    # 5. Create TRAINING_METADATA table
    print("\n5. Creating TRAINING_METADATA table...")
    cursor.execute("""
    CREATE TABLE TRAINING_METADATA (
        ID VARCHAR2(36) PRIMARY KEY,
        DATASET_ID VARCHAR2(36) NOT NULL,
        WORKSPACE_NAME VARCHAR2(500) DEFAULT 'default',
        PROBLEM_TYPE VARCHAR2(50) NOT NULL,
        TARGET_VARIABLE VARCHAR2(200) NOT NULL,
        FEATURE_VARIABLES CLOB,
        MODEL_TYPE VARCHAR2(200) NOT NULL,
        MODEL_PARAMS_JSON CLOB CHECK (MODEL_PARAMS_JSON IS JSON),
        METRICS_JSON CLOB CHECK (METRICS_JSON IS JSON),
        TRAINING_DURATION NUMBER(10, 3),
        CREATED_AT TIMESTAMP DEFAULT SYSTIMESTAMP,
        CONSTRAINT FK_TRAINING_DATASET FOREIGN KEY (DATASET_ID)
            REFERENCES DATASETS(ID) ON DELETE CASCADE
    )
    """)
    cursor.execute("CREATE INDEX idx_training_dataset ON TRAINING_METADATA(DATASET_ID)")
    cursor.execute("CREATE INDEX idx_training_workspace ON TRAINING_METADATA(WORKSPACE_NAME)")
    cursor.execute("CREATE INDEX idx_training_created ON TRAINING_METADATA(CREATED_AT DESC)")
    print("✅ TRAINING_METADATA table created")
    
    # 6. Create PREDICTION_FEEDBACK table
    print("\n6. Creating PREDICTION_FEEDBACK table...")
    cursor.execute("""
    CREATE TABLE PREDICTION_FEEDBACK (
        ID VARCHAR2(36) PRIMARY KEY,
        PREDICTION_ID VARCHAR2(36) UNIQUE NOT NULL,
        DATASET_ID VARCHAR2(36) NOT NULL,
        MODEL_NAME VARCHAR2(200) NOT NULL,
        IS_CORRECT CHAR(1) NOT NULL,
        PREDICTION VARCHAR2(500),
        ACTUAL_OUTCOME VARCHAR2(500),
        FEEDBACK_COMMENT CLOB,
        CREATED_AT TIMESTAMP DEFAULT SYSTIMESTAMP,
        CONSTRAINT FK_FEEDBACK_DATASET FOREIGN KEY (DATASET_ID) 
            REFERENCES DATASETS(ID) ON DELETE CASCADE,
        CONSTRAINT CHK_IS_CORRECT CHECK (IS_CORRECT IN ('Y', 'N'))
    )
    """)
    cursor.execute("CREATE INDEX idx_feedback_dataset_model ON PREDICTION_FEEDBACK(DATASET_ID, MODEL_NAME)")
    cursor.execute("CREATE INDEX idx_feedback_created ON PREDICTION_FEEDBACK(CREATED_AT DESC)")
    print("✅ PREDICTION_FEEDBACK table created")
    
    conn.commit()
    
    # Verify tables
    print("\n📊 Verifying schema...")
    cursor.execute("""
        SELECT table_name FROM user_tables 
        WHERE table_name IN ('WORKSPACES', 'DATASETS', 'DATASET_BLOBS', 'SAVED_STATES', 'TRAINING_METADATA', 'PREDICTION_FEEDBACK')
        ORDER BY table_name
    """)
    
    tables = [row[0] for row in cursor.fetchall()]
    
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  ✓ {table}: {count} rows")
    
    # Verify foreign key constraints
    print("\n🔗 Verifying foreign key constraints...")
    cursor.execute("""
        SELECT constraint_name, table_name, r_constraint_name
        FROM user_constraints 
        WHERE constraint_type = 'R'
        AND table_name IN ('DATASETS', 'DATASET_BLOBS', 'SAVED_STATES', 'TRAINING_METADATA', 'PREDICTION_FEEDBACK')
        ORDER BY table_name, constraint_name
    """)
    
    fks = cursor.fetchall()
    for fk in fks:
        print(f"  ✓ {fk[1]}.{fk[0]} -> {fk[2]}")
    
    print(f"\n✅ Oracle schema created successfully!")
    print(f"   - {len(tables)} tables created")
    print(f"   - {len(fks)} foreign key constraints")
    print("\n🎯 Schema now matches Oracle adapter expectations:")
    print("   ✅ WORKSPACES table for workspace operations")
    print("   ✅ DATASETS table with WORKSPACE_ID foreign key")
    print("   ✅ DATASET_BLOBS table for file storage")
    print("   ✅ All foreign key constraints properly defined")
    
    cursor.close()
    conn.close()
    
    return True

if __name__ == "__main__":
    try:
        success = create_correct_oracle_schema()
        print("\n🏆 Schema creation completed successfully!")
    except Exception as e:
        print(f"\n❌ Error creating schema: {e}")
        import traceback
        traceback.print_exc()