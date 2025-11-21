"""
Workspace Management Routes
Organize datasets, track training history, and compare models over time
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from datetime import datetime
from uuid import uuid4
import logging

from app.database.db_helper import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workspace", tags=["workspace"])


@router.post("/create")
async def create_workspace(request: Dict[str, Any]):
    """
    Create a new workspace
    
    Request: {
        "name": "Sales Forecasting Q4 2024",
        "description": "Quarterly sales prediction models",
        "tags": ["sales", "forecasting"]
    }
    """
    try:
        name = request.get("name", "").strip()
        if not name:
            raise HTTPException(400, "Workspace name is required")
        
        db_adapter = get_db()
        
        workspace = {
            "id": str(uuid4()),
            "name": name,
            "description": request.get("description", ""),
            "tags": request.get("tags", []),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "dataset_count": 0,
            "training_count": 0
        }
        
        await db_adapter.create_workspace(workspace)
        logger.info(f"✅ Created workspace: {name}")
        
        return {"workspace": workspace, "message": "Workspace created successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create workspace: {str(e)}", exc_info=True)
        raise HTTPException(500, f"Failed to create workspace: {str(e)}")


@router.get("/list")
async def list_workspaces():
    """Get all workspaces"""
    try:
        db_adapter = get_db()
        workspaces = await db_adapter.get_workspaces()
        return {"workspaces": workspaces}
    except Exception as e:
        logger.error(f"Failed to list workspaces: {str(e)}", exc_info=True)
        raise HTTPException(500, f"Failed to list workspaces: {str(e)}")


@router.get("/{workspace_id}")
async def get_workspace(workspace_id: str):
    """Get workspace details with datasets and training history"""
    try:
        db_adapter = get_db()
        workspace = await db_adapter.get_workspace(workspace_id)
        
        if not workspace:
            raise HTTPException(404, "Workspace not found")
        
        # Get datasets in this workspace
        datasets = await db_adapter.get_workspace_datasets(workspace_id)
        
        # Get training history for this workspace
        training_history = await db_adapter.get_workspace_training_history(workspace_id)
        
        return {
            "workspace": workspace,
            "datasets": datasets,
            "training_history": training_history
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workspace: {str(e)}", exc_info=True)
        raise HTTPException(500, f"Failed to get workspace: {str(e)}")


@router.post("/{workspace_id}/add-dataset")
async def add_dataset_to_workspace(workspace_id: str, request: Dict[str, Any]):
    """Add a dataset to workspace"""
    try:
        dataset_id = request.get("dataset_id")
        if not dataset_id:
            raise HTTPException(400, "dataset_id is required")
        
        db_adapter = get_db()
        
        # Verify workspace exists
        workspace = await db_adapter.get_workspace(workspace_id)
        if not workspace:
            raise HTTPException(404, "Workspace not found")
        
        # Update dataset with workspace_id
        await db_adapter.update_dataset(dataset_id, {"workspace_id": workspace_id})
        
        # Update workspace dataset count
        await db_adapter.increment_workspace_dataset_count(workspace_id)
        
        logger.info(f"✅ Added dataset {dataset_id} to workspace {workspace_id}")
        
        return {"message": "Dataset added to workspace successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add dataset to workspace: {str(e)}", exc_info=True)
        raise HTTPException(500, f"Failed to add dataset: {str(e)}")


@router.get("/{workspace_id}/performance-trends")
async def get_performance_trends(workspace_id: str):
    """
    Get 30-day performance trends for models in this workspace
    Shows how models perform over time
    """
    try:
        db_adapter = get_db()
        
        workspace = await db_adapter.get_workspace(workspace_id)
        if not workspace:
            raise HTTPException(404, "Workspace not found")
        
        # Get all training runs in this workspace
        training_history = await db_adapter.get_workspace_training_history(workspace_id)
        
        # Group by model type and calculate trends
        model_trends = {}
        for training in training_history:
            model_type = training.get("model_type", "Unknown")
            if model_type not in model_trends:
                model_trends[model_type] = []
            
            model_trends[model_type].append({
                "timestamp": training.get("timestamp"),
                "metrics": training.get("metrics", {}),
                "dataset_id": training.get("dataset_id")
            })
        
        # Calculate best model recommendation
        best_model = None
        best_score = -float('inf')
        
        for model_type, runs in model_trends.items():
            if runs:
                avg_score = sum(r["metrics"].get("r2_score", 0) or r["metrics"].get("accuracy", 0) for r in runs) / len(runs)
                if avg_score > best_score:
                    best_score = avg_score
                    best_model = {
                        "model_type": model_type,
                        "avg_score": avg_score,
                        "total_runs": len(runs)
                    }
        
        return {
            "workspace_id": workspace_id,
            "model_trends": model_trends,
            "best_model_recommendation": best_model,
            "total_training_runs": len(training_history)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get performance trends: {str(e)}", exc_info=True)
        raise HTTPException(500, f"Failed to get trends: {str(e)}")


@router.delete("/{workspace_id}")
async def delete_workspace(workspace_id: str):
    """Delete a workspace"""
    try:
        db_adapter = get_db()
        
        workspace = await db_adapter.get_workspace(workspace_id)
        if not workspace:
            raise HTTPException(404, "Workspace not found")
        
        await db_adapter.delete_workspace(workspace_id)
        logger.info(f"✅ Deleted workspace: {workspace_id}")
        
        return {"message": "Workspace deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete workspace: {str(e)}", exc_info=True)
        raise HTTPException(500, f"Failed to delete workspace: {str(e)}")
