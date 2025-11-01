"""
Visualization Service
Handles chart generation and validation
"""
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
from typing import Dict, Any, List
import logging
from app.services.chart_insights import generate_chart_insight


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
        # Check for data traces
        if 'data' not in plotly_data or not plotly_data['data']:
            return False
        # Check that data has actual values
        for trace in plotly_data['data']:
            if isinstance(trace, dict):
                # Check for x or y data
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


def generate_auto_charts(df: pd.DataFrame, max_charts: int = 15) -> List[Dict[str, Any]]:
    """Generate up to 15 intelligent charts with comprehensive validation"""
    
    charts = []
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
    
    # 1-3: Distribution charts for top 3 numeric columns
    for col in numeric_cols[:3]:
        try:
            col_data = df[col].dropna()
            if len(col_data) < 2:
                continue
            fig = go.Figure(data=[go.Histogram(x=col_data, nbinsx=min(30, len(col_data)//2), name=col)])
            fig.update_layout(
                title=f"Distribution of {col}", 
                xaxis_title=col, 
                yaxis_title="Frequency", 
                width=700, 
                height=400
            )
            chart = {
                "type": "histogram",
                "title": f"Distribution of {col}",
                "plotly_data": json.loads(fig.to_json()),
                "description": f"Shows frequency distribution of {col}. Mean: {col_data.mean():.2f}, Std: {col_data.std():.2f}"
            }
            if validate_chart_data(chart):
                charts.append(chart)
        except Exception as e:
            logging.warning(f"Failed to generate histogram for {col}: {str(e)}")
    
    # 4-6: Box plots for numeric columns
    for col in numeric_cols[:3]:
        try:
            col_data = df[col].dropna()
            if len(col_data) < 2:
                continue
            fig = go.Figure(data=[go.Box(y=col_data, name=col)])
            fig.update_layout(title=f"Box Plot: {col}", yaxis_title=col, width=700, height=400)
            chart = {
                "type": "box",
                "title": f"Box Plot: {col}",
                "plotly_data": json.loads(fig.to_json()),
                "description": f"Identifies outliers and spread in {col}. Median: {col_data.median():.2f}"
            }
            if validate_chart_data(chart):
                charts.append(chart)
        except Exception as e:
            logging.warning(f"Failed to generate box plot for {col}: {str(e)}")
    
    # 7-9: Categorical distribution
    for col in categorical_cols[:3]:
        try:
            value_counts = df[col].value_counts().head(10)
            if len(value_counts) == 0:
                continue
            fig = go.Figure(data=[go.Bar(x=value_counts.index.astype(str), y=value_counts.values)])
            fig.update_layout(title=f"Top Categories in {col}", xaxis_title=col, yaxis_title="Count", width=700, height=400)
            chart = {
                "type": "bar",
                "title": f"Top Categories in {col}",
                "plotly_data": json.loads(fig.to_json()),
                "description": f"Top {len(value_counts)} categories in {col}. Most common: {value_counts.index[0]} ({value_counts.values[0]} occurrences)"
            }
            if validate_chart_data(chart):
                charts.append(chart)
        except Exception as e:
            logging.warning(f"Failed to generate bar chart for {col}: {str(e)}")
    
    # 10-12: Time series trends
    if datetime_cols:
        for dt_col in datetime_cols[:1]:
            for num_col in numeric_cols[:2]:
                try:
                    temp_df = df[[dt_col, num_col]].dropna().sort_values(dt_col)
                    if len(temp_df) < 2:
                        continue
                    fig = go.Figure(data=[go.Scatter(x=temp_df[dt_col], y=temp_df[num_col], mode='lines+markers', name=num_col)])
                    fig.update_layout(title=f"{num_col} Over Time", xaxis_title=dt_col, yaxis_title=num_col, width=700, height=400)
                    chart = {
                        "type": "timeseries",
                        "title": f"{num_col} Over Time",
                        "plotly_data": json.loads(fig.to_json()),
                        "description": f"Time series showing {num_col} trends. Peak: {temp_df[num_col].max():.2f}, Low: {temp_df[num_col].min():.2f}"
                    }
                    if validate_chart_data(chart):
                        charts.append(chart)
                except Exception as e:
                    logging.warning(f"Failed to generate time series for {num_col}: {str(e)}")
    
    # 13-15: Scatter plots for correlation
    if len(numeric_cols) >= 2:
        pairs_added = 0
        for i in range(len(numeric_cols)):
            for j in range(i+1, len(numeric_cols)):
                if pairs_added >= 3: break
                try:
                    temp_df = df[[numeric_cols[i], numeric_cols[j]]].dropna()
                    if len(temp_df) < 3:
                        continue
                    
                    corr = temp_df[numeric_cols[i]].corr(temp_df[numeric_cols[j]])
                    if abs(corr) > 0.3:
                        fig = px.scatter(temp_df, x=numeric_cols[i], y=numeric_cols[j], trendline="ols")
                        fig.update_layout(title=f"{numeric_cols[i]} vs {numeric_cols[j]}", width=700, height=400)
                        chart = {
                            "type": "scatter",
                            "title": f"{numeric_cols[i]} vs {numeric_cols[j]}",
                            "plotly_data": json.loads(fig.to_json()),
                            "description": f"Correlation: {corr:.2f}. {'Strong' if abs(corr) > 0.7 else 'Moderate'} {'positive' if corr > 0 else 'negative'} relationship."
                        }
                        if validate_chart_data(chart):
                            charts.append(chart)
                            pairs_added += 1
                except Exception as e:
                    logging.warning(f"Failed to generate scatter plot: {str(e)}")
    
    logging.info(f"Generated {len(charts)} valid charts out of maximum {max_charts}")
    return charts[:max_charts]


def generate_single_chart(
    df: pd.DataFrame,
    chart_type: str,
    x_col: str = None,
    y_col: str = None,
    **kwargs
) -> Dict[str, Any]:
    """Generate a single chart based on specifications"""
    
    try:
        if chart_type == "histogram" and x_col:
            fig = px.histogram(df, x=x_col, **kwargs)
        elif chart_type == "scatter" and x_col and y_col:
            fig = px.scatter(df, x=x_col, y=y_col, **kwargs)
        elif chart_type == "line" and x_col and y_col:
            fig = px.line(df, x=x_col, y=y_col, **kwargs)
        elif chart_type == "bar" and x_col:
            value_counts = df[x_col].value_counts()
            fig = go.Figure(data=[go.Bar(x=value_counts.index.astype(str), y=value_counts.values)])
        elif chart_type == "box" and y_col:
            fig = px.box(df, y=y_col, **kwargs)
        elif chart_type == "pie" and x_col:
            value_counts = df[x_col].value_counts().head(10)
            fig = go.Figure(data=[go.Pie(labels=value_counts.index.astype(str), values=value_counts.values)])
        elif chart_type == "correlation":
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if len(numeric_cols) < 2:
                return None
            corr_matrix = df[numeric_cols].corr()
            fig = go.Figure(data=go.Heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns,
                y=corr_matrix.columns,
                colorscale='RdBu',
                zmid=0
            ))
            fig.update_layout(title="Correlation Heatmap")
        else:
            return None
        
        chart = {
            "type": chart_type,
            "title": kwargs.get("title", f"{chart_type.capitalize()} Chart"),
            "plotly_data": json.loads(fig.to_json()),
            "description": kwargs.get("description", f"Generated {chart_type} chart")
        }
        
        if validate_chart_data(chart):
            return chart
        return None
        
    except Exception as e:
        logging.error(f"Failed to generate {chart_type} chart: {str(e)}")
        return None
