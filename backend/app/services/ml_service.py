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
            
            # Suppress TensorFlow warnings
            import os as tf_os
            tf_os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            
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
            logging.info("LSTM model added to training pipeline")
        except Exception as e:
            logging.warning(f"LSTM not available - {str(e)}")
    else:
        logging.info(f"Dataset too small for LSTM training (need 50+ rows, have {len(X_train)})")
    
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
            if not is_lstm:
                if hasattr(model, 'feature_importances_'):
                    # For tree-based models (Random Forest, XGBoost, Decision Tree)
                    importances = model.feature_importances_
                    feature_imp_pairs = sorted(zip(feature_cols, importances), key=lambda x: x[1], reverse=True)
                    feature_importance_dict = {feat: float(imp) for feat, imp in feature_imp_pairs[:10]}
                elif hasattr(model, 'coef_'):
                    # For Linear Regression - use absolute coefficients as importance
                    importances = np.abs(model.coef_)
                    feature_imp_pairs = sorted(zip(feature_cols, importances), key=lambda x: x[1], reverse=True)
                    feature_importance_dict = {feat: float(imp) for feat, imp in feature_imp_pairs[:10]}
            elif is_lstm:
                # For LSTM, use simple permutation importance
                # Calculate baseline score
                baseline_score = r2_test
                
                # Calculate feature importance by permuting each feature
                importances = []
                for i, feat in enumerate(feature_cols):
                    # Create a copy of test data
                    X_test_perm = X_test.copy()
                    # Permute this feature
                    X_test_perm.iloc[:, i] = np.random.permutation(X_test_perm.iloc[:, i].values)
                    # Reshape for LSTM
                    X_test_perm_lstm = X_test_perm.values.reshape((X_test_perm.shape[0], X_test_perm.shape[1], 1))
                    # Predict with permuted feature
                    y_pred_perm = model.predict(X_test_perm_lstm, verbose=0).flatten()
                    # Calculate score decrease
                    perm_score = r2_score(y_test, y_pred_perm)
                    importance = max(0, baseline_score - perm_score)  # How much performance dropped
                    importances.append(importance)
                
                # Normalize importances
                if sum(importances) > 0:
                    importances = [imp / sum(importances) for imp in importances]
                    feature_imp_pairs = sorted(zip(feature_cols, importances), key=lambda x: x[1], reverse=True)
                    feature_importance_dict = {feat: float(imp) for feat, imp in feature_imp_pairs[:10]}
                else:
                    # Fallback: equal importance for all features
                    equal_importance = 1.0 / len(feature_cols)
                    feature_importance_dict = {feat: equal_importance for feat in feature_cols[:10]}
            
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



# ============================================================================
# PHASE 1: CLASSIFICATION SUPPORT
# ============================================================================

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score
)
from sklearn.preprocessing import LabelEncoder


def detect_problem_type(df: pd.DataFrame, target_column: str) -> str:
    """
    Automatically detect whether the problem is regression or classification
    based on the target column characteristics.
    
    Returns: "regression", "classification", or "time_series"
    """
    if target_column not in df.columns:
        raise ValueError(f"Target column '{target_column}' not found in dataframe")
    
    target_data = df[target_column]
    
    # Check if it's a datetime column (time series indicator)
    if pd.api.types.is_datetime64_any_dtype(target_data):
        return "time_series"
    
    # Check if it's categorical or object type
    if pd.api.types.is_categorical_dtype(target_data) or pd.api.types.is_object_dtype(target_data):
        return "classification"
    
    # For numeric columns, check unique value count
    if pd.api.types.is_numeric_dtype(target_data):
        unique_count = target_data.nunique()
        total_count = len(target_data.dropna())
        
        # If unique values are less than 5% of total or less than 20, likely classification
        if unique_count < 20 or (unique_count / total_count) < 0.05:
            logging.info(f"Detected classification problem: {unique_count} unique values in target")
            return "classification"
        else:
            logging.info(f"Detected regression problem: {unique_count} unique values in target")
            return "regression"
    
    # Default to regression
    return "regression"


