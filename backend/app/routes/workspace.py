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
        
        # Return a clean copy without any MongoDB-specific fields
        clean_workspace = {
            "id": workspace["id"],
            "name": workspace["name"],
            "description": workspace["description"],
            "tags": workspace["tags"],
            "created_at": workspace["created_at"],
            "updated_at": workspace["updated_at"],
            "dataset_count": workspace["dataset_count"],
            "training_count": workspace["training_count"]
        }
        
        return {"workspace": clean_workspace, "message": "Workspace created successfully"}
    
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


@router.get("/{workspace_id}/holistic-score")
async def get_holistic_workspace_score(workspace_id: str):
    """
    Calculate holistic performance score for workspace
    
    Aggregates all model training results and provides:
    - Overall performance score (0-100)
    - Average model accuracy
    - Best performing model
    - Improvement trend
    - Training activity level
    """
    try:
        db_adapter = get_db()
        
        # Verify workspace exists
        workspace = await db_adapter.get_workspace(workspace_id)
        if not workspace:
            raise HTTPException(404, "Workspace not found")
        
        # Get all training metadata for this workspace
        training_history = await db_adapter.get_workspace_training_history(workspace_id)
        
        if not training_history or len(training_history) == 0:
            return {
                "workspace_id": workspace_id,
                "score": 0,
                "grade": "N/A",
                "message": "No training data available",
                "details": {
                    "avg_accuracy": 0,
                    "best_model": None,
                    "training_count": 0,
                    "trend": "no_data"
                }
            }
        
        # Extract scores from training history
        scores = []
        for training in training_history:
            metrics = training.get("metrics", {})
            # Handle both regression (r2_score) and classification (accuracy)
            score = metrics.get("r2_score") or metrics.get("accuracy") or 0
            scores.append(score)
        
        # Calculate metrics
        avg_accuracy = sum(scores) / len(scores) if scores else 0
        best_score = max(scores) if scores else 0
        training_count = len(training_history)
        
        # Find best model
        best_model_info = None
        if training_history:
            best_training = max(
                training_history,
                key=lambda t: (t.get("metrics", {}).get("r2_score") or 
                              t.get("metrics", {}).get("accuracy") or 0)
            )
            best_model_info = {
                "model_type": best_training.get("model_type"),
                "score": (best_training.get("metrics", {}).get("r2_score") or 
                         best_training.get("metrics", {}).get("accuracy") or 0),
                "problem_type": best_training.get("problem_type")
            }
        
        # Calculate improvement trend (compare recent vs historical)
        improvement_trend = 0
        if len(scores) >= 5:
            recent_avg = sum(scores[-5:]) / 5
            historical_avg = sum(scores[:-5]) / len(scores[:-5]) if len(scores) > 5 else avg_accuracy
            improvement_trend = (recent_avg - historical_avg) / max(historical_avg, 0.01)
        
        trend_label = "improving" if improvement_trend > 0.05 else "declining" if improvement_trend < -0.05 else "stable"
        
        # Calculate holistic score (0-100)
        # Weighted formula:
        # - 40% average accuracy
        # - 30% best model score
        # - 20% improvement trend (normalized)
        # - 10% training activity (bonus for more training runs)
        
        activity_bonus = min(training_count / 20, 1.0)  # Cap at 20 runs for max bonus
        trend_component = max(min(improvement_trend, 0.2), -0.2) + 0.2  # Normalize -0.2 to 0.4 -> 0 to 0.6
        
        holistic_score = (
            avg_accuracy * 0.4 +
            best_score * 0.3 +
            (trend_component / 0.6) * 0.2 +  # Normalize trend to 0-1 range
            activity_bonus * 0.1
        ) * 100
        
        holistic_score = round(max(0, min(100, holistic_score)), 2)
        
        # Determine grade
        if holistic_score >= 90:
            grade = "A+"
        elif holistic_score >= 80:
            grade = "A"
        elif holistic_score >= 70:
            grade = "B"
        elif holistic_score >= 60:
            grade = "C"
        else:
            grade = "D"
        
        logger.info(f"Calculated holistic score for workspace {workspace_id}: {holistic_score} ({grade})")
        
        return {
            "workspace_id": workspace_id,
            "workspace_name": workspace.get("name"),
            "score": holistic_score,
            "grade": grade,
            "details": {
                "avg_accuracy": round(avg_accuracy, 4),
                "best_model": best_model_info,
                "training_count": training_count,
                "trend": trend_label,
                "improvement_rate": round(improvement_trend * 100, 2)  # As percentage
            },
            "interpretation": {
                "score_meaning": f"This workspace has {'excellent' if holistic_score >= 80 else 'good' if holistic_score >= 60 else 'moderate' if holistic_score >= 40 else 'low'} overall performance",
                "recommendation": (
                    "Continue training with current approach" if holistic_score >= 80 else
                    "Try different models or feature engineering" if holistic_score >= 60 else
                    "Consider data quality improvements and hyperparameter tuning" if holistic_score >= 40 else
                    "Review data quality, feature selection, and problem formulation"
                )
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to calculate holistic score: {str(e)}", exc_info=True)
        raise HTTPException(500, f"Failed to calculate score: {str(e)}")



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
