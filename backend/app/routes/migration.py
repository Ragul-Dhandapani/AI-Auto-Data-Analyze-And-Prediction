"""
Migration endpoints for database schema updates
"""
from fastapi import APIRouter, HTTPException
from app.database.adapters.factory import get_database_adapter
import logging

router = APIRouter(prefix="/migration", tags=["migration"])
logger = logging.getLogger(__name__)

@router.post("/add-workspace-column")
async def add_workspace_column():
    """Add workspace_name column to training_metadata table"""
    db_adapter = get_database_adapter()
    
    try:
        # Check if column exists
        check_query = """
        SELECT COUNT(*) as col_count
        FROM user_tab_columns
        WHERE table_name = 'TRAINING_METADATA'
        AND column_name = 'WORKSPACE_NAME'
        """
        
        result = await db_adapter._execute(check_query)
        
        if result and result[0][0] > 0:
            return {"status": "success", "message": "workspace_name column already exists"}
        
        # Add column
        alter_query = """
        ALTER TABLE training_metadata 
        ADD (workspace_name VARCHAR2(200) DEFAULT 'default')
        """
        await db_adapter._execute(alter_query)
        
        # Create index
        index_query = """
        CREATE INDEX idx_training_workspace 
        ON training_metadata(workspace_name)
        """
        try:
            await db_adapter._execute(index_query)
        except Exception as e:
            if 'ORA-00955' not in str(e):  # Ignore if index exists
                raise
                
        return {
            "status": "success",
            "message": "workspace_name column added successfully"
        }
        
    except Exception as e:
        logger.error(f"Migration error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
