#!/usr/bin/env python3
"""
AutoPredict MCP Server
Provides data analysis and prediction capabilities as MCP tools
"""

import asyncio
import json
from typing import Any
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

import pandas as pd
import numpy as np
from io import BytesIO
import base64
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage

load_dotenv()

EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

# Store datasets in memory
datasets = {}

server = Server("autopredict")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="analyze_data",
            description="Analyze a dataset and get profiling information including statistics, missing values, and data quality metrics",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_id": {
                        "type": "string",
                        "description": "Unique identifier for the dataset"
                    },
                    "data_base64": {
                        "type": "string",
                        "description": "Base64 encoded CSV data (provide this or dataset_id)"
                    }
                },
                "required": []
            }
        ),
        types.Tool(
            name="predict_with_ml",
            description="Run predictive analysis on a dataset using machine learning models",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_id": {
                        "type": "string",
                        "description": "Dataset identifier"
                    },
                    "target_column": {
                        "type": "string",
                        "description": "Name of the column to predict"
                    },
                    "model_type": {
                        "type": "string",
                        "enum": ["random_forest", "gradient_boosting", "linear_regression", "decision_tree"],
                        "description": "Type of ML model to use",
                        "default": "random_forest"
                    }
                },
                "required": ["dataset_id", "target_column"]
            }
        ),
        types.Tool(
            name="generate_insights",
            description="Generate AI-powered insights and recommendations from a dataset",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_id": {
                        "type": "string",
                        "description": "Dataset identifier"
                    },
                    "focus_area": {
                        "type": "string",
                        "description": "Optional: Specific area to focus on (trends, patterns, anomalies, etc.)"
                    }
                },
                "required": ["dataset_id"]
            }
        ),
        types.Tool(
            name="clean_data",
            description="Automatically clean data by handling missing values, duplicates, and outliers",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_id": {
                        "type": "string",
                        "description": "Dataset identifier"
                    }
                },
                "required": ["dataset_id"]
            }
        ),
        types.Tool(
            name="upload_dataset",
            description="Upload a new dataset from CSV data",
            inputSchema={
                "type": "object",
                "properties": {
                    "csv_base64": {
                        "type": "string",
                        "description": "Base64 encoded CSV file content"
                    },
                    "dataset_name": {
                        "type": "string",
                        "description": "Name for the dataset"
                    }
                },
                "required": ["csv_base64", "dataset_name"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    
    if name == "upload_dataset":
        csv_data = base64.b64decode(arguments["csv_base64"])
        df = pd.read_csv(BytesIO(csv_data))
        
        dataset_id = f"ds_{len(datasets)}"
        datasets[dataset_id] = df
        
        return [
            types.TextContent(
                type="text",
                text=json.dumps({
                    "dataset_id": dataset_id,
                    "name": arguments["dataset_name"],
                    "rows": len(df),
                    "columns": len(df.columns),
                    "column_names": df.columns.tolist()
                }, indent=2)
            )
        ]
    
    elif name == "analyze_data":
        dataset_id = arguments.get("dataset_id")
        
        if "data_base64" in arguments:
            csv_data = base64.b64decode(arguments["data_base64"])
            df = pd.read_csv(BytesIO(csv_data))
            dataset_id = f"temp_{len(datasets)}"
            datasets[dataset_id] = df
        else:
            df = datasets.get(dataset_id)
            if df is None:
                return [types.TextContent(type="text", text="Dataset not found")]
        
        profile = {
            "dataset_id": dataset_id,
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": [],
            "missing_values_total": int(df.isnull().sum().sum()),
            "duplicate_rows": int(df.duplicated().sum())
        }
        
        for col in df.columns:
            col_info = {
                "name": col,
                "dtype": str(df[col].dtype),
                "missing_count": int(df[col].isnull().sum()),
                "unique_count": int(df[col].nunique())
            }
            
            if pd.api.types.is_numeric_dtype(df[col]):
                col_info["stats"] = {
                    "mean": float(df[col].mean()) if not df[col].isnull().all() else None,
                    "median": float(df[col].median()) if not df[col].isnull().all() else None,
                    "std": float(df[col].std()) if not df[col].isnull().all() else None,
                    "min": float(df[col].min()) if not df[col].isnull().all() else None,
                    "max": float(df[col].max()) if not df[col].isnull().all() else None
                }
            
            profile["columns"].append(col_info)
        
        return [types.TextContent(type="text", text=json.dumps(profile, indent=2))]
    
    elif name == "predict_with_ml":
        dataset_id = arguments["dataset_id"]
        target_column = arguments["target_column"]
        model_type = arguments.get("model_type", "random_forest")
        
        df = datasets.get(dataset_id)
        if df is None:
            return [types.TextContent(type="text", text="Dataset not found")]
        
        if target_column not in df.columns:
            return [types.TextContent(type="text", text=f"Target column '{target_column}' not found")]
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        feature_cols = [col for col in numeric_cols if col != target_column]
        
        if not feature_cols:
            return [types.TextContent(type="text", text="No numeric features available")]
        
        X = df[feature_cols].fillna(df[feature_cols].median())
        y = df[target_column].fillna(df[target_column].median())
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        if model_type == "random_forest":
            model = RandomForestRegressor(n_estimators=100, random_state=42)
        elif model_type == "gradient_boosting":
            model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        elif model_type == "linear_regression":
            model = LinearRegression()
        elif model_type == "decision_tree":
            model = DecisionTreeRegressor(random_state=42)
        else:
            model = RandomForestRegressor(n_estimators=100, random_state=42)
        
        model.fit(X_train, y_train)
        train_score = model.score(X_train, y_train)
        test_score = model.score(X_test, y_test)
        
        predictions = model.predict(X_test)
        
        result = {
            "model_type": model_type,
            "train_score": float(train_score),
            "test_score": float(test_score),
            "predictions_sample": predictions[:10].tolist(),
            "actuals_sample": y_test[:10].tolist()
        }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "generate_insights":
        dataset_id = arguments["dataset_id"]
        focus_area = arguments.get("focus_area", "general analysis")
        
        df = datasets.get(dataset_id)
        if df is None:
            return [types.TextContent(type="text", text="Dataset not found")]
        
        summary = f"""Dataset Overview:
- Rows: {len(df)}
- Columns: {len(df.columns)}
- Missing Values: {df.isnull().sum().sum()}
- Focus: {focus_area}

Column Summary:
"""
        for col in df.columns[:10]:
            summary += f"\n- {col}: {df[col].dtype}, {df[col].nunique()} unique values"
        
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"insights_{dataset_id}",
            system_message="You are a data analysis expert. Provide clear, actionable insights."
        ).with_model("openai", "gpt-4o-mini")
        
        message = UserMessage(
            text=f"Analyze this dataset and provide 3-5 key insights focusing on {focus_area}:\n{summary}"
        )
        
        insights = await chat.send_message(message)
        
        return [types.TextContent(type="text", text=insights)]
    
    elif name == "clean_data":
        dataset_id = arguments["dataset_id"]
        df = datasets.get(dataset_id)
        
        if df is None:
            return [types.TextContent(type="text", text="Dataset not found")]
        
        cleaning_report = []
        
        # Remove duplicates
        dup_count = df.duplicated().sum()
        if dup_count > 0:
            df = df.drop_duplicates()
            cleaning_report.append(f"Removed {dup_count} duplicate rows")
        
        # Handle missing values
        for col in df.columns:
            missing = df[col].isnull().sum()
            if missing > 0:
                if pd.api.types.is_numeric_dtype(df[col]):
                    df[col].fillna(df[col].median(), inplace=True)
                    cleaning_report.append(f"Filled {missing} missing values in '{col}' with median")
                else:
                    df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else 'Unknown', inplace=True)
                    cleaning_report.append(f"Filled {missing} missing values in '{col}' with mode")
        
        datasets[dataset_id] = df
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "cleaning_report": cleaning_report,
                "new_row_count": len(df)
            }, indent=2)
        )]
    
    else:
        return [types.TextContent(type="text", text="Unknown tool")]

async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="autopredict",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
