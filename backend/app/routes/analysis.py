"""
Analysis Routes
Handles data analysis, ML training, and visualization
"""
from fastapi import APIRouter, HTTPException
import pandas as pd
import numpy as np
from typing import Dict, Any
from datetime import datetime, timezone
import json
import uuid
import io
from cachetools import TTLCache
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio

from app.models.pydantic_models import HolisticRequest, SaveStateRequest
from app.database.db_helper import get_db
from app.database.adapters.factory import get_database_adapter
from app.services.data_service import generate_data_profile, get_correlation_matrix, clean_data
from app.services.ml_service import train_multiple_models, suggest_best_target_column, train_models_auto, detect_problem_type
from app.services.domain_detection import detect_domain, get_domain_specific_insights
from app.services.domain_visualizations import generate_domain_specific_charts
# Enhanced ML Service with 30+ models
HAS_ENHANCED_ML = False
try:
    from app.services.ml_service_enhanced import (
        train_classification_models_enhanced,
        train_regression_models_enhanced,
        get_available_models,
        get_model_recommendations
    )
    HAS_ENHANCED_ML = True
except ImportError:
    HAS_ENHANCED_ML = False
from app.services.visualization_service_v2 import generate_auto_charts_v2 as generate_auto_charts
from app.services import time_series_service
from app.services.chat_service import process_chat_message
from app.services.azure_openai_service import get_azure_openai_service
# Phase 3: Import new services for analytics, explainability, and AI insights
from app.services.analytics_tracking_service import track_chart_view, get_popular_charts_for_dataset_type
from app.services.model_explainability_service import generate_shap_explanation, generate_lime_explanation, explain_prediction_in_words
from app.services.ai_insights_service import generate_statistical_insights, generate_anomaly_detection_insights, generate_business_recommendations
# Intelligence Services
from app.services.chart_intelligence_service import chart_intelligence
from app.services.variable_intelligence_service import variable_intelligence
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/run")
async def run_analysis(request: Dict[str, Any]):
    """Run specific analysis type (profile, clean, or visualize) - for DataProfiler and VisualizationPanel components"""
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
                db_adapter = get_db()
                dataset = await db_adapter.get_dataset(dataset_id)
                if dataset:
                    # Update dataset with cleaned data (removed updated_at - not in Oracle schema)
                    updates = {
                        "data": cleaned_df.to_dict('records'),
                        "row_count": len(cleaned_df)
                    }
                    await db_adapter.update_dataset(dataset_id, updates)
            
            return {
                "cleaning_report": cleaning_report,
                "rows_before": len(df),
                "rows_after": len(cleaned_df)
            }
        
        elif analysis_type == "visualize":
            # 🧠 INTELLIGENT VISUALIZATION SYSTEM
            # Use advanced AI-powered visualization engine
            from app.services.intelligent_visualization_service import get_intelligent_visualization_service
            import json
            
            logger.info(f"🧠 Starting intelligent visualization analysis for dataset: {dataset_id}")
            
            viz_service = get_intelligent_visualization_service()
            result = await viz_service.analyze_and_generate(df)
            
            # Flatten categories into a single list for frontend compatibility
            all_charts = []
            all_skipped = []
            
            categories_data = result.get('categories', {})
            for category_name, category_data in categories_data.items():
                charts = category_data.get('charts', [])
                skipped = category_data.get('skipped', [])
                
                # Add category tag to each chart
                for chart in charts:
                    chart['category'] = category_name
                    all_charts.append(chart)
                
                # Add category info to skipped messages
                for skip_msg in skipped:
                    all_skipped.append({
                        'category': category_name,
                        'message': skip_msg
                    })
            
            logger.info(f"✅ Generated {len(all_charts)} intelligent charts across {len(categories_data)} categories")
            
            # Ensure all data is JSON serializable
            def make_serializable(obj):
                """Recursively convert objects to JSON-serializable format"""
                if isinstance(obj, dict):
                    return {k: make_serializable(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [make_serializable(item) for item in obj]
                elif isinstance(obj, (str, int, float, bool, type(None))):
                    return obj
                elif hasattr(obj, 'to_dict'):
                    return make_serializable(obj.to_dict())
                elif hasattr(obj, '__dict__'):
                    return make_serializable(obj.__dict__)
                else:
                    return str(obj)
            
            response_data = {
                "charts": make_serializable(all_charts),
                "skipped": make_serializable(all_skipped),
                "insights": make_serializable(result.get('insights', [])),
                "total_charts": int(result.get('total_charts', 0)),
                "total_skipped": int(result.get('total_skipped', 0))
            }
            
            logger.info(f"✅ Response prepared with {len(all_charts)} charts")
            
            return response_data
        
        elif analysis_type == "insights":
            # Generate AI insights using Azure OpenAI
            try:
                from app.services.azure_openai_service import get_azure_openai_service
                
                azure_service = get_azure_openai_service()
                
                if not azure_service.is_available():
                    return {
                        "insights": "AI insights require Azure OpenAI to be configured. Please set up Azure OpenAI credentials to generate intelligent insights about your data."
                    }
                
                # Prepare data summary
                profile = generate_data_profile(df)
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
                
                data_summary = {
                    'row_count': len(df),
                    'column_count': len(df.columns)
                }
                
                analysis_results = {
                    'numeric_columns': numeric_cols[:5],
                    'categorical_columns': categorical_cols[:5],
                    'missing_values': profile.get('missing_values_total', 0),
                    'duplicate_rows': profile.get('duplicate_rows', 0)
                }
                
                # Generate insights using Azure OpenAI
                insights_text = await azure_service.generate_insights(
                    data_summary=data_summary,
                    analysis_results=analysis_results,
                    context='general'
                )
                
                return {
                    "insights": insights_text,
                    "summary": {
                        "total_records": len(df),
                        "total_columns": len(df.columns),
                        "numeric_columns": len(numeric_cols),
                        "categorical_columns": len(categorical_cols),
                        "data_quality_score": 100 - (profile.get('missing_values_total', 0) / (len(df) * len(df.columns)) * 100)
                    }
                }
            except Exception as e:
                logger.error(f"AI insights generation failed: {str(e)}", exc_info=True)
                # Safe fallback that doesn't rely on undefined variables
                try:
                    profile = generate_data_profile(df)
                    numeric_count = len(df.select_dtypes(include=[np.number]).columns)
                    categorical_count = len(df.select_dtypes(include=['object', 'category']).columns)
                except:
                    numeric_count = 0
                    categorical_count = 0
                
                return {
                    "insights": f"Unable to generate AI insights at this time. You can still explore the data using profile statistics and visualizations.",
                    "error": str(e),
                    "summary": {
                        "total_records": len(df),
                        "total_columns": len(df.columns),
                        "numeric_columns": numeric_count,
                        "categorical_columns": categorical_count
                    }
                }
        
        else:
            raise HTTPException(400, f"Unknown analysis type: {analysis_type}")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Analysis failed: {str(e)}")


async def load_dataframe(dataset_id: str) -> pd.DataFrame:
    """Load dataset into DataFrame with caching for performance"""
    from cachetools import TTLCache
    import time
    
    # DataFrame cache: Stores loaded DataFrames for 30 minutes
    if not hasattr(load_dataframe, 'cache'):
        load_dataframe.cache = TTLCache(maxsize=100, ttl=1800)
    
    # Check cache first
    if dataset_id in load_dataframe.cache:
        logger.info(f"✅ DataFrame loaded from cache for dataset {dataset_id}")
        return load_dataframe.cache[dataset_id].copy()
    
    logger.info(f"Loading dataset {dataset_id} from database...")
    start_time = time.time()
    
    from app.database.db_helper import get_db
    db_adapter = get_db()
    dataset = await db_adapter.get_dataset(dataset_id)
    
    if not dataset:
        raise HTTPException(404, "Dataset not found")
    
    logger.info(f"Loading dataset {dataset_id}, storage_type: {dataset.get('storage_type', 'direct')}")
    
    # Load data based on storage type
    if dataset.get("storage_type") == "blob":
        file_id = dataset.get("gridfs_file_id") or dataset.get("file_id")
        if file_id:
            try:
                data = await db_adapter.retrieve_file(file_id)
                logger.info(f"BLOB data loaded, size: {len(data)} bytes")
                
                # Get stored dtypes from dataset metadata
                stored_dtypes = dataset.get("dtypes", {})
                
                # Check file type from original filename
                filename = dataset.get("name", "")
                
                if filename.endswith('.csv'):
                    # Load CSV directly from bytes
                    df = pd.read_csv(io.BytesIO(data))
                    
                    # Apply stored dtypes to ensure correct types
                    if stored_dtypes:
                        for col, dtype_str in stored_dtypes.items():
                            if col in df.columns:
                                try:
                                    if 'int' in dtype_str:
                                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype('int64')
                                    elif 'float' in dtype_str:
                                        df[col] = pd.to_numeric(df[col], errors='coerce')
                                    elif 'object' in dtype_str or 'str' in dtype_str:
                                        df[col] = df[col].astype(str)
                                    elif 'bool' in dtype_str:
                                        df[col] = df[col].astype(bool)
                                    elif 'datetime' in dtype_str:
                                        df[col] = pd.to_datetime(df[col], errors='coerce')
                                except Exception as e:
                                    logger.warning(f"Could not convert column {col} to {dtype_str}: {e}")
                        
                        logger.info(f"Applied stored dtypes to {len(stored_dtypes)} columns")
                
                elif filename.endswith(('.xlsx', '.xls')):
                    # Load Excel directly from bytes
                    df = pd.read_excel(io.BytesIO(data))
                else:
                    # Fallback: Try to parse as JSON (backward compatibility)
                    import json
                    try:
                        data_dict = json.loads(data.decode('utf-8'))
                        df = pd.DataFrame(data_dict)
                    except:
                        # If JSON fails, try CSV
                        df = pd.read_csv(io.BytesIO(data))
                
                logger.info(f"DataFrame created from BLOB: {df.shape}, dtypes: {df.dtypes.to_dict()}")
                
            except Exception as e:
                logger.error(f"Error loading BLOB data: {str(e)}")
                raise HTTPException(500, f"Error loading dataset from BLOB: {str(e)}")
        else:
            raise HTTPException(500, "BLOB file ID not found")
    else:
        # Load from inline data
        data = dataset.get("data", [])
        if not data:
            raise HTTPException(500, "No data found in dataset")
        
        df = pd.DataFrame(data)
        logger.info(f"DataFrame loaded from inline data: {df.shape}")
    
    # Validate DataFrame is not empty
    if df.empty:
        logger.error(f"DataFrame is empty after loading dataset {dataset_id}")
        raise HTTPException(400, "Loaded DataFrame is empty")
    
    # Cache the DataFrame
    load_dataframe.cache[dataset_id] = df.copy()
    
    load_time = time.time() - start_time
    logger.info(f"✅ Cached DataFrame for dataset {dataset_id} (load time: {load_time:.2f}s)")
    
    return df


def train_models_with_selection(df, target_column, problem_type, selected_models):
    """
    Train models using enhanced ML service with model selection
    
    Args:
        df: DataFrame with features and target
        target_column: Name of target column
        problem_type: classification or regression
        selected_models: List of model keys to train
    
    Returns:
        Dictionary with trained models results
    """
    from sklearn.model_selection import train_test_split
    import logging
    
    logger = logging.getLogger(__name__)
    
    # Prepare data - CRITICAL: Filter to numeric columns only
    X = df.drop(columns=[target_column])
    y = df[target_column]
    
    # Select only numeric columns for training
    numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    if len(numeric_cols) == 0:
        logger.warning("No numeric columns found for training")
        return {'models': [], 'problem_type': problem_type, 'best_score': 0}
    
    X = X[numeric_cols]
    logger.info(f"Training with {len(numeric_cols)} numeric features: {numeric_cols[:10]}")
    
    # Handle missing values - drop rows with NaN
    initial_len = len(X)
    valid_indices = ~(X.isna().any(axis=1) | y.isna())
    X = X[valid_indices]
    y = y[valid_indices]
    
    if len(X) < 10:
        logger.warning(f"Insufficient data after removing NaN values: {len(X)} rows")
        return {'models': [], 'problem_type': problem_type, 'best_score': 0}
    
    if len(X) < initial_len:
        logger.info(f"Removed {initial_len - len(X)} rows with NaN values")
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # ========================================
    # AUTO-DETECT PROBLEM TYPE IF NEEDED
    # ========================================
    # Check if target variable type matches problem type
    unique_values = y.nunique()
    is_numeric_continuous = pd.api.types.is_numeric_dtype(y) and unique_values > 20
    is_categorical = pd.api.types.is_object_dtype(y) or pd.api.types.is_categorical_dtype(y) or unique_values <= 20
    
    # Auto-detect problem type if set to "auto"
    if problem_type == 'auto':
        if is_numeric_continuous:
            problem_type = 'regression'
            logger.info(f"🔍 Auto-detected REGRESSION (target has {unique_values} unique continuous values)")
        else:
            problem_type = 'classification'
            logger.info(f"🔍 Auto-detected CLASSIFICATION (target has {unique_values} unique categorical values)")
    
    # Validate and auto-correct problem type
    if problem_type == 'classification' and is_numeric_continuous:
        logger.warning(f"⚠️ Problem type mismatch: '{problem_type}' selected but target has {unique_values} unique continuous values")
        logger.info(f"🔄 Auto-correcting to REGRESSION (target has {unique_values} unique values, all numeric)")
        problem_type = 'regression'
    elif problem_type == 'regression' and is_categorical:
        logger.warning(f"⚠️ Problem type mismatch: '{problem_type}' selected but target has {unique_values} unique categorical values")
        logger.info(f"🔄 Auto-correcting to CLASSIFICATION (target has {unique_values} unique values or is categorical)")
        problem_type = 'classification'
    
    logger.info(f"✅ Final problem type: {problem_type} (target has {unique_values} unique values)")
    
    # Train with enhanced service
    if problem_type == 'classification':
        results, best_model, best_score = train_classification_models_enhanced(
            X_train, y_train, X_test, y_test, selected_models
        )
    else:  # regression
        results, best_model, best_score = train_regression_models_enhanced(
            X_train, y_train, X_test, y_test, selected_models
        )
    
    # Format results to match expected structure
    formatted_models = []
    for result in results:
        model_dict = {
            'model_name': result['model_name'],
            'target_column': target_column,
            **result
        }
        formatted_models.append(model_dict)
    
    return {
        'models': formatted_models,
        'problem_type': problem_type,
        'best_score': best_score
    }


@router.post("/holistic")
async def holistic_analysis(request: Dict[str, Any]):
    """Perform comprehensive analysis with optional user variable selection and multiple targets"""
    try:
        # DEBUG: Log the RAW request immediately
        logging.info(f"🔍 RAW REQUEST RECEIVED: {json.dumps(request, indent=2)}")
        
        dataset_id = request.get("dataset_id")
        workspace_name = request.get("workspace_name", "default")  # NEW: Workspace name for linking training metadata
        logger.info(f"🔍 DEBUG: Received workspace_name: '{workspace_name}' for dataset {dataset_id}")
        user_selection = request.get("user_selection")  # Optional user-provided target and features
        
        # CRITICAL NEW: Extract user expectation for AI context
        user_expectation = None
        if user_selection and isinstance(user_selection, dict):
            user_expectation = user_selection.get("user_expectation")
            if user_expectation:
                logger.info(f"💭 USER EXPECTATION: {user_expectation}")
        
        # DEBUG: Log user_selection immediately after extraction
        logging.info(f"🔍 USER_SELECTION EXTRACTED: {json.dumps(user_selection, indent=2) if user_selection else 'None'}")
        problem_type = request.get("problem_type", "auto")  # "auto", "regression", "classification", or "time_series"
        selected_models = request.get("selected_models")  # NEW: Optional list of model keys to train
        use_ai_recommendations = request.get("use_ai_recommendations", False)  # NEW: Use AI model recommendations
        
        df = await load_dataframe(dataset_id)
        original_size = len(df)
        
        # Performance optimization: Intelligent sampling for large datasets
        SAMPLE_THRESHOLD = 10000  # Sample if more than 10000 rows (increased from 5000)
        SAMPLE_SIZE = 5000  # Use 5000 rows for training (increased from 3000)
        is_sampled = False
        
        if len(df) > SAMPLE_THRESHOLD:
            # Stratified sampling if target is available, otherwise random
            df_analysis = df.sample(n=SAMPLE_SIZE, random_state=42)
            is_sampled = True
            logging.info(f"Performance optimization: Sampled {SAMPLE_SIZE} rows from {original_size} for faster analysis")
        else:
            df_analysis = df.copy()
        
        # Update training counter
        db_adapter = get_db()
        await db_adapter.increment_training_count(dataset_id)
        
        # 1. Data Profiling (use full dataset for profiling)
        profile = generate_data_profile(df)
        
        # 2. Train ML Models with user selection if provided
        numeric_cols = df_analysis.select_dtypes(include=[np.number]).columns.tolist()
        models_result = {"models": [], "message": "No numeric columns for ML training"}
        selection_feedback = None
        
        logging.info(f"Holistic analysis: Found {len(numeric_cols)} numeric columns, dataset size: {len(df_analysis)}")
        
        # Process user variable selection with intelligence
        target_cols = []
        target_feature_mapping = {}  # Maps target -> list of features
        selection_feedback = None
        
        # AI-POWERED VARIABLE VALIDATION
        if user_selection and user_selection != {}:
            # DEBUG: Log what we actually received
            logging.info(f"🔍 DEBUG - Received user_selection: {json.dumps(user_selection, indent=2)}")
            
            # Extract user's choices
            user_targets = user_selection.get("target_variables", [])
            user_target = user_selection.get("target_variable")
            
            logging.info(f"🔍 DEBUG - user_target: {user_target}, user_targets: {user_targets}")
            
            # Convert to list format
            if user_target and not user_targets:
                features_from_selection = user_selection.get("selected_features", [])
                logging.info(f"🔍 DEBUG - Converting single target. Features extracted: {features_from_selection}")
                user_targets = [{"target": user_target, "features": features_from_selection}]
                logging.info(f"🔍 DEBUG - Converted user_targets: {user_targets}")
            elif not user_targets and not user_target:
                user_targets = []
                logging.info("🔍 DEBUG - No targets found, setting empty array")
            
            # Extract all targets and features for validation
            all_user_targets = []
            all_user_features = []
            
            if isinstance(user_targets, list):
                for t in user_targets:
                    if isinstance(t, dict):
                        target_name = t.get("target")
                        if target_name:
                            all_user_targets.append(target_name)
                            all_user_features.extend(t.get("features", []))
            
            # Remove duplicates
            all_user_features = list(set(all_user_features))
            
            logging.info(f"Validating user selection: targets={all_user_targets}, features={all_user_features[:5]}")
            
            # VALIDATE WITH AI
            if all_user_targets or all_user_features:
                try:
                    validation = variable_intelligence.validate_variable_selection(
                        df=df_analysis,
                        target_variables=all_user_targets,
                        features=all_user_features
                    )
                    
                    logging.info(f"Variable validation result: valid={validation['valid']}, override={validation['override_needed']}")
                    
                    # If override is needed, use AI suggestions
                    if validation['override_needed'] and validation['suggested_target']:
                        logging.warning(f"AI overriding variables. Suggested target: {validation['suggested_target']}")
                        
                        # Use AI suggestions
                        target_cols = [validation['suggested_target']]
                        target_feature_mapping[validation['suggested_target']] = validation['suggested_features']
                        
                        # Create rich feedback for user
                        selection_feedback = {
                            "status": "override",
                            "message": f"⚠️ **AI Variable Selection Override**\n\n{validation['explanation']}\n\n" +
                                     f"✅ **Proceeding with AI-recommended variables for better results.**",
                            "used_targets": target_cols,
                            "is_multi_target": False,
                            "confidence": validation['confidence'],
                            "ai_override": True,
                            "original_targets": all_user_targets,
                            "original_features": all_user_features[:10]
                        }
                    elif validation['valid']:
                        # User selection is good, use it
                        logging.info("User selection validated successfully")
                        for t in user_targets:
                            if isinstance(t, dict):
                                target_name = t.get("target")
                                if target_name in df_analysis.columns:
                                    target_cols.append(target_name)
                                    target_feature_mapping[target_name] = t.get("features", [])
                        
                        selection_feedback = {
                            "status": "used",
                            "message": f"✅ Your variable selection looks good! (Confidence: {validation['confidence']*100:.0f}%)",
                            "used_targets": target_cols,
                            "is_multi_target": len(target_cols) > 1
                        }
                    
                except Exception as e:
                    logging.error(f"Variable validation failed: {str(e)}")
                    # Fall back to manual validation below
        
            # Manual fallback validation (if AI validation failed or wasn't attempted)
            # ONLY run if target_cols is still empty (AI validation didn't add targets)
            if user_selection and user_selection != {} and len(target_cols) == 0:
                user_targets = user_selection.get("target_variables", [])
                user_target = user_selection.get("target_variable")
                
                # Convert single target to list format
                if user_target and not user_targets:
                    user_targets = [{"target": user_target, "features": user_selection.get("selected_features", [])}]
                
                # Process targets manually
                if user_targets and isinstance(user_targets, list):
                    for target_info in user_targets:
                        if isinstance(target_info, dict):
                            target_name = target_info.get("target")
                            target_features = target_info.get("features", [])
                            
                            if target_name and target_name in df_analysis.columns:
                                if pd.api.types.is_numeric_dtype(df_analysis[target_name].dtype):
                                    target_cols.append(target_name)
                                    target_feature_mapping[target_name] = target_features
                                    logging.info(f"Manual validation: Added target {target_name}")
        
        logging.info(f"Final target_cols after validation: {target_cols}")
        
        # If no valid targets from user selection, auto-detect AND inform user
        if len(target_cols) == 0:
            if user_selection:
                # User provided selection but it failed - create feedback
                selection_feedback = {
                    "status": "modified",
                    "message": "⚠️ Your variable selection could not be used. Possible reasons:\n" +
                               "• Selected targets are not numeric columns\n" +
                               "• Selected targets not found in dataset\n" +
                               "• No targets were selected\n\n" +
                               "Using auto-detection instead.",
                    "used_targets": [],
                    "is_multi_target": False
                }
                logging.warning("User selection failed validation, falling back to auto-detection")
            
            # Auto-detect target
            if len(numeric_cols) >= 2:
                target_col = suggest_best_target_column(df_analysis)
                if target_col:
                    target_cols.append(target_col)
                    target_feature_mapping[target_col] = []  # Empty means use all features
                    logging.info(f"Auto-suggested target column: {target_col}")
                    
                    # Update feedback to show what was auto-selected
                    if selection_feedback:
                        selection_feedback["message"] += f"\n\n✅ Auto-selected target: '{target_col}'"
                        selection_feedback["used_targets"] = [target_col]
        
        # Handle time series separately - don't train ML models
        if problem_type == "time_series":
            # For time series, user should use the dedicated /api/analysis/time-series endpoint
            # Return helpful message instead of training models
            models_result = {
                "models": [],
                "message": "⏰ Time Series Analysis Selected",
                "problem_type": "time_series",
                "training_info": {
                    "note": "Time series forecasting requires a dedicated endpoint. Please use the Time Series analysis feature with a datetime column."
                }
            }
            all_models = []
            
            # Provide helpful feedback
            if selection_feedback:
                selection_feedback["message"] = "⏰ **Time Series Analysis Mode**\n\n" + \
                    "For time series forecasting and trend analysis, please ensure you have:\n" + \
                    "1. A datetime/timestamp column in your dataset\n" + \
                    "2. A numeric target variable to forecast\n\n" + \
                    "Time series models (Prophet, LSTM, ARIMA) will analyze temporal patterns and generate forecasts."
            else:
                selection_feedback = {
                    "status": "info",
                    "message": "⏰ **Time Series Analysis Mode**\n\n" + \
                        "For time series forecasting, use the dedicated time series analysis feature. " + \
                        "This mode supports Prophet, LSTM, and ARIMA models for temporal pattern analysis.",
                    "used_targets": target_cols if target_cols else []
                }
        else:
            # Process each target for regression/classification WITH PARALLEL PROCESSING
            all_models = []
            all_feedback_messages = []
            
            # Function to train models for a single target (for parallel execution)
            def train_single_target(target_col, selected_features):
                logging.info(f"Processing target: {target_col} with {len(selected_features)} selected features")
                
                feedback_parts = []
                models = []
                
                # Separate numeric and categorical selected features
                numeric_selected = []
                categorical_selected = []
                excluded_features = []
                
                try:
                    if selected_features:
                        for feat in selected_features:
                        if feat in df_analysis.columns and feat != target_col:
                            if pd.api.types.is_numeric_dtype(df_analysis[feat].dtype):
                                numeric_selected.append(feat)
                            else:
                                # Check cardinality for categorical features
                                unique_count = df_analysis[feat].nunique()
                                if unique_count <= 50:  # Reasonable for one-hot encoding
                                    categorical_selected.append(feat)
                                else:
                                    excluded_features.append(f"{feat} (too many categories: {unique_count})")
                    
                    # Build feedback message for this target
                    feedback_parts = []
                    feedback_parts.append(f"✅ Target '{target_col}':")
                    if numeric_selected:
                        feedback_parts.append(f"   • Numeric features: {', '.join(numeric_selected)}")
                    if categorical_selected:
                        feedback_parts.append(f"   • Categorical features (encoded): {', '.join(categorical_selected)}")
                    if excluded_features:
                        feedback_parts.append(f"   • ⚠️ Excluded: {', '.join(excluded_features)}")
                    
                        feedback_parts.append("\n".join(parts))
                    
                    # Train models for this target
                    if selected_features:
                        # Create subset dataframe with selected features + target
                        train_columns = selected_features + [target_col]
                        df_subset = df_analysis[train_columns].copy()
                        
                        # Handle categorical features with one-hot encoding
                        if categorical_selected:
                            df_subset = pd.get_dummies(df_subset, columns=categorical_selected, drop_first=True, dtype=int)
                            logging.info(f"Encoded {len(categorical_selected)} categorical features for target {target_col}")
                        
                        # Use enhanced ML service if selected_models provided
                        if selected_models and HAS_ENHANCED_ML:
                            target_models = train_models_with_selection(df_subset, target_col, problem_type, selected_models)
                        else:
                            target_models = train_models_auto(df_subset, target_col, problem_type=problem_type)
                    else:
                        # Train on all numeric features
                        if selected_models and HAS_ENHANCED_ML:
                            target_models = train_models_with_selection(df_analysis, target_col, problem_type, selected_models)
                        else:
                            target_models = train_models_auto(df_analysis, target_col, problem_type=problem_type)
                    
                    # Collect models
                    if target_models.get("models"):
                        models = target_models["models"]
                        logging.info(f"Trained {len(models)} models for target {target_col}")
                    
                except Exception as e:
                    logging.error(f"ML training failed for target {target_col}: {str(e)}", exc_info=True)
                    feedback_parts.append(f"⚠️ Training failed for target '{target_col}': {str(e)}")
                
                return {"models": models, "feedback": "\n\n".join(feedback_parts) if feedback_parts else ""}
            
            # Execute training in parallel for all targets
            logging.info(f"Starting parallel training for {len(target_cols)} target(s)")
            with ThreadPoolExecutor(max_workers=min(len(target_cols), 4)) as executor:
                futures = {
                    executor.submit(train_single_target, target_col, target_feature_mapping.get(target_col, [])): target_col
                    for target_col in target_cols
                }
                
                for future in as_completed(futures):
                    target_col = futures[future]
                    try:
                        result = future.result()
                        all_models.extend(result["models"])
                        if result["feedback"]:
                            all_feedback_messages.append(result["feedback"])
                    except Exception as e:
                        logging.error(f"Failed to get result for {target_col}: {e}")
                        all_feedback_messages.append(f"⚠️ Failed to train models for '{target_col}': {str(e)}")
        
            # Build final selection feedback (only for regression/classification)
            if all_feedback_messages:
                selection_feedback = {
                    "status": "used",
                    "message": "\n\n".join(all_feedback_messages),
                    "used_targets": target_cols,
                    "is_multi_target": len(target_cols) > 1
                }
            
            # Update models_result
            models_result = {"models": all_models}
            
            # ==========================================
            # SAVE ALL TRAINING METADATA TO DATABASE
            # ==========================================
            try:
                logger.info(f"💾 Saving training metadata for {len(all_models)} models...")
                db_adapter = get_db()
                
                for model in all_models:
                    # Extract feature variables used
                    feature_vars = []
                    target_var = model.get('target_column', target_cols[0] if target_cols else 'unknown')
                    
                    # Get features from target_feature_mapping or use all numeric columns except target
                    if target_var in target_feature_mapping:
                        feature_vars = target_feature_mapping[target_var]
                    else:
                        # Use all numeric columns except target
                        feature_vars = [col for col in numeric_cols if col != target_var]
                    
                    # Prepare metrics
                    metrics = {}
                    if problem_type == 'regression':
                        metrics = {
                            'r2_score': model.get('r2_score'),
                            'rmse': model.get('rmse'),
                            'mae': model.get('mae'),
                            'mse': model.get('mse')
                        }
                    else:  # classification
                        metrics = {
                            'accuracy': model.get('accuracy'),
                            'precision': model.get('precision'),
                            'recall': model.get('recall'),
                            'f1_score': model.get('f1_score')
                        }
                    
                    # Add confidence if available
                    if model.get('confidence'):
                        metrics['confidence'] = model.get('confidence')
                    
                    # Create training metadata record
                    metadata = {
                        'dataset_id': dataset_id,
                        'workspace_name': workspace_name,
                        'problem_type': problem_type,
                        'target_variable': target_var,
                        'feature_variables': feature_vars,
                        'model_type': model.get('model_name', 'Unknown'),
                        'model_params': model.get('hyperparameters', {}),
                        'metrics': metrics,
                        'training_duration': model.get('training_time', 0.0)
                    }
                    
                    # Save to database
                    metadata_id = await db_adapter.save_training_metadata(metadata)
                    logger.info(f"✅ Saved metadata for {model.get('model_name')}: {metadata_id}")
                
                logger.info(f"✅ Successfully saved training metadata for ALL {len(all_models)} models!")
                
            except Exception as e:
                logger.error(f"⚠️ Failed to save training metadata: {str(e)}")
                # Don't fail the entire request if metadata saving fails
        
        # Add performance info if sampled
        if is_sampled:
            models_result["performance_info"] = {
                "sampled": True,
                "original_size": original_size,
                "sample_size": SAMPLE_SIZE,
                "message": f"⚡ Performance optimized: Used {SAMPLE_SIZE} samples from {original_size} rows for faster analysis"
            }
        
        # 3. Generate Auto Charts - filtered to user selection if provided
        if user_selection and len(target_cols) > 0:
            # Use first target for chart generation (or could generate for all targets)
            first_target = target_cols[0]
            selected_features = target_feature_mapping.get(first_target, [])
            
            if selected_features:
                chart_columns = [first_target] + selected_features
                df_charts = df_analysis[chart_columns].copy()
                auto_charts, skipped_charts = generate_auto_charts(df_charts, max_charts=15)
            else:
                auto_charts, skipped_charts = generate_auto_charts(df_analysis, max_charts=15)
        else:
            auto_charts, skipped_charts = generate_auto_charts(df_analysis, max_charts=15)
        
        # 4. Correlation Analysis - filtered to user selection if provided
        if user_selection and len(target_cols) > 0:
            first_target = target_cols[0]
            selected_features = target_feature_mapping.get(first_target, [])
            
            if selected_features:
                corr_columns = [first_target] + selected_features
                df_corr = df_analysis[corr_columns].select_dtypes(include=[np.number]).copy()
                correlations = get_correlation_matrix(df_corr)
            else:
                correlations = get_correlation_matrix(df_analysis)
        else:
            correlations = get_correlation_matrix(df_analysis)
        
        # ==========================================
        # PHASE 3: Enhanced AI Insights & Explainability
        # ==========================================
        
        # 5A. Generate comprehensive AI insights using Azure OpenAI
        ai_insights_list = []
        insights = "Analysis complete. Explore the charts and model results above."
        
        try:
            # Try Azure OpenAI first for enterprise insights
            azure_service = get_azure_openai_service()
            if azure_service.is_available():
                data_summary = {
                    'row_count': len(df_analysis),
                    'column_count': len(df_analysis.columns),
                    'target_column': target_cols[0] if target_cols else None
                }
                analysis_results = {
                    'target_column': target_cols[0] if target_cols else None,
                    'problem_type': problem_type,
                    'ml_models': all_models[:3]  # Top 3 models
                }
                
                # CRITICAL: Include user expectation and domain context in insights generation
                # Detect domain if user expectation is provided
                detected_domain = "general"
                if user_expectation:
                    try:
                        domain_info = await azure_service.detect_domain_and_adapt(
                            user_expectation=user_expectation,
                            columns=df_analysis.columns.tolist()
                        )
                        detected_domain = domain_info.get('domain', 'general')
                        logger.info(f"📊 Domain detected for insights: {detected_domain}")
                    except:
                        pass
                
                insights = await azure_service.generate_insights(
                    data_summary=data_summary,
                    analysis_results=analysis_results,
                    context='business',
                    user_expectation=user_expectation,  # User's prediction goal context
                    domain=detected_domain  # Domain-adapted terminology
                )
                logger.info(f"✅ Azure OpenAI insights generated with user context (domain: {detected_domain})")
            else:
                # Fallback to existing insights
                # Prepare correlation matrix for insights
                corr_dict = {}
                if correlations.get('matrix'):
                    for key_corr in correlations['correlations']:
                        target = key_corr.get('target', '')
                        if target and target not in corr_dict:
                            corr_dict[target] = {}
                        for feat, corr_val in key_corr.get('correlations', {}).items():
                            if target:
                                corr_dict[target][feat] = corr_val
                
                # Generate statistical insights using AI
                target_for_insights = target_cols[0] if target_cols else None
                ai_insights_list = await generate_statistical_insights(
                    df_analysis,
                    target_column=target_for_insights,
                    correlation_matrix=corr_dict
                )
            
            # Generate anomaly detection insights
            numeric_columns_list = df_analysis.select_dtypes(include=[np.number]).columns.tolist()
            if numeric_columns_list:
                anomaly_insights = await generate_anomaly_detection_insights(
                    df_analysis,
                    numeric_columns=numeric_columns_list[:5]  # Top 5 numeric columns
                )
                if anomaly_insights:
                    ai_insights_list.extend(anomaly_insights)
            
            # Convert insights list to readable text for backward compatibility
            if ai_insights_list:
                insights = "🤖 AI-Powered Insights:\n\n"
                for idx, insight in enumerate(ai_insights_list[:7], 1):  # Top 7 insights
                    insights += f"{idx}. **{insight.get('title', 'Insight')}**\n"
                    insights += f"   {insight.get('description', '')}\n"
                    if insight.get('recommendation'):
                        insights += f"   💡 Recommendation: {insight.get('recommendation')}\n"
                    insights += "\n"
            
            logging.info(f"Generated {len(ai_insights_list)} AI insights")
        except Exception as e:
            logging.error(f"AI insights generation failed: {str(e)}", exc_info=True)
            insights = "Analysis complete. Explore the charts and model results above."
        
        # 5B. Model Explainability (SHAP/LIME) for best performing model
        explainability_results = {}
        try:
            if all_models:
                # Find best model
                best_model_info = max(all_models, key=lambda m: m.get('r2_score', 0))
                if best_model_info and best_model_info.get('r2_score', 0) > 0.5:  # Only explain good models
                    logging.info(f"Generating explainability for best model: {best_model_info.get('model_name')}")
                    
                    # Note: We'd need to store the actual trained model object to generate SHAP/LIME
                    # For now, we'll provide a placeholder structure that frontend can display
                    explainability_results = {
                        "model_name": best_model_info.get('model_name'),
                        "target_variable": best_model_info.get('target_variable'),
                        "available": True,
                        "feature_importance": best_model_info.get('feature_importance', {}),
                        "explanation_text": f"The {best_model_info.get('model_name')} model achieves {best_model_info.get('r2_score', 0):.2%} accuracy. " +
                                           f"Top influential features: {', '.join(list(best_model_info.get('feature_importance', {}).keys())[:3])}.",
                        "note": "Full SHAP/LIME visualizations available in model details view."
                    }
        except Exception as e:
            logging.error(f"Model explainability failed: {str(e)}", exc_info=True)
        
        # 5C. Business Recommendations using AI
        business_recommendations = []
        try:
            if ai_insights_list and all_models:
                best_model_metrics = {
                    "best_model": {
                        "name": best_model_info.get('model_name') if all_models else "Unknown",
                        "r2_score": best_model_info.get('r2_score', 0) if all_models else 0,
                        "rmse": best_model_info.get('rmse', 0) if all_models else 0
                    }
                }
                target_for_recommendations = target_cols[0] if target_cols else "target"
                
                business_recommendations = await generate_business_recommendations(
                    insights=ai_insights_list[:5],
                    target_column=target_for_recommendations,
                    model_performance=best_model_metrics
                )
                logging.info(f"Generated {len(business_recommendations)} business recommendations")
        except Exception as e:
            logging.error(f"Business recommendations failed: {str(e)}", exc_info=True)
        
        # Update dataset training metadata
        db_adapter = get_db()
        dataset = await db_adapter.get_dataset(dataset_id)
        training_count = dataset.get("training_count", 0) + 1
        last_trained_at = datetime.now(timezone.utc).isoformat()
        
        # Update dataset with new training metadata
        try:
            await db_adapter.update_dataset(dataset_id, {
                "training_count": training_count,
                "last_trained_at": last_trained_at,
                "updated_at": last_trained_at
            })
            logger.info(f"Updated training metadata: count={training_count}, last_trained={last_trained_at}")
        except Exception as e:
            logger.warning(f"Failed to update training metadata: {str(e)}")
        
        # Build enhanced volume analysis from profile data
        volume_analysis = {
            "total_records": int(len(df)),
            "by_dimensions": [],
            "summary": {
                "total_columns": int(len(df.columns)),
                "numeric_columns": int(len(df.select_dtypes(include=[np.number]).columns)),
                "categorical_columns": int(len(df.select_dtypes(include=['object', 'category']).columns)),
                "memory_usage_mb": float(round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2))
            }
        }
        
        # Add categorical breakdown for volume analysis
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        for col in categorical_cols[:5]:  # Top 5 categorical columns
            value_counts = df[col].value_counts()
            # Convert to Python native types for JSON serialization
            value_counts_dict = {str(k): int(v) for k, v in value_counts.head(10).items()}
            
            # Calculate insights
            total = int(value_counts.sum())
            top_category = str(value_counts.index[0]) if len(value_counts) > 0 else "N/A"
            top_value = int(value_counts.iloc[0]) if len(value_counts) > 0 else 0
            top_percentage = float((top_value / total * 100)) if len(value_counts) > 0 and total > 0 else 0.0
            
            # Check for imbalance
            imbalance_status = ""
            if top_percentage > 70:
                imbalance_status = " ⚠️ Highly imbalanced - one category dominates."
            elif top_percentage > 50:
                imbalance_status = " ⚠️ Moderately imbalanced."
            
            # Calculate diversity
            unique_count = int(len(value_counts))
            diversity_pct = float((unique_count / total) * 100)
            
            diversity_status = ""
            if diversity_pct > 50:
                diversity_status = " High diversity - many unique values."
            elif diversity_pct < 5:
                diversity_status = " Low diversity - few unique values."
            
            volume_analysis["by_dimensions"].append({
                "dimension": str(col),
                "breakdown": value_counts_dict,
                "total_unique": unique_count,
                "top_value": top_category,
                "top_percentage": round(top_percentage, 1),
                "insights": f"Most common: {top_category} ({top_percentage:.1f}%). Total unique values: {unique_count}.{imbalance_status}{diversity_status}",
                "chart_data": {
                    "labels": [str(k) for k in value_counts_dict.keys()],
                    "values": [int(v) for v in value_counts_dict.values()]
                }
            })
        
        # Add numeric column volume analysis
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        numeric_volume = []
        for col in numeric_cols[:5]:  # Top 5 numeric columns
            col_min = float(df[col].min())
            col_max = float(df[col].max())
            col_mean = float(df[col].mean())
            col_median = float(df[col].median())
            col_std = float(df[col].std())
            
            # Calculate range analysis
            range_size = col_max - col_min
            range_status = ""
            if col_std > 0:
                coefficient_variation = (col_std / col_mean) * 100 if col_mean != 0 else 0
                if coefficient_variation > 100:
                    range_status = " High variability detected."
                elif coefficient_variation < 10:
                    range_status = " Low variability - values are consistent."
            
            numeric_volume.append({
                "dimension": str(col),
                "min": round(col_min, 2),
                "max": round(col_max, 2),
                "mean": round(col_mean, 2),
                "median": round(col_median, 2),
                "std": round(col_std, 2),
                "range": round(range_size, 2),
                "insights": f"Range: {col_min:.2f} to {col_max:.2f}. Mean: {col_mean:.2f}, Median: {col_median:.2f}.{range_status}"
            })
        
        volume_analysis["numeric_summary"] = numeric_volume
        
        # PHASE 4: Domain Detection and Domain-Specific Insights
        domain_info = None
        domain_insights = None
        domain_charts = []
        
        if target_cols and len(target_cols) > 0:
            target_col = target_cols[0]
            # Get feature columns
            feature_columns = [col for col in df_analysis.select_dtypes(include=[np.number]).columns if col != target_col]
            
            # Detect domain
            domain_info = detect_domain(df_analysis, feature_columns, target_col)
            
            # Get domain-specific insights
            domain_insights = get_domain_specific_insights(
                domain_info["domain"],
                df_analysis,
                target_col,
                predictions=None  # We can pass predictions here if needed
            )
            
            # Generate domain-specific charts (only for small-medium datasets to avoid slowdown)
            if domain_info and domain_info.get("visualization_config") and len(df_analysis) <= 10000:
                try:
                    domain_charts = generate_domain_specific_charts(
                        domain=domain_info["domain"],
                        df=df_analysis,
                        target_column=target_col,
                        viz_config=domain_info["visualization_config"]
                    )
                    logging.info(f"Generated {len(domain_charts)} domain-specific charts")
                except Exception as e:
                    logging.error(f"Domain chart generation failed: {e}")
                    domain_charts = []
            elif len(df_analysis) > 10000:
                logging.info(f"Skipping domain charts for large dataset ({len(df_analysis)} rows)")
                domain_charts = []
        
        response = {
            "profile": profile,
            "models": models_result.get("models", []),
            "ml_models": models_result.get("models", []),  # Frontend expects ml_models
            "auto_charts": auto_charts,
            "skipped_charts": skipped_charts,  # Why charts were not generated
            "correlations": correlations,
            "insights": insights,
            "training_info": models_result.get("training_info", {}),
            "volume_analysis": volume_analysis,  # Frontend expects volume_analysis
            "training_metadata": {
                "training_count": training_count,
                "last_trained_at": last_trained_at,
                "dataset_size": len(df)
            },
            # Phase 3: Enhanced AI features
            "ai_insights": ai_insights_list,  # Structured insights list
            "explainability": explainability_results,  # Model explainability info
            "business_recommendations": business_recommendations,  # AI-generated recommendations
            "phase_3_enabled": True,  # Flag to indicate Phase 3 features are available
            # Phase 1: Problem type information
            "problem_type": models_result.get("problem_type", problem_type),  # Detected or specified problem type
            "n_classes": models_result.get("n_classes"),  # For classification
            "class_labels": models_result.get("class_labels"),  # For classification
            # Phase 4: Domain Detection
            "domain_info": domain_info,  # Domain detection results
            "domain_insights": domain_insights,  # Domain-specific insights and recommendations
            "domain_charts": domain_charts  # Domain-specific visualizations
        }
        
        # Add selection feedback if user made a selection
        if selection_feedback:
            response["selection_feedback"] = selection_feedback
        
        # Add user expectation to response for frontend display/storage
        if user_expectation:
            response["user_expectation"] = user_expectation
        
        # PHASE 3: Generate historical trends and domain-adapted forecasting summaries
        sre_forecast = {}
        historical_trends = {}
        if all_models and len(all_models) > 0 and target_cols:
            try:
                # Calculate historical trends for target variable
                target_col = target_cols[0]
                if target_col in df_analysis.columns:
                    try:
                        target_data = df_analysis[target_col].dropna()
                        if len(target_data) > 0:
                            historical_trends = {
                                "target_variable": target_col,
                                "current_value": float(target_data.iloc[-1]) if len(target_data) > 0 else None,
                                "mean": float(target_data.mean()),
                                "median": float(target_data.median()),
                                "min": float(target_data.min()),
                                "max": float(target_data.max()),
                                "std": float(target_data.std()),
                                "trend": "increasing" if len(target_data) > 10 and target_data.iloc[-5:].mean() > target_data.iloc[:5].mean() else "decreasing" if len(target_data) > 10 and target_data.iloc[-5:].mean() < target_data.iloc[:5].mean() else "stable",
                                "recent_avg": float(target_data.iloc[-10:].mean()) if len(target_data) >= 10 else float(target_data.mean()),
                                "historical_avg": float(target_data.mean()),
                                "data_points": len(target_data)
                            }
                            logger.info(f"📊 Historical trends calculated for {target_col}")
                    except Exception as e:
                        logger.error(f"Failed to calculate historical trends: {str(e)}")
                
                logger.info(f"🔮 Generating domain-adapted forecast summaries for {len(all_models)} models...")
                
                # Detect domain for adapted terminology
                domain = "general"
                if user_expectation:
                    domain_info = await azure_service.detect_domain_and_adapt(
                        user_expectation=user_expectation,
                        columns=df_analysis.columns.tolist()
                    )
                    domain = domain_info.get('domain', 'general')
                    logger.info(f"📊 Detected domain: {domain}")
                
                # CRITICAL FIX: Azure service expects 'ml_models' key, not 'models'
                model_results_for_forecast = {
                    "ml_models": all_models,  # Use all_models directly
                    "problem_type": problem_type
                }
                
                sre_forecast = await azure_service.generate_sre_forecast(
                    model_results=model_results_for_forecast,
                    data_summary=data_summary,
                    target_column=target_cols[0] if target_cols else "unknown",
                    user_expectation=user_expectation,
                    domain=domain,
                    columns=df_analysis.columns.tolist()
                )
                if sre_forecast and not sre_forecast.get('error'):
                    response["sre_forecast"] = sre_forecast
                    response["detected_domain"] = domain  # Include domain in response
                    logger.info(f"✅ Domain-adapted forecast generated for {domain}: {len(sre_forecast.get('forecasts', []))} forecasts, {len(sre_forecast.get('critical_alerts', []))} alerts")
                elif sre_forecast and sre_forecast.get('error'):
                    logger.error(f"❌ SRE forecast generation failed: {sre_forecast.get('error')}")
                
                # Add historical trends to response
                if historical_trends:
                    response["historical_trends"] = historical_trends
                    logger.info(f"✅ Historical trends added to response")
            except Exception as e:
                logger.error(f"Failed to generate forecast: {str(e)}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Analysis failed: {str(e)}")


@router.post("/suggest-from-expectation")
async def suggest_from_expectation(request: Dict[str, Any]):
    """
    Smart Selection: Suggest target and features based on user's natural language expectation
    DOMAIN-AGNOSTIC: Works for any dataset type (IT, finance, ecommerce, food, healthcare, etc.)
    """
    try:
        dataset_id = request.get("dataset_id")
        user_expectation = request.get("user_expectation", "")
        
        if not user_expectation:
            raise HTTPException(400, "user_expectation is required")
        
        # Load dataset
        df = await load_dataframe(dataset_id)
        
        # Prepare column information
        columns = df.columns.tolist()
        dtypes = {col: str(df[col].dtype) for col in columns}
        
        # Get sample data (first row as dict)
        sample_data = df.head(1).to_dict('records')[0] if len(df) > 0 else {}
        
        # Use Azure OpenAI for smart suggestions
        azure_service = get_azure_openai_service()
        
        if not azure_service.is_available():
            raise HTTPException(503, "AI suggestions require Azure OpenAI to be configured")
        
        logger.info(f"🧠 Generating smart selection for: '{user_expectation}'")
        
        suggestions = await azure_service.suggest_target_and_features(
            user_expectation=user_expectation,
            columns=columns,
            dtypes=dtypes,
            sample_data=sample_data
        )
        
        logger.info(f"✅ Smart selection generated: target={suggestions.get('suggested_target')}, features={len(suggestions.get('suggested_features', []))}")
        
        return {
            "success": True,
            "suggestions": suggestions,
            "dataset_info": {
                "total_columns": len(columns),
                "row_count": len(df)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Smart selection failed: {str(e)}")
        raise HTTPException(500, f"Failed to generate suggestions: {str(e)}")


@router.post("/chat-action")
async def chat_action(request: Dict[str, Any]):
    """Handle chat-based analysis actions with Azure OpenAI intelligence"""
    try:
        dataset_id = request.get("dataset_id")
        message = request.get("message", "")
        conversation_history = request.get("conversation_history", [])
        
        df = await load_dataframe(dataset_id)
        
        # Try Azure OpenAI first
        azure_service = get_azure_openai_service()
        
        if azure_service.is_available():
            # Check if it's a chart request
            if any(keyword in message.lower() for keyword in ['chart', 'plot', 'graph', 'visualize', 'show']):
                # Parse chart request with Azure OpenAI
                columns = df.columns.tolist()
                parsed = await azure_service.parse_chart_request(message, columns)
                
                if parsed.get('columns_found'):
                    # Generate chart
                    from app.services.chat_service import (
                        handle_scatter_chart_request_v2,
                        handle_line_chart_request_v2,
                        handle_bar_chart_request_v2,
                        handle_histogram_chart_request
                    )
                    
                    chart_type = parsed['chart_type']
                    x_col = parsed.get('x_column')
                    y_col = parsed.get('y_column')
                    
                    if chart_type == 'scatter' and x_col and y_col:
                        return handle_scatter_chart_request_v2(df, x_col, y_col, parsed.get('explanation', ''))
                    elif chart_type == 'line':
                        return handle_line_chart_request_v2(df, x_col, y_col, parsed.get('explanation', ''))
                    elif chart_type == 'bar' and x_col:
                        return handle_bar_chart_request_v2(df, x_col, parsed.get('explanation', ''))
                    elif chart_type == 'histogram' and x_col:
                        return handle_histogram_chart_request(df, x_col, parsed.get('explanation', ''))
                else:
                    return {
                        "type": "error",
                        "message": parsed.get('error', 'Could not parse chart request'),
                        "success": False
                    }
            else:
                # General Q&A with Azure OpenAI
                data_context = {
                    'columns': df.columns.tolist(),
                    'row_count': len(df),
                    'problem_type': 'general'
                }
                result = await azure_service.chat_with_data(message, data_context, conversation_history)
                return result
        else:
            # Fallback to chat service (now uses Azure OpenAI)
            from app.services.chat_service import process_chat_message_async
            result = await process_chat_message_async(df, message, conversation_history)
            return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat action error: {str(e)}")
        raise HTTPException(500, f"Chat action failed: {str(e)}")


@router.post("/save-state")
async def save_analysis_state(request: SaveStateRequest):
    """Save analysis state with GridFS for large states - OPTIMIZED"""
    try:
        state_id = str(uuid.uuid4())
        
        # OPTIMIZATION 1: Remove large/redundant data from analysis_data before saving
        # analysis_data structure: {predictive_analysis: {...}, visualization: {...}, data_profiler: {...}}
        optimized_analysis_data = {}
        if request.analysis_data:
            for section_key, section_value in request.analysis_data.items():
                # Handle each section (predictive_analysis, visualization, data_profiler)
                if not isinstance(section_value, dict):
                    optimized_analysis_data[section_key] = section_value
                    continue
                
                optimized_section = {}
                for key, value in section_value.items():
                    # Skip storing large chart data - only store config
                    if key == "auto_charts" and isinstance(value, list):
                        optimized_section[key] = [
                            {
                                "chart_type": chart.get("chart_type"),
                                "title": chart.get("title"),
                                "description": chart.get("description"),
                                # Don't store full plotly data, only metadata
                            }
                            for chart in value[:5]  # Limit to first 5 charts
                        ]
                    # Store model results - KEEP FULL MODEL DATA FOR RESTORE
                    elif key == "ml_models" and isinstance(value, list):
                        # CRITICAL FIX: Store complete model data for proper restore
                        optimized_section[key] = value
                    # Skip raw data, keep only metadata
                    elif key not in ["raw_data", "full_dataset", "data_preview"]:
                        optimized_section[key] = value
                
                optimized_analysis_data[section_key] = optimized_section
        
        # OPTIMIZATION 2: Limit chat history to last 50 messages
        optimized_chat_history = request.chat_history[-50:] if request.chat_history else []
        
        # Prepare optimized state data
        full_state_data = {
            "analysis_data": optimized_analysis_data,
            "chat_history": optimized_chat_history
        }
        
        # Calculate size
        state_json = json.dumps(full_state_data)
        state_size = len(state_json.encode('utf-8'))
        
        logger.info(f"Saving workspace: {request.state_name}, size: {state_size / 1024:.2f} KB")
        
        # Choose storage method - Use BLOB/GridFS for anything > 2MB
        if state_size > 2 * 1024 * 1024:  # 2MB threshold (reduced from 10MB)
            # Store in BLOB/GridFS with compression
            import gzip
            compressed_data = gzip.compress(state_json.encode('utf-8'))
            
            db_adapter = get_db()
            file_id = await db_adapter.store_file(
                f"workspace_{state_id}.json.gz",
                compressed_data,
                metadata={
                    "type": "workspace_state",
                    "state_id": state_id,
                    "dataset_id": request.dataset_id,
                    "state_name": request.state_name,
                    "compressed": True
                }
            )
            
            # Use 'blob' for Oracle, 'gridfs' is MongoDB-specific but we normalize to 'blob'
            storage_type = "blob"  # Works for both MongoDB (GridFS) and Oracle (BLOB)
            
            # Extract user expectation and domain from analysis data if present
            user_expectation = None
            detected_domain = None
            if analysis_data and isinstance(analysis_data, dict):
                if 'user_expectation' in analysis_data:
                    user_expectation = analysis_data.get('user_expectation')
                if 'detected_domain' in analysis_data:
                    detected_domain = analysis_data.get('detected_domain')
            
            state_doc = {
                "id": state_id,
                "dataset_id": request.dataset_id,
                "state_name": request.state_name,
                "storage_type": storage_type,
                "file_id": str(file_id),  # Renamed from gridfs_file_id for compatibility
                "size_bytes": state_size,
                "compressed_size": len(compressed_data),
                "user_expectation": user_expectation,  # NEW: Store user's prediction goal
                "detected_domain": detected_domain,  # NEW: Store detected domain
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            logger.info(f"Stored in BLOB storage with compression: {len(compressed_data) / 1024:.2f} KB")
        else:
            # Store directly in database
            # Extract user expectation from analysis data if present
            user_expectation = None
            detected_domain = None
            if analysis_data and isinstance(analysis_data, dict):
                if 'user_expectation' in analysis_data:
                    user_expectation = analysis_data.get('user_expectation')
                if 'detected_domain' in analysis_data:
                    detected_domain = analysis_data.get('detected_domain')
            
            state_doc = {
                "id": state_id,
                "dataset_id": request.dataset_id,
                "state_name": request.state_name,
                "storage_type": "direct",
                "analysis_data": optimized_analysis_data,
                "chat_history": optimized_chat_history,
                "size_bytes": state_size,
                "user_expectation": user_expectation,  # NEW: Store user's prediction goal
                "detected_domain": detected_domain,  # NEW: Store detected domain
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            logger.info(f"Stored directly in database: {state_size / 1024:.2f} KB")
        
        # Insert with timeout protection
        db_adapter = get_db()
        await db_adapter.save_workspace(state_doc)
        
        # CRITICAL FIX: Update training_metadata with the workspace_name
        # This ensures training metadata shows the correct workspace name
        try:
            await db_adapter.update_training_metadata_workspace_name(
                dataset_id=request.dataset_id,
                workspace_name=request.state_name
            )
            logger.info(f"✅ Updated training metadata with workspace_name: {request.state_name}")
        except Exception as update_error:
            logger.warning(f"⚠️ Failed to update training metadata workspace_name: {update_error}")
            # Don't fail the save operation if metadata update fails
        
        return {
            "state_id": state_id,
            "message": f"Workspace '{request.state_name}' saved successfully",
            "storage_type": state_doc["storage_type"],
            "size_mb": round(state_size / (1024 * 1024), 2),
            "optimized": True
        }
        
    except Exception as e:
        logger.error(f"Failed to save workspace: {str(e)}", exc_info=True)
        raise HTTPException(500, f"Failed to save state: {str(e)}")


@router.get("/load-state/{state_id}")
async def load_analysis_state(state_id: str):
    """Load saved analysis state - OPTIMIZED"""
    try:
        db_adapter = get_db()
        state = await db_adapter.get_workspace(state_id)
        if not state:
            raise HTTPException(404, "Analysis state not found")
        
        # Load from BLOB/GridFS if needed
        if state.get("storage_type") in ["blob", "gridfs"]:
            # Support both old 'gridfs_file_id' and new 'file_id' field names
            file_id = state.get("file_id") or state.get("gridfs_file_id")
            if file_id:
                data = await db_adapter.retrieve_file(file_id)
                
                # Check if data is compressed (assume it is if filename ends with .gz)
                if file_id and str(file_id).endswith('.gz'):
                    import gzip
                    data = gzip.decompress(data)
                
                full_state_data = json.loads(data.decode('utf-8'))
                
                state["analysis_data"] = full_state_data.get("analysis_data", {})
                state["chat_history"] = full_state_data.get("chat_history", [])
                state.pop("gridfs_file_id", None)
                state.pop("file_id", None)
                state.pop("storage_type", None)
        
        return state
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to load workspace: {str(e)}", exc_info=True)
        raise HTTPException(500, f"Failed to load state: {str(e)}")
        raise HTTPException(500, f"Failed to load state: {str(e)}")


@router.get("/saved-states/{dataset_id}")
async def get_saved_states(dataset_id: str):
    """Get all saved states for a dataset"""
    try:
        db_adapter = get_database_adapter()
        states = await db_adapter.list_workspaces(dataset_id)
        return {"states": states}
    except Exception as e:
        logger.error(f"Failed to fetch saved states: {str(e)}")
        raise HTTPException(500, f"Failed to fetch saved states: {str(e)}")


@router.delete("/delete-state/{state_id}")
async def delete_analysis_state(state_id: str):
    """Delete saved analysis state"""
    try:
        db_adapter = get_db()
        state = await db_adapter.get_workspace(state_id)
        if not state:
            raise HTTPException(404, "Analysis state not found")
        
        # Delete BLOB/GridFS file if exists
        if state.get("storage_type") in ["blob", "gridfs"]:
            file_id = state.get("file_id") or state.get("gridfs_file_id")
            if file_id:
                try:
                    await db_adapter.delete_file(file_id)
                except:
                    pass
        
        # Delete metadata
        db_adapter = get_db()
        result = await db_adapter.delete_workspace(state_id)
        if result.deleted_count == 0:
            raise HTTPException(404, "Analysis state not found")
        
        return {"message": "Analysis state deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to delete state: {str(e)}")


# ============================================
# Intelligence Endpoints
# ============================================

@router.post("/validate-chart-request")
async def validate_chart_request(request: Dict[str, Any]):
    """
    Validate if a chart request is feasible
    Returns intelligent feedback and suggestions
    """
    try:
        dataset_id = request.get("dataset_id")
        chart_type = request.get("chart_type")
        column = request.get("column")
        y_column = request.get("y_column")
        
        if not dataset_id or not chart_type or not column:
            raise HTTPException(400, "Missing required fields: dataset_id, chart_type, column")
        
        # Load dataset
        db_adapter = get_db()
        dataset = await db_adapter.get_dataset(dataset_id)
        if not dataset:
            raise HTTPException(404, "Dataset not found")
        
        # Load data
        if dataset.get("gridfs_file_id") or dataset.get("file_id"):
            file_id = dataset.get("gridfs_file_id") or dataset.get("file_id")
            data_bytes = await db_adapter.retrieve_file(file_id)
            df = pd.read_json(io.BytesIO(data_bytes))
        else:
            df = pd.DataFrame(dataset.get("data", []))
        
        # Validate chart request
        validation = chart_intelligence.validate_chart_request(
            df=df,
            chart_type=chart_type,
            column=column,
            y_column=y_column
        )
        
        return validation
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating chart request: {str(e)}")
        raise HTTPException(500, f"Validation failed: {str(e)}")


@router.post("/validate-variables")
async def validate_variables(request: Dict[str, Any]):
    """
    Validate variable selection and suggest better alternatives if needed
    """
    try:
        dataset_id = request.get("dataset_id")
        target_variables = request.get("target_variables", [])
        features = request.get("features", [])
        
        if not dataset_id:
            raise HTTPException(400, "Missing dataset_id")
        
        # Handle both formats
        if not isinstance(target_variables, list):
            target_variables = [target_variables] if target_variables else []
        
        # Load dataset
        db_adapter = get_db()
        dataset = await db_adapter.get_dataset(dataset_id)
        if not dataset:
            raise HTTPException(404, "Dataset not found")
        
        # Load data
        if dataset.get("gridfs_file_id") or dataset.get("file_id"):
            file_id = dataset.get("gridfs_file_id") or dataset.get("file_id")
            data_bytes = await db_adapter.retrieve_file(file_id)
            df = pd.read_json(io.BytesIO(data_bytes))
        else:
            df = pd.DataFrame(dataset.get("data", []))
        
        # Validate variables
        validation = variable_intelligence.validate_variable_selection(
            df=df,
            target_variables=target_variables,
            features=features
        )
        
        return validation
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating variables: {str(e)}")
        raise HTTPException(500, f"Validation failed: {str(e)}")



@router.post("/time-series")
async def time_series_analysis_endpoint(request: Dict[str, Any]):
    """
    Perform time series forecasting and anomaly detection
    
    Request format:
    {
        "dataset_id": "string",
        "time_column": "string",
        "target_column": "string",
        "forecast_periods": 30 (optional),
        "forecast_method": "prophet" | "lstm" | "both" (optional, default: "prophet")
    }
    """
    try:
        dataset_id = request.get("dataset_id")
        time_column = request.get("time_column")
        target_column = request.get("target_column")
        forecast_periods = request.get("forecast_periods", 30)
        forecast_method = request.get("forecast_method", "prophet")
        
        if not all([dataset_id, time_column, target_column]):
            raise HTTPException(400, "Missing required parameters: dataset_id, time_column, target_column")
        
        # Load dataframe
        df = await load_dataframe(dataset_id)
        
        # Validate columns exist
        if time_column not in df.columns:
            raise HTTPException(400, f"Time column '{time_column}' not found in dataset")
        if target_column not in df.columns:
            raise HTTPException(400, f"Target column '{target_column}' not found in dataset")
        
        # Perform time series analysis
        results = time_series_service.analyze_time_series(
            df=df,
            time_column=time_column,
            target_column=target_column,
            forecast_periods=forecast_periods,
            forecast_method=forecast_method
        )
        
        # Update training counter
        db_adapter = get_db()
        await db_adapter.increment_training_count(dataset_id)
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Time series analysis failed: {str(e)}")
        raise HTTPException(500, f"Time series analysis failed: {str(e)}")


@router.get("/datetime-columns/{dataset_id}")
async def get_datetime_columns(dataset_id: str):
    """
    Get all potential datetime columns in the dataset
    """
    try:
        df = await load_dataframe(dataset_id)
        datetime_cols = time_series_service.detect_datetime_columns(df)
        
        return {
            "datetime_columns": datetime_cols,
            "total_columns": len(df.columns)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to detect datetime columns: {str(e)}")
        raise HTTPException(500, f"Failed to detect datetime columns: {str(e)}")


@router.post("/hyperparameter-tuning")
async def hyperparameter_tuning_endpoint(request: Dict[str, Any]):
    """
    Perform hyperparameter tuning for a specific model
    
    Request format:
    {
        "dataset_id": "string",
        "target_column": "string",
        "model_type": "random_forest" | "xgboost" | "lightgbm",
        "problem_type": "regression" | "classification",
        "search_type": "grid" | "random",
        "param_grid": {} (optional),
        "n_iter": 20 (for random search)
    }
    """
    try:
        from app.services import hyperparameter_service
        
        dataset_id = request.get("dataset_id")
        target_column = request.get("target_column")
        model_type = request.get("model_type", "random_forest")
        problem_type = request.get("problem_type", "regression")
        search_type = request.get("search_type", "grid")
        param_grid = request.get("param_grid")
        n_iter = request.get("n_iter", 20)
        
        if not all([dataset_id, target_column]):
            raise HTTPException(400, "Missing required parameters")
        
        # Load data
        df = await load_dataframe(dataset_id)
        
        # Prepare features and target
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        feature_cols = [col for col in numeric_cols if col != target_column]
        
        X = df[feature_cols].fillna(df[feature_cols].mean())
        y = df[target_column].fillna(df[target_column].mean() if problem_type == "regression" else df[target_column].mode()[0])
        
        # Split data
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Perform tuning
        if search_type == "grid":
            results = hyperparameter_service.tune_hyperparameters_grid(
                X_train, y_train, model_type, problem_type, param_grid
            )
        else:
            results = hyperparameter_service.tune_hyperparameters_random(
                X_train, y_train, model_type, problem_type, param_grid, n_iter
            )
        
        if "error" in results:
            raise HTTPException(500, results["error"])
        
        # Remove model object from response (not JSON serializable)
        results_clean = {k: v for k, v in results.items() if k != "model"}
        
        return {
            "success": True,
            "model_type": model_type,
            "search_type": search_type,
            **results_clean
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Hyperparameter tuning failed: {str(e)}")
        raise HTTPException(500, f"Tuning failed: {str(e)}")


@router.post("/feedback/submit")
async def submit_prediction_feedback(request: Dict[str, Any]):
    """
    Submit user feedback for a prediction
    
    Request format:
    {
        "prediction_id": "string",
        "is_correct": bool,
        "actual_outcome": any (optional),
        "user_comment": "string" (optional)
    }
    """
    try:
        from app.services.feedback_service import FeedbackTracker
        
        prediction_id = request.get("prediction_id")
        is_correct = request.get("is_correct")
        actual_outcome = request.get("actual_outcome")
        user_comment = request.get("user_comment")
        
        if not prediction_id or is_correct is None:
            raise HTTPException(400, "Missing required parameters")
        
        tracker = FeedbackTracker(db)
        success = await tracker.submit_feedback(
            prediction_id,
            is_correct,
            actual_outcome,
            user_comment
        )
        
        if success:
            return {"success": True, "message": "Feedback submitted successfully"}
        else:
            raise HTTPException(404, "Prediction not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Feedback submission failed: {str(e)}")
        raise HTTPException(500, f"Failed to submit feedback: {str(e)}")


@router.get("/feedback/stats/{dataset_id}/{model_name}")
async def get_feedback_stats(dataset_id: str, model_name: str):
    """
    Get feedback statistics for a model
    """
    try:
        from app.services.feedback_service import FeedbackTracker
        
        tracker = FeedbackTracker(db)
        stats = await tracker.get_model_performance_stats(dataset_id, model_name)
        
        return stats
        
    except Exception as e:
        logging.error(f"Failed to get feedback stats: {str(e)}")
        raise HTTPException(500, f"Failed to get stats: {str(e)}")


@router.post("/feedback/retrain")
async def retrain_with_feedback(request: Dict[str, Any]):
    """
    Retrain model using feedback data
    
    Request format:
    {
        "dataset_id": "string",
        "model_name": "string",
        "target_column": "string"
    }
    """
    try:
        from app.services.feedback_service import FeedbackTracker
        from app.services.ml_service import train_models_auto
        
        dataset_id = request.get("dataset_id")
        model_name = request.get("model_name")
        target_column = request.get("target_column")
        
        if not all([dataset_id, model_name, target_column]):
            raise HTTPException(400, "Missing required parameters")
        
        # Get feedback data
        tracker = FeedbackTracker(db)
        feedback_df = await tracker.prepare_retraining_data(dataset_id, model_name)
        
        if feedback_df.empty:
            raise HTTPException(400, "No feedback data available for retraining")
        
        # Rename actual_outcome to target column
        feedback_df = feedback_df.rename(columns={"actual_outcome": target_column})
        
        # Train model with feedback data
        results = train_models_auto(feedback_df, target_column, problem_type="auto")
        
        return {
            "success": True,
            "message": f"Model retrained with {len(feedback_df)} feedback samples",
            "models": results.get("models", []),
            "feedback_samples": len(feedback_df)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Retraining failed: {str(e)}")
        raise HTTPException(500, f"Retraining failed: {str(e)}")


@router.post("/relational/join")
async def join_datasets(request: Dict[str, Any]):
    """
    Join multiple datasets
    
    Request format:
    {
        "dataset_ids": ["id1", "id2"],
        "join_keys": [{"left": "col1", "right": "col2"}],
        "join_type": "inner" | "left" | "right" | "outer"
    }
    """
    try:
        from app.services.relational_service import join_tables, detect_foreign_keys
        
        dataset_ids = request.get("dataset_ids", [])
        join_keys = request.get("join_keys", [])
        join_type = request.get("join_type", "inner")
        auto_detect = request.get("auto_detect", False)
        
        if len(dataset_ids) < 2:
            raise HTTPException(400, "At least 2 datasets required for join")
        
        # Load datasets
        dfs = []
        for dataset_id in dataset_ids:
            df = await load_dataframe(dataset_id)
            dfs.append(df)
        
        # Auto-detect foreign keys if requested
        if auto_detect and len(dfs) == 2:
            detected_fks = detect_foreign_keys(dfs[0], dfs[1])
            if detected_fks:
                return {
                    "auto_detected_keys": [
                        {"left": left, "right": right} 
                        for left, right in detected_fks
                    ]
                }
        
        # Perform join
        if len(join_keys) == 0:
            raise HTTPException(400, "No join keys specified")
        
        result_df = dfs[0]
        for i in range(1, len(dfs)):
            if i - 1 < len(join_keys):
                join_key = join_keys[i - 1]
                result_df = join_tables(
                    result_df,
                    dfs[i],
                    left_on=join_key["left"],
                    right_on=join_key["right"],
                    how=join_type
                )
        
        # Store joined dataset
        joined_id = str(uuid.uuid4())
        dataset_doc = {
            "id": joined_id,
            "name": f"Joined_{len(dataset_ids)}_tables",
            "source": "relational_join",
            "columns": result_df.columns.tolist(),
            "dtypes": {col: str(dtype) for col, dtype in result_df.dtypes.items()},
            "row_count": len(result_df),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        db_adapter = get_db()
        dataset_id = await db_adapter.create_dataset(dataset_doc)
        
        return {
            "success": True,
            "joined_dataset_id": joined_id,
            "row_count": len(result_df),
            "column_count": len(result_df.columns)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Dataset join failed: {str(e)}")
        raise HTTPException(500, f"Join failed: {str(e)}")


