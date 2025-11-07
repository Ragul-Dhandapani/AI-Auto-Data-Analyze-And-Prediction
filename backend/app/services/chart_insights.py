"""
Chart Insights Service
Generates AI-powered insights for charts
"""
import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


async def generate_chart_insight(chart_type: str, chart_title: str, data_summary: Dict[str, Any]) -> str:
    """
    Generate AI-powered insight for a chart using Azure OpenAI
    
    Args:
        chart_type: Type of chart (histogram, scatter, bar, etc.)
        chart_title: Title of the chart
        data_summary: Summary statistics about the data in the chart
        
    Returns:
        Insightful description of the chart
    """
    from app.services.azure_openai_service import get_azure_openai_service
    
    azure_service = get_azure_openai_service()
    
    if not azure_service.is_available():
        # Fallback to basic description if Azure OpenAI not configured
        return generate_basic_insight(chart_type, chart_title, data_summary)
    
    try:
        prompt = f"""Analyze this {chart_type} chart and provide a concise insight (1-2 sentences):

Chart: {chart_title}
Data Summary: {data_summary}

Focus on:
- Key patterns or trends
- Outliers or anomalies
- Business implications
- Actionable recommendations"""
        
        response = azure_service.client.chat.completions.create(
            model=azure_service.deployment,
            messages=[
                {"role": "system", "content": "You are a data visualization expert. Provide concise, actionable insights about charts in 1-2 sentences. Focus on patterns, trends, and business implications."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=150
        )
        insight = response if isinstance(response, str) else str(response)
        
        # Ensure insight is concise (limit to 200 chars)
        if len(insight) > 200:
            insight = insight[:197] + "..."
        
        return insight
        
    except Exception as e:
        logger.warning(f"Failed to generate AI insight: {str(e)}")
        return generate_basic_insight(chart_type, chart_title, data_summary)


def generate_basic_insight(chart_type: str, chart_title: str, data_summary: Dict[str, Any]) -> str:
    """Generate basic insight without AI"""
    
    if chart_type == "histogram":
        if 'mean' in data_summary and 'std' in data_summary:
            return f"Distribution shows mean of {data_summary['mean']:.2f} with standard deviation {data_summary['std']:.2f}. {'Right-skewed' if data_summary.get('skew', 0) > 0 else 'Left-skewed' if data_summary.get('skew', 0) < 0 else 'Symmetric'} pattern."
        return f"Distribution analysis of {chart_title}."
    
    elif chart_type == "scatter":
        if 'correlation' in data_summary:
            corr = data_summary['correlation']
            strength = "Strong" if abs(corr) > 0.7 else "Moderate" if abs(corr) > 0.4 else "Weak"
            direction = "positive" if corr > 0 else "negative"
            return f"{strength} {direction} relationship (r={corr:.2f}). {'As one increases, the other tends to ' + ('increase' if corr > 0 else 'decrease') + '.'}"
        return f"Relationship analysis between variables."
    
    elif chart_type == "bar":
        if 'top_category' in data_summary and 'top_count' in data_summary:
            total = data_summary.get('total', data_summary['top_count'])
            pct = (data_summary['top_count'] / total * 100) if total > 0 else 0
            return f"'{data_summary['top_category']}' dominates with {data_summary['top_count']} occurrences ({pct:.1f}% of total). Clear leader in the category."
        return f"Category distribution in {chart_title}."
    
    elif chart_type == "box":
        if 'median' in data_summary and 'iqr' in data_summary:
            return f"Median value at {data_summary['median']:.2f}. IQR: {data_summary['iqr']:.2f}. {'Contains outliers' if data_summary.get('outliers', 0) > 0 else 'No significant outliers'}."
        return f"Statistical distribution of {chart_title}."
    
    elif chart_type == "timeseries":
        if 'trend' in data_summary:
            return f"{data_summary['trend']} trend observed. Range: {data_summary.get('min', 0):.2f} to {data_summary.get('max', 0):.2f}."
        return f"Time-based trend analysis."
    
    else:
        return f"Visual analysis of {chart_title}."
