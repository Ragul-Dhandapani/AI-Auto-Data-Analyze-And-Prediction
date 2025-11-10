"""
AI-Powered Insights Generation Service
Uses Azure OpenAI for intelligent insights
"""
import os
import json
import logging
from typing import Dict, List, Optional
from pathlib import Path
import pandas as pd
import numpy as np
from dotenv import load_dotenv

# Standardized .env loading
ROOT_DIR = Path(__file__).parent.parent.parent
load_dotenv(ROOT_DIR / '.env')

logger = logging.getLogger(__name__)

# Use Azure OpenAI service
from app.services.azure_openai_service import get_azure_openai_service


async def generate_statistical_insights(
    df: pd.DataFrame,
    target_column: Optional[str] = None,
    correlation_matrix: Optional[Dict] = None
) -> List[Dict]:
    """
    Generate AI-powered statistical insights about the dataset using Azure OpenAI
    
    Args:
        df: Input dataframe
        target_column: Target variable for prediction
        correlation_matrix: Pre-computed correlation matrix
    
    Returns:
        List of insight dictionaries
    """
    azure_service = get_azure_openai_service()
    
    if not azure_service.is_available():
        return _generate_rule_based_insights(df, target_column, correlation_matrix)
    
    try:
        # Prepare context for Azure OpenAI
        context = _prepare_dataset_context(df, target_column, correlation_matrix)
        
        # Create prompt
        prompt = f"""
Analyze the following dataset statistics and provide 5-7 key insights:

{context}

Please provide insights in the following JSON format:
{{
  "insights": [
    {{
      "type": "statistical|anomaly|trend|correlation|business",
      "title": "Short title",
      "description": "Detailed explanation",
      "severity": "info|warning|critical",
      "recommendation": "Actionable recommendation"
    }}
  ]
}}

Focus on:
1. Statistical anomalies or unusual patterns
2. Strong correlations and what they mean
3. Data quality issues
4. Business implications
5. Actionable recommendations
"""
        
        # Use Azure OpenAI to generate insights
        response = azure_service.client.chat.completions.create(
            model=azure_service.deployment,
            messages=[
                {"role": "system", "content": "You are an expert data analyst. Provide insights in JSON format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        # Parse response
        insights = _parse_llm_response(response.choices[0].message.content)
        logger.info(f"Generated {len(insights)} AI insights using Azure OpenAI")
        return insights
    
    except Exception as e:
        logger.error(f"Error generating AI insights: {str(e)}")
        return _generate_rule_based_insights(df, target_column, correlation_matrix)


async def generate_anomaly_detection_insights(
    df: pd.DataFrame,
    numeric_columns: List[str]
) -> List[Dict]:
    """
    Use AI to detect and explain anomalies in the data
    
    Args:
        df: Input dataframe
        numeric_columns: List of numeric columns to analyze
    
    Returns:
        List of anomaly insights
    """
    try:
        anomalies = []
        
        for col in numeric_columns:
            # Calculate basic statistics
            mean = df[col].mean()
            std = df[col].std()
            
            # Find outliers using IQR method
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = df[(df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR)]
            
            if len(outliers) > 0:
                outlier_percentage = (len(outliers) / len(df)) * 100
                
                anomalies.append({
                    "type": "anomaly",
                    "title": f"Outliers detected in {col}",
                    "description": f"Found {len(outliers)} outliers ({outlier_percentage:.1f}% of data). "
                                 f"Values range from {outliers[col].min():.2f} to {outliers[col].max():.2f}, "
                                 f"while normal range is {Q1:.2f} to {Q3:.2f}.",
                    "severity": "warning" if outlier_percentage < 5 else "critical",
                    "recommendation": f"Investigate these {len(outliers)} outlier values to determine if they are "
                                    f"data entry errors, measurement errors, or legitimate extreme values."
                })
        
        return anomalies
    
    except Exception as e:
        logger.error(f"Error detecting anomalies: {str(e)}")
        return []


async def generate_trend_analysis(
    df: pd.DataFrame,
    time_column: Optional[str] = None,
    value_columns: Optional[List[str]] = None
) -> List[Dict]:
    """
    Analyze trends in time-series or sequential data
    
    Args:
        df: Input dataframe
        time_column: Column representing time/sequence
        value_columns: Columns to analyze for trends
    
    Returns:
        List of trend insights
    """
    if not time_column or not value_columns:
        return []
    
    try:
        trends = []
        
        # Sort by time
        df_sorted = df.sort_values(time_column)
        
        for col in value_columns:
            # Calculate trend direction
            first_half = df_sorted[col].iloc[:len(df_sorted)//2].mean()
            second_half = df_sorted[col].iloc[len(df_sorted)//2:].mean()
            
            change_pct = ((second_half - first_half) / first_half) * 100 if first_half != 0 else 0
            
            if abs(change_pct) > 10:  # Significant change
                direction = "increasing" if change_pct > 0 else "decreasing"
                trends.append({
                    "type": "trend",
                    "title": f"{col} is {direction}",
                    "description": f"{col} shows a {abs(change_pct):.1f}% {direction} trend over time. "
                                 f"First half average: {first_half:.2f}, Second half average: {second_half:.2f}.",
                    "severity": "info",
                    "recommendation": f"Monitor {col} closely. Consider forecasting future values and "
                                    f"understanding the drivers of this {direction} trend."
                })
        
        return trends
    
    except Exception as e:
        logger.error(f"Error analyzing trends: {str(e)}")
        return []


async def generate_business_recommendations(
    insights: List[Dict],
    target_column: str,
    model_performance: Dict
) -> List[Dict]:
    """
    Generate business-focused recommendations based on analysis
    
    Args:
        insights: Previously generated insights
        target_column: Target variable name
        model_performance: Model accuracy/performance metrics
    
    Returns:
        List of business recommendations
    """
    azure_service = get_azure_openai_service()
    
    if not azure_service.is_available():
        return _generate_rule_based_recommendations(insights, target_column, model_performance)
    
    try:
        # Prepare context
        insights_text = "\n".join([f"- {ins['title']}: {ins['description']}" for ins in insights[:5]])
        
        prompt = f"""
Based on the following data insights and model performance, provide 3-5 strategic business recommendations:

Target Variable: {target_column}
Model Performance: {json.dumps(model_performance, indent=2)}

Key Insights:
{insights_text}

Provide recommendations in JSON format:
{{
  "recommendations": [
    {{
      "priority": "high|medium|low",
      "title": "Brief recommendation title",
      "description": "Detailed recommendation",
      "expected_impact": "Expected business impact",
      "implementation_effort": "low|medium|high"
    }}
  ]
}}
"""
        
        # Use Azure OpenAI
        response = azure_service.client.chat.completions.create(
            model=azure_service.deployment,
            messages=[
                {"role": "system", "content": "You are a business strategist who translates data insights into actionable business recommendations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        recommendations = _parse_llm_response(response.choices[0].message.content)
        logger.info(f"Generated {len(recommendations)} business recommendations using Azure OpenAI")
        return recommendations
    
    except Exception as e:
        logger.error(f"Error generating business recommendations: {str(e)}")
        return _generate_rule_based_recommendations(insights, target_column, model_performance)


def _prepare_dataset_context(
    df: pd.DataFrame,
    target_column: Optional[str],
    correlation_matrix: Optional[Dict]
) -> str:
    """Prepare dataset summary for LLM"""
    context = f"""
Dataset Overview:
- Rows: {len(df)}
- Columns: {len(df.columns)}
- Numeric columns: {len(df.select_dtypes(include=[np.number]).columns)}
- Categorical columns: {len(df.select_dtypes(include=['object']).columns)}

"""
    
    if target_column:
        context += f"Target Variable: {target_column}\n"
        context += f"Target Statistics: mean={df[target_column].mean():.2f}, std={df[target_column].std():.2f}\n\n"
    
    # Add top correlations
    if correlation_matrix and target_column:
        context += "Top Correlations with Target:\n"
        target_corrs = correlation_matrix.get(target_column, {})
        sorted_corrs = sorted(target_corrs.items(), key=lambda x: abs(x[1]), reverse=True)[:5]
        for var, corr in sorted_corrs:
            if var != target_column:
                context += f"- {var}: {corr:.3f}\n"
    
    # Add missing data info
    missing_cols = df.isnull().sum()
    if missing_cols.sum() > 0:
        context += "\nMissing Data:\n"
        for col, count in missing_cols[missing_cols > 0].items():
            pct = (count / len(df)) * 100
            context += f"- {col}: {count} ({pct:.1f}%)\n"
    
    return context


def _parse_llm_response(response: str) -> List[Dict]:
    """Parse LLM JSON response"""
    try:
        # Try to extract JSON from response
        if "```json" in response:
            json_start = response.find("```json") + 7
            json_end = response.find("```", json_start)
            json_str = response[json_start:json_end].strip()
        elif "{" in response:
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            json_str = response[json_start:json_end]
        else:
            return []
        
        data = json.loads(json_str)
        return data.get("insights", data.get("recommendations", []))
    
    except Exception as e:
        logger.error(f"Error parsing LLM response: {str(e)}")
        return []


def _generate_rule_based_insights(
    df: pd.DataFrame,
    target_column: Optional[str],
    correlation_matrix: Optional[Dict]
) -> List[Dict]:
    """Fallback rule-based insights when LLM is not available"""
    insights = []
    
    # Data quality insight
    missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
    if missing_pct > 0:
        insights.append({
            "type": "statistical",
            "title": "Missing Data Detected",
            "description": f"Dataset contains {missing_pct:.1f}% missing values across all columns.",
            "severity": "warning" if missing_pct < 10 else "critical",
            "recommendation": "Consider imputation strategies or removing columns with excessive missing data."
        })
    
    # Correlation insight
    if correlation_matrix and target_column:
        target_corrs = correlation_matrix.get(target_column, {})
        strong_corrs = [(k, v) for k, v in target_corrs.items() if abs(v) > 0.7 and k != target_column]
        
        if strong_corrs:
            insights.append({
                "type": "correlation",
                "title": f"Strong Correlations with {target_column}",
                "description": f"Found {len(strong_corrs)} variables with strong correlation (>0.7) to target.",
                "severity": "info",
                "recommendation": "These strongly correlated variables are key predictors. Ensure they're included in your model."
            })
    
    return insights


def _generate_rule_based_recommendations(
    insights: List[Dict],
    target_column: str,
    model_performance: Dict
) -> List[Dict]:
    """Fallback rule-based recommendations"""
    recommendations = []
    
    # Performance-based recommendation
    best_model = model_performance.get("best_model", {})
    if best_model:
        r2 = best_model.get("r2_score", 0)
        if r2 > 0.8:
            recommendations.append({
                "priority": "high",
                "title": "Deploy High-Performing Model",
                "description": f"Model achieves {r2:.2%} accuracy. Consider deploying to production.",
                "expected_impact": "Accurate predictions for {target_column}",
                "implementation_effort": "medium"
            })
    
    return recommendations


# ============================================
# Azure OpenAI Integration (Commented)
# ============================================
"""
# Uncomment for Azure OpenAI integration

from openai import AzureOpenAI

async def generate_insights_azure(
    df: pd.DataFrame,
    target_column: Optional[str] = None
) -> List[Dict]:
    '''
    Generate insights using Azure OpenAI
    
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
        
        context = _prepare_dataset_context(df, target_column, None)
        
        response = client.chat.completions.create(
            model=os.environ.get('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-4'),
            messages=[
                {'role': 'system', 'content': 'You are an expert data analyst.'},
                {'role': 'user', 'content': f'Analyze this dataset and provide insights:\\n\\n{context}'}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        insights_text = response.choices[0].message.content
        return _parse_llm_response(insights_text)
    
    except Exception as e:
        logger.error(f"Error with Azure OpenAI: {str(e)}")
        return _generate_rule_based_insights(df, target_column, None)
"""
