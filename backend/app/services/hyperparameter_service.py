"""
Hyperparameter Tuning Service
Provides grid search, random search, and manual tuning capabilities
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


def get_default_hyperparameters(model_type: str, problem_type: str) -> Dict[str, Any]:
    """
    Get default hyperparameter ranges for different models
    
    Args:
        model_type: "random_forest", "xgboost", "lightgbm"
        problem_type: "regression" or "classification"
    
    Returns:
        Dictionary of hyperparameter ranges
    """
    if model_type == "random_forest":
        return {
            "n_estimators": [50, 100, 200, 300],
            "max_depth": [5, 10, 20, 30, None],
            "min_samples_split": [2, 5, 10],
            "min_samples_leaf": [1, 2, 4],
            "max_features": ["sqrt", "log2", None]
        }
    
    elif model_type == "xgboost":
        return {
            "n_estimators": [50, 100, 200],
            "max_depth": [3, 5, 7, 10],
            "learning_rate": [0.01, 0.05, 0.1, 0.2],
            "subsample": [0.6, 0.8, 1.0],
            "colsample_bytree": [0.6, 0.8, 1.0]
        }
    
    elif model_type == "lightgbm" and HAS_LIGHTGBM:
        return {
            "n_estimators": [50, 100, 200],
            "max_depth": [3, 5, 7, 10],
            "learning_rate": [0.01, 0.05, 0.1],
            "num_leaves": [31, 50, 70, 100],
            "subsample": [0.6, 0.8, 1.0]
        }
    
    return {}


def tune_hyperparameters_grid(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    model_type: str,
    problem_type: str,
    param_grid: Dict[str, List] = None,
    cv: int = 3
) -> Dict[str, Any]:
    """
    Perform grid search hyperparameter tuning
    
    Args:
        X_train: Training features
        y_train: Training target
        model_type: Type of model to tune
        problem_type: "regression" or "classification"
        param_grid: Custom parameter grid (if None, use defaults)
        cv: Number of cross-validation folds
    
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
    n_iter: int = 20,
    cv: int = 3
) -> Dict[str, Any]:
    """
    Perform random search hyperparameter tuning
    
    Args:
        X_train: Training features
        y_train: Training target
        model_type: Type of model to tune
        problem_type: "regression" or "classification"
        param_distributions: Custom parameter distributions
        n_iter: Number of random combinations to try
        cv: Number of cross-validation folds
    
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
