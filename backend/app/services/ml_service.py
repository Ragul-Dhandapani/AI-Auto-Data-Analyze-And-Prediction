"""
Machine Learning Service
Handles model training, prediction, and evaluation
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import xgboost as xgb
import logging

# Try to import LightGBM (optional)
try:
    import lightgbm as lgb
    HAS_LIGHTGBM = True
except ImportError:
    HAS_LIGHTGBM = False
    logging.warning("LightGBM not available, skipping in model training")


def train_multiple_models(
    df: pd.DataFrame, 
    target_column: str,
    test_size: float = 0.2,
    random_state: int = 42
) -> Dict[str, Any]:
    """Train multiple ML models and return results"""
    
    # Prepare data
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if target_column not in numeric_cols:
        raise ValueError(f"Target column '{target_column}' must be numeric")
    
    feature_cols = [col for col in numeric_cols if col != target_column]
    
    if not feature_cols:
        raise ValueError("No numeric features available for training")
    
    # Handle missing values
    X = df[feature_cols].fillna(df[feature_cols].mean())
    y = df[target_column].fillna(df[target_column].mean())
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    
    # Define models
    models = {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(n_estimators=100, random_state=random_state, n_jobs=-1),
        "XGBoost": xgb.XGBRegressor(n_estimators=100, random_state=random_state, n_jobs=-1),
        "Decision Tree": DecisionTreeRegressor(random_state=random_state)
    }
    
    # Add LightGBM if available
    if HAS_LIGHTGBM:
        models["LightGBM"] = lgb.LGBMRegressor(n_estimators=100, random_state=random_state, n_jobs=-1, verbose=-1)
    
    # Add LSTM for larger datasets (simplified version)
    if len(X_train) >= 50:  # Only for datasets with sufficient data
        try:
            import tensorflow as tf
            from tensorflow import keras
            
            # Simple LSTM implementation
            lstm_model = keras.Sequential([
                keras.layers.LSTM(50, activation='relu', input_shape=(X_train.shape[1], 1)),
                keras.layers.Dense(1)
            ])
            lstm_model.compile(optimizer='adam', loss='mse')
            
            # Reshape for LSTM
            X_train_lstm = X_train.values.reshape((X_train.shape[0], X_train.shape[1], 1))
            X_test_lstm = X_test.values.reshape((X_test.shape[0], X_test.shape[1], 1))
            
            models["LSTM Neural Network"] = {
                "model": lstm_model,
                "X_train": X_train_lstm,
                "X_test": X_test_lstm,
                "is_lstm": True
            }
        except:
            logging.warning("LSTM not available - TensorFlow not installed or compatible")
    
    results = []
    best_model = None
    best_score = -float('inf')
    
    for model_name, model_obj in models.items():
        try:
            # Handle LSTM special case
            is_lstm = isinstance(model_obj, dict) and model_obj.get("is_lstm")
            
            if is_lstm:
                model = model_obj["model"]
                X_train_data = model_obj["X_train"]
                X_test_data = model_obj["X_test"]
                
                # Train LSTM
                model.fit(X_train_data, y_train, epochs=50, batch_size=32, verbose=0, validation_split=0.2)
                
                # Make predictions
                y_pred_train = model.predict(X_train_data, verbose=0).flatten()
                y_pred_test = model.predict(X_test_data, verbose=0).flatten()
            else:
                model = model_obj
                # Train model
                model.fit(X_train, y_train)
                
                # Make predictions
                y_pred_train = model.predict(X_train)
                y_pred_test = model.predict(X_test)
            
            # Calculate metrics
            r2_train = r2_score(y_train, y_pred_train)
            r2_test = r2_score(y_test, y_pred_test)
            
            # RMSE calculation (compatible with older scikit-learn versions)
            mse_train = mean_squared_error(y_train, y_pred_train)
            mse_test = mean_squared_error(y_test, y_pred_test)
            rmse_train = np.sqrt(mse_train)
            rmse_test = np.sqrt(mse_test)
            
            mae_test = mean_absolute_error(y_test, y_pred_test)
            
            # Feature importance (if available)
            feature_importance_dict = {}
            if not is_lstm and hasattr(model, 'feature_importances_'):
                importances = model.feature_importances_
                # Sort by importance
                feature_imp_pairs = sorted(zip(feature_cols, importances), key=lambda x: x[1], reverse=True)
                # Convert to dict for frontend
                feature_importance_dict = {feat: float(imp) for feat, imp in feature_imp_pairs[:10]}
            
            # Calculate confidence level based on R² score
            if r2_test >= 0.7:
                confidence = "High"
            elif r2_test >= 0.5:
                confidence = "Medium"
            else:
                confidence = "Low"
            
            model_result = {
                "model_name": model_name,
                "r2_score": float(r2_test),
                "r2_train": float(r2_train),
                "rmse": float(rmse_test),
                "rmse_train": float(rmse_train),
                "mae": float(mae_test),
                "confidence": confidence,  # Frontend expects this
                "feature_importance": feature_importance_dict,  # Frontend expects dict
                "features_used": feature_cols,
                "target": target_column,
                "target_column": target_column,  # Frontend expects this
                "n_train_samples": len(X_train),
                "n_test_samples": len(X_test)
            }
            
            results.append(model_result)
            
            # Track best model
            if r2_test > best_score:
                best_score = r2_test
                best_model = model_name
                
        except Exception as e:
            logging.warning(f"Failed to train {model_name}: {str(e)}")
            continue
    
    # Sort by R² score
    results.sort(key=lambda x: x["r2_score"], reverse=True)
    
    return {
        "models": results,
        "best_model": best_model,
        "target_column": target_column,
        "feature_columns": feature_cols,
        "training_info": {
            "test_size": test_size,
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "total_features": len(feature_cols)
        }
    }


def predict_value(
    model_data: Dict[str, Any],
    input_features: Dict[str, float]
) -> Dict[str, Any]:
    """Make prediction using trained model"""
    # This would require model persistence (joblib/pickle)
    # For now, return placeholder
    return {
        "prediction": None,
        "note": "Model persistence not implemented yet"
    }


def calculate_model_performance_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray
) -> Dict[str, float]:
    """Calculate comprehensive performance metrics"""
    return {
        "r2_score": float(r2_score(y_true, y_pred)),
        "rmse": float(mean_squared_error(y_true, y_pred, squared=False)),
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "mse": float(mean_squared_error(y_true, y_pred))
    }


def suggest_best_target_column(df: pd.DataFrame) -> str:
    """Suggest the best target column for prediction"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if not numeric_cols:
        return None
    
    # Prefer columns with high variance and fewer missing values
    best_col = None
    best_score = -1
    
    for col in numeric_cols:
        # Calculate score based on variance and completeness
        variance = df[col].var()
        completeness = 1 - (df[col].isnull().sum() / len(df))
        score = variance * completeness
        
        if score > best_score:
            best_score = score
            best_col = col
    
    return best_col
