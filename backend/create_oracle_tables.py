"""
Simple Oracle Schema Creator - Execute each table creation directly
"""
import cx_Oracle
import os

# Initialize client
try:
    cx_Oracle.init_oracle_client(lib_dir='/opt/oracle/instantclient_19_23')
    print("✅ Oracle Client initialized")
except Exception as e:
    print(f"⚠️  Oracle Client: {e}")

# Connect
dsn = cx_Oracle.makedsn(
    'promise-ai-test-oracle.cgxf9inhpsec.us-east-1.rds.amazonaws.com',
    '1521',
    service_name='ORCL'
)
conn = cx_Oracle.connect(user='testuser', password='DbPasswordTest', dsn=dsn)
cursor = conn.cursor()

print("✅ Connected to Oracle database\n")

# Drop existing tables
print("🗑️  Dropping existing tables (if any)...")
for table in ['PREDICTION_FEEDBACK', 'WORKSPACE_STATES', 'FILE_STORAGE', 'DATASETS']:
    try:
        cursor.execute(f"DROP TABLE {table} CASCADE CONSTRAINTS")
        print(f"  ✓ Dropped {table}")
    except:
        pass

try:
    cursor.execute("DROP SEQUENCE file_storage_seq")
except:
    pass

conn.commit()

print("\n🔧 Creating tables...\n")

# 1. Create DATASETS table
print("Creating DATASETS table...")
cursor.execute("""
CREATE TABLE datasets (
    id VARCHAR2(36) PRIMARY KEY,
    name VARCHAR2(500) NOT NULL,
    source VARCHAR2(50) DEFAULT 'upload',
    row_count NUMBER(12) DEFAULT 0,
    column_count NUMBER(6) DEFAULT 0,
    columns_json CLOB CHECK (columns_json IS JSON),
    dtypes_json CLOB CHECK (dtypes_json IS JSON),
    data_preview_json CLOB CHECK (data_preview_json IS JSON),
    storage_type VARCHAR2(20) DEFAULT 'direct',
    file_id VARCHAR2(36),
    training_count NUMBER(6) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_trained_at TIMESTAMP,
    CONSTRAINT chk_storage_type CHECK (storage_type IN ('direct', 'blob'))
)
""")
cursor.execute("CREATE INDEX idx_datasets_created ON datasets(created_at DESC)")
cursor.execute("CREATE INDEX idx_datasets_name ON datasets(name)")
cursor.execute("CREATE INDEX idx_datasets_file_id ON datasets(file_id)")
print("✅ DATASETS table created")

# 2. Create FILE_STORAGE table
print("\nCreating FILE_STORAGE table...")
cursor.execute("CREATE SEQUENCE file_storage_seq START WITH 1 INCREMENT BY 1")
cursor.execute("""
CREATE TABLE file_storage (
    id VARCHAR2(36) PRIMARY KEY,
    filename VARCHAR2(500) NOT NULL,
    file_data BLOB,
    metadata_json CLOB CHECK (metadata_json IS JSON),
    file_size NUMBER(15) DEFAULT 0,
    compressed CHAR(1) DEFAULT 'N',
    original_size NUMBER(15),
    mime_type VARCHAR2(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_compressed CHECK (compressed IN ('Y', 'N'))
)
""")
cursor.execute("CREATE INDEX idx_file_storage_filename ON file_storage(filename)")
cursor.execute("CREATE INDEX idx_file_storage_created ON file_storage(created_at DESC)")
print("✅ FILE_STORAGE table created")

# 3. Create WORKSPACE_STATES table
print("\nCreating WORKSPACE_STATES table...")
cursor.execute("""
CREATE TABLE workspace_states (
    id VARCHAR2(36) PRIMARY KEY,
    dataset_id VARCHAR2(36) NOT NULL,
    state_name VARCHAR2(500) NOT NULL,
    storage_type VARCHAR2(20) DEFAULT 'direct',
    file_id VARCHAR2(36),
    analysis_data_json CLOB CHECK (analysis_data_json IS JSON),
    chat_history_json CLOB CHECK (chat_history_json IS JSON),
    size_bytes NUMBER(15) DEFAULT 0,
    compressed_size NUMBER(15),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_workspace_dataset FOREIGN KEY (dataset_id) 
        REFERENCES datasets(id) ON DELETE CASCADE,
    CONSTRAINT fk_workspace_file FOREIGN KEY (file_id) 
        REFERENCES file_storage(id) ON DELETE SET NULL,
    CONSTRAINT chk_ws_storage_type CHECK (storage_type IN ('direct', 'blob'))
)
""")
cursor.execute("CREATE INDEX idx_workspace_dataset ON workspace_states(dataset_id)")
cursor.execute("CREATE INDEX idx_workspace_name ON workspace_states(state_name)")
cursor.execute("CREATE INDEX idx_workspace_created ON workspace_states(created_at DESC)")
print("✅ WORKSPACE_STATES table created")

# 4. Create PREDICTION_FEEDBACK table
print("\nCreating PREDICTION_FEEDBACK table...")
cursor.execute("""
CREATE TABLE prediction_feedback (
    id VARCHAR2(36) PRIMARY KEY,
    prediction_id VARCHAR2(36) UNIQUE NOT NULL,
    dataset_id VARCHAR2(36) NOT NULL,
    model_name VARCHAR2(200) NOT NULL,
    is_correct CHAR(1) NOT NULL,
    prediction VARCHAR2(500),
    actual_outcome VARCHAR2(500),
    "comment" CLOB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_feedback_dataset FOREIGN KEY (dataset_id) 
        REFERENCES datasets(id) ON DELETE CASCADE,
    CONSTRAINT chk_is_correct CHECK (is_correct IN ('Y', 'N'))
)
""")
cursor.execute("CREATE INDEX idx_feedback_prediction ON prediction_feedback(prediction_id)")
cursor.execute("CREATE INDEX idx_feedback_dataset_model ON prediction_feedback(dataset_id, model_name)")
cursor.execute("CREATE INDEX idx_feedback_created ON prediction_feedback(created_at DESC)")
print("✅ PREDICTION_FEEDBACK table created")

conn.commit()

# Verify
print("\n📊 Verifying tables...")
cursor.execute("SELECT table_name FROM user_tables ORDER BY table_name")
tables = [row[0] for row in cursor.fetchall()]

for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"  ✓ {table}: {count} rows")

print(f"\n✅ All {len(tables)} tables created successfully!")

cursor.close()
conn.close()
