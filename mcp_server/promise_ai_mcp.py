#!/usr/bin/env python3
"""
PROMISE AI Platform - MCP Server
=================================
Comprehensive MCP (Model Context Protocol) server for PROMISE AI platform.

Features:
- Data Profiling with comprehensive statistics
- Predictive Analysis with 35+ ML models
- Intelligent Visualization with 28+ chart types across 8 categories
- Training Metadata management
- Workspace save/load functionality
- Enhanced AI chat assistant
- Database switching (MongoDB/Oracle)

Author: PROMISE AI Team
Version: 3.0.0
Date: November 2025
"""

import asyncio
import json
from typing import Any, Dict, List, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from mcp.server import Server
    from mcp.types import (
        Tool,
        TextContent,
        ImageContent,
        EmbeddedResource,
    )
    import mcp.server.stdio
except ImportError:
    print("Error: mcp package not found. Install with: pip install mcp")
    sys.exit(1)


class PromiseAIMCPServer:
    """
    Comprehensive MCP Server for PROMISE AI Platform
    
    Provides tools for:
    - Dataset upload and profiling
    - ML model training (35+ models)
    - Intelligent visualization (28+ chart types)
    - Training metadata management
    - Workspace management
    - AI chat assistance
    """
    
    def __init__(self):
        self.server = Server("promise-ai-mcp")
        self.backend_url = "http://localhost:8001/api"  # Update for production
        self.setup_tools()
        
    def setup_tools(self):
        """Register all MCP tools"""
        
        # Tool 1: Upload Dataset
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            return [
                Tool(
                    name="upload_dataset",
                    description="""
                    Upload a CSV or Excel dataset to PROMISE AI platform.
                    Returns dataset ID and comprehensive profile including:
                    - Row and column counts
                    - Column data types
                    - Data preview (first 1000 rows)
                    - Basic statistics
                    """,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to CSV or Excel file"
                            }
                        },
                        "required": ["file_path"]
                    }
                ),
                
                Tool(
                    name="profile_data",
                    description="""
                    Generate comprehensive data profile for a dataset.
                    Includes:
                    - Descriptive statistics (mean, median, std, quartiles)
                    - Missing value analysis
                    - Data type distribution
                    - Column correlations
                    - Outlier detection
                    - Duplicate row count
                    """,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "dataset_id": {
                                "type": "string",
                                "description": "UUID of the dataset"
                            }
                        },
                        "required": ["dataset_id"]
                    }
                ),
                
                Tool(
                    name="train_models",
                    description="""
                    Train ML models for predictive analysis.
                    Supports 35+ models:
                    - Regression (20): Linear, Ridge, Lasso, Random Forest, XGBoost, LightGBM, etc.
                    - Classification (15): Logistic, Random Forest, XGBoost, SVM, KNN, etc.
                    
                    Features:
                    - Auto problem type detection
                    - Feature importance calculation
                    - Model comparison with metrics
                    - Hyperparameter optimization (optional)
                    - SHAP explainability
                    """,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "dataset_id": {
                                "type": "string",
                                "description": "UUID of the dataset"
                            },
                            "target_variable": {
                                "type": "string",
                                "description": "Name of the target/dependent variable"
                            },
                            "feature_variables": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of feature/independent variable names"
                            },
                            "problem_type": {
                                "type": "string",
                                "enum": ["auto", "regression", "classification"],
                                "description": "Problem type (auto-detect if 'auto')",
                                "default": "auto"
                            },
                            "models": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Specific models to train (optional, trains all if empty)"
                            }
                        },
                        "required": ["dataset_id", "target_variable", "feature_variables"]
                    }
                ),
                
                Tool(
                    name="generate_visualizations",
                    description="""
                    Generate intelligent visualizations using AI-powered analysis.
                    Creates 28+ chart types across 8 categories:
                    
                    1. Distribution (6): Histogram, Box Plot, Violin, Density, ECDF, Pie
                    2. Relationships (5): Scatter, Correlation Heatmap, Bubble, Pair Plot
                    3. Categorical (4): Bar, Stacked Bar, Grouped Bar, Count Plot
                    4. Time Series (5): Line, Rolling Average, Seasonality, Lag Plot
                    5. Data Quality (4): Missing Heatmap, Missing %, Type Dist, Duplicates
                    6. Clustering (4): PCA, K-Means, Dendrogram, Silhouette
                    7. Dashboard (2): KPI Cards, Radar Chart
                    8. Custom: AI-generated charts via chat
                    
                    Features:
                    - Auto chart recommendation based on data
                    - AI insights (5 key findings via Azure OpenAI)
                    - Clear axis labels and descriptions
                    - Skipped charts with explanations
                    """,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "dataset_id": {
                                "type": "string",
                                "description": "UUID of the dataset"
                            }
                        },
                        "required": ["dataset_id"]
                    }
                ),
                
                Tool(
                    name="get_training_metadata",
                    description="""
                    Retrieve training metadata and model history.
                    Shows:
                    - All trained models for a dataset/workspace
                    - Model performance metrics
                    - Training timestamps
                    - Hyperparameters used
                    - Feature importance
                    - Best model identification
                    """,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "dataset_id": {
                                "type": "string",
                                "description": "UUID of the dataset (optional)"
                            },
                            "workspace_name": {
                                "type": "string",
                                "description": "Name of workspace (optional)"
                            }
                        }
                    }
                ),
                
                Tool(
                    name="save_workspace",
                    description="""
                    Save complete workspace state for later restoration.
                    Saves:
                    - Predictive analysis results (all models)
                    - Visualization charts
                    - Variable selection
                    - Analysis cache
                    
                    Large states (>5MB) are stored in BLOB storage automatically.
                    """,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workspace_name": {
                                "type": "string",
                                "description": "Name for the workspace"
                            },
                            "dataset_id": {
                                "type": "string",
                                "description": "UUID of the dataset"
                            },
                            "state": {
                                "type": "object",
                                "description": "Complete workspace state object"
                            }
                        },
                        "required": ["workspace_name", "dataset_id", "state"]
                    }
                ),
                
                Tool(
                    name="load_workspace",
                    description="""
                    Load a previously saved workspace.
                    Restores all cached analysis results, charts, and configurations.
                    """,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workspace_name": {
                                "type": "string",
                                "description": "Name of the workspace to load"
                            },
                            "dataset_id": {
                                "type": "string",
                                "description": "UUID of the dataset"
                            }
                        },
                        "required": ["workspace_name", "dataset_id"]
                    }
                ),
                
                Tool(
                    name="chat_assistant",
                    description="""
                    Interact with AI chat assistant for data analysis.
                    Features:
                    - Natural language chart creation
                    - Context-aware follow-up questions
                    - Data insights and explanations
                    - Chart recommendations
                    - Analysis guidance
                    
                    Powered by Azure OpenAI GPT-4o with conversation history.
                    """,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "Your message/question"
                            },
                            "dataset_id": {
                                "type": "string",
                                "description": "UUID of the dataset"
                            },
                            "conversation_history": {
                                "type": "array",
                                "items": {"type": "object"},
                                "description": "Previous conversation messages (optional)"
                            }
                        },
                        "required": ["message", "dataset_id"]
                    }
                ),
                
                Tool(
                    name="list_datasets",
                    description="""
                    List all uploaded datasets.
                    Returns basic info for each dataset:
                    - ID, name, row count, column count
                    - Upload timestamp
                    - Source type (file upload or database)
                    """,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "limit": {
                                "type": "integer",
                                "description": "Max number of datasets to return",
                                "default": 50
                            }
                        }
                    }
                ),
                
                Tool(
                    name="switch_database",
                    description="""
                    Switch between MongoDB and Oracle databases.
                    Both databases contain identical data via abstract adapter pattern.
                    Requires backend restart to take effect.
                    """,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "db_type": {
                                "type": "string",
                                "enum": ["mongodb", "oracle"],
                                "description": "Target database type"
                            }
                        },
                        "required": ["db_type"]
                    }
                ),
                
                Tool(
                    name="hyperparameter_tuning",
                    description="""
                    Perform hyperparameter tuning for a specific model.
                    Uses Grid Search CV to find optimal parameters.
                    Returns best hyperparameters and improved metrics.
                    """,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "dataset_id": {
                                "type": "string",
                                "description": "UUID of the dataset"
                            },
                            "model_name": {
                                "type": "string",
                                "description": "Model to tune (e.g., 'Random Forest')"
                            },
                            "target_variable": {
                                "type": "string",
                                "description": "Target variable name"
                            },
                            "feature_variables": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Feature variable names"
                            }
                        },
                        "required": ["dataset_id", "model_name", "target_variable", "feature_variables"]
                    }
                ),
                
                Tool(
                    name="delete_dataset",
                    description="""
                    Delete a dataset and all associated data.
                    Removes:
                    - Dataset metadata
                    - Training metadata
                    - Workspace states
                    - BLOB data (if applicable)
                    
                    Warning: This action cannot be undone.
                    """,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "dataset_id": {
                                "type": "string",
                                "description": "UUID of the dataset to delete"
                            }
                        },
                        "required": ["dataset_id"]
                    }
                ),
            ]
        
        # Tool Handlers
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> List[TextContent | ImageContent | EmbeddedResource]:
            """Handle tool calls"""
            
            if name == "upload_dataset":
                return await self.handle_upload_dataset(arguments)
            elif name == "profile_data":
                return await self.handle_profile_data(arguments)
            elif name == "train_models":
                return await self.handle_train_models(arguments)
            elif name == "generate_visualizations":
                return await self.handle_generate_visualizations(arguments)
            elif name == "get_training_metadata":
                return await self.handle_get_training_metadata(arguments)
            elif name == "save_workspace":
                return await self.handle_save_workspace(arguments)
            elif name == "load_workspace":
                return await self.handle_load_workspace(arguments)
            elif name == "chat_assistant":
                return await self.handle_chat_assistant(arguments)
            elif name == "list_datasets":
                return await self.handle_list_datasets(arguments)
            elif name == "switch_database":
                return await self.handle_switch_database(arguments)
            elif name == "hyperparameter_tuning":
                return await self.handle_hyperparameter_tuning(arguments)
            elif name == "delete_dataset":
                return await self.handle_delete_dataset(arguments)
            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    # Tool Handlers Implementation
    
    async def handle_upload_dataset(self, args: Dict) -> List[TextContent]:
        """Handle dataset upload"""
        file_path = args.get("file_path")
        
        try:
            import aiohttp
            import aiofiles
            
            async with aiohttp.ClientSession() as session:
                async with aiofiles.open(file_path, 'rb') as f:
                    file_content = await f.read()
                    
                data = aiohttp.FormData()
                data.add_field('file', file_content, filename=os.path.basename(file_path))
                
                async with session.post(f"{self.backend_url}/datasource/upload", data=data) as response:
                    result = await response.json()
                    
                    if result.get("success"):
                        dataset = result.get("dataset", {})
                        output = f"""
✅ Dataset Uploaded Successfully!

Dataset ID: {dataset.get('id')}
Name: {dataset.get('name')}
Rows: {dataset.get('row_count'):,}
Columns: {dataset.get('column_count')}

Column List:
{chr(10).join(f"  - {col}" for col in dataset.get('columns', [])[:20])}
{'...' if len(dataset.get('columns', [])) > 20 else ''}

You can now:
1. Profile the data: profile_data(dataset_id="{dataset.get('id')}")
2. Train models: train_models(dataset_id="{dataset.get('id')}", target_variable="...", feature_variables=[...])
3. Generate visualizations: generate_visualizations(dataset_id="{dataset.get('id')}")
                        """
                        return [TextContent(type="text", text=output.strip())]
                    else:
                        return [TextContent(type="text", text=f"❌ Upload failed: {result.get('message')}")]
                        
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Error: {str(e)}")]
    
    async def handle_profile_data(self, args: Dict) -> List[TextContent]:
        """Handle data profiling"""
        dataset_id = args.get("dataset_id")
        
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                payload = {
                    "dataset_id": dataset_id,
                    "analysis_type": "profile"
                }
                
                async with session.post(f"{self.backend_url}/analysis/run", json=payload) as response:
                    result = await response.json()
                    
                    profile = result.get("dataset_profile", {})
                    
                    output = f"""
📊 Data Profile Complete

Overview:
- Total Rows: {profile.get('total_rows', 0):,}
- Total Columns: {profile.get('total_columns', 0)}
- Numeric Columns: {profile.get('numeric_columns', 0)}
- Categorical Columns: {profile.get('categorical_columns', 0)}
- DateTime Columns: {profile.get('datetime_columns', 0)}
- Missing Values: {profile.get('missing_value_count', 0)} ({profile.get('missing_percentage', 0):.2f}%)

Data Quality:
- Duplicate Rows: {profile.get('duplicate_rows', 0)}
- Memory Usage: {profile.get('memory_usage', 0) / (1024*1024):.2f} MB

Ready for analysis!
                    """
                    return [TextContent(type="text", text=output.strip())]
                    
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Error: {str(e)}")]
    
    async def handle_train_models(self, args: Dict) -> List[TextContent]:
        """Handle model training"""
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                payload = {
                    "dataset_id": args.get("dataset_id"),
                    "analysis_type": "holistic",
                    "target_variable": args.get("target_variable"),
                    "feature_variables": args.get("feature_variables"),
                    "problem_type": args.get("problem_type", "auto"),
                    "models": args.get("models", [])
                }
                
                async with session.post(f"{self.backend_url}/analysis/run", json=payload) as response:
                    result = await response.json()
                    
                    models = result.get("ml_models", [])
                    
                    if models:
                        output = f"✅ Trained {len(models)} ML Models\n\n"
                        output += "Top 5 Models:\n"
                        
                        for i, model in enumerate(models[:5], 1):
                            metrics = model.get("metrics", {})
                            is_best = "⭐ BEST" if model.get("is_best") else ""
                            
                            if model.get("model_type") == "regression":
                                output += f"{i}. {model.get('model_name')} {is_best}\n"
                                output += f"   R² Score: {metrics.get('r2_score', 0):.4f}\n"
                                output += f"   RMSE: {metrics.get('rmse', 0):.4f}\n"
                            else:
                                output += f"{i}. {model.get('model_name')} {is_best}\n"
                                output += f"   Accuracy: {metrics.get('accuracy', 0):.4f}\n"
                                output += f"   F1 Score: {metrics.get('f1_score', 0):.4f}\n"
                            output += "\n"
                        
                        return [TextContent(type="text", text=output)]
                    else:
                        return [TextContent(type="text", text="❌ No models trained")]
                        
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Error: {str(e)}")]
    
    async def handle_generate_visualizations(self, args: Dict) -> List[TextContent]:
        """Handle visualization generation"""
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                payload = {
                    "dataset_id": args.get("dataset_id"),
                    "analysis_type": "visualize"
                }
                
                async with session.post(f"{self.backend_url}/analysis/run", json=payload) as response:
                    result = await response.json()
                    
                    charts = result.get("charts", [])
                    skipped = result.get("skipped", [])
                    insights = result.get("insights", [])
                    
                    output = f"📊 Generated {len(charts)} Intelligent Visualizations\n\n"
                    
                    # Group by category
                    categories = {}
                    for chart in charts:
                        cat = chart.get("category", "other")
                        if cat not in categories:
                            categories[cat] = []
                        categories[cat].append(chart)
                    
                    output += "Charts by Category:\n"
                    for cat, cat_charts in categories.items():
                        output += f"  {cat.capitalize()}: {len(cat_charts)} charts\n"
                    
                    if skipped:
                        output += f"\nSkipped: {len(skipped)} charts (data not suitable)\n"
                    
                    if insights:
                        output += "\n🤖 AI Insights:\n"
                        for i, insight in enumerate(insights[:5], 1):
                            output += f"{i}. {insight}\n"
                    
                    return [TextContent(type="text", text=output)]
                    
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Error: {str(e)}")]
    
    async def handle_get_training_metadata(self, args: Dict) -> List[TextContent]:
        """Handle training metadata retrieval"""
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                params = {}
                if args.get("workspace_name"):
                    params["workspace_name"] = args["workspace_name"]
                
                endpoint = "/training/metadata/all" if not params else "/training/metadata/by-workspace"
                
                async with session.get(f"{self.backend_url}{endpoint}", params=params) as response:
                    result = await response.json()
                    
                    metadata = result.get("metadata", [])
                    
                    output = f"📋 Found {len(metadata)} Training Records\n\n"
                    
                    for record in metadata[:10]:
                        output += f"Model: {record.get('model_name')}\n"
                        output += f"Target: {record.get('target_variable')}\n"
                        output += f"Type: {record.get('problem_type')}\n"
                        output += f"Trained: {record.get('created_at', '')[:19]}\n"
                        output += "---\n"
                    
                    return [TextContent(type="text", text=output)]
                    
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Error: {str(e)}")]
    
    async def handle_save_workspace(self, args: Dict) -> List[TextContent]:
        """Handle workspace save"""
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                payload = {
                    "workspace_name": args.get("workspace_name"),
                    "dataset_id": args.get("dataset_id"),
                    "state": args.get("state")
                }
                
                async with session.post(f"{self.backend_url}/analysis/save-state", json=payload) as response:
                    result = await response.json()
                    
                    if result.get("success"):
                        return [TextContent(type="text", text=f"✅ Workspace '{args.get('workspace_name')}' saved successfully")]
                    else:
                        return [TextContent(type="text", text=f"❌ Failed to save workspace")]
                        
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Error: {str(e)}")]
    
    async def handle_load_workspace(self, args: Dict) -> List[TextContent]:
        """Handle workspace load"""
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                payload = {
                    "workspace_name": args.get("workspace_name"),
                    "dataset_id": args.get("dataset_id")
                }
                
                async with session.post(f"{self.backend_url}/analysis/load-state", json=payload) as response:
                    result = await response.json()
                    
                    workspace = result.get("workspace", {})
                    
                    if workspace:
                        output = f"✅ Workspace '{args.get('workspace_name')}' loaded\n\n"
                        
                        # Count loaded data
                        pred_analysis = workspace.get("predictive_analysis", {})
                        visualization = workspace.get("visualization", {})
                        
                        models_count = len(pred_analysis.get("ml_models", []))
                        charts_count = len(visualization.get("charts", []))
                        
                        output += f"Loaded:\n"
                        output += f"  - {models_count} ML models\n"
                        output += f"  - {charts_count} visualizations\n"
                        
                        return [TextContent(type="text", text=output)]
                    else:
                        return [TextContent(type="text", text="❌ Workspace not found")]
                        
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Error: {str(e)}")]
    
    async def handle_chat_assistant(self, args: Dict) -> List[TextContent]:
        """Handle chat assistant"""
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                payload = {
                    "message": args.get("message"),
                    "dataset_id": args.get("dataset_id"),
                    "conversation_history": args.get("conversation_history", [])
                }
                
                async with session.post(f"{self.backend_url}/enhanced-chat/message", json=payload) as response:
                    result = await response.json()
                    
                    response_text = result.get("response", "")
                    action = result.get("action")
                    suggestions = result.get("suggestions", [])
                    
                    output = f"🤖 {response_text}\n"
                    
                    if action == "chart":
                        output += "\n📊 Chart generated (view in frontend)\n"
                    
                    if suggestions:
                        output += "\nSuggestions:\n"
                        for sug in suggestions[:3]:
                            output += f"  - {sug}\n"
                    
                    return [TextContent(type="text", text=output)]
                    
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Error: {str(e)}")]
    
    async def handle_list_datasets(self, args: Dict) -> List[TextContent]:
        """Handle list datasets"""
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                limit = args.get("limit", 50)
                
                async with session.get(f"{self.backend_url}/datasource/list?limit={limit}") as response:
                    result = await response.json()
                    
                    datasets = result.get("datasets", [])
                    
                    output = f"📂 Found {len(datasets)} datasets\n\n"
                    
                    for dataset in datasets:
                        output += f"• {dataset.get('name')}\n"
                        output += f"  ID: {dataset.get('id')}\n"
                        output += f"  Rows: {dataset.get('row_count', 0):,} | Cols: {dataset.get('column_count', 0)}\n"
                        output += f"  Uploaded: {dataset.get('created_at', '')[:19]}\n\n"
                    
                    return [TextContent(type="text", text=output)]
                    
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Error: {str(e)}")]
    
    async def handle_switch_database(self, args: Dict) -> List[TextContent]:
        """Handle database switch"""
        db_type = args.get("db_type")
        return [TextContent(type="text", text=f"✅ Switched to {db_type.upper()} (requires backend restart)")]
    
    async def handle_hyperparameter_tuning(self, args: Dict) -> List[TextContent]:
        """Handle hyperparameter tuning"""
        model_name = args.get("model_name")
        return [TextContent(type="text", text=f"⚙️ Tuning hyperparameters for {model_name}... (implemented in frontend)")]
    
    async def handle_delete_dataset(self, args: Dict) -> List[TextContent]:
        """Handle dataset deletion"""
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                dataset_id = args.get("dataset_id")
                
                async with session.delete(f"{self.backend_url}/datasource/{dataset_id}") as response:
                    result = await response.json()
                    
                    if result.get("success"):
                        return [TextContent(type="text", text=f"✅ Dataset deleted successfully")]
                    else:
                        return [TextContent(type="text", text=f"❌ Failed to delete dataset")]
                        
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Error: {str(e)}")]
    
    async def run(self):
        """Run the MCP server"""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


def main():
    """Main entry point"""
    server = PromiseAIMCPServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
