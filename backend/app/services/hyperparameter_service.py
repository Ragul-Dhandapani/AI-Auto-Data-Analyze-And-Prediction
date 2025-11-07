"""
Hyperparameter Tuning Service with Azure OpenAI Integration
Provides grid search, random search, and AI-powered hyperparameter recommendations
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List
import logging
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
import xgboost as xgb
from sklearn.metrics import make_scorer, accuracy_score, mean_squared_error, r2_score

try:
    import lightgbm as lgb
    HAS_LIGHTGBM = True
except ImportError:
    HAS_LIGHTGBM = False
    logging.warning("LightGBM not available")

logger = logging.getLogger(__name__)


def get_default_hyperparameters(model_type: str, problem_type: str) -> Dict[str, Any]:
    """
    Get default hyperparameter ranges for different models
    ULTRA-OPTIMIZED: Minimal grid for maximum speed (< 60s target)
    
    Args:
        model_type: "random_forest", "xgboost", "lightgbm"
        problem_type: "regression" or "classification"
    
    Returns:
        Dictionary of hyperparameter ranges
    """
    if model_type == "random_forest":
        return {
            "n_estimators": [50, 100],       # Reduced to 2 options (from 3)
            "max_depth": [10, None],         # Reduced to 2 options (from 3)
            "min_samples_split": [2, 5],     # Keep 2 options
            "max_features": ["sqrt"]         # Reduced to 1 option (most effective)
        }
    
    elif model_type == "xgboost":
        return {
            "n_estimators": [50, 100],           # Reduced to 2 options (from 3)
            "max_depth": [3, 5],                 # Reduced to 2 options (from 3)
            "learning_rate": [0.1, 0.2],         # Reduced to 2 options (from 3)
            "subsample": [0.8],                  # Reduced to 1 option
            "colsample_bytree": [0.8]            # Reduced to 1 option
        }
    
    elif model_type == "lightgbm" and HAS_LIGHTGBM:
        return {
            "n_estimators": [50, 100],         # Reduced to 2
            "max_depth": [3, 5],               # Reduced to 2 
            "learning_rate": [0.05, 0.1],      # Reduced to 2
            "num_leaves": [31, 50],            # Reduced to 2
            "subsample": [0.8]                 # Reduced to 1
        }
    
    return {}


def tune_hyperparameters_grid(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    model_type: str,
    problem_type: str,
    param_grid: Dict[str, List] = None,
    cv: int = 2  # OPTIMIZED: Reduced from 3 to 2 for speed
) -> Dict[str, Any]:
    """
    Perform grid search hyperparameter tuning
    ULTRA-OPTIMIZED: CV=2, minimal param grid for < 60s execution
    
    Args:
        X_train: Training features
        y_train: Training target
        model_type: Type of model to tune
        problem_type: "regression" or "classification"
        param_grid: Custom parameter grid (if None, use defaults)
        cv: Number of cross-validation folds (default 2 for speed)
    
    Returns:
        Dictionary with best parameters and scores
    """
    try:
        # Get parameter grid
        if param_grid is None:
            param_grid = get_default_hyperparameters(model_type, problem_type)
        
        # Select base model
        if model_type == "random_forest":
            if problem_type == "classification":
                base_model = RandomForestClassifier(random_state=42, n_jobs=-1)
                scoring = 'accuracy'
            else:
                base_model = RandomForestRegressor(random_state=42, n_jobs=-1)
                scoring = 'r2'
        
        elif model_type == "xgboost":
            if problem_type == "classification":
                base_model = xgb.XGBClassifier(random_state=42, n_jobs=-1, eval_metric='logloss')
                scoring = 'accuracy'
            else:
                base_model = xgb.XGBRegressor(random_state=42, n_jobs=-1)
                scoring = 'r2'
        
        elif model_type == "lightgbm" and HAS_LIGHTGBM:
            if problem_type == "classification":
                base_model = lgb.LGBMClassifier(random_state=42, n_jobs=-1, verbose=-1)
                scoring = 'accuracy'
            else:
                base_model = lgb.LGBMRegressor(random_state=42, n_jobs=-1, verbose=-1)
                scoring = 'r2'
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
        
        # Perform grid search
        grid_search = GridSearchCV(
            base_model,
            param_grid,
            cv=cv,
            scoring=scoring,
            n_jobs=-1,
            verbose=0
        )
        
        grid_search.fit(X_train, y_train)
        
        return {
            "best_params": grid_search.best_params_,
            "best_score": float(grid_search.best_score_),
            "cv_results": {
                "mean_test_score": grid_search.cv_results_['mean_test_score'].tolist(),
                "params": [str(p) for p in grid_search.cv_results_['params']]
            },
            "model": grid_search.best_estimator_
        }
    
    except Exception as e:
        logging.error(f"Grid search failed: {str(e)}")
        return {"error": str(e)}


def tune_hyperparameters_random(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    model_type: str,
    problem_type: str,
    param_distributions: Dict[str, List] = None,
    n_iter: int = 10,  # OPTIMIZED: Reduced from 20 to 10
    cv: int = 2        # OPTIMIZED: Reduced from 3 to 2
) -> Dict[str, Any]:
    """
    Perform random search hyperparameter tuning
    ULTRA-OPTIMIZED: n_iter=10, CV=2 for maximum speed
    
    Args:
        X_train: Training features
        y_train: Training target
        model_type: Type of model to tune
        problem_type: "regression" or "classification"
        param_distributions: Custom parameter distributions
        n_iter: Number of random combinations to try (default 10)
        cv: Number of cross-validation folds (default 2)
    
    Returns:
        Dictionary with best parameters and scores
    """
    try:
        # Get parameter distributions
        if param_distributions is None:
            param_distributions = get_default_hyperparameters(model_type, problem_type)
        
        # Select base model
        if model_type == "random_forest":
            if problem_type == "classification":
                base_model = RandomForestClassifier(random_state=42, n_jobs=-1)
                scoring = 'accuracy'
            else:
                base_model = RandomForestRegressor(random_state=42, n_jobs=-1)
                scoring = 'r2'
        
        elif model_type == "xgboost":
            if problem_type == "classification":
                base_model = xgb.XGBClassifier(random_state=42, n_jobs=-1, eval_metric='logloss')
                scoring = 'accuracy'
            else:
                base_model = xgb.XGBRegressor(random_state=42, n_jobs=-1)
                scoring = 'r2'
        
        elif model_type == "lightgbm" and HAS_LIGHTGBM:
            if problem_type == "classification":
                base_model = lgb.LGBMClassifier(random_state=42, n_jobs=-1, verbose=-1)
                scoring = 'accuracy'
            else:
                base_model = lgb.LGBMRegressor(random_state=42, n_jobs=-1, verbose=-1)
                scoring = 'r2'
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
        
        # Perform random search
        random_search = RandomizedSearchCV(
            base_model,
            param_distributions,
            n_iter=n_iter,
            cv=cv,
            scoring=scoring,
            n_jobs=-1,
            verbose=0,
            random_state=42
        )
        
        random_search.fit(X_train, y_train)
        
        return {
            "best_params": random_search.best_params_,
            "best_score": float(random_search.best_score_),
            "cv_results": {
                "mean_test_score": random_search.cv_results_['mean_test_score'].tolist(),
                "params": [str(p) for p in random_search.cv_results_['params']]
            },
            "model": random_search.best_estimator_
        }
    
    except Exception as e:
        logging.error(f"Random search failed: {str(e)}")
        return {"error": str(e)}



async def get_ai_hyperparameter_recommendations(
    model_type: str,
    problem_type: str,
    data_summary: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Get AI-powered hyperparameter recommendations using Azure OpenAI
    
    Args:
        model_type: Type of model ("random_forest", "xgboost", "lightgbm")
        problem_type: "regression" or "classification"
        data_summary: Dataset characteristics (row_count, feature_count, etc.)
    
    Returns:
        AI recommendations for optimal hyperparameters
    """
    try:
        from app.services.azure_openai_service import get_azure_openai_service
        
        azure_service = get_azure_openai_service()
        
        if not azure_service.is_available():
            logger.warning("Azure OpenAI not available, using default parameters")
            return {
                "recommended_params": get_default_hyperparameters(model_type, problem_type),
                "reasoning": "Azure OpenAI unavailable - using default parameters",
                "tuning_strategy": "grid_search"
            }
        
        # Prepare context for AI
        context = f"""
Dataset Characteristics:
- Rows: {data_summary.get('row_count', 'unknown')}
- Features: {data_summary.get('feature_count', 'unknown')}
- Problem Type: {problem_type}
- Model: {model_type}
- Missing Data: {data_summary.get('missing_percentage', 0)}%

Task: Recommend optimal hyperparameters for {model_type} model.
Consider dataset size, feature count, and problem complexity.
Provide specific parameter ranges for tuning.
"""
        
        response = await azure_service.generate_completion(
            prompt=context,
            max_tokens=800,
            temperature=0.3
        )
        
        return {
            "recommended_params": get_default_hyperparameters(model_type, problem_type),
            "ai_reasoning": response,
            "tuning_strategy": "grid_search" if data_summary.get('row_count', 0) < 10000 else "random_search",
            "estimated_time": "< 60 seconds"
        }
    
    except Exception as e:
        logger.error(f"AI recommendations failed: {str(e)}")
        return {
            "recommended_params": get_default_hyperparameters(model_type, problem_type),
            "reasoning": f"Error: {str(e)}",
            "tuning_strategy": "grid_search"
        }


