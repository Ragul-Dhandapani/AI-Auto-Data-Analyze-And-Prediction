#!/usr/bin/env python3
"""
PROMISE AI MCP Server v2.0 - Complete Integration
Exposes ALL backend functionality to external AI agents
Matches refactored backend endpoints
"""

import asyncio
import json
from typing import Any, List, Dict, Optional
import sys
import os
import aiohttp

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

# Configuration
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

server = Server("promise-ai-mcp")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List all available PROMISE AI tools"""
    return [
        # Data Source Tools
        types.Tool(
            name="upload_dataset",
            description="Upload a CSV/Excel file for analysis. Returns dataset_id and metadata.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to CSV or Excel file"},
                    "file_name": {"type": "string", "description": "Name of the file"}
                },
                "required": ["file_path"]
            }
        ),
        
        types.Tool(
            name="get_datasets",
            description="Get list of all uploaded datasets (max 10 recent)",
            inputSchema={"type": "object", "properties": {}}
        ),
        
        types.Tool(
            name="delete_dataset",
            description="Delete a dataset and all its workspaces",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_id": {"type": "string", "description": "ID of dataset to delete"}
                },
                "required": ["dataset_id"]
            }
        ),
        
        # Analysis Tools
        types.Tool(
            name="generate_data_profile",
            description="Generate comprehensive data profiling (row count, columns, missing values, statistics)",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_id": {"type": "string", "description": "Dataset ID"}
                },
                "required": ["dataset_id"]
            }
        ),
        
        types.Tool(
            name="generate_ai_insights",
            description="Generate AI-powered insights about the dataset using LLM",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_id": {"type": "string", "description": "Dataset ID"}
                },
                "required": ["dataset_id"]
            }
        ),
        
        types.Tool(
            name="clean_data",
            description="Clean dataset (remove duplicates, handle missing values). Returns cleaning report.",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_id": {"type": "string", "description": "Dataset ID"}
                },
                "required": ["dataset_id"]
            }
        ),
        
        types.Tool(
            name="run_holistic_analysis",
            description="Run complete analysis: ML models, charts, correlations, insights",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_id": {"type": "string", "description": "Dataset ID"}
                },
                "required": ["dataset_id"]
            }
        ),
        
        types.Tool(
            name="generate_visualizations",
            description="Generate auto charts (histograms, box plots, scatter plots, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_id": {"type": "string", "description": "Dataset ID"}
                },
                "required": ["dataset_id"]
            }
        ),
        
        # Chat Tools
        types.Tool(
            name="chat_analysis",
            description="Ask questions or request custom analysis via natural language (e.g., 'show correlation', 'create scatter plot')",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_id": {"type": "string", "description": "Dataset ID"},
                    "message": {"type": "string", "description": "Natural language query or command"},
                    "conversation_history": {
                        "type": "array",
                        "description": "Previous conversation messages",
                        "items": {"type": "object"},
                        "default": []
                    }
                },
                "required": ["dataset_id", "message"]
            }
        ),
        
        # Workspace Tools
        types.Tool(
            name="save_workspace",
            description="Save current analysis state as a named workspace",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_id": {"type": "string", "description": "Dataset ID"},
                    "workspace_name": {"type": "string", "description": "Name for this workspace"},
                    "analysis_data": {"type": "object", "description": "Complete analysis data to save"}
                },
                "required": ["dataset_id", "workspace_name", "analysis_data"]
            }
        ),
        
        types.Tool(
            name="load_workspace",
            description="Load a previously saved workspace",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace_id": {"type": "string", "description": "Workspace ID"}
                },
                "required": ["workspace_id"]
            }
        ),
        
        types.Tool(
            name="get_workspaces",
            description="Get all saved workspaces for a dataset",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_id": {"type": "string", "description": "Dataset ID"}
                },
                "required": ["dataset_id"]
            }
        ),
        
        types.Tool(
            name="delete_workspace",
            description="Delete a saved workspace",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace_id": {"type": "string", "description": "Workspace ID"}
                },
                "required": ["workspace_id"]
            }
        ),
        
        # Training Metadata Tools
        types.Tool(
            name="get_training_metadata",
            description="Get training metadata for all datasets (training count, scores, improvements)",
            inputSchema={"type": "object", "properties": {}}
        ),
        
        types.Tool(
            name="download_training_pdf",
            description="Generate and download PDF report of training metadata",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_id": {"type": "string", "description": "Dataset ID"},
                    "workspace_ids": {
                        "type": "array",
                        "description": "Optional: specific workspace IDs to include",
                        "items": {"type": "string"}
                    }
                },
                "required": ["dataset_id"]
            }
        ),
        
        # Database Connection Tools
        types.Tool(
            name="test_database_connection",
            description="Test connection to external database (PostgreSQL, MySQL, Oracle, SQL Server, MongoDB)",
            inputSchema={
                "type": "object",
                "properties": {
                    "db_type": {"type": "string", "enum": ["postgresql", "mysql", "oracle", "sqlserver", "mongodb"]},
                    "host": {"type": "string"},
                    "port": {"type": "integer"},
                    "database": {"type": "string"},
                    "username": {"type": "string"},
                    "password": {"type": "string"}
                },
                "required": ["db_type", "host", "database"]
            }
        ),
        
        types.Tool(
            name="list_database_tables",
            description="List all tables in a connected database",
            inputSchema={
                "type": "object",
                "properties": {
                    "db_type": {"type": "string"},
                    "host": {"type": "string"},
                    "port": {"type": "integer"},
                    "database": {"type": "string"},
                    "username": {"type": "string"},
                    "password": {"type": "string"}
                },
                "required": ["db_type", "host", "database"]
            }
        ),
        
        types.Tool(
            name="load_database_table",
            description="Load data from a database table",
            inputSchema={
                "type": "object",
                "properties": {
                    "db_type": {"type": "string"},
                    "host": {"type": "string"},
                    "port": {"type": "integer"},
                    "database": {"type": "string"},
                    "username": {"type": "string"},
                    "password": {"type": "string"},
                    "table_name": {"type": "string"}
                },
                "required": ["db_type", "host", "database", "table_name"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Execute tool calls"""
    
    try:
        async with aiohttp.ClientSession() as session:
            
            # Data Source Tools
            if name == "get_datasets":
                async with session.get(f"{API_BASE}/datasets") as response:
                    data = await response.json()
                    return [types.TextContent(type="text", text=json.dumps(data, indent=2))]
            
            elif name == "delete_dataset":
                dataset_id = arguments["dataset_id"]
                async with session.delete(f"{API_BASE}/datasets/{dataset_id}") as response:
                    data = await response.json()
                    return [types.TextContent(type="text", text=json.dumps(data, indent=2))]
            
            # Analysis Tools
            elif name == "generate_data_profile":
                payload = {
                    "dataset_id": arguments["dataset_id"],
                    "analysis_type": "profile"
                }
                async with session.post(f"{API_BASE}/analysis/run", json=payload) as response:
                    data = await response.json()
                    return [types.TextContent(type="text", text=json.dumps(data, indent=2))]
            
            elif name == "generate_ai_insights":
                payload = {
                    "dataset_id": arguments["dataset_id"],
                    "analysis_type": "insights"
                }
                async with session.post(f"{API_BASE}/analysis/run", json=payload) as response:
                    data = await response.json()
                    return [types.TextContent(type="text", text=json.dumps(data, indent=2))]
            
            elif name == "clean_data":
                payload = {
                    "dataset_id": arguments["dataset_id"],
                    "analysis_type": "clean"
                }
                async with session.post(f"{API_BASE}/analysis/run", json=payload) as response:
                    data = await response.json()
                    return [types.TextContent(type="text", text=json.dumps(data, indent=2))]
            
            elif name == "run_holistic_analysis":
                payload = {"dataset_id": arguments["dataset_id"]}
                async with session.post(f"{API_BASE}/analysis/holistic", json=payload) as response:
                    data = await response.json()
                    return [types.TextContent(type="text", text=json.dumps(data, indent=2))]
            
            elif name == "generate_visualizations":
                payload = {
                    "dataset_id": arguments["dataset_id"],
                    "analysis_type": "visualize"
                }
                async with session.post(f"{API_BASE}/analysis/run", json=payload) as response:
                    data = await response.json()
                    return [types.TextContent(type="text", text=json.dumps(data, indent=2))]
            
            # Chat Tools
            elif name == "chat_analysis":
                payload = {
                    "dataset_id": arguments["dataset_id"],
                    "message": arguments["message"],
                    "conversation_history": arguments.get("conversation_history", [])
                }
                async with session.post(f"{API_BASE}/analysis/chat-action", json=payload) as response:
                    data = await response.json()
                    return [types.TextContent(type="text", text=json.dumps(data, indent=2))]
            
            # Workspace Tools
            elif name == "save_workspace":
                payload = {
                    "dataset_id": arguments["dataset_id"],
                    "state_name": arguments["workspace_name"],
                    "analysis_data": arguments["analysis_data"]
                }
                async with session.post(f"{API_BASE}/analysis/save-state", json=payload) as response:
                    data = await response.json()
                    return [types.TextContent(type="text", text=json.dumps(data, indent=2))]
            
            elif name == "load_workspace":
                workspace_id = arguments["workspace_id"]
                async with session.get(f"{API_BASE}/analysis/load-state/{workspace_id}") as response:
                    data = await response.json()
                    return [types.TextContent(type="text", text=json.dumps(data, indent=2))]
            
            elif name == "get_workspaces":
                dataset_id = arguments["dataset_id"]
                async with session.get(f"{API_BASE}/analysis/saved-states/{dataset_id}") as response:
                    data = await response.json()
                    return [types.TextContent(type="text", text=json.dumps(data, indent=2))]
            
            elif name == "delete_workspace":
                workspace_id = arguments["workspace_id"]
                async with session.delete(f"{API_BASE}/analysis/delete-state/{workspace_id}") as response:
                    data = await response.json()
                    return [types.TextContent(type="text", text=json.dumps(data, indent=2))]
            
            # Training Metadata Tools
            elif name == "get_training_metadata":
                async with session.get(f"{API_BASE}/training-metadata") as response:
                    data = await response.json()
                    return [types.TextContent(type="text", text=json.dumps(data, indent=2))]
            
            # Database Tools
            elif name == "test_database_connection":
                async with session.post(f"{API_BASE}/datasource/test-connection", json=arguments) as response:
                    data = await response.json()
                    return [types.TextContent(type="text", text=json.dumps(data, indent=2))]
            
            elif name == "list_database_tables":
                async with session.post(f"{API_BASE}/datasource/list-tables", json=arguments) as response:
                    data = await response.json()
                    return [types.TextContent(type="text", text=json.dumps(data, indent=2))]
            
            elif name == "load_database_table":
                async with session.post(f"{API_BASE}/datasource/load-table", json=arguments) as response:
                    data = await response.json()
                    return [types.TextContent(type="text", text=json.dumps(data, indent=2))]
            
            else:
                return [types.TextContent(type="text", text=f"Unknown tool: {name}")]
    
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Run the MCP server"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="promise-ai-mcp",
                server_version="2.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