def train_classification_models(
    df: pd.DataFrame,
    target_column: str,
    test_size: float = 0.2,
    random_state: int = 42
) -> Dict[str, Any]:
    """
    Train multiple classification models and return results with classification metrics
    """
    
    # Prepare data
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    # Target can be numeric or categorical for classification
    if target_column not in df.columns:
        raise ValueError(f"Target column '{target_column}' not found")
    
    # Get feature columns (all numeric except target)
    feature_cols = [col for col in numeric_cols if col != target_column]
    
    if not feature_cols:
        raise ValueError("No numeric features available for training")
    
    # Handle missing values in features
    X = df[feature_cols].fillna(df[feature_cols].mean())
    
    # Handle target variable
    y = df[target_column].copy()
    
    # Encode target if it's categorical
    label_encoder = None
    class_labels = None
    if pd.api.types.is_object_dtype(y) or pd.api.types.is_categorical_dtype(y):
        label_encoder = LabelEncoder()
        y = label_encoder.fit_transform(y.fillna('missing'))
        class_labels = label_encoder.classes_.tolist()
    else:
        y = y.fillna(y.mode()[0] if not y.mode().empty else 0)
        class_labels = sorted(y.unique().tolist())
    
    # Check if binary or multiclass
    n_classes = len(class_labels)
    is_binary = n_classes == 2
    
    logging.info(f"Classification task: {n_classes} classes ({'binary' if is_binary else 'multiclass'})")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    
    # Define classification models
    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=random_state),
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=random_state, n_jobs=-1),
        "XGBoost": xgb.XGBClassifier(n_estimators=100, random_state=random_state, n_jobs=-1, eval_metric='logloss'),
        "Decision Tree": DecisionTreeClassifier(random_state=random_state)
    }
    
    # Add LightGBM if available
    if HAS_LIGHTGBM:
        models["LightGBM"] = lgb.LGBMClassifier(n_estimators=100, random_state=random_state, n_jobs=-1, verbose=-1)
    
    # Add LSTM for larger datasets
    if len(X_train) >= 50:
        try:
            import tensorflow as tf
            from tensorflow import keras
            
            # Suppress TensorFlow warnings
            import os as tf_os
            tf_os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            
            # Simple LSTM classifier
            lstm_model = keras.Sequential([
                keras.layers.LSTM(50, activation='relu', input_shape=(X_train.shape[1], 1)),
                keras.layers.Dense(n_classes, activation='softmax' if n_classes > 2 else 'sigmoid')
            ])
            lstm_model.compile(
                optimizer='adam',
                loss='sparse_categorical_crossentropy' if n_classes > 2 else 'binary_crossentropy',
                metrics=['accuracy']
            )
            
            # Reshape for LSTM
            X_train_lstm = X_train.values.reshape((X_train.shape[0], X_train.shape[1], 1))
            X_test_lstm = X_test.values.reshape((X_test.shape[0], X_test.shape[1], 1))
            
            models["LSTM Neural Network"] = {
                "model": lstm_model,
                "X_train": X_train_lstm,
                "X_test": X_test_lstm,
                "is_lstm": True
            }
            logging.info("LSTM classifier added to training pipeline")
        except Exception as e:
            logging.warning(f"LSTM classifier not available - {str(e)}")
    
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
                y_pred_train_proba = model.predict(X_train_data, verbose=0)
                y_pred_test_proba = model.predict(X_test_data, verbose=0)
                
                if n_classes > 2:
                    y_pred_train = np.argmax(y_pred_train_proba, axis=1)
                    y_pred_test = np.argmax(y_pred_test_proba, axis=1)
                else:
                    y_pred_train = (y_pred_train_proba > 0.5).astype(int).flatten()
                    y_pred_test = (y_pred_test_proba > 0.5).astype(int).flatten()
            else:
                model = model_obj
                # Train model
                model.fit(X_train, y_train)
                
                # Make predictions
                y_pred_train = model.predict(X_train)
                y_pred_test = model.predict(X_test)
            
            # Calculate classification metrics
            accuracy_train = accuracy_score(y_train, y_pred_train)
            accuracy_test = accuracy_score(y_test, y_pred_test)
            
            # Multi-class metrics
            precision_test = precision_score(y_test, y_pred_test, average='weighted', zero_division=0)
            recall_test = recall_score(y_test, y_pred_test, average='weighted', zero_division=0)
            f1_test = f1_score(y_test, y_pred_test, average='weighted', zero_division=0)
            
            # Confusion matrix
            cm = confusion_matrix(y_test, y_pred_test)
            cm_list = cm.tolist()
            
            # ROC-AUC (only for binary or if predict_proba available)
            roc_auc = None
            try:
                if is_binary and not is_lstm:
                    if hasattr(model, 'predict_proba'):
                        y_proba = model.predict_proba(X_test)[:, 1]
                        roc_auc = roc_auc_score(y_test, y_proba)
            except Exception as e:
                logging.warning(f"Could not calculate ROC-AUC for {model_name}: {str(e)}")
            
            # Feature importance (if available)
            feature_importance_dict = {}
            if not is_lstm:
                if hasattr(model, 'feature_importances_'):
                    importances = model.feature_importances_
                    feature_imp_pairs = sorted(zip(feature_cols, importances), key=lambda x: x[1], reverse=True)
                    feature_importance_dict = {feat: float(imp) for feat, imp in feature_imp_pairs[:10]}
                elif hasattr(model, 'coef_'):
                    # For Logistic Regression
                    if len(model.coef_.shape) == 1:
                        importances = np.abs(model.coef_)
                    else:
                        importances = np.abs(model.coef_).mean(axis=0)
                    feature_imp_pairs = sorted(zip(feature_cols, importances), key=lambda x: x[1], reverse=True)
                    feature_importance_dict = {feat: float(imp) for feat, imp in feature_imp_pairs[:10]}
            elif is_lstm:
                # Permutation importance for LSTM
                baseline_score = accuracy_test
                importances = []
                for i, feat in enumerate(feature_cols):
                    X_test_perm = X_test.copy()
                    X_test_perm.iloc[:, i] = np.random.permutation(X_test_perm.iloc[:, i].values)
                    X_test_perm_lstm = X_test_perm.values.reshape((X_test_perm.shape[0], X_test_perm.shape[1], 1))
                    y_pred_perm_proba = model.predict(X_test_perm_lstm, verbose=0)
                    if n_classes > 2:
                        y_pred_perm = np.argmax(y_pred_perm_proba, axis=1)
                    else:
                        y_pred_perm = (y_pred_perm_proba > 0.5).astype(int).flatten()
                    perm_score = accuracy_score(y_test, y_pred_perm)
                    importance = max(0, baseline_score - perm_score)
                    importances.append(importance)
                
                if sum(importances) > 0:
                    importances = [imp / sum(importances) for imp in importances]
                    feature_imp_pairs = sorted(zip(feature_cols, importances), key=lambda x: x[1], reverse=True)
                    feature_importance_dict = {feat: float(imp) for feat, imp in feature_imp_pairs[:10]}
                else:
                    equal_importance = 1.0 / len(feature_cols)
                    feature_importance_dict = {feat: equal_importance for feat in feature_cols[:10]}
            
            # Calculate confidence level based on accuracy
            if accuracy_test >= 0.85:
                confidence = "High"
            elif accuracy_test >= 0.70:
                confidence = "Medium"
            else:
                confidence = "Low"
            
            model_result = {
                "model_name": model_name,
                "problem_type": "classification",
                "accuracy": float(accuracy_test),
                "accuracy_train": float(accuracy_train),
                "precision": float(precision_test),
                "recall": float(recall_test),
                "f1_score": float(f1_test),
                "confusion_matrix": cm_list,
                "roc_auc": float(roc_auc) if roc_auc is not None else None,
                "confidence": confidence,
                "feature_importance": feature_importance_dict,
                "features_used": feature_cols,
                "target": target_column,
                "target_column": target_column,
                "n_train_samples": len(X_train),
                "n_test_samples": len(X_test),
                "n_classes": n_classes,
                "class_labels": class_labels
            }
            
            results.append(model_result)
            
            # Track best model (by accuracy)
            if accuracy_test > best_score:
                best_score = accuracy_test
                best_model = model_name
        
        except Exception as e:
            logging.warning(f"Failed to train {model_name}: {str(e)}")
            continue
    
    # Sort by accuracy
    results.sort(key=lambda x: x["accuracy"], reverse=True)
    
    return {
        "models": results,
        "best_model": best_model,
        "target_column": target_column,
        "feature_columns": feature_cols,
        "problem_type": "classification",
        "n_classes": n_classes,
        "class_labels": class_labels,
        "training_info": {
            "test_size": test_size,
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "total_features": len(feature_cols)
        }
    }


def train_models_auto(
    df: pd.DataFrame,
    target_column: str,
    problem_type: str = "auto",
    test_size: float = 0.2,
    random_state: int = 42
) -> Dict[str, Any]:
    """
    Unified function to train models with automatic problem type detection.
    
    Args:
        df: DataFrame with features and target
        target_column: Name of target column
        problem_type: "auto", "regression", "classification", or "time_series"
        test_size: Test split ratio
        random_state: Random seed
    
    Returns:
        Dictionary with model results and metadata
    """
    
    # Auto-detect problem type if requested
    if problem_type == "auto":
        detected_type = detect_problem_type(df, target_column)
        logging.info(f"Auto-detected problem type: {detected_type}")
        problem_type = detected_type
    
    # Route to appropriate training function
    if problem_type == "classification":
        return train_classification_models(df, target_column, test_size, random_state)
    elif problem_type == "regression":
        result = train_multiple_models(df, target_column, test_size, random_state)
        # Add problem_type to result for consistency
        result["problem_type"] = "regression"
        return result
    elif problem_type == "time_series":
        # Time series will be handled by separate service
        raise ValueError("Time series forecasting should use time_series_service.py")
    else:
        raise ValueError(f"Unknown problem type: {problem_type}")
