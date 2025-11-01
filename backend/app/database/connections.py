"""
External Database Connection Functions
Supports PostgreSQL, MySQL, Oracle, SQL Server
"""
import cx_Oracle
import psycopg2
import pymysql
import pandas as pd
from typing import List, Dict

# Try to import pyodbc (optional - SQL Server support)
try:
    import pyodbc
    HAS_PYODBC = True
except ImportError:
    HAS_PYODBC = False
    import logging
    logging.warning("pyodbc not available, SQL Server connections will not work")


def test_oracle_connection(config: dict) -> dict:
    """Test Oracle database connection"""
    try:
        dsn = cx_Oracle.makedsn(
            config.get('host'),
            config.get('port', 1521),
            service_name=config.get('service_name')
        )
        conn = cx_Oracle.connect(
            user=config.get('username'),
            password=config.get('password'),
            dsn=dsn
        )
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM DUAL")
        cursor.close()
        conn.close()
        return {"success": True, "message": "Connection successful"}
    except Exception as e:
        return {"success": False, "message": str(e)}


def test_postgresql_connection(config: dict) -> dict:
    """Test PostgreSQL database connection"""
    try:
        conn = psycopg2.connect(
            host=config.get('host'),
            port=config.get('port', 5432),
            database=config.get('database'),
            user=config.get('username'),
            password=config.get('password')
        )
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        return {"success": True, "message": "Connection successful"}
    except Exception as e:
        return {"success": False, "message": str(e)}


def test_mysql_connection(config: dict) -> dict:
    """Test MySQL database connection"""
    try:
        conn = pymysql.connect(
            host=config.get('host'),
            port=int(config.get('port', 3306)),
            database=config.get('database'),
            user=config.get('username'),
            password=config.get('password')
        )
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        return {"success": True, "message": "Connection successful"}
    except Exception as e:
        return {"success": False, "message": str(e)}


def test_sqlserver_connection(config: dict) -> dict:
    """Test SQL Server database connection"""
    if not HAS_PYODBC:
        return {"success": False, "message": "SQL Server support not available (pyodbc not installed)"}
    
    try:
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={config.get('host')},{config.get('port', 1433)};"
            f"DATABASE={config.get('database')};"
            f"UID={config.get('username')};"
            f"PWD={config.get('password')}"
        )
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        return {"success": True, "message": "Connection successful"}
    except Exception as e:
        return {"success": False, "message": str(e)}


