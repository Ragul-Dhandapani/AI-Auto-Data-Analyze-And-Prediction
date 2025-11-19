"""
Intelligent Prediction API Route
Exposes the Enhanced MCP functionality via REST API
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging

router = APIRouter(prefix="/intelligent-prediction", tags=["Intelligent Prediction"])
logger = logging.getLogger(__name__)


class IntelligentPredictionRequest(BaseModel):
    data_source: Dict[str, Any]  # {'type': 'file', 'path': '...'} or {'type': 'oracle', 'config': {...}, 'table': '...'}
    user_prompt: str  # Natural language description
    target_column: str
    feature_columns: List[str]
    models_to_train: Optional[List[str]] = None  # Default: ['random_forest', 'xgboost']
    problem_type: Optional[str] = None  # 'regression' or 'classification', auto-detect if None
    include_forecasting: bool = True
    include_insights: bool = True
    test_size: float = 0.2


@router.post("/train-and-predict")
async def train_and_predict(request: IntelligentPredictionRequest):
    """
    Complete ML pipeline: Train models, make predictions, generate forecasts and insights
    
    Example Request:
    ```json
    {
      "data_source": {
        "type": "file",
        "path": "/data/customers.csv"
      },
      "user_prompt": "Predict customer churn to run retention campaigns",
      "target_column": "churned",
      "feature_columns": ["purchase_freq", "support_tickets", "account_age"],
      "models_to_train": ["random_forest", "xgboost"],
      "include_forecasting": true,
      "include_insights": true
    }
    ```
    
    Returns:
    - training_summary
    - predictions
    - model_comparison
    - best_model
    - feature_importance
    - forecasting (if enabled)
    - insights (if enabled)
    """
    
    try:
        from app.mcp.intelligent_prediction_mcp import IntelligentPredictionMCP
        
        logger.info(f"📥 Intelligent Prediction Request: {request.user_prompt}")
        
        # Initialize MCP
        mcp = IntelligentPredictionMCP()
        
        # Run pipeline
        result = mcp.train_and_predict(
            data_source=request.data_source,
            user_prompt=request.user_prompt,
            target_column=request.target_column,
            feature_columns=request.feature_columns,
            models_to_train=request.models_to_train,
            problem_type=request.problem_type,
            include_forecasting=request.include_forecasting,
            include_insights=request.include_insights,
            test_size=request.test_size
        )
        
        logger.info(f"✅ Pipeline completed in {result['execution_time']:.1f}s")
        
        return {
            "status": "success",
            "data": result
        }
    
    except Exception as e:
        logger.error(f"❌ Intelligent Prediction failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.get("/available-models")
async def get_available_models():
    """
    Get list of available models for training
    
    Returns models for both regression and classification
    """
    try:
        from app.mcp.intelligent_prediction_mcp import IntelligentPredictionMCP
        
        mcp = IntelligentPredictionMCP()
        
        return {
            "status": "success",
            "data": {
                "regression_models": [k for k, v in mcp.REGRESSION_MODELS.items() if v is not None],
                "classification_models": [k for k, v in mcp.CLASSIFICATION_MODELS.items() if v is not None]
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quick-predict")
async def quick_predict(
    file_path: str,
    user_prompt: str,
    target_column: str,
    feature_columns: List[str]
):
    """
    Simplified endpoint for quick predictions
    Uses default settings (Random Forest + XGBoost, with forecasting and insights)
    
    Query Parameters:
    - file_path: Path to CSV file
    - user_prompt: What you want to predict
    - target_column: Column to predict
    - feature_columns: Comma-separated feature columns
    
    Example:
    ```
    POST /api/intelligent-prediction/quick-predict
    ?file_path=/data/customers.csv
    &user_prompt=Predict customer churn
    &target_column=churned
    &feature_columns=purchase_freq,support_tickets,account_age
    ```
    """
    try:
        from app.mcp.intelligent_prediction_mcp import IntelligentPredictionMCP
        
        mcp = IntelligentPredictionMCP()
        
        result = mcp.train_and_predict(
            data_source={'type': 'file', 'path': file_path},
            user_prompt=user_prompt,
            target_column=target_column,
            feature_columns=feature_columns,
            include_forecasting=True,
            include_insights=True
        )
        
        return {"status": "success", "data": result}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
