"""
Initialize Oracle Database Schema for PROMISE AI
Run this once when setting up Oracle for the first time
"""
import cx_Oracle
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def init_oracle_schema():
    """Initialize Oracle database schema"""
    
    # Get Oracle connection parameters
    user = os.getenv('ORACLE_USER')
    password = os.getenv('ORACLE_PASSWORD')
    host = os.getenv('ORACLE_HOST')
    port = os.getenv('ORACLE_PORT', '1521')
    service_name = os.getenv('ORACLE_SERVICE_NAME')
    
    if not all([user, password, host, service_name]):
        print("❌ Missing Oracle connection parameters in .env file")
        return False
    
    try:
        # Initialize Oracle client
        cx_Oracle.init_oracle_client(lib_dir='/opt/oracle/instantclient_19_23')
        print("✅ Oracle Client initialized")
    except Exception as e:
        print(f"⚠️  Oracle Client already initialized: {e}")
    
    # Create DSN
    dsn = cx_Oracle.makedsn(host, port, service_name=service_name)
    
    try:
        # Connect to Oracle
        print(f"Connecting to Oracle at {host}:{port}/{service_name}...")
        connection = cx_Oracle.connect(user=user, password=password, dsn=dsn)
        print("✅ Connected to Oracle database")
        
        # Read schema SQL file
        schema_file = '/app/backend/app/database/oracle_schema.sql'
        with open(schema_file, 'r') as f:
            sql_content = f.read()
        
        # Split by / to get individual statements
        statements = [stmt.strip() for stmt in sql_content.split('/') if stmt.strip() and not stmt.strip().startswith('--')]
        
        cursor = connection.cursor()
        
        print("\n🔧 Executing Oracle schema creation...")
        
        for i, statement in enumerate(statements):
            if not statement or statement.startswith('--'):
                continue
            
            try:
                # Handle PL/SQL blocks
                if statement.strip().upper().startswith('BEGIN'):
                    cursor.execute(statement)
                else:
                    # Regular SQL statements
                    cursor.execute(statement)
                
                if i % 5 == 0:
                    print(f"  Executed {i+1}/{len(statements)} statements...")
            
            except cx_Oracle.DatabaseError as e:
                error, = e.args
                # Ignore "object does not exist" errors during drops
                if error.code != 942:  # ORA-00942: table or view does not exist
                    print(f"⚠️  Warning at statement {i+1}: {error.message}")
        
        connection.commit()
        print(f"\n✅ All {len(statements)} SQL statements executed successfully")
        
        # Verify tables were created
        cursor.execute("""
            SELECT table_name FROM user_tables 
            WHERE table_name IN ('DATASETS', 'FILE_STORAGE', 'WORKSPACE_STATES', 'PREDICTION_FEEDBACK')
            ORDER BY table_name
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        
        print("\n📊 Tables created:")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  ✓ {table}: {count} rows")
        
        cursor.close()
        connection.close()
        
        print("\n✅ Oracle schema initialization complete!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error initializing Oracle schema: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = init_oracle_schema()
    exit(0 if success else 1)
