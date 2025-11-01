"""
Training Metadata Routes
Handles training history and metadata
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from app.database.mongodb import db

router = APIRouter(prefix="/training", tags=["training"])


@router.get("/metadata")
async def get_training_metadata():
    """Get comprehensive training metadata for all datasets"""
    try:
        # Get all datasets
        datasets_cursor = db.datasets.find({}, {"_id": 0})
        datasets = await datasets_cursor.to_list(length=None)
        
        # Get all saved states
        states_cursor = db.analysis_states.find({}, {"_id": 0})
        saved_states = await states_cursor.to_list(length=None)
        
        # Organize metadata
        metadata = []
        
        for dataset in datasets:
            dataset_id = dataset.get("id")
            dataset_name = dataset.get("name")
            
            # Get workspaces for this dataset
            dataset_states = [s for s in saved_states if s.get("dataset_id") == dataset_id]
            
            # Calculate training metadata
            training_count = dataset.get("training_count", 0)
            last_trained = dataset.get("last_trained_at")
            
            # Get model scores (from latest workspace if available)
            initial_scores = {}
            current_scores = {}
            initial_score = None  # Single score for frontend compatibility
            current_score = None  # Single score for frontend compatibility
            
            if dataset_states:
                # Sort states by creation date
                sorted_states = sorted(
                    dataset_states,
                    key=lambda x: x.get("created_at", ""),
                    reverse=False  # Oldest first
                )
                
                # Get initial state (oldest)
                if len(sorted_states) > 0:
                    first_state = sorted_states[0]
                    first_analysis = first_state.get("analysis_data", {})
                    first_models = first_analysis.get("models", []) or first_analysis.get("ml_models", [])
                    
                    if first_models:
                        # Get best model from first training
                        best_first = max(first_models, key=lambda x: x.get("r2_score", 0))
                        initial_score = best_first.get("r2_score", 0)
                        
                        for model in first_models:
                            model_name = model.get("model_name")
                            r2_score = model.get("r2_score", 0)
                            initial_scores[model_name] = r2_score
                
                # Get latest state
                latest_state = sorted_states[-1]  # Most recent
                latest_analysis = latest_state.get("analysis_data", {})
                latest_models = latest_analysis.get("models", []) or latest_analysis.get("ml_models", [])
                
                if latest_models:
                    # Get best model from latest training
                    best_latest = max(latest_models, key=lambda x: x.get("r2_score", 0))
                    current_score = best_latest.get("r2_score", 0)
                    
                    for model in latest_models:
                        model_name = model.get("model_name")
                        r2_score = model.get("r2_score", 0)
                        current_scores[model_name] = r2_score
            
            # Calculate improvement percentage
            improvement_percentage = 0
            if initial_score and current_score and initial_score > 0:
                improvement_percentage = ((current_score - initial_score) / initial_score) * 100
            
            metadata.append({
                "dataset_id": dataset_id,
                "dataset_name": dataset_name,
                "training_count": training_count,
                "last_trained": last_trained,
                "initial_scores": initial_scores,
                "current_scores": current_scores,
                "initial_score": initial_score if initial_score is not None else 0,  # Frontend expects this
                "current_score": current_score if current_score is not None else 0,  # Frontend expects this
                "improvement_percentage": improvement_percentage,  # Frontend expects this
                "improvement": {
                    model: ((current_scores.get(model, 0) - initial_scores.get(model, 0)) / initial_scores.get(model, 1)) * 100
                    if initial_scores.get(model, 0) > 0 else 0
                    for model in current_scores.keys()
                },
                "workspaces": [
                    {
                        "workspace_name": state.get("state_name"),
                        "saved_at": state.get("created_at"),
                        "workspace_id": state.get("id")
                    }
                    for state in dataset_states
                ],
                "row_count": dataset.get("row_count"),
                "column_count": dataset.get("column_count")
            })
        
        return {"metadata": metadata}
        
    except Exception as e:
        raise HTTPException(500, f"Failed to fetch training metadata: {str(e)}")
