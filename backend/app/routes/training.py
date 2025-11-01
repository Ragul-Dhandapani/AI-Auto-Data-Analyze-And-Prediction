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
            
            if dataset_states:
                # Get latest state
                latest_state = sorted(
                    dataset_states, 
                    key=lambda x: x.get("created_at", ""), 
                    reverse=True
                )[0]
                
                # Extract model scores
                analysis_data = latest_state.get("analysis_data", {})
                models = analysis_data.get("models", [])
                
                for model in models:
                    model_name = model.get("model_name")
                    r2_score = model.get("r2_score", 0)
                    current_scores[model_name] = r2_score
            
            metadata.append({
                "dataset_id": dataset_id,
                "dataset_name": dataset_name,
                "training_count": training_count,
                "last_trained": last_trained,
                "initial_scores": initial_scores,
                "current_scores": current_scores,
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
