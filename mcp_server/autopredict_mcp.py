#!/usr/bin/env python3
"""
PROMISE AI MCP Server - Complete Data Analysis & Visualization
Exposes all core functionality for external AI agents
"""

import asyncio
import json
from typing import Any, List, Dict, Optional
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

import pandas as pd
import numpy as np
from io import BytesIO
import base64
from datetime import datetime, timezone
import uuid

# ML Libraries
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import xgboost as xgb

# Visualization
import plotly.express as px
import plotly.graph_objects as go

# LLM Integration
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage

load_dotenv()
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

# In-memory storage
datasets = {}
analysis_results = {}
visualizations = {}

server = Server("promise-ai-complete")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List all available tools for PROMISE AI"""
    return [
        types.Tool(
            name="upload_dataset",
            description="Upload and profile a dataset from CSV data (base64 encoded)",
            inputSchema={
                "type": "object",
                "properties": {
                    "csv_base64": {"type": "string", "description": "Base64 encoded CSV data"},
                    "dataset_name": {"type": "string", "description": "Name for the dataset"}
                },
                "required": ["csv_base64", "dataset_name"]
            }
        ),
        types.Tool(
            name="get_data_profile",
            description="Get comprehensive data profiling report for a dataset",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_id": {"type": "string", "description": "Dataset ID"}
                },
                "required": ["dataset_id"]
            }
        ),
        types.Tool(
            name="train_ml_models",
            description="Train multiple ML models on dataset",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_id": {"type": "string", "description": "Dataset ID"},
                    "target_column": {"type": "string", "description": "Target column"}
                },
                "required": ["dataset_id", "target_column"]
            }
        ),
        types.Tool(
            name="generate_visualizations",
            description="Generate comprehensive visualizations",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_id": {"type": "string", "description": "Dataset ID"},
                    "chart_types": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["dataset_id"]
            }
        ),
        types.Tool(
            name="analyze_correlations",
            description="Analyze correlations between numeric columns",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_id": {"type": "string", "description": "Dataset ID"}
                },
                "required": ["dataset_id"]
            }
        ),
        types.Tool(
            name="list_datasets",
            description="List all uploaded datasets",
            inputSchema={"type": "object", "properties": {}}
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
    """Handle tool execution"""
    
    if name == "upload_dataset":
        return await upload_dataset(arguments)
    elif name == "get_data_profile":
        return await get_data_profile(arguments)
    elif name == "train_ml_models":
        return await train_ml_models(arguments)
    elif name == "generate_visualizations":
        return await generate_visualizations(arguments)
    elif name == "analyze_correlations":
        return await analyze_correlations(arguments)
    elif name == "list_datasets":
        return await list_datasets(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")


async def upload_dataset(args: dict) -> list[types.TextContent]:
    """Upload and profile dataset"""
    try:
        csv_base64 = args["csv_base64"]
        dataset_name = args["dataset_name"]
        
        csv_data = base64.b64decode(csv_base64)
        df = pd.read_csv(BytesIO(csv_data))
        
        dataset_id = str(uuid.uuid4())
        
        datasets[dataset_id] = {
            "id": dataset_id,
            "name": dataset_name,
            "dataframe": df,
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": df.columns.tolist(),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        profile = {
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": df.columns.tolist(),
            "numeric_columns": df.select_dtypes(include=[np.number]).columns.tolist()
        }
        
        return [types.TextContent(type="text", text=json.dumps({
            "success": True, "dataset_id": dataset_id, "profile": profile
        }, indent=2))]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]


async def get_data_profile(args: dict) -> list[types.TextContent]:
    """Get comprehensive data profiling"""
    try:
        dataset_id = args["dataset_id"]
        if dataset_id not in datasets:
            return [types.TextContent(type="text", text="Dataset not found")]
        
        df = datasets[dataset_id]["dataframe"]
        
        profile = {
            "basic_info": {
                "row_count": len(df),
                "column_count": len(df.columns),
                "duplicate_rows": int(df.duplicated().sum())
            },
            "missing_data": {
                "total_missing": int(df.isnull().sum().sum()),
                "missing_by_column": df.isnull().sum().to_dict()
            },
            "numeric_summary": df.describe().to_dict()
        }
        
        return [types.TextContent(type="text", text=json.dumps(profile, indent=2, default=str))]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]


async def train_ml_models(args: dict) -> list[types.TextContent]:
    """Train ML models"""
    try:
        dataset_id = args["dataset_id"]
        target_column = args["target_column"]
        
        if dataset_id not in datasets:
            return [types.TextContent(type="text", text="Dataset not found")]
        
        df = datasets[dataset_id]["dataframe"]
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if target_column not in numeric_cols:
            return [types.TextContent(type="text", text="Target must be numeric")]
        
        feature_cols = [col for col in numeric_cols if col != target_column]
        X = df[feature_cols].fillna(df[feature_cols].mean())
        y = df[target_column].fillna(df[target_column].mean())
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        models = {
            "Linear Regression": LinearRegression(),
            "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
            "XGBoost": xgb.XGBRegressor(n_estimators=100, random_state=42)
        }
        
        results = []
        for model_name, model in models.items():
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            r2 = r2_score(y_test, y_pred)
            results.append({"model_name": model_name, "r2_score": float(r2)})
        
        return [types.TextContent(type="text", text=json.dumps({
            "success": True, "models": results
        }, indent=2))]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]


async def generate_visualizations(args: dict) -> list[types.TextContent]:
    """Generate visualizations"""
    try:
        dataset_id = args["dataset_id"]
        if dataset_id not in datasets:
            return [types.TextContent(type="text", text="Dataset not found")]
        
        df = datasets[dataset_id]["dataframe"]
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        charts = []
        
        # Histogram
        if numeric_cols:
            for col in numeric_cols[:3]:
                fig = px.histogram(df, x=col, title=f"Distribution of {col}")
                charts.append({"type": "histogram", "title": f"Distribution of {col}"})
        
        # Correlation
        if len(numeric_cols) > 1:
            corr_matrix = df[numeric_cols].corr()
            charts.append({"type": "correlation", "title": "Correlation Heatmap"})
        
        return [types.TextContent(type="text", text=json.dumps({
            "success": True, "chart_count": len(charts), "charts": charts
        }, indent=2))]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]


async def analyze_correlations(args: dict) -> list[types.TextContent]:
    """Analyze correlations"""
    try:
        dataset_id = args["dataset_id"]
        if dataset_id not in datasets:
            return [types.TextContent(type="text", text="Dataset not found")]
        
        df = datasets[dataset_id]["dataframe"]
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_cols) < 2:
            return [types.TextContent(type="text", text="Need 2+ numeric columns")]
        
        corr_matrix = df[numeric_cols].corr()
        
        correlations = []
        for i, col1 in enumerate(numeric_cols):
            for col2 in numeric_cols[i+1:]:
                corr_value = corr_matrix.loc[col1, col2]
                if abs(corr_value) > 0.1:
                    correlations.append({
                        "feature1": col1,
                        "feature2": col2,
                        "correlation": float(corr_value)
                    })
        
        return [types.TextContent(type="text", text=json.dumps({
            "success": True, "correlations": correlations
        }, indent=2))]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]


async def list_datasets(args: dict) -> list[types.TextContent]:
    """List all datasets"""
    dataset_list = [{"id": k, "name": v["name"], "rows": v["row_count"]} for k, v in datasets.items()]
    return [types.TextContent(type="text", text=json.dumps({
        "success": True, "count": len(dataset_list), "datasets": dataset_list
    }, indent=2))]


async def main():
    """Run MCP server"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="promise-ai-complete",
                server_version="2.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
