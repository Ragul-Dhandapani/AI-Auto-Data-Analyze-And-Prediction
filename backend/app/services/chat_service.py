"""
Chat Service
Handles AI-powered chat interactions and dynamic analysis
"""
import pandas as pd
from typing import Dict, Any, List
from emergentintegrations.llm.chat import LlmChat
import os
import logging


def process_chat_message(
    df: pd.DataFrame,
    message: str,
    conversation_history: List[Dict[str, str]],
    llm_key: str = None
) -> Dict[str, Any]:
    """Process chat message and determine action"""
    
    message_lower = message.lower()
    
    # IMPORTANT: Check for removal first to avoid false positives
    if any(keyword in message_lower for keyword in ['remove', 'delete']):
        return handle_remove_request(message)
    # Detect chart requests
    elif any(keyword in message_lower for keyword in ['pie chart', 'pie']):
        return handle_pie_chart_request(df, message)
    elif any(keyword in message_lower for keyword in ['bar chart', 'bar', 'distribution']):
        return handle_bar_chart_request(df, message)
    elif any(keyword in message_lower for keyword in ['line chart', 'line', 'trend']):
        return handle_line_chart_request(df, message)
    elif any(keyword in message_lower for keyword in ['scatter', 'relationship', 'vs']):
        return handle_scatter_chart_request(df, message)
    elif any(keyword in message_lower for keyword in ['correlation', 'correlations']):
        return handle_correlation_request(df)
    else:
        # General conversation - use LLM
        return handle_general_query(df, message, conversation_history, llm_key)


def handle_pie_chart_request(df: pd.DataFrame, message: str) -> Dict[str, Any]:
    """Handle pie chart generation request"""
    import plotly.graph_objects as go
    import json
    
    # Find categorical column
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    if not categorical_cols:
        return {
            "action": "message",
            "message": "No categorical columns found for pie chart. Please specify a column or upload data with categories."
        }
    
    # Use first categorical column
    col = categorical_cols[0]
    value_counts = df[col].value_counts().head(10)
    
    fig = go.Figure(data=[go.Pie(
        labels=value_counts.index.astype(str),
        values=value_counts.values,
        hole=0.3
    )])
    fig.update_layout(title=f"Distribution of {col}")
    
    return {
        "action": "add_chart",
        "message": f"Here's a pie chart showing the distribution of {col}",
        "chart_data": {
            "type": "pie",
            "title": f"Distribution of {col}",
            "plotly_data": json.loads(fig.to_json()),
            "description": f"Pie chart showing top 10 categories in {col}"
        }
    }


def handle_bar_chart_request(df: pd.DataFrame, message: str) -> Dict[str, Any]:
    """Handle bar chart generation request"""
    import plotly.graph_objects as go
    import json
    
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    if not categorical_cols:
        return {
            "action": "message",
            "message": "No categorical columns found for bar chart."
        }
    
    col = categorical_cols[0]
    value_counts = df[col].value_counts().head(15)
    
    fig = go.Figure(data=[go.Bar(
        x=value_counts.index.astype(str),
        y=value_counts.values
    )])
    fig.update_layout(
        title=f"Bar Chart of {col}",
        xaxis_title=col,
        yaxis_title="Count"
    )
    
    return {
        "action": "add_chart",
        "message": f"Here's a bar chart showing {col} distribution",
        "chart_data": {
            "type": "bar",
            "title": f"Bar Chart of {col}",
            "plotly_data": json.loads(fig.to_json()),
            "description": f"Bar chart showing frequency of {col}"
        }
    }


def handle_line_chart_request(df: pd.DataFrame, message: str) -> Dict[str, Any]:
    """Handle line chart generation request"""
    import plotly.graph_objects as go
    import json
    
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    if len(numeric_cols) < 1:
        return {
            "action": "message",
            "message": "No numeric columns found for line chart."
        }
    
    col = numeric_cols[0]
    
    fig = go.Figure(data=[go.Scatter(
        y=df[col].head(100),
        mode='lines+markers',
        name=col
    )])
    fig.update_layout(
        title=f"Line Chart of {col}",
        xaxis_title="Index",
        yaxis_title=col
    )
    
    return {
        "action": "add_chart",
        "message": f"Here's a line chart showing {col} trend",
        "chart_data": {
            "type": "line",
            "title": f"Line Chart of {col}",
            "plotly_data": json.loads(fig.to_json()),
            "description": f"Line chart showing {col} over sequence"
        }
    }