async def explain_hyperparameter_results(
    best_params: Dict[str, Any],
    best_score: float,
    model_type: str,
    problem_type: str
) -> str:
    """
    Get AI explanation of hyperparameter tuning results
    
    Args:
        best_params: Best parameters found
        best_score: Best score achieved
        model_type: Type of model
        problem_type: "regression" or "classification"
    
    Returns:
        Human-readable explanation
    """
    try:
        from app.services.azure_openai_service import get_azure_openai_service
        
        azure_service = get_azure_openai_service()
        
        if not azure_service.is_available():
            return f"Best {model_type} parameters: {best_params}. Score: {best_score:.4f}"
        
        metric_name = "accuracy" if problem_type == "classification" else "R² score"
        
        context = f"""
Hyperparameter Tuning Results:
- Model: {model_type}
- Problem: {problem_type}
- Best Parameters: {best_params}
- Best {metric_name}: {best_score:.4f}

Task: Explain these results in simple business terms.
Why did these parameters work best?
What do they mean for model performance?
Provide actionable insights.
"""
        
        explanation = await azure_service.generate_completion(
            prompt=context,
            max_tokens=500,
            temperature=0.5
        )
        
        return explanation
    
    except Exception as e:
        logger.error(f"Explanation generation failed: {str(e)}")
        return f"Best parameters found: {best_params} with score {best_score:.4f}"
