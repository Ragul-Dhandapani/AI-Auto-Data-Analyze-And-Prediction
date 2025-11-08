"""
Migration script to add workspace_name column to training_metadata table
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.database.adapters.factory import get_database_adapter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_migration():
    """Add workspace_name column to training_metadata"""
    db_adapter = get_database_adapter()
    
    # Initialize connection
    await db_adapter.initialize()
    logger.info("✅ Database connection initialized")
    
    try:
        # Check if column already exists
        check_query = """
        SELECT COUNT(*) as col_count
        FROM user_tab_columns
        WHERE table_name = 'TRAINING_METADATA'
        AND column_name = 'WORKSPACE_NAME'
        """
        
        result = await db_adapter._execute(check_query)
        
        if result and result[0][0] > 0:
            logger.info("✅ workspace_name column already exists")
            return
        
        # Add column
        logger.info("Adding workspace_name column...")
        alter_query = """
        ALTER TABLE training_metadata 
        ADD (workspace_name VARCHAR2(200) DEFAULT 'default')
        """
        await db_adapter._execute(alter_query)
        logger.info("✅ Column added successfully")
        
        # Create index
        logger.info("Creating index...")
        index_query = """
        CREATE INDEX idx_training_workspace 
        ON training_metadata(workspace_name)
        """
        try:
            await db_adapter._execute(index_query)
            logger.info("✅ Index created successfully")
        except Exception as e:
            if 'ORA-00955' in str(e):  # Index already exists
                logger.info("✅ Index already exists")
            else:
                raise
                
    except Exception as e:
        logger.error(f"❌ Migration failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(run_migration())
