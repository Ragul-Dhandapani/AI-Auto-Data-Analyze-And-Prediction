"""
Model Management Routes
Handles model selection, recommendations, and catalog
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/models", tags=["models"])


@router.get("/available")
async def get_available_models(problem_type: str):
    """
    Get list of available models for a problem type
    
    Args:
        problem_type: classification, regression, clustering, dimensionality, anomaly, auto
    
    Returns:
        List of available models with descriptions
    """
    try:
        from app.services.ml_service_enhanced import get_available_models
        
        # Handle "auto" problem type by returning both classification and regression models
        if problem_type == "auto":
            classification_models = get_available_models("classification")
            regression_models = get_available_models("regression")
            models = classification_models + regression_models
            actual_problem_type = "classification/regression"
        else:
            models = get_available_models(problem_type)
            actual_problem_type = problem_type
        
        return {
            "problem_type": actual_problem_type,
            "models": models,
            "count": len(models)
        }
        
    except Exception as e:
        logger.error(f"Failed to get available models: {str(e)}")
        raise HTTPException(500, f"Failed to get models: {str(e)}")


@router.post("/recommend")
async def recommend_models(request: Dict[str, Any]):
    """
    Get AI-powered model recommendations
    
    Body:
        {
            "problem_type": "classification|regression",
            "data_summary": {
                "row_count": 1000,
                "feature_count": 20,
                "missing_percentage": 5
            }
        }
    
    Returns:
        Recommended models with reasoning
    """
    try:
        problem_type = request.get("problem_type")
        data_summary = request.get("data_summary", {})
        
        # Use Azure OpenAI for recommendations
        from app.services.azure_openai_service import get_azure_openai_service
        
        azure_service = get_azure_openai_service()
        
        if azure_service.is_available():
            recommendations = await azure_service.recommend_models(
                data_summary=data_summary,
                problem_type=problem_type
            )
        else:
            # Fallback to rule-based recommendations
            from app.services.ml_service_enhanced import get_model_recommendations
            import pandas as pd
            
            # Create dummy data for recommendations
            X = pd.DataFrame([[0] * data_summary.get('feature_count', 10)])
            y = pd.Series([0] * data_summary.get('row_count', 100))
            
            model_keys = get_model_recommendations(X, y, problem_type)
            recommendations = {
                "recommendations": model_keys,
                "reasoning": "Rule-based recommendations (Azure OpenAI unavailable)",
                "expected_performance": "medium"
            }
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Failed to recommend models: {str(e)}")
        raise HTTPException(500, f"Failed to recommend: {str(e)}")


@router.get("/catalog")
async def get_model_catalog():
    """
    Get complete model catalog with all categories
    
    Returns:
        Complete catalog of all available models
    """
    try:
        from app.services.ml_service_enhanced import (
            CLASSIFICATION_MODELS,
            REGRESSION_MODELS,
            CLUSTERING_MODELS,
            DIMENSIONALITY_MODELS,
            ANOMALY_MODELS
        )
        
        catalog = {
            "classification": [
                {
                    "key": k,
                    "name": v["name"],
                    "description": v["description"]
                }
                for k, v in CLASSIFICATION_MODELS.items()
            ],
            "regression": [
                {
                    "key": k,
                    "name": v["name"],
                    "description": v["description"]
                }
                for k, v in REGRESSION_MODELS.items()
            ],
            "clustering": [
                {
                    "key": k,
                    "name": v["name"],
                    "description": v["description"]
                }
                for k, v in CLUSTERING_MODELS.items()
            ],
            "dimensionality": [
                {
                    "key": k,
                    "name": v["name"],
                    "description": v["description"]
                }
                for k, v in DIMENSIONALITY_MODELS.items()
            ],
            "anomaly": [
                {
                    "key": k,
                    "name": v["name"],
                    "description": v["description"]
                }
                for k, v in ANOMALY_MODELS.items()
            ]
        }
        
        total_models = sum(len(v) for v in catalog.values())
        
        return {
            "catalog": catalog,
            "total_models": total_models,
            "categories": list(catalog.keys())
        }
        
    except Exception as e:
        logger.error(f"Failed to get catalog: {str(e)}")
        raise HTTPException(500, f"Failed to get catalog: {str(e)}")
