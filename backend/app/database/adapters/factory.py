"""Database Adapter Factory - Selects database based on configuration"""
import os
import logging
from typing import Optional

from .base import DatabaseAdapter
from .mongodb_adapter import MongoDBAdapter
from .oracle_adapter import OracleAdapter

logger = logging.getLogger(__name__)

_adapter_instance: Optional[DatabaseAdapter] = None

def get_database_adapter() -> DatabaseAdapter:
    """
    Get database adapter instance (singleton pattern)
    
    Selects adapter based on DB_TYPE environment variable:
    - 'mongodb' (default): Use MongoDB
    - 'oracle': Use Oracle 23
    
    Returns:
        DatabaseAdapter instance (MongoDB or Oracle)
    """
    global _adapter_instance
    
    if _adapter_instance is not None:
        return _adapter_instance
    
    db_type = os.getenv('DB_TYPE', 'mongodb').lower()
    
    logger.info(f"🔧 Initializing database adapter: {db_type}")
    
    if db_type == 'oracle':
        # Oracle configuration
        oracle_user = os.getenv('ORACLE_USER')
        oracle_password = os.getenv('ORACLE_PASSWORD')
        oracle_host = os.getenv('ORACLE_HOST', 'localhost')
        oracle_port = os.getenv('ORACLE_PORT', '1521')
        oracle_service = os.getenv('ORACLE_SERVICE_NAME', 'XEPDB1')
        
        if not oracle_user or not oracle_password:
            raise ValueError("ORACLE_USER and ORACLE_PASSWORD must be set in .env for Oracle database")
        
        # Build Oracle connection string
        connection_string = f"{oracle_user}/{oracle_password}@{oracle_host}:{oracle_port}/{oracle_service}"
        
        pool_size = int(os.getenv('ORACLE_POOL_SIZE', '10'))
        _adapter_instance = OracleAdapter(connection_string, pool_size)
        
        logger.info(f"✅ Oracle adapter initialized: {oracle_host}:{oracle_port}/{oracle_service}")
    
    else:  # mongodb (default)
        # MongoDB configuration
        mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
        db_name = os.getenv('DB_NAME', 'autopredict_db')
        
        _adapter_instance = MongoDBAdapter(mongo_url, db_name)
        
        logger.info(f"✅ MongoDB adapter initialized: {mongo_url}/{db_name}")
    
    return _adapter_instance


async def initialize_database():
    """Initialize database connection (call at startup)"""
    adapter = get_database_adapter()
    await adapter.connect()
    logger.info("🚀 Database connection established")


async def close_database():
    """Close database connection (call at shutdown)"""
    global _adapter_instance
    if _adapter_instance:
        await _adapter_instance.disconnect()
        _adapter_instance = None
        logger.info("🔒 Database connection closed")


def reset_adapter():
    """Reset adapter instance (useful for testing)"""
    global _adapter_instance
    _adapter_instance = None
