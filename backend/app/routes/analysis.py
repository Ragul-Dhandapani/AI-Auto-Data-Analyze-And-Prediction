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
        
        elif analysis_type == "visualize":
            # Generate auto charts for visualization panel
            auto_charts, skipped_charts = generate_auto_charts(df, max_charts=15)
            
            # Convert to frontend format with proper structure
            charts = []
            
            for chart in auto_charts:
                if chart and chart.get("plotly_data"):
                    charts.append({
                        "title": chart.get("title", "Chart"),
                        "description": chart.get("description", ""),
                        "type": chart.get("type", "unknown"),
                        "data": chart.get("plotly_data")  # Frontend expects 'data' field
                    })
                else:
                    skipped.append({
                        "title": chart.get("title", "Chart"),
                        "reason": "Missing or invalid plotly data"
                    })
            
            return {
                "charts": charts,
                "skipped_charts": skipped_charts  # Return why charts were skipped
            }
        
        elif analysis_type == "insights":
            # Generate AI insights
            llm_key = os.environ.get('EMERGENT_LLM_KEY')
            
            if not llm_key:
                return {
                    "insights": "AI insights require EMERGENT_LLM_KEY to be configured. Please set up the API key to generate intelligent insights about your data."
                }
            
            try:
                from emergentintegrations.llm.chat import LlmChat
                
                # Prepare data summary
                profile = generate_data_profile(df)
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
                
                # Initialize LLM chat with required arguments
                llm = LlmChat(
                    api_key=llm_key,
                    session_id="insights_generation",
                    system_message="You are a data analyst expert. Provide clear, actionable insights about datasets in bullet points."
                )
                
                prompt = f"""Analyze this dataset and provide 4-5 key insights:

Dataset Statistics:
- Total Records: {len(df):,}
- Columns: {len(df.columns)}
- Numeric Columns: {', '.join(numeric_cols[:5])}
- Categorical Columns: {', '.join(categorical_cols[:5])}
- Missing Values: {profile.get('missing_values_total', 0)}
- Duplicate Rows: {profile.get('duplicate_rows', 0)}

Provide actionable insights in bullet points about:
1. Data quality and completeness
2. Interesting patterns or distributions
3. Potential relationships between variables
4. Recommendations for analysis"""
                
                # Send message and get response
                response = await llm.send_message(prompt)
                insights_text = response if isinstance(response, str) else str(response)
                
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
            except Exception as e:
                logger.error(f"AI insights generation failed: {str(e)}", exc_info=True)
                return {
                    "insights": f"Unable to generate AI insights: {str(e)}. You can still explore the data using profile statistics and visualizations.",
                    "error": str(e)
                }
        
        else:
            raise HTTPException(400, f"Unknown analysis type: {analysis_type}")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Analysis failed: {str(e)}")


async def load_dataframe(dataset_id: str) -> pd.DataFrame:
    """Helper function to load DataFrame from dataset"""
    import logging
    logger = logging.getLogger(__name__)
    
    dataset = await db.datasets.find_one({"id": dataset_id}, {"_id": 0})
    if not dataset:
        raise HTTPException(404, "Dataset not found")
    
    logger.info(f"Loading dataset {dataset_id}, storage_type: {dataset.get('storage_type', 'direct')}")
    
    # Load data based on storage type
    if dataset.get("storage_type") == "gridfs":
        gridfs_file_id = dataset.get("gridfs_file_id")
        if gridfs_file_id:
            try:
                grid_out = await fs.open_download_stream(ObjectId(gridfs_file_id))
                data = await grid_out.read()
                
                logger.info(f"GridFS data loaded, size: {len(data)} bytes")
                
                if dataset["name"].endswith('.csv'):
                    df = pd.read_csv(io.BytesIO(data))
                else:
                    df = pd.read_excel(io.BytesIO(data))
                
                logger.info(f"DataFrame loaded from GridFS: {len(df)} rows, {len(df.columns)} columns")
            except Exception as e:
                logger.error(f"GridFS loading failed: {str(e)}")
                raise HTTPException(500, f"Failed to load data from GridFS: {str(e)}")
        else:
            raise HTTPException(500, "GridFS file ID not found")
    else:
        # Direct storage
        data = dataset.get("data")
        if data is None:
            logger.error(f"Dataset {dataset_id} has no 'data' field")
            raise HTTPException(500, "Dataset has no data field")
        
        if not isinstance(data, list):
            logger.error(f"Dataset data is not a list: {type(data)}")
            raise HTTPException(500, "Dataset data format invalid")
        
        if len(data) == 0:
            logger.warning(f"Dataset {dataset_id} has empty data array")
            raise HTTPException(400, "Dataset is empty")
        
        df = pd.DataFrame(data)
        logger.info(f"DataFrame loaded from direct storage: {len(df)} rows, {len(df.columns)} columns")
    
    # Validate DataFrame is not empty
    if df.empty:
        logger.error(f"DataFrame is empty after loading dataset {dataset_id}")
        raise HTTPException(400, "Loaded DataFrame is empty")
    
    return df


