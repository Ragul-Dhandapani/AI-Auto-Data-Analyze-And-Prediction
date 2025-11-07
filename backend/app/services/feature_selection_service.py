"""
Feature Selection Service
AI-powered feature selection and explanation generation
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.feature_selection import mutual_info_regression, mutual_info_classif
import logging

logger = logging.getLogger(__name__)


def detect_variable_types(df: pd.DataFrame) -> Dict[str, List[str]]:
    """
    Detect and categorize variables by type
    
    Returns:
        Dict with 'numeric', 'categorical', 'datetime', 'text' keys
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
    
    # Detect text columns (high cardinality string columns)
    text_cols = [
        col for col in categorical_cols 
        if df[col].nunique() > len(df) * 0.5  # More than 50% unique values
    ]
    
    # Remove text columns from categorical
    categorical_cols = [col for col in categorical_cols if col not in text_cols]
    
    return {
        'numeric': numeric_cols,
        'categorical': categorical_cols,
        'datetime': datetime_cols,
        'text': text_cols
    }


def calculate_feature_importance_rf(
    df: pd.DataFrame, 
    target_col: str,
    task_type: str = 'auto'
) -> Dict[str, float]:
    """
    Calculate feature importance using Random Forest
    
    Args:
        df: DataFrame with features and target
        target_col: Target column name
        task_type: 'regression', 'classification', or 'auto'
    
    Returns:
        Dict of feature names to importance scores
    """
    try:
        # Prepare features
        X = df.drop(columns=[target_col])
        y = df[target_col]
        
        # Handle categorical variables
        X_encoded = pd.get_dummies(X, drop_first=True)
        
        # Auto-detect task type
        if task_type == 'auto':
            if y.dtype in ['int64', 'int32'] and y.nunique() < 20:
                task_type = 'classification'
            elif y.dtype in ['float64', 'float32']:
                task_type = 'regression'
            else:
                task_type = 'classification'
        
        # Train Random Forest
        if task_type == 'regression':
            model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
        else:
            model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
        
        model.fit(X_encoded, y)
        
        # Get feature importance
        importance_dict = dict(zip(X_encoded.columns, model.feature_importances_))
        
        # Aggregate importance for original features (before one-hot encoding)
        original_importance = {}
        for col in X.columns:
            # Sum importance of all encoded columns that came from this feature
            related_cols = [c for c in X_encoded.columns if c.startswith(col)]
            original_importance[col] = sum(importance_dict.get(c, 0) for c in related_cols)
        
        return original_importance
    
    except Exception as e:
        logger.error(f"Error calculating RF feature importance: {str(e)}")
        return {}


def calculate_mutual_information(
    df: pd.DataFrame,
    target_col: str,
    task_type: str = 'auto'
) -> Dict[str, float]:
    """
    Calculate mutual information between features and target
    
    Args:
        df: DataFrame with features and target
        target_col: Target column name
        task_type: 'regression', 'classification', or 'auto'
    
    Returns:
        Dict of feature names to MI scores
    """
    try:
        X = df.drop(columns=[target_col])
        y = df[target_col]
        
        # Handle categorical variables
        X_encoded = pd.get_dummies(X, drop_first=True)
        
        # Auto-detect task type
        if task_type == 'auto':
            if y.dtype in ['int64', 'int32'] and y.nunique() < 20:
                task_type = 'classification'
            else:
                task_type = 'regression'
        
        # Calculate mutual information
        if task_type == 'regression':
            mi_scores = mutual_info_regression(X_encoded, y, random_state=42)
        else:
            mi_scores = mutual_info_classif(X_encoded, y, random_state=42)
        
        mi_dict = dict(zip(X_encoded.columns, mi_scores))
        
        # Aggregate MI for original features
        original_mi = {}
        for col in X.columns:
            related_cols = [c for c in X_encoded.columns if c.startswith(col)]
            original_mi[col] = sum(mi_dict.get(c, 0) for c in related_cols)
        
        return original_mi
    
    except Exception as e:
        logger.error(f"Error calculating mutual information: {str(e)}")
        return {}


def calculate_correlation_scores(
    df: pd.DataFrame,
    target_col: str
) -> Dict[str, float]:
    """
    Calculate correlation between numeric features and target
    
    Args:
        df: DataFrame with features and target
        target_col: Target column name
    
    Returns:
        Dict of feature names to correlation scores (absolute values)
    """
    try:
        # Only use numeric columns
        numeric_df = df.select_dtypes(include=[np.number])
        
        if target_col not in numeric_df.columns:
            return {}
        
        correlations = numeric_df.corr()[target_col].drop(target_col)
        
        # Return absolute correlation values
        return {col: abs(corr) for col, corr in correlations.items()}
    
    except Exception as e:
        logger.error(f"Error calculating correlations: {str(e)}")
        return {}


