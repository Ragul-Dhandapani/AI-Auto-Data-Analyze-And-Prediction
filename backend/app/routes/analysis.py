"""
Analysis Routes
Handles data analysis, ML training, and visualization
"""
from fastapi import APIRouter, HTTPException
import pandas as pd
import numpy as np
from typing import Dict, Any
from datetime import datetime, timezone
from bson import ObjectId
import json
import uuid
import io

from app.models.pydantic_models import HolisticRequest, SaveStateRequest
from app.database.mongodb import db, fs
from app.services.data_service import generate_data_profile, get_correlation_matrix, clean_data
from app.services.ml_service import train_multiple_models, suggest_best_target_column
from app.services.visualization_service import generate_auto_charts
from app.services.chat_service import process_chat_message
import os

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/run")
async def run_analysis(request: Dict[str, Any]):
    """Run specific analysis type (profile or clean) - for DataProfiler component"""
    try:
        dataset_id = request.get("dataset_id")
        analysis_type = request.get("analysis_type", "profile")
        
        df = await load_dataframe(dataset_id)
        
        if analysis_type == "profile":
            # Return data profile
            profile = generate_data_profile(df)
            return profile
        
        elif analysis_type == "clean":
            # Run data cleaning
            cleaned_df, cleaning_report = clean_data(df)
            
            # Update dataset with cleaned data if changes were made
            if cleaning_report:
                # Store cleaned data
                dataset = await db.datasets.find_one({"id": dataset_id}, {"_id": 0})
                if dataset:
                    data_dict = cleaned_df.to_dict('records')
                    await db.datasets.update_one(
                        {"id": dataset_id},
                        {"$set": {
                            "data": data_dict,
                            "row_count": len(cleaned_df),
                            "updated_at": datetime.now(timezone.utc).isoformat()
                        }}
                    )
            
            return {
                "cleaning_report": cleaning_report,
                "rows_before": len(df),
                "rows_after": len(cleaned_df)
            }
        
        else:
            raise HTTPException(400, f"Unknown analysis type: {analysis_type}")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Analysis failed: {str(e)}")


async def load_dataframe(dataset_id: str) -> pd.DataFrame:
    """Helper function to load DataFrame from dataset"""
    dataset = await db.datasets.find_one({"id": dataset_id}, {"_id": 0})
    if not dataset:
        raise HTTPException(404, "Dataset not found")
    
    # Load data based on storage type
    if dataset.get("storage_type") == "gridfs":
        gridfs_file_id = dataset.get("gridfs_file_id")
        if gridfs_file_id:
            grid_out = await fs.open_download_stream(ObjectId(gridfs_file_id))
            data = await grid_out.read()
            if dataset["name"].endswith('.csv'):
                df = pd.read_csv(io.BytesIO(data))
            else:
                df = pd.read_excel(io.BytesIO(data))
        else:
            raise HTTPException(500, "GridFS file ID not found")
    else:
        df = pd.DataFrame(dataset.get("data", []))
    
    return df


