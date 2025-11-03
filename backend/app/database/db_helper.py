"""
Database Helper Module
Provides easy access to database adapter for route handlers
"""
from app.database.adapters.factory import get_database_adapter
from app.database.adapters.base import DatabaseAdapter

def get_db() -> DatabaseAdapter:
    """
    Get database adapter instance
    
    Usage in routes:
        from app.database.db_helper import get_db
        
        db = get_db()
        dataset = await db.get_dataset(dataset_id)
    """
    return get_database_adapter()
