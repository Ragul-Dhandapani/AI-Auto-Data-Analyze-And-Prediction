from fastapi import APIRouter, HTTPException
from typing import Optional
from app.database.adapters.factory import get_database_adapter
import logging

router = APIRouter(prefix="/training", tags=["training"])
logger = logging.getLogger(__name__)

@router.get("/metadata")
async def get_training_metadata(
    dataset_id: Optional[str] = None,
    workspace_name: Optional[str] = None,
    limit: int = 100
):
    """Get training metadata with optional filters"""
    try:
        db_adapter = get_database_adapter()
        
        # Build query with optional filters
        query_parts = ["SELECT * FROM (",
                      "SELECT * FROM training_metadata",
                      "WHERE 1=1"]
        params = {}
        
        if dataset_id:
            query_parts.append("AND dataset_id = :dataset_id")
            params['dataset_id'] = dataset_id
            
        if workspace_name:
            query_parts.append("AND workspace_name = :workspace_name")
            params['workspace_name'] = workspace_name
            
        query_parts.append("ORDER BY created_at DESC")
        query_parts.append(") WHERE ROWNUM <= :limit")
        params['limit'] = limit
        
        query = " ".join(query_parts)
        rows = await db_adapter._execute(query, params)
        
        metadata_list = []
        for row in rows:
            metadata_list.append(db_adapter._row_to_dict(row))
            
        # Group by dataset for organization
        datasets = {}
        for meta in metadata_list:
            ds_id = meta.get('dataset_id')
            if ds_id not in datasets:
                datasets[ds_id] = {
                    'dataset_id': ds_id,
                    'workspaces': {}
                }
            
            ws_name = meta.get('workspace_name', 'default')
            if ws_name not in datasets[ds_id]['workspaces']:
                datasets[ds_id]['workspaces'][ws_name] = []
                
            datasets[ds_id]['workspaces'][ws_name].append(meta)
        
        return {
            "metadata": metadata_list,
            "grouped_by_workspace": datasets,
            "total_training_sessions": len(metadata_list)
        }
        
    except Exception as e:
        logger.error(f"Error fetching training metadata: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metadata/by-workspace")
async def get_metadata_by_workspace():
    """Get comprehensive training metadata grouped by dataset and workspace"""
    try:
        db_adapter = get_database_adapter()
        
        # Get all datasets
        datasets_query = "SELECT id, name FROM datasets ORDER BY created_at DESC"
        dataset_rows = await db_adapter._execute(datasets_query)
        
        result = []
        
        for ds_row in dataset_rows:
            ds_id = ds_row[0]
            ds_name = ds_row[1]
            
            # Get workspace states for this dataset
            ws_query = """
            SELECT state_name, created_at, state_size_kb
            FROM workspace_states
            WHERE dataset_id = :dataset_id
            ORDER BY created_at DESC
            """
            ws_rows = await db_adapter._execute(ws_query, {'dataset_id': ds_id})
            
            workspaces = []
            for ws_row in ws_rows:
                ws_name = ws_row[0]
                ws_created = ws_row[1]
                ws_size = ws_row[2]
                
                # Get training runs for this workspace
                training_query = """
                SELECT *
                FROM training_metadata
                WHERE dataset_id = :dataset_id
                AND workspace_name = :workspace_name
                ORDER BY created_at DESC
                """
                training_rows = await db_adapter._execute(
                    training_query,
                    {'dataset_id': ds_id, 'workspace_name': ws_name}
                )
                
                training_runs = []
                for tr_row in training_rows:
                    training_runs.append(db_adapter._row_to_dict(tr_row))
                
                workspaces.append({
                    'workspace_name': ws_name,
                    'created_at': ws_created.isoformat() if ws_created else None,
                    'size_kb': ws_size,
                    'training_runs': training_runs,
                    'total_models': len(training_runs)
                })
            
            result.append({
                'dataset_id': ds_id,
                'dataset_name': ds_name,
                'workspaces': workspaces,
                'total_workspaces': len(workspaces)
            })
        
        return {
            'datasets': result,
            'total_datasets': len(result)
        }
        
    except Exception as e:
        logger.error(f"Error fetching workspace metadata: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
