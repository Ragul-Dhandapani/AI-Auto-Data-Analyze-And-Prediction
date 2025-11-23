"""
AI-Powered Hyperparameter Tuning Suggestions Service
"""
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

def get_hyperparameter_suggestions(problem_type: str, model_types: List[str], dataset_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate AI-powered hyperparameter suggestions
    Returns format: {model_name: {param_name: {min: X, max: Y, optimal: Z}}}
    """
    suggestions = {}
    dataset_size = dataset_info.get('row_count', 0)
    
    for model_type in model_types:
        if "randomforest" in model_type.lower() or "RandomForest" in model_type:
            suggestions[model_type] = {
                "n_estimators": {
                    "min": 50,
                    "max": 500,
                    "optimal": 200 if dataset_size > 1000 else 100,
                    "description": "Number of trees in the forest"
                },
                "max_depth": {
                    "min": 5,
                    "max": 30,
                    "optimal": 15 if dataset_size > 5000 else 10,
                    "description": "Maximum depth of each tree"
                },
                "min_samples_split": {
                    "min": 2,
                    "max": 20,
                    "optimal": 5,
                    "description": "Minimum samples required to split a node"
                },
                "min_samples_leaf": {
                    "min": 1,
                    "max": 10,
                    "optimal": 2,
                    "description": "Minimum samples required at a leaf node"
                }
            }
        elif "xgb" in model_type.lower() or "XGB" in model_type:
            suggestions[model_type] = {
                "n_estimators": {
                    "min": 50,
                    "max": 500,
                    "optimal": 200,
                    "description": "Number of boosting rounds"
                },
                "max_depth": {
                    "min": 3,
                    "max": 10,
                    "optimal": 6,
                    "description": "Maximum tree depth"
                },
                "learning_rate": {
                    "min": 0.01,
                    "max": 0.3,
                    "optimal": 0.05,
                    "description": "Step size shrinkage to prevent overfitting"
                },
                "subsample": {
                    "min": 0.5,
                    "max": 1.0,
                    "optimal": 0.8,
                    "description": "Subsample ratio of training instances"
                },
                "colsample_bytree": {
                    "min": 0.5,
                    "max": 1.0,
                    "optimal": 0.8,
                    "description": "Subsample ratio of columns for each tree"
                }
            }
        elif "linear" in model_type.lower():
            if problem_type == "regression":
                suggestions[model_type] = {
                    "alpha": {
                        "min": 0.0001,
                        "max": 10.0,
                        "optimal": 1.0,
                        "description": "Regularization strength (Ridge)"
                    }
                }
            else:
                suggestions[model_type] = {
                    "C": {
                        "min": 0.01,
                        "max": 100,
                        "optimal": 1.0,
                        "description": "Inverse regularization strength"
                    },
                    "max_iter": {
                        "min": 100,
                        "max": 1000,
                        "optimal": 200,
                        "description": "Maximum iterations for convergence"
                    }
                }
        elif "gradient" in model_type.lower():
            suggestions[model_type] = {
                "n_estimators": {
                    "min": 50,
                    "max": 500,
                    "optimal": 150,
                    "description": "Number of boosting stages"
                },
                "learning_rate": {
                    "min": 0.01,
                    "max": 0.3,
                    "optimal": 0.1,
                    "description": "Shrinks contribution of each tree"
                },
                "max_depth": {
                    "min": 3,
                    "max": 10,
                    "optimal": 5,
                    "description": "Maximum depth of trees"
                }
            }
        elif "lstm" in model_type.lower():
            suggestions[model_type] = {
                "units": {
                    "min": 32,
                    "max": 256,
                    "optimal": 64,
                    "description": "Number of LSTM units in each layer"
                },
                "epochs": {
                    "min": 10,
                    "max": 100,
                    "optimal": 50,
                    "description": "Number of training epochs"
                },
                "batch_size": {
                    "min": 16,
                    "max": 128,
                    "optimal": 32,
                    "description": "Number of samples per gradient update"
                }
            }
    
    logger.info(f"✅ Generated hyperparameter suggestions for {len(suggestions)} models")
    return suggestions