def suggest_features_ai(
    df: pd.DataFrame,
    target_col: str,
    top_n: int = 10
) -> Dict[str, any]:
    """
    AI-powered feature suggestion combining multiple methods
    
    Args:
        df: DataFrame with features and target
        target_col: Target column name
        top_n: Number of top features to suggest
    
    Returns:
        Dict with suggested features and their scores/explanations
    """
    try:
        # Calculate feature importance using multiple methods
        rf_importance = calculate_feature_importance_rf(df, target_col)
        mi_scores = calculate_mutual_information(df, target_col)
        corr_scores = calculate_correlation_scores(df, target_col)
        
        # Combine scores (weighted average)
        all_features = set(list(rf_importance.keys()) + list(mi_scores.keys()) + list(corr_scores.keys()))
        
        combined_scores = {}
        for feature in all_features:
            rf_score = rf_importance.get(feature, 0)
            mi_score = mi_scores.get(feature, 0)
            corr_score = corr_scores.get(feature, 0)
            
            # Weighted combination (RF: 40%, MI: 40%, Corr: 20%)
            combined_scores[feature] = (
                0.4 * rf_score +
                0.4 * mi_score +
                0.2 * corr_score
            )
        
        # Sort by combined score
        sorted_features = sorted(
            combined_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_n]
        
        # Prepare results
        suggestions = []
        for feature, score in sorted_features:
            suggestions.append({
                'feature': feature,
                'combined_score': float(score),
                'rf_importance': float(rf_importance.get(feature, 0)),
                'mutual_info': float(mi_scores.get(feature, 0)),
                'correlation': float(corr_scores.get(feature, 0)),
                'explanation': generate_feature_explanation(
                    feature,
                    target_col,
                    rf_importance.get(feature, 0),
                    mi_scores.get(feature, 0),
                    corr_scores.get(feature, 0)
                )
            })
        
        return {
            'target': target_col,
            'suggested_features': suggestions,
            'total_features': len(df.columns) - 1,
            'method': 'combined'
        }
    
    except Exception as e:
        logger.error(f"Error in AI feature suggestion: {str(e)}")
        return {
            'target': target_col,
            'suggested_features': [],
            'error': str(e)
        }


def generate_feature_explanation(
    feature: str,
    target: str,
    rf_score: float,
    mi_score: float,
    corr_score: float
) -> str:
    """
    Generate human-readable explanation for why a feature was selected
    
    Args:
        feature: Feature name
        rf_score: Random Forest importance score
        mi_score: Mutual information score
        corr_score: Correlation score
    
    Returns:
        Human-readable explanation string
    """
    explanations = []
    
    # Correlation explanation
    if corr_score > 0.7:
        explanations.append(f"has a strong {int(corr_score * 100)}% correlation with {target}")
    elif corr_score > 0.4:
        explanations.append(f"has a moderate {int(corr_score * 100)}% correlation with {target}")
    
    # Random Forest explanation
    if rf_score > 0.1:
        explanations.append(f"shows high importance ({int(rf_score * 100)}%) in decision tree models")
    elif rf_score > 0.05:
        explanations.append(f"shows moderate importance in decision tree models")
    
    # Mutual Information explanation
    if mi_score > 0.1:
        explanations.append(f"shares significant information with the target variable")
    
    if not explanations:
        explanations.append(f"contributes to predicting {target}")
    
    return f"Feature '{feature}' was selected because it " + " and ".join(explanations) + "."


# ============================================
# Azure OpenAI Integration (Commented)
# ============================================
"""
# Uncomment and configure for Azure AI integration

import openai
from openai import AzureOpenAI

def generate_feature_explanation_ai(
    feature: str,
    target: str,
    rf_score: float,
    mi_score: float,
    corr_score: float,
    df_sample: pd.DataFrame
) -> str:
    '''
    Generate AI-powered explanation using Azure OpenAI
    
    Configuration:
    - Set AZURE_OPENAI_KEY in environment
    - Set AZURE_OPENAI_ENDPOINT
    - Set AZURE_OPENAI_DEPLOYMENT_NAME
    '''
    try:
        client = AzureOpenAI(
            api_key=os.environ.get('AZURE_OPENAI_KEY'),
            api_version=os.environ.get('AZURE_OPENAI_API_VERSION', '2024-12-01-preview'),
            azure_endpoint=os.environ.get('AZURE_OPENAI_ENDPOINT')
        )
        
        prompt = f'''
        Explain why the feature "{feature}" is important for predicting "{target}".
        
        Feature Statistics:
        - Random Forest Importance: {rf_score:.3f}
        - Mutual Information: {mi_score:.3f}
        - Correlation: {corr_score:.3f}
        
        Sample Data:
        {df_sample[[feature, target]].head(5).to_string()}
        
        Provide a concise, 1-2 sentence explanation that a business user can understand.
        '''
        
        response = client.chat.completions.create(
            model=os.environ.get('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-4'),
            messages=[
                {'role': 'system', 'content': 'You are a data science expert explaining feature importance.'},
                {'role': 'user', 'content': prompt}
            ],
            max_tokens=100,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        logger.error(f"Error generating AI explanation: {str(e)}")
        return generate_feature_explanation(feature, target, rf_score, mi_score, corr_score)
"""
