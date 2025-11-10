#!/usr/bin/env python3
"""
PROMISE AI MCP Server
Exposes PROMISE AI functionality as Model Context Protocol tools for AI assistants
"""
import asyncio
import json
import os
import sys
from typing import Any, Dict, List, Optional
import logging

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from mcp.server.models import InitializationOptions
    from mcp.server import NotificationOptions, Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError:
    print("Error: MCP SDK not installed. Install with: pip install mcp")
    sys.exit(1)

import httpx
from dotenv import load_dotenv

# Load environment variables
from pathlib import Path
ROOT_DIR = Path(__file__).parent.parent.parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Backend API URL
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

# Initialize MCP server
server = Server("promise-ai-server")

# HTTP client for API calls
client = httpx.AsyncClient(timeout=300.0)


@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """
    List all available PROMISE AI tools
    """
    return [
        Tool(
            name="upload_dataset",
            description="Upload a CSV dataset to PROMISE AI for analysis. Accepts file content as base64 or file path.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the CSV file to upload"
                    },
                    "dataset_name": {
                        "type": "string",
                        "description": "Optional name for the dataset"
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="list_datasets",
            description="List all uploaded datasets with metadata (columns, row count, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of datasets to return (default: 10)"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="run_predictive_analysis",
            description="Run predictive analysis on a dataset with multiple ML models (regression, classification, or auto-detect)",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_id": {
                        "type": "string",
                        "description": "ID of the dataset to analyze"
                    },
                    "target_column": {
                        "type": "string",
                        "description": "Target variable to predict (optional, will auto-detect if not provided)"
                    },
                    "problem_type": {
                        "type": "string",
                        "enum": ["auto", "regression", "classification", "time_series"],
                        "description": "Type of problem (default: auto)"
                    },
                    "feature_columns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of feature columns to use (optional)"
                    }
                },
                "required": ["dataset_id"]
            }
        ),
        Tool(
            name="run_time_series_analysis",
            description="Run time series forecasting with Prophet or LSTM, including anomaly detection",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_id": {
                        "type": "string",
                        "description": "ID of the dataset"
                    },
                    "time_column": {
                        "type": "string",
                        "description": "Name of the datetime column"
                    },
                    "target_column": {
                        "type": "string",
                        "description": "Target column to forecast"
                    },
                    "forecast_periods": {
                        "type": "integer",
                        "description": "Number of periods to forecast (default: 30)"
                    },
                    "forecast_method": {
                        "type": "string",
                        "enum": ["prophet", "lstm", "both"],
                        "description": "Forecasting method (default: prophet)"
                    }
                },
                "required": ["dataset_id", "time_column", "target_column"]
            }
        ),
        Tool(
            name="tune_hyperparameters",
            description="Optimize model hyperparameters using grid search or random search",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_id": {
                        "type": "string",
                        "description": "ID of the dataset"
                    },
                    "target_column": {
                        "type": "string",
                        "description": "Target column to predict"
                    },
                    "model_type": {
                        "type": "string",
                        "enum": ["random_forest", "xgboost", "lightgbm"],
                        "description": "Model type to tune"
                    },
                    "problem_type": {
                        "type": "string",
                        "enum": ["regression", "classification"],
                        "description": "Problem type"
                    },
                    "search_type": {
                        "type": "string",
                        "enum": ["grid", "random"],
                        "description": "Search strategy (default: grid)"
                    }
                },
                "required": ["dataset_id", "target_column", "model_type", "problem_type"]
            }
        ),
        Tool(
            name="get_training_metadata",
            description="Get training history and model performance metadata for all datasets",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="submit_feedback",
            description="Submit feedback on model predictions for active learning",
            inputSchema={
                "type": "object",
                "properties": {
                    "prediction_id": {
                        "type": "string",
                        "description": "ID of the prediction"
                    },
                    "is_correct": {
                        "type": "boolean",
                        "description": "Whether the prediction was correct"
                    },
                    "actual_outcome": {
                        "type": "string",
                        "description": "Actual outcome value (optional)"
                    },
                    "comment": {
                        "type": "string",
                        "description": "Optional comment about the prediction"
                    }
                },
                "required": ["prediction_id", "is_correct"]
            }
        ),
        Tool(
            name="get_dataset_profile",
            description="Get detailed statistical profile of a dataset",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_id": {
                        "type": "string",
                        "description": "ID of the dataset to profile"
                    }
                },
                "required": ["dataset_id"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(
    name: str,
    arguments: Dict[str, Any]
) -> List[TextContent]:
    """
    Handle tool execution
    """
    try:
        logger.info(f"Executing tool: {name} with arguments: {arguments}")
        
        if name == "upload_dataset":
            result = await upload_dataset(arguments)
        elif name == "list_datasets":
            result = await list_datasets(arguments)
        elif name == "run_predictive_analysis":
            result = await run_predictive_analysis(arguments)
        elif name == "run_time_series_analysis":
            result = await run_time_series_analysis(arguments)
        elif name == "tune_hyperparameters":
            result = await tune_hyperparameters(arguments)
        elif name == "get_training_metadata":
            result = await get_training_metadata(arguments)
        elif name == "submit_feedback":
            result = await submit_feedback(arguments)
        elif name == "get_dataset_profile":
            result = await get_dataset_profile(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    except Exception as e:
        logger.error(f"Error executing tool {name}: {str(e)}")
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e)}, indent=2)
        )]


