"""
Model Explainability Service
SHAP and LIME implementations for model interpretability
"""
import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Optional, Tuple
import json

logger = logging.getLogger(__name__)

# Try to import SHAP and LIME
try:
    import shap
    HAS_SHAP = True
except ImportError:
    HAS_SHAP = False
    logger.warning("SHAP not installed. Install with: pip install shap")

try:
    import lime
    import lime.lime_tabular
    HAS_LIME = True
except ImportError:
    HAS_LIME = False
    logger.warning("LIME not installed. Install with: pip install lime")


def generate_shap_explanation(
    model,
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    model_type: str = "tree"
) -> Dict:
    """
    Generate SHAP explanations for model predictions
    
    Args:
        model: Trained model
        X_train: Training data
        X_test: Test data for explanation
        model_type: Type of model ("tree", "linear", "deep", "kernel")
    
    Returns:
        Dict with SHAP values and visualizations
    """
    if not HAS_SHAP:
        return {"error": "SHAP not installed"}
    
    try:
        # Select appropriate explainer
        if model_type == "tree":
            explainer = shap.TreeExplainer(model)
        elif model_type == "linear":
            explainer = shap.LinearExplainer(model, X_train)
        else:
            # Use KernelExplainer as fallback (slower but works for any model)
            explainer = shap.KernelExplainer(
                model.predict,
                shap.sample(X_train, 100)  # Sample for efficiency
            )
        
        # Calculate SHAP values
        shap_values = explainer.shap_values(X_test)
        
        # Handle multi-output models
        if isinstance(shap_values, list):
            shap_values = shap_values[0]  # Use first output for simplicity
        
        # Get feature importance
        feature_importance = np.abs(shap_values).mean(axis=0)
        feature_names = X_test.columns.tolist()
        
        # Sort by importance
        importance_dict = dict(zip(feature_names, feature_importance))
        sorted_importance = sorted(
            importance_dict.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Generate summary data
        summary_data = {
            "feature_importance": {
                feat: float(imp) for feat, imp in sorted_importance
            },
            "shap_values": shap_values.tolist() if hasattr(shap_values, 'tolist') else shap_values,
            "base_value": float(explainer.expected_value) if hasattr(explainer, 'expected_value') else 0.0,
            "feature_names": feature_names
        }
        
        logger.info("Generated SHAP explanations successfully")
        return summary_data
    
    except Exception as e:
        logger.error(f"Error generating SHAP explanations: {str(e)}")
        return {"error": str(e)}


def generate_lime_explanation(
    model,
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    instance_index: int = 0,
    num_features: int = 10
) -> Dict:
    """
    Generate LIME explanation for a specific prediction
    
    Args:
        model: Trained model
        X_train: Training data
        X_test: Test data
        instance_index: Which test instance to explain
        num_features: Number of top features to show
    
    Returns:
        Dict with LIME explanation
    """
    if not HAS_LIME:
        return {"error": "LIME not installed"}
    
    try:
        # Create LIME explainer
        explainer = lime.lime_tabular.LimeTabularExplainer(
            X_train.values,
            feature_names=X_train.columns.tolist(),
            mode='regression',
            verbose=False
        )
        
        # Explain specific instance
        instance = X_test.iloc[instance_index].values
        explanation = explainer.explain_instance(
            instance,
            model.predict,
            num_features=num_features
        )
        
        # Extract explanation data
        explanation_list = explanation.as_list()
        
        explanation_data = {
            "instance_index": instance_index,
            "predicted_value": float(model.predict([instance])[0]),
            "explanations": [
                {
                    "feature": feat,
                    "contribution": float(contrib)
                }
                for feat, contrib in explanation_list
            ],
            "intercept": float(explanation.intercept[0]) if hasattr(explanation, 'intercept') else 0.0
        }
        
        logger.info(f"Generated LIME explanation for instance {instance_index}")
        return explanation_data
    
    except Exception as e:
        logger.error(f"Error generating LIME explanation: {str(e)}")
        return {"error": str(e)}


def generate_feature_interaction_analysis(
    model,
    X_data: pd.DataFrame,
    feature1: str,
    feature2: str,
    num_points: int = 20
) -> Dict:
    """
    Analyze interaction between two features
    
    Args:
        model: Trained model
        X_data: Input data
        feature1: First feature name
        feature2: Second feature name
        num_points: Number of points to sample for interaction
    
    Returns:
        Interaction analysis data
    """
    try:
        # Get feature value ranges
        f1_min, f1_max = X_data[feature1].min(), X_data[feature1].max()
        f2_min, f2_max = X_data[feature2].min(), X_data[feature2].max()
        
        # Create grid
        f1_values = np.linspace(f1_min, f1_max, num_points)
        f2_values = np.linspace(f2_min, f2_max, num_points)
        
        # Create interaction data
        interaction_data = []
        
        # Use mean values for other features
        base_instance = X_data.mean().to_dict()
        
        for f1_val in f1_values:
            for f2_val in f2_values:
                instance = base_instance.copy()
                instance[feature1] = f1_val
                instance[feature2] = f2_val
                
                # Predict
                X_instance = pd.DataFrame([instance])
                prediction = model.predict(X_instance)[0]
                
                interaction_data.append({
                    feature1: float(f1_val),
                    feature2: float(f2_val),
                    "prediction": float(prediction)
                })
        
        return {
            "feature1": feature1,
            "feature2": feature2,
            "interaction_data": interaction_data
        }
    
    except Exception as e:
        logger.error(f"Error analyzing feature interaction: {str(e)}")
        return {"error": str(e)}


def generate_partial_dependence_data(
    model,
    X_data: pd.DataFrame,
    feature: str,
    num_points: int = 50
) -> Dict:
    """
    Generate partial dependence plot data
    
    Args:
        model: Trained model
        X_data: Input data
        feature: Feature to analyze
        num_points: Number of points to generate
    
    Returns:
        Partial dependence data
    """
    try:
        # Get feature range
        f_min, f_max = X_data[feature].min(), X_data[feature].max()
        feature_values = np.linspace(f_min, f_max, num_points)
        
        # Calculate partial dependence
        predictions = []
        
        for f_val in feature_values:
            # Create copies of data with feature set to specific value
            X_temp = X_data.copy()
            X_temp[feature] = f_val
            
            # Average predictions
            avg_pred = model.predict(X_temp).mean()
            predictions.append(float(avg_pred))
        
        return {
            "feature": feature,
            "feature_values": feature_values.tolist(),
            "predictions": predictions
        }
    
    except Exception as e:
        logger.error(f"Error generating partial dependence: {str(e)}")
        return {"error": str(e)}


def explain_prediction_in_words(
    explanation_data: Dict,
    target_name: str = "target"
) -> str:
    """
    Convert SHAP/LIME explanation to human-readable text
    
    Args:
        explanation_data: SHAP or LIME explanation dict
        target_name: Name of target variable
    
    Returns:
        Human-readable explanation
    """
    try:
        if "explanations" in explanation_data:
            # LIME format
            exp_list = explanation_data["explanations"]
            predicted = explanation_data.get("predicted_value", "N/A")
            
            explanation_text = f"Predicted {target_name}: {predicted:.2f}\n\n"
            explanation_text += "Top factors influencing this prediction:\n"
            
            for i, exp in enumerate(exp_list[:5], 1):
                contrib = exp["contribution"]
                direction = "increases" if contrib > 0 else "decreases"
                explanation_text += f"{i}. {exp['feature']} {direction} the prediction by {abs(contrib):.3f}\n"
        
        elif "feature_importance" in explanation_data:
            # SHAP format
            feat_imp = explanation_data["feature_importance"]
            
            explanation_text = f"Model explanation for {target_name}:\n\n"
            explanation_text += "Most important features:\n"
            
            for i, (feat, imp) in enumerate(list(feat_imp.items())[:5], 1):
                explanation_text += f"{i}. {feat}: importance score {imp:.3f}\n"
        
        else:
            explanation_text = "Unable to generate explanation from provided data."
        
        return explanation_text
    
    except Exception as e:
        logger.error(f"Error explaining prediction in words: {str(e)}")
        return f"Error generating explanation: {str(e)}"



async def explain_shap_results_with_ai(
    shap_values: Dict,
    feature_names: List[str],
    problem_type: str
) -> str:
    """
    Convert technical SHAP results into business-friendly explanations using Azure OpenAI
    
    Args:
        shap_values: SHAP values dictionary
        feature_names: List of feature names
        problem_type: "regression" or "classification"
    
    Returns:
        Human-readable explanation
    """
    try:
        from app.services.azure_openai_service import get_azure_openai_service
        
        azure_service = get_azure_openai_service()
        
        if not azure_service.is_available():
            return "SHAP values calculated successfully. Azure OpenAI unavailable for detailed explanation."
        
        # Get top features by absolute SHAP value
        if 'feature_importance' in shap_values:
            top_features = sorted(
                shap_values['feature_importance'].items(),
                key=lambda x: abs(x[1]),
                reverse=True
            )[:5]
        else:
            top_features = [(f, 0.0) for f in feature_names[:5]]
        
        context = f"""
Model Explainability Analysis (SHAP):
- Problem Type: {problem_type}
- Top 5 Most Important Features:
{chr(10).join([f"  {i+1}. {feat}: {val:.4f}" for i, (feat, val) in enumerate(top_features)])}

Task: Explain these SHAP results in simple business terms.
- What do these values mean?
- Which features drive predictions the most?
- Provide actionable insights (2-3 sentences per top feature)
Keep it non-technical and business-focused.
"""
        
        explanation = await azure_service.generate_completion(
            prompt=context,
            max_tokens=800,
            temperature=0.5
        )
        
        return explanation
    
    except Exception as e:
        logger.error(f"AI explanation failed: {str(e)}")
        return f"SHAP analysis completed. Top features: {', '.join([f[0] for f in top_features])}"


async def explain_lime_results_with_ai(
    lime_explanation: Dict,
    instance_data: Dict,
    problem_type: str
) -> str:
    """
    Convert LIME results into business-friendly explanations using Azure OpenAI
    
    Args:
        lime_explanation: LIME explanation dictionary
        instance_data: Data for the instance being explained
        problem_type: "regression" or "classification"
    
    Returns:
        Human-readable explanation
    """
    try:
        from app.services.azure_openai_service import get_azure_openai_service
        
        azure_service = get_azure_openai_service()
        
        if not azure_service.is_available():
            return "LIME explanation generated. Azure OpenAI unavailable for detailed interpretation."
        
        # Extract feature contributions
        top_contributions = lime_explanation.get('local_explanation', [])[:5]
        
        context = f"""
Local Model Explanation (LIME) for Single Prediction:
- Problem Type: {problem_type}
- Instance Features: {instance_data}
- Top 5 Feature Contributions to this specific prediction:
{chr(10).join([f"  {i+1}. {contrib}" for i, contrib in enumerate(top_contributions)])}

Task: Explain why the model made THIS specific prediction.
- What features influenced this particular prediction?
- How do they compare to typical predictions?
- Provide clear, actionable insights for this one case.
Use simple business language, not technical jargon.
"""
        
        explanation = await azure_service.generate_completion(
            prompt=context,
            max_tokens=700,
            temperature=0.5
        )
        
        return explanation
    
    except Exception as e:
        logger.error(f"AI LIME explanation failed: {str(e)}")
        return "LIME local explanation generated successfully."


async def generate_overall_explainability_summary(
    model_name: str,
    shap_summary: str,
    feature_importance: Dict[str, float],
    problem_type: str,
    performance_metric: float
) -> str:
    """
    Generate comprehensive model explainability summary using Azure OpenAI
    
    Args:
        model_name: Name of the model
        shap_summary: SHAP analysis summary
        feature_importance: Feature importance scores
        problem_type: "regression" or "classification"
        performance_metric: Model performance score
    
    Returns:
        Executive summary of model explainability
    """
    try:
        from app.services.azure_openai_service import get_azure_openai_service
        
        azure_service = get_azure_openai_service()
        
        if not azure_service.is_available():
            return f"{model_name} model trained successfully with {len(feature_importance)} features."
        
        metric_name = "Accuracy" if problem_type == "classification" else "R² Score"
        
        top_5_features = sorted(feature_importance.items(), key=lambda x: abs(x[1]), reverse=True)[:5]
        
        context = f"""
Model Explainability Executive Summary:
- Model: {model_name}
- Problem Type: {problem_type}
- Performance: {metric_name} = {performance_metric:.4f}
- Total Features: {len(feature_importance)}
- Top 5 Most Important Features:
{chr(10).join([f"  {i+1}. {feat}: {score:.4f}" for i, (feat, score) in enumerate(top_5_features)])}

SHAP Analysis Summary:
{shap_summary}

Task: Create an executive summary that:
1. Explains how the model makes predictions (in simple terms)
2. Highlights the most important drivers (top features)
3. Provides business recommendations based on insights
4. Mentions model reliability and when to trust predictions

Keep it concise (4-5 sentences) and business-focused.
"""
        
        summary = await azure_service.generate_completion(
            prompt=context,
            max_tokens=600,
            temperature=0.4
        )
        
        return summary
    
    except Exception as e:
        logger.error(f"Executive summary generation failed: {str(e)}")
        return f"{model_name} trained with {performance_metric:.4f} {metric_name}. Top features: {', '.join([f[0] for f in top_5_features])}"