@router.post("/holistic")
async def holistic_analysis(request: HolisticRequest):
    """Perform comprehensive analysis"""
    try:
        df = await load_dataframe(request.dataset_id)
        
        # Update training counter
        await db.datasets.update_one(
            {"id": request.dataset_id},
            {"$inc": {"training_count": 1}}
        )
        
        # 1. Data Profiling
        profile = generate_data_profile(df)
        
        # 2. Train ML Models
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        models_result = {"models": [], "message": "No numeric columns for ML training"}
        
        if len(numeric_cols) >= 2:
            # Suggest best target column
            target_col = suggest_best_target_column(df)
            if target_col:
                try:
                    models_result = train_multiple_models(df, target_col)
                except Exception as e:
                    models_result = {"models": [], "error": str(e)}
        
        # 3. Generate Auto Charts
        auto_charts = generate_auto_charts(df, max_charts=15)
        
        # 4. Correlation Analysis
        correlations = get_correlation_matrix(df)
        
        # 5. Generate AI insights (if LLM key available)
        insights = "Analysis complete. Explore the charts and model results above."
        llm_key = os.environ.get('EMERGENT_LLM_KEY')
        if llm_key:
            try:
                from emergentintegrations.llm.chat import LlmChat
                llm = LlmChat(api_key=llm_key, model="gpt-4o-mini")
                
                summary = {
                    "rows": len(df),
                    "columns": len(df.columns),
                    "numeric_columns": numeric_cols,
                    "top_correlations": correlations['correlations'][:3] if correlations['correlations'] else []
                }
                
                prompt = f"""Analyze this dataset and provide 3-4 key insights:
Dataset: {summary}

Provide concise, actionable insights."""
                
                insights = llm.send_user_message(prompt)
            except:
                pass
        
        # Get dataset info for training metadata
        dataset = await db.datasets.find_one({"id": request.dataset_id}, {"_id": 0})
        training_count = dataset.get("training_count", 1)
        last_trained_at = dataset.get("updated_at", datetime.now(timezone.utc).isoformat())
        
        # Build volume analysis from profile data
        volume_analysis = {
            "total_records": len(df),
            "by_dimensions": []
        }
        
        # Add categorical breakdown for volume analysis
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        for col in categorical_cols[:3]:  # Top 3 categorical columns
            value_counts = df[col].value_counts().to_dict()
            volume_analysis["by_dimensions"].append({
                "dimension": col,
                "breakdown": value_counts
            })
        
        return {
            "profile": profile,
            "models": models_result.get("models", []),
            "ml_models": models_result.get("models", []),  # Frontend expects ml_models
            "auto_charts": auto_charts,
            "correlations": correlations,
            "insights": insights,
            "training_info": models_result.get("training_info", {}),
            "volume_analysis": volume_analysis,  # Frontend expects volume_analysis
            "training_metadata": {
                "training_count": training_count,
                "last_trained_at": last_trained_at,
                "dataset_size": len(df)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Analysis failed: {str(e)}")


@router.post("/chat-action")
async def chat_action(request: Dict[str, Any]):
    """Handle chat-based analysis actions"""
    try:
        dataset_id = request.get("dataset_id")
        message = request.get("message", "")
        conversation_history = request.get("conversation_history", [])
        
        df = await load_dataframe(dataset_id)
        
        # Get LLM key
        llm_key = os.environ.get('EMERGENT_LLM_KEY')
        
        # Process message
        result = process_chat_message(df, message, conversation_history, llm_key)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Chat action failed: {str(e)}")


@router.post("/save-state")
async def save_analysis_state(request: SaveStateRequest):
    """Save analysis state with GridFS for large states"""
    try:
        state_id = str(uuid.uuid4())
        
        # Prepare full state data
        full_state_data = {
            "analysis_data": request.analysis_data,
            "chat_history": request.chat_history
        }
        
        # Calculate size
        state_json = json.dumps(full_state_data)
        state_size = len(state_json.encode('utf-8'))
        
        # Choose storage method
        if state_size > 10 * 1024 * 1024:  # 10MB threshold
            # Store in GridFS
            file_id = await fs.upload_from_stream(
                f"workspace_{state_id}.json",
                state_json.encode('utf-8'),
                metadata={
                    "type": "workspace_state",
                    "state_id": state_id,
                    "dataset_id": request.dataset_id,
                    "state_name": request.state_name
                }
            )
            
            state_doc = {
                "id": state_id,
                "dataset_id": request.dataset_id,
                "state_name": request.state_name,
                "storage_type": "gridfs",
                "gridfs_file_id": str(file_id),
                "size_bytes": state_size,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        else:
            # Store directly
            state_doc = {
                "id": state_id,
                "dataset_id": request.dataset_id,
                "state_name": request.state_name,
                "storage_type": "direct",
                "analysis_data": request.analysis_data,
                "chat_history": request.chat_history,
                "size_bytes": state_size,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        
        await db.analysis_states.insert_one(state_doc)
        
        return {
            "state_id": state_id,
            "message": f"Analysis state '{request.state_name}' saved successfully",
            "storage_type": state_doc["storage_type"],
            "size_mb": round(state_size / (1024 * 1024), 2)
        }
        
    except Exception as e:
        raise HTTPException(500, f"Failed to save state: {str(e)}")


@router.get("/load-state/{state_id}")
async def load_analysis_state(state_id: str):
    """Load saved analysis state"""
    try:
        state = await db.analysis_states.find_one({"id": state_id}, {"_id": 0})
        if not state:
            raise HTTPException(404, "Analysis state not found")
        
        # Load from GridFS if needed
        if state.get("storage_type") == "gridfs":
            gridfs_file_id = state.get("gridfs_file_id")
            if gridfs_file_id:
                grid_out = await fs.open_download_stream(ObjectId(gridfs_file_id))
                data = await grid_out.read()
                full_state_data = json.loads(data.decode('utf-8'))
                
                state["analysis_data"] = full_state_data.get("analysis_data", {})
                state["chat_history"] = full_state_data.get("chat_history", [])
                state.pop("gridfs_file_id", None)
                state.pop("storage_type", None)
        
        return state
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to load state: {str(e)}")


@router.get("/saved-states/{dataset_id}")
async def get_saved_states(dataset_id: str):
    """Get all saved states for a dataset"""
    try:
        cursor = db.analysis_states.find({"dataset_id": dataset_id}, {"_id": 0})
        states = await cursor.to_list(length=None)
        return {"states": states}
    except Exception as e:
        raise HTTPException(500, f"Failed to fetch saved states: {str(e)}")


@router.delete("/delete-state/{state_id}")
async def delete_analysis_state(state_id: str):
    """Delete saved analysis state"""
    try:
        state = await db.analysis_states.find_one({"id": state_id}, {"_id": 0})
        if not state:
            raise HTTPException(404, "Analysis state not found")
        
        # Delete GridFS file if exists
        if state.get("storage_type") == "gridfs" and state.get("gridfs_file_id"):
            try:
                await fs.delete(ObjectId(state["gridfs_file_id"]))
            except:
                pass
        
        # Delete metadata
        result = await db.analysis_states.delete_one({"id": state_id})
        if result.deleted_count == 0:
            raise HTTPException(404, "Analysis state not found")
        
        return {"message": "Analysis state deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to delete state: {str(e)}")
