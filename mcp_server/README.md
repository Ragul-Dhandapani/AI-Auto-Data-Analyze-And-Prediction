# PROMISE AI MCP Server

Model Context Protocol server for PROMISE AI - Provides data analysis and ML capabilities to AI agents.

## Features

- **Dataset Management**: Upload and manage datasets
- **Holistic Analysis**: Comprehensive ML analysis with auto-charts
- **Visualizations**: Generate 15+ intelligent charts
- **Workspace Management**: Save and load analysis states
- **ML Models**: RandomForest, LinearRegression with auto-training
- **AI Insights**: LLM-powered insights generation

## Tools Available

1. `upload_dataset` - Upload CSV data
2. `holistic_analysis` - Run comprehensive analysis
3. `generate_visualizations` - Create charts
4. `save_workspace` - Save analysis state

## Installation

### For Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "autopredict": {
      "command": "python",
      "args": ["/app/mcp_server/autopredict_mcp.py"],
      "env": {
        "EMERGENT_LLM_KEY": "sk-emergent-9Ef52962b9aA8Cf87A"
      }
    }
  }
}
```

### For VS Code (Cline Extension)

Add to Cline MCP settings:

```json
{
  "autopredict": {
    "command": "python",
    "args": ["/app/mcp_server/autopredict_mcp.py"],
    "env": {
      "EMERGENT_LLM_KEY": "sk-emergent-9Ef52962b9aA8Cf87A"
    }
  }
}
```

## Usage Example

```python
# In Claude or any MCP client:

# 1. Upload a dataset
result = use_mcp_tool(
    "autopredict",
    "upload_dataset",
    {
        "csv_base64": "<base64_encoded_csv>",
        "dataset_name": "sales_data"
    }
)

# 2. Analyze the data
analysis = use_mcp_tool(
    "autopredict",
    "analyze_data",
    {"dataset_id": "ds_0"}
)

# 3. Run predictions
predictions = use_mcp_tool(
    "autopredict",
    "predict_with_ml",
    {
        "dataset_id": "ds_0",
        "target_column": "revenue",
        "model_type": "random_forest"
    }
)

# 4. Get AI insights
insights = use_mcp_tool(
    "autopredict",
    "generate_insights",
    {
        "dataset_id": "ds_0",
        "focus_area": "sales trends and anomalies"
    }
)
```

## Testing

```bash
# Test the server
python /app/mcp_server/autopredict_mcp.py
```

## Requirements

All dependencies are already installed in the main project.
