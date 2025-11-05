"""
Enhanced Visualization Service V2
- Faster chart generation
- More intelligent chart combinations (up to 25+ charts)
- Better validation to avoid empty charts
"""
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
from typing import Dict, Any, List, Tuple
import logging
from itertools import combinations

logger = logging.getLogger(__name__)


def validate_chart_data(chart_dict: Dict[str, Any]) -> bool:
    """Validate that chart has proper plotly data"""
    try:
        if not chart_dict or not isinstance(chart_dict, dict):
            return False
        if 'plotly_data' not in chart_dict:
            return False
        plotly_data = chart_dict['plotly_data']
        if not isinstance(plotly_data, dict):
            return False
        if 'data' not in plotly_data or not plotly_data['data']:
            return False
        for trace in plotly_data['data']:
            if isinstance(trace, dict):
                has_data = False
                for key in ['x', 'y', 'values', 'z']:
                    if key in trace and trace[key] and len(trace[key]) > 0:
                        has_data = True
                        break
                if not has_data:
                    return False
        return True
    except:
        return False


def generate_auto_charts_v2(df: pd.DataFrame, max_charts: int = 25) -> Tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
    """
    Generate up to 25+ intelligent charts with comprehensive validation
    OPTIMIZED for speed and variety
    """
    charts = []
    skipped_charts = []
    
    # Identify column types
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()
    datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
    
    logger.info(f"Analyzing: {len(numeric_cols)} numeric, {len(categorical_cols)} categorical, {len(datetime_cols)} datetime columns")
    
    # CATEGORY 1: Distribution Charts (histograms for numeric)
    for col in numeric_cols[:5]:  # Top 5 numeric columns
        try:
            col_data = df[col].dropna()
            if len(col_data) < 2:
                continue
            
            fig = go.Figure(data=[go.Histogram(x=col_data, nbinsx=min(30, len(col_data)//2))])
            fig.update_layout(title=f"Distribution of {col}", xaxis_title=col, yaxis_title="Frequency")
            
            chart = {
                "type": "histogram",
                "title": f"Distribution of {col}",
                "plotly_data": json.loads(fig.to_json()),
                "description": f"Mean: {col_data.mean():.2f}, Std: {col_data.std():.2f}"
            }
            if validate_chart_data(chart):
                charts.append(chart)
        except Exception as e:
            logger.warning(f"Skipped distribution for {col}: {e}")
    
    # CATEGORY 2: Box plots for numeric (outlier detection)
    for col in numeric_cols[:4]:  # Top 4
        try:
            col_data = df[col].dropna()
            if len(col_data) < 3:
                continue
            
            fig = go.Figure(data=[go.Box(y=col_data, name=col)])
            fig.update_layout(title=f"Box Plot: {col} (Outlier Detection)", yaxis_title=col)
            
            chart = {
                "type": "box",
                "title": f"Box Plot: {col}",
                "plotly_data": json.loads(fig.to_json()),
                "description": f"Identifies outliers and quartile distribution"
            }
            if validate_chart_data(chart):
                charts.append(chart)
        except Exception as e:
            logger.warning(f"Skipped box plot for {col}: {e}")
    
    # CATEGORY 3: Categorical distributions (bar charts)
    for col in categorical_cols[:5]:  # Top 5 categorical
        try:
            value_counts = df[col].value_counts().head(15)  # Top 15 categories
            if len(value_counts) < 1:
                continue
            
            fig = go.Figure(data=[go.Bar(x=value_counts.index, y=value_counts.values)])
            fig.update_layout(title=f"Top Categories: {col}", xaxis_title=col, yaxis_title="Count")
            
            chart = {
                "type": "bar",
                "title": f"Top Categories: {col}",
                "plotly_data": json.loads(fig.to_json()),
                "description": f"Shows distribution of {len(value_counts)} categories"
            }
            if validate_chart_data(chart):
                charts.append(chart)
        except Exception as e:
            logger.warning(f"Skipped categorical for {col}: {e}")
    
    # CATEGORY 4: Numeric vs Numeric scatter plots (correlations)
    if len(numeric_cols) >= 2:
        # Generate up to 6 scatter plots from meaningful combinations
        pairs = list(combinations(numeric_cols[:5], 2))[:6]  # Max 6 pairs
        for col1, col2 in pairs:
            try:
                valid_data = df[[col1, col2]].dropna()
                if len(valid_data) < 3:
                    continue
                
                fig = px.scatter(valid_data, x=col1, y=col2, title=f"{col1} vs {col2}")
                
                chart = {
                    "type": "scatter",
                    "title": f"{col1} vs {col2}",
                    "plotly_data": json.loads(fig.to_json()),
                    "description": f"Relationship between {col1} and {col2}"
                }
                if validate_chart_data(chart):
                    charts.append(chart)
                    
                if len(charts) >= max_charts:
                    break
            except Exception as e:
                logger.warning(f"Skipped scatter {col1} vs {col2}: {e}")
    
    # CATEGORY 5: Categorical vs Numeric (grouped bar/violin)
    if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
        # Up to 4 combinations
        for cat_col in categorical_cols[:2]:
            for num_col in numeric_cols[:2]:
                try:
                    # Only use categories with reasonable cardinality
                    n_categories = df[cat_col].nunique()
                    if n_categories < 2 or n_categories > 20:
                        continue
                    
                    valid_data = df[[cat_col, num_col]].dropna()
                    if len(valid_data) < 3:
                        continue
                    
                    fig = px.box(valid_data, x=cat_col, y=num_col, title=f"{num_col} by {cat_col}")
                    
                    chart = {
                        "type": "box_grouped",
                        "title": f"{num_col} by {cat_col}",
                        "plotly_data": json.loads(fig.to_json()),
                        "description": f"Distribution of {num_col} across {cat_col} categories"
                    }
                    if validate_chart_data(chart):
                        charts.append(chart)
                        
                    if len(charts) >= max_charts:
                        break
                except Exception as e:
                    logger.warning(f"Skipped {cat_col} vs {num_col}: {e}")
            if len(charts) >= max_charts:
                break
    
    # CATEGORY 6: Time series (if datetime columns exist)
    if len(datetime_cols) >= 1 and len(numeric_cols) >= 1:
        for dt_col in datetime_cols[:2]:
            for num_col in numeric_cols[:3]:
                try:
                    valid_data = df[[dt_col, num_col]].dropna().sort_values(dt_col)
                    if len(valid_data) < 3:
                        continue
                    
                    fig = px.line(valid_data, x=dt_col, y=num_col, title=f"{num_col} over Time")
                    
                    chart = {
                        "type": "line",
                        "title": f"{num_col} over Time",
                        "plotly_data": json.loads(fig.to_json()),
                        "description": f"Trend of {num_col} over {dt_col}"
                    }
                    if validate_chart_data(chart):
                        charts.append(chart)
                        
                    if len(charts) >= max_charts:
                        break
                except Exception as e:
                    logger.warning(f"Skipped time series {dt_col} vs {num_col}: {e}")
            if len(charts) >= max_charts:
                break
    
    # CATEGORY 7: Correlation heatmap (if 3+ numeric columns)
    if len(numeric_cols) >= 3:
        try:
            numeric_data = df[numeric_cols[:10]].dropna()  # Max 10 columns for readability
            if len(numeric_data) >= 3:
                corr = numeric_data.corr()
                
                fig = go.Figure(data=go.Heatmap(
                    z=corr.values,
                    x=corr.columns,
                    y=corr.columns,
                    colorscale='RdBu',
                    zmid=0
                ))
                fig.update_layout(title="Correlation Heatmap")
                
                chart = {
                    "type": "heatmap",
                    "title": "Correlation Heatmap",
                    "plotly_data": json.loads(fig.to_json()),
                    "description": "Shows correlations between numeric variables"
                }
                if validate_chart_data(chart):
                    charts.append(chart)
        except Exception as e:
            logger.warning(f"Skipped correlation heatmap: {e}")
    
    # CATEGORY 8: Pie charts for top categorical with few categories
    for col in categorical_cols[:3]:
        try:
            value_counts = df[col].value_counts().head(8)  # Max 8 slices
            n_unique = df[col].nunique()
            
            if n_unique < 2 or n_unique > 10 or len(value_counts) < 2:
                continue
            
            fig = go.Figure(data=[go.Pie(labels=value_counts.index, values=value_counts.values)])
            fig.update_layout(title=f"Distribution: {col}")
            
            chart = {
                "type": "pie",
                "title": f"Distribution: {col}",
                "plotly_data": json.loads(fig.to_json()),
                "description": f"Proportions of {col} categories"
            }
            if validate_chart_data(chart):
                charts.append(chart)
                
            if len(charts) >= max_charts:
                break
        except Exception as e:
            logger.warning(f"Skipped pie chart for {col}: {e}")
    
    logger.info(f"Generated {len(charts)} valid charts, skipped {len(skipped_charts)}")
    return charts[:max_charts], skipped_charts