def get_oracle_tables(config: dict) -> List[str]:
    """List tables from Oracle database"""
    try:
        dsn = cx_Oracle.makedsn(
            config.get('host'),
            config.get('port', 1521),
            service_name=config.get('service_name')
        )
        conn = cx_Oracle.connect(
            user=config.get('username'),
            password=config.get('password'),
            dsn=dsn
        )
        cursor = conn.cursor()
        cursor.execute("""
            SELECT table_name FROM user_tables 
            ORDER BY table_name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return tables
    except Exception as e:
        raise Exception(f"Failed to list tables: {str(e)}")


def get_postgresql_tables(config: dict) -> List[str]:
    """List tables from PostgreSQL database"""
    try:
        conn = psycopg2.connect(
            host=config.get('host'),
            port=config.get('port', 5432),
            database=config.get('database'),
            user=config.get('username'),
            password=config.get('password')
        )
        cursor = conn.cursor()
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return tables
    except Exception as e:
        raise Exception(f"Failed to list tables: {str(e)}")


def get_mysql_tables(config: dict) -> List[str]:
    """List tables from MySQL database"""
    try:
        conn = pymysql.connect(
            host=config.get('host'),
            port=int(config.get('port', 3306)),
            database=config.get('database'),
            user=config.get('username'),
            password=config.get('password')
        )
        cursor = conn.cursor()
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = DATABASE()
            ORDER BY table_name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return tables
    except Exception as e:
        raise Exception(f"Failed to list tables: {str(e)}")


def get_sqlserver_tables(config: dict) -> List[str]:
    """List tables from SQL Server database"""
    if not HAS_PYODBC:
        raise Exception("SQL Server support not available (pyodbc not installed)")
    
    try:
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={config.get('host')},{config.get('port', 1433)};"
            f"DATABASE={config.get('database')};"
            f"UID={config.get('username')};"
            f"PWD={config.get('password')}"
        )
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return tables
    except Exception as e:
        raise Exception(f"Failed to list tables: {str(e)}")


def load_table_data(source_type: str, config: dict, table_name: str) -> pd.DataFrame:
    """Load data from database table"""
    if source_type == 'oracle':
        dsn = cx_Oracle.makedsn(
            config.get('host'),
            config.get('port', 1521),
            service_name=config.get('service_name')
        )
        conn = cx_Oracle.connect(
            user=config.get('username'),
            password=config.get('password'),
            dsn=dsn
        )
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
        conn.close()
        return df
    elif source_type == 'postgresql':
        conn = psycopg2.connect(
            host=config.get('host'),
            port=config.get('port', 5432),
            database=config.get('database'),
            user=config.get('username'),
            password=config.get('password')
        )
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
        conn.close()
        return df
    elif source_type == 'mysql':
        conn = pymysql.connect(
            host=config.get('host'),
            port=int(config.get('port', 3306)),
            database=config.get('database'),
            user=config.get('username'),
            password=config.get('password')
        )
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
        conn.close()
        return df
    elif source_type == 'sqlserver':
        if not HAS_PYODBC:
            raise ValueError("SQL Server support not available (pyodbc not installed)")
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={config.get('host')},{config.get('port', 1433)};"
            f"DATABASE={config.get('database')};"
            f"UID={config.get('username')};"
            f"PWD={config.get('password')}"
        )
        conn = pyodbc.connect(conn_str)
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
        conn.close()
        return df
    else:
        raise ValueError(f"Unsupported source type: {source_type}")


def parse_connection_string(source_type: str, conn_str: str) -> dict:
    """Parse connection string into config dictionary"""
    from urllib.parse import urlparse
    
    config = {}
    
    try:
        if source_type in ['postgresql', 'mysql']:
            parsed = urlparse(conn_str)
            config['host'] = parsed.hostname or 'localhost'
            config['port'] = parsed.port or (5432 if source_type == 'postgresql' else 3306)
            config['database'] = parsed.path.lstrip('/') if parsed.path else ''
            config['username'] = parsed.username or ''
            config['password'] = parsed.password or ''
            
        elif source_type == 'oracle':
            parsed = urlparse(conn_str)
            config['host'] = parsed.hostname or 'localhost'
            config['port'] = parsed.port or 1521
            config['service_name'] = parsed.path.lstrip('/') if parsed.path else 'ORCL'
            config['username'] = parsed.username or ''
            config['password'] = parsed.password or ''
            
        elif source_type == 'sqlserver':
            if conn_str.startswith(('mssql://', 'sqlserver://')):
                parsed = urlparse(conn_str)
                config['host'] = parsed.hostname or 'localhost'
                config['port'] = parsed.port or 1433
                config['database'] = parsed.path.lstrip('/') if parsed.path else ''
                config['username'] = parsed.username or ''
                config['password'] = parsed.password or ''
            else:
                # Parse key-value format
                parts = dict(item.split('=', 1) for item in conn_str.split(';') if '=' in item)
                config['host'] = parts.get('Server', '').split(',')[0]
                config['port'] = int(parts.get('Server', ',1433').split(',')[1]) if ',' in parts.get('Server', '') else 1433
                config['database'] = parts.get('Database', '')
                config['username'] = parts.get('User Id', parts.get('UID', ''))
                config['password'] = parts.get('Password', parts.get('PWD', ''))
                
        elif source_type == 'mongodb':
            parsed = urlparse(conn_str)
            config['host'] = parsed.hostname or 'localhost'
            config['port'] = parsed.port or 27017
            config['database'] = parsed.path.lstrip('/') if parsed.path else ''
            config['username'] = parsed.username or ''
            config['password'] = parsed.password or ''
            
    except Exception as e:
        raise ValueError(f"Failed to parse connection string: {str(e)}")
    
    return config