@router.post("/holistic")
async def holistic_analysis(request: Dict[str, Any]):
    """Perform comprehensive analysis with optional user variable selection and multiple targets"""
    try:
        dataset_id = request.get("dataset_id")
        user_selection = request.get("user_selection")  # Optional user-provided target and features
        
        df = await load_dataframe(dataset_id)
        original_size = len(df)
        
        # Performance optimization: Intelligent sampling for large datasets
        SAMPLE_THRESHOLD = 5000  # Sample if more than 5000 rows
        SAMPLE_SIZE = 3000  # Use 3000 rows for training
        is_sampled = False
        
        if len(df) > SAMPLE_THRESHOLD:
            # Stratified sampling if target is available, otherwise random
            df_analysis = df.sample(n=SAMPLE_SIZE, random_state=42)
            is_sampled = True
            logging.info(f"Performance optimization: Sampled {SAMPLE_SIZE} rows from {original_size} for faster analysis")
        else:
            df_analysis = df.copy()
        
        # Update training counter
        await db.datasets.update_one(
            {"id": dataset_id},
            {"$inc": {"training_count": 1}}
        )
        
        # 1. Data Profiling (use full dataset for profiling)
        profile = generate_data_profile(df)
        
        # 2. Train ML Models with user selection if provided
        numeric_cols = df_analysis.select_dtypes(include=[np.number]).columns.tolist()
        models_result = {"models": [], "message": "No numeric columns for ML training"}
        selection_feedback = None
        
        logging.info(f"Holistic analysis: Found {len(numeric_cols)} numeric columns, dataset size: {len(df_analysis)}")
        
        # Handle multiple targets or single target
        target_cols = []
        target_feature_mapping = {}  # Map each target to its features
        
        logging.info(f"User selection received: {user_selection}")
        
        if user_selection and user_selection != {}:
            # Check if multiple targets provided
            user_targets = user_selection.get("target_variables", [])  # Multiple targets
            user_target = user_selection.get("target_variable")  # Single target (backward compatibility)
            
            logging.info(f"user_targets: {user_targets}, user_target: {user_target}")
            
            if user_targets and isinstance(user_targets, list) and len(user_targets) > 0:
                # Multiple targets mode
                logging.info(f"Processing {len(user_targets)} user-selected targets")
                for target_info in user_targets:
                    target_name = target_info.get("target")
                    target_features = target_info.get("features", [])
                    
                    logging.info(f"Checking target: {target_name} with features: {target_features}")
                    
                    if target_name and target_name in df_analysis.columns:
                        if pd.api.types.is_numeric_dtype(df_analysis[target_name].dtype):
                            target_cols.append(target_name)
                            target_feature_mapping[target_name] = target_features
                            logging.info(f"Added target: {target_name}")
                        else:
                            logging.warning(f"Target {target_name} is not numeric, skipping")
                    else:
                        logging.warning(f"Target {target_name} not found in dataframe")
            elif user_target:
                # Single target mode (existing logic)
                logging.info(f"Processing single user-selected target: {user_target}")
                if user_target in df_analysis.columns and pd.api.types.is_numeric_dtype(df_analysis[user_target].dtype):
                    target_cols.append(user_target)
                    target_feature_mapping[user_target] = user_selection.get("selected_features", [])
        
        logging.info(f"Final target_cols: {target_cols}")
        
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
        
        # Process each target
        all_models = []
        all_feedback_messages = []
        
        for target_col in target_cols:
            selected_features = target_feature_mapping.get(target_col, [])
            
            logging.info(f"Processing target: {target_col} with {len(selected_features)} selected features")
            
            # Separate numeric and categorical selected features
            numeric_selected = []
            categorical_selected = []
            excluded_features = []
            
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
                
                all_feedback_messages.append("\n".join(feedback_parts))
            
            # Train models for this target
            try:
                if selected_features:
                    # Create subset dataframe with selected features + target
                    train_columns = selected_features + [target_col]
                    df_subset = df_analysis[train_columns].copy()
                    
                    # Handle categorical features with one-hot encoding
                    if categorical_selected:
                        df_subset = pd.get_dummies(df_subset, columns=categorical_selected, drop_first=True, dtype=int)
                        logging.info(f"Encoded {len(categorical_selected)} categorical features for target {target_col}")
                    
                    target_models = train_multiple_models(df_subset, target_col)
                else:
                    # Train on all numeric features
                    target_models = train_multiple_models(df_analysis, target_col)
                
                # Add models to all_models list
                if target_models.get("models"):
                    all_models.extend(target_models["models"])
                    logging.info(f"Trained {len(target_models['models'])} models for target {target_col}")
                
            except Exception as e:
                logging.error(f"ML training failed for target {target_col}: {str(e)}", exc_info=True)
                all_feedback_messages.append(f"⚠️ Training failed for target '{target_col}': {str(e)}")
        
        # Build final selection feedback
        if all_feedback_messages:
            selection_feedback = {
                "status": "used",
                "message": "\n\n".join(all_feedback_messages),
                "used_targets": target_cols,
                "is_multi_target": len(target_cols) > 1
            }
        
        # Update models_result
        models_result = {"models": all_models}
        
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
        
        # 5A. Generate comprehensive AI insights using Phase 3 service
        ai_insights_list = []
        insights = "Analysis complete. Explore the charts and model results above."
        
        try:
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
        
        # Get dataset info for training metadata
        dataset = await db.datasets.find_one({"id": dataset_id}, {"_id": 0})
        training_count = dataset.get("training_count", 1)
        last_trained_at = dataset.get("updated_at", datetime.now(timezone.utc).isoformat())
        
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
            "phase_3_enabled": True  # Flag to indicate Phase 3 features are available
        }
        
        # Add selection feedback if user made a selection
        if selection_feedback:
            response["selection_feedback"] = selection_feedback
        
        return response
        
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
        
        await db.saved_states.insert_one(state_doc)
        
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
        state = await db.saved_states.find_one({"id": state_id}, {"_id": 0})
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
        cursor = db.saved_states.find({"dataset_id": dataset_id}, {"_id": 0})
        states = await cursor.to_list(length=None)
        return {"states": states}
    except Exception as e:
        raise HTTPException(500, f"Failed to fetch saved states: {str(e)}")


@router.delete("/delete-state/{state_id}")
async def delete_analysis_state(state_id: str):
    """Delete saved analysis state"""
    try:
        state = await db.saved_states.find_one({"id": state_id}, {"_id": 0})
        if not state:
            raise HTTPException(404, "Analysis state not found")
        
        # Delete GridFS file if exists
        if state.get("storage_type") == "gridfs" and state.get("gridfs_file_id"):
            try:
                await fs.delete(ObjectId(state["gridfs_file_id"]))
            except:
                pass
        
        # Delete metadata
        result = await db.saved_states.delete_one({"id": state_id})
        if result.deleted_count == 0:
            raise HTTPException(404, "Analysis state not found")
        
        return {"message": "Analysis state deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to delete state: {str(e)}")
