# PROMISE AI MCP Server

Model Context Protocol server for PROMISE AI - Provides data analysis and ML capabilities to AI agents.

## Available Tools

### 1. upload_dataset
Upload a CSV dataset for analysis
- **Input:** `csv_base64` (base64 encoded CSV), `dataset_name`
- **Output:** Dataset ID and metadata

### 2. analyze_data
Get comprehensive data profiling and statistics
- **Input:** `dataset_id` or `data_base64`
- **Output:** Column statistics, missing values, data types

### 3. predict_with_ml
Run predictive analysis using ML models
- **Input:** `dataset_id`, `target_column`, `model_type` (random_forest, gradient_boosting, linear_regression, decision_tree)
- **Output:** Model performance metrics and predictions

### 4. generate_insights
Get AI-powered insights and recommendations
- **Input:** `dataset_id`, optional `focus_area`
- **Output:** Natural language insights

### 5. clean_data
Automatically clean data
- **Input:** `dataset_id`
- **Output:** Cleaning report

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