def handle_scatter_chart_request(df: pd.DataFrame, message: str) -> Dict[str, Any]:
    """Handle scatter plot generation request"""
    import plotly.express as px
    import json
    
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    if len(numeric_cols) < 2:
        return {
            "action": "message",
            "message": "Need at least 2 numeric columns for scatter plot."
        }
    
    x_col, y_col = numeric_cols[0], numeric_cols[1]
    
    fig = px.scatter(df, x=x_col, y=y_col, trendline="ols")
    fig.update_layout(title=f"{x_col} vs {y_col}")
    
    return {
        "action": "add_chart",
        "message": f"Here's a scatter plot showing relationship between {x_col} and {y_col}",
        "chart_data": {
            "type": "scatter",
            "title": f"{x_col} vs {y_col}",
            "plotly_data": json.loads(fig.to_json()),
            "description": f"Scatter plot showing {x_col} vs {y_col} with trend line"
        }
    }


def handle_correlation_request(df: pd.DataFrame) -> Dict[str, Any]:
    """Handle correlation analysis request"""
    import plotly.graph_objects as go
    import json
    import numpy as np
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if len(numeric_cols) < 2:
        return {
            "action": "message",
            "message": "Need at least 2 numeric columns for correlation analysis."
        }
    
    corr_matrix = df[numeric_cols].corr()
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmid=0,
        text=corr_matrix.values.round(2),
        texttemplate='%{text}',
        textfont={"size": 10}
    ))
    fig.update_layout(title="Correlation Heatmap", width=700, height=600)
    
    # Find strong correlations
    strong_corrs = []
    for i in range(len(numeric_cols)):
        for j in range(i+1, len(numeric_cols)):
            corr_val = corr_matrix.iloc[i, j]
            if abs(corr_val) > 0.5:
                strong_corrs.append(f"{numeric_cols[i]} & {numeric_cols[j]}: {corr_val:.2f}")
    
    description = "Correlation heatmap showing relationships between numeric features."
    if strong_corrs:
        description += f" Strong correlations: {', '.join(strong_corrs[:3])}"
    
    return {
        "action": "add_chart",
        "message": "Here's the correlation analysis for your data",
        "chart_data": {
            "type": "correlation",
            "title": "Correlation Heatmap",
            "plotly_data": json.loads(fig.to_json()),
            "description": description,
            "correlations": corr_matrix.to_dict()
        }
    }


def handle_remove_request(message: str) -> Dict[str, Any]:
    """Handle chart removal request"""
    message_lower = message.lower()
    
    # Extract what to remove
    if 'correlation' in message_lower:
        chart_type = 'correlation'
    elif 'pie' in message_lower:
        chart_type = 'pie'
    elif 'bar' in message_lower:
        chart_type = 'bar'
    elif 'line' in message_lower:
        chart_type = 'line'
    elif 'scatter' in message_lower:
        chart_type = 'scatter'
    else:
        return {
            "action": "message",
            "message": "Please specify which chart to remove (e.g., 'remove pie chart', 'remove correlation')"
        }
    
    return {
        "action": "remove_section",
        "message": f"Removing {chart_type} chart",
        "section_type": chart_type
    }


def handle_general_query(
    df: pd.DataFrame,
    message: str,
    conversation_history: List[Dict[str, str]],
    llm_key: str = None
) -> Dict[str, Any]:
    """Handle general conversational queries using LLM"""
    
    if not llm_key:
        return {
            "action": "message",
            "message": "LLM key not configured. I can help you create charts (pie, bar, line, scatter, correlation). Just ask!"
        }
    
    try:
        # Prepare data summary for LLM
        summary = {
            "rows": len(df),
            "columns": list(df.columns),
            "numeric_columns": df.select_dtypes(include=['number']).columns.tolist(),
            "categorical_columns": df.select_dtypes(include=['object', 'category']).columns.tolist()
        }
        
        llm = LlmChat(api_key=llm_key, model="gpt-4o-mini")
        
        prompt = f"""You are analyzing a dataset with the following characteristics:
- Rows: {summary['rows']}
- Columns: {', '.join(summary['columns'])}
- Numeric columns: {', '.join(summary['numeric_columns'])}
- Categorical columns: {', '.join(summary['categorical_columns'])}

User question: {message}

Provide a helpful, concise answer based on the dataset structure."""
        
        response = llm.send_user_message(prompt)
        
        return {
            "action": "message",
            "message": response
        }
        
    except Exception as e:
        logging.error(f"LLM query failed: {str(e)}")
        return {
            "action": "message",
            "message": "I can help you create visualizations. Try asking for pie charts, bar charts, correlations, or scatter plots!"
        }