# Tool implementation functions

async def upload_dataset(args: Dict[str, Any]) -> Dict[str, Any]:
    """Upload a dataset to PROMISE AI"""
    file_path = args.get("file_path")
    dataset_name = args.get("dataset_name", os.path.basename(file_path))
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, "rb") as f:
        files = {"file": (dataset_name, f, "text/csv")}
        response = await client.post(f"{API_BASE}/datasource/upload", files=files)
        response.raise_for_status()
        return response.json()


async def list_datasets(args: Dict[str, Any]) -> Dict[str, Any]:
    """List all datasets"""
    limit = args.get("limit", 10)
    response = await client.get(f"{API_BASE}/datasets", params={"limit": limit})
    response.raise_for_status()
    return response.json()


async def run_predictive_analysis(args: Dict[str, Any]) -> Dict[str, Any]:
    """Run predictive analysis"""
    payload = {
        "dataset_id": args["dataset_id"],
        "target_column": args.get("target_column"),
        "problem_type": args.get("problem_type", "auto"),
        "feature_columns": args.get("feature_columns"),
        "variable_selection": {
            "mode": "manual" if args.get("target_column") else "auto",
            "targets": [{"column": args.get("target_column")}] if args.get("target_column") else []
        }
    }
    
    response = await client.post(f"{API_BASE}/analysis/holistic", json=payload)
    response.raise_for_status()
    return response.json()


async def run_time_series_analysis(args: Dict[str, Any]) -> Dict[str, Any]:
    """Run time series analysis"""
    payload = {
        "dataset_id": args["dataset_id"],
        "time_column": args["time_column"],
        "target_column": args["target_column"],
        "forecast_periods": args.get("forecast_periods", 30),
        "forecast_method": args.get("forecast_method", "prophet")
    }
    
    response = await client.post(f"{API_BASE}/analysis/time-series", json=payload)
    response.raise_for_status()
    return response.json()


async def tune_hyperparameters(args: Dict[str, Any]) -> Dict[str, Any]:
    """Tune model hyperparameters"""
    payload = {
        "dataset_id": args["dataset_id"],
        "target_column": args["target_column"],
        "model_type": args["model_type"],
        "problem_type": args["problem_type"],
        "search_type": args.get("search_type", "grid")
    }
    
    response = await client.post(f"{API_BASE}/analysis/hyperparameter-tuning", json=payload)
    response.raise_for_status()
    return response.json()


async def get_training_metadata(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get training metadata"""
    response = await client.get(f"{API_BASE}/training/metadata")
    response.raise_for_status()
    return response.json()


async def submit_feedback(args: Dict[str, Any]) -> Dict[str, Any]:
    """Submit prediction feedback"""
    payload = {
        "prediction_id": args["prediction_id"],
        "is_correct": args["is_correct"],
        "actual_outcome": args.get("actual_outcome"),
        "comment": args.get("comment")
    }
    
    response = await client.post(f"{API_BASE}/feedback/submit", json=payload)
    response.raise_for_status()
    return response.json()


async def get_dataset_profile(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get dataset profile"""
    dataset_id = args["dataset_id"]
    response = await client.get(f"{API_BASE}/datasets/{dataset_id}/profile")
    response.raise_for_status()
    return response.json()


async def main():
    """
    Main entry point for the MCP server
    """
    logger.info(f"Starting PROMISE AI MCP Server")
    logger.info(f"Backend URL: {BACKEND_URL}")
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="promise-ai",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
