# PROMISE AI - MCP Server Documentation

**Model Context Protocol (MCP) Server** for PROMISE AI allows AI assistants (like Claude Desktop) to access PROMISE AI's ML capabilities as tools.

## 📋 Overview

The MCP Server exposes PROMISE AI functionality through a standardized protocol, enabling AI assistants to:
- Upload and manage datasets
- Run predictive analysis
- Perform time series forecasting
- Tune hyperparameters
- Submit feedback for active learning
- Access training metadata

## 📦 Prerequisites

- Python 3.11+
- PROMISE AI backend running
- MCP SDK installed

## 🔧 Installation

### Step 1: Install MCP SDK

```bash
# Install MCP Python SDK
pip install mcp

# Or add to requirements.txt
echo "mcp>=0.1.0" >> requirements.txt
pip install -r requirements.txt
```

### Step 2: Configure Environment

The MCP server uses the same `.env` configuration as the backend:

```bash
# Ensure backend .env is configured
cd backend
cat .env

# Should contain:
REACT_APP_BACKEND_URL=http://localhost:8001
MONGO_URL=mongodb://localhost:27017
DB_NAME=autopredict_db
```

## ▶️ Running the MCP Server

### Standalone Mode

```bash
# From project root
python mcp_server.py

# Expected output:
# INFO:__main__:Starting PROMISE AI MCP Server
# INFO:__main__:Backend URL: http://localhost:8001
```

### With Claude Desktop

Add to Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "promise-ai": {
      "command": "python",
      "args": ["/absolute/path/to/promise-ai/mcp_server.py"],
      "env": {
        "REACT_APP_BACKEND_URL": "http://localhost:8001"
      }
    }
  }
}
```

Restart Claude Desktop to load the MCP server.

## 🛠 Available Tools

### 1. upload_dataset

**Description**: Upload a CSV dataset to PROMISE AI

**Parameters**:
```json
{
  "file_path": "/path/to/data.csv",
  "dataset_name": "My Dataset" // optional
}
```

**Example Usage in Claude**:
```
Upload the file /Users/me/sales_data.csv to PROMISE AI
```

**Response**:
```json
{
  "id": "dataset-uuid",
  "name": "sales_data.csv",
  "row_count": 5000,
  "column_count": 10,
  "columns": ["date", "sales", "region"],
  "message": "Dataset uploaded successfully"
}
```

### 2. list_datasets

**Description**: List all uploaded datasets

**Parameters**:
```json
{
  "limit": 10 // optional, default: 10
}
```

**Example Usage in Claude**:
```
Show me all datasets in PROMISE AI
```

**Response**:
```json
{
  "datasets": [
    {
      "id": "uuid",
      "name": "sales_data.csv",
      "row_count": 5000,
      "column_count": 10
    }
  ]
}
```

### 3. run_predictive_analysis

**Description**: Run ML analysis on a dataset

**Parameters**:
```json
{
  "dataset_id": "dataset-uuid",
  "target_column": "sales", // optional, will auto-detect
  "problem_type": "auto", // auto, regression, classification
  "feature_columns": ["date", "region"] // optional
}
```

**Example Usage in Claude**:
```
Run predictive analysis on dataset xyz-123 with target column 'sales'
```

**Response**:
```json
{
  "ml_models": [
    {
      "model_name": "Random Forest",
      "r2_score": 0.85,
      "rmse": 125.5
    }
  ],
  "ai_insights": [],
  "business_recommendations": []
}
```

### 4. run_time_series_analysis

**Description**: Forecast future values with time series models

**Parameters**:
```json
{
  "dataset_id": "dataset-uuid",
  "time_column": "date",
  "target_column": "sales",
  "forecast_periods": 30, // optional, default: 30
  "forecast_method": "prophet" // prophet, lstm, both
}
```

**Example Usage in Claude**:
```
Forecast next 60 days of sales using Prophet on dataset xyz-123
```

**Response**:
```json
{
  "prophet_forecast": {
    "forecast": [{"ds": "2025-01-01", "yhat": 1500}],
    "metrics": {"mape": 5.2}
  },
  "anomalies": {
    "anomaly_count": 15
  }
}
```

### 5. tune_hyperparameters

**Description**: Optimize model parameters

**Parameters**:
```json
{
  "dataset_id": "dataset-uuid",
  "target_column": "sales",
  "model_type": "random_forest", // random_forest, xgboost, lightgbm
  "problem_type": "regression", // regression, classification
  "search_type": "grid" // grid, random
}
```

**Example Usage in Claude**:
```
Tune hyperparameters for Random Forest on dataset xyz-123 targeting 'sales'
```

**Response**:
```json
{
  "best_params": {
    "n_estimators": 100,
    "max_depth": 10
  },
  "best_score": 0.89
}
```

### 6. get_training_metadata

**Description**: Get training history and model performance

**Parameters**: None

**Example Usage in Claude**:
```
Show me training history for all models
```

**Response**:
```json
{
  "metadata": [
    {
      "dataset_name": "Sales Data",
      "training_count": 5,
      "improvement_percentage": 18.67
    }
  ]
}
```

### 7. submit_feedback

**Description**: Submit feedback on predictions

**Parameters**:
```json
{
  "prediction_id": "pred-uuid",
  "is_correct": true,
  "actual_outcome": "1500", // optional
  "comment": "Very accurate" // optional
}
```

**Example Usage in Claude**:
```
Mark prediction pred-123 as correct with actual value 1500
```

**Response**:
```json
{
  "message": "Feedback submitted successfully",
  "feedback_id": "feedback-uuid"
}
```

### 8. get_dataset_profile

**Description**: Get statistical profile of a dataset

**Parameters**:
```json
{
  "dataset_id": "dataset-uuid"
}
```

**Example Usage in Claude**:
```
Profile dataset xyz-123
```

**Response**:
```json
{
  "row_count": 5000,
  "column_count": 10,
  "missing_values": {"col1": 5},
  "data_types": {"sales": "numeric"}
}
```

## 🔍 Testing the MCP Server

### Test with cURL

The MCP server uses stdio (standard input/output) protocol, so direct cURL testing isn't possible. Instead:

### Test with Python Script

```python
import asyncio
import json
from mcp_server import handle_call_tool

async def test():
    # Test upload
    result = await handle_call_tool(
        "upload_dataset",
        {"file_path": "/path/to/test.csv"}
    )
    print(json.dumps(result, indent=2))
    
    # Test list datasets
    result = await handle_call_tool(
        "list_datasets",
        {"limit": 5}
    )
    print(json.dumps(result, indent=2))

asyncio.run(test())
```

### Test with Claude Desktop

Once configured, you can test in Claude:

```
User: Show me all datasets in PROMISE AI

Claude: Let me check the datasets...
[Uses list_datasets tool]

I found 3 datasets:
1. sales_data.csv - 5000 rows, 10 columns
2. customer_data.csv - 3000 rows, 8 columns
3. inventory.csv - 1200 rows, 6 columns
```

## ⚠️ Troubleshooting

### Error: "MCP SDK not installed"

```bash
pip install mcp
```

### Error: "Backend URL not found"

Ensure `.env` file has `REACT_APP_BACKEND_URL` set:

```bash
cd backend
echo "REACT_APP_BACKEND_URL=http://localhost:8001" >> .env
```

### Error: "Connection refused"

Make sure PROMISE AI backend is running:

```bash
cd backend
source venv/bin/activate
python server.py
```

### Claude Desktop Not Loading Server

1. Check config file path:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. Verify absolute paths in config

3. Restart Claude Desktop completely

4. Check Claude Desktop logs:
   - macOS: `~/Library/Logs/Claude/mcp*.log`

## 🔒 Security Considerations

1. **File Access**: MCP server can access any file on the system. Run with appropriate permissions.

2. **Backend Access**: Ensure backend URL is correct and secure.

3. **Authentication**: Currently no authentication. Add in production:
   ```python
   # In mcp_server.py
   headers = {"Authorization": f"Bearer {API_TOKEN}"}
   ```

4. **Network**: Only expose MCP server to trusted AI assistants.

## 📊 Performance

- **Tool Execution Time**: Same as API endpoints (8-15 seconds for analysis)
- **Concurrency**: Single request at a time per MCP connection
- **Timeout**: 300 seconds (5 minutes) default

## 🔗 Integration with Other AI Assistants

The MCP protocol is supported by:
- **Claude Desktop** (Anthropic)
- **VS Code with MCP extension**
- **Custom MCP clients**

### Example: Custom MCP Client

```python
import asyncio
from mcp.client import Client

async def main():
    async with Client() as client:
        # Connect to server
        await client.connect("python", ["mcp_server.py"])
        
        # List tools
        tools = await client.list_tools()
        print(f"Available tools: {[t.name for t in tools]}")
        
        # Call tool
        result = await client.call_tool(
            "list_datasets",
            {"limit": 5}
        )
        print(result)

asyncio.run(main())
```

## 📝 Example Workflows

### Workflow 1: Complete Analysis

```
1. User: Upload /data/sales.csv to PROMISE AI
   [MCP: upload_dataset]

2. User: Run analysis on the sales dataset
   [MCP: run_predictive_analysis]

3. User: Show me the best model
   [MCP reads response and shows Random Forest: R²=0.89]

4. User: Tune the Random Forest parameters
   [MCP: tune_hyperparameters]

5. User: Save these results
   [User manually saves in PROMISE AI UI]
```

### Workflow 2: Time Series Forecasting

```
1. User: List my datasets
   [MCP: list_datasets]

2. User: Forecast next 30 days using the timeseries_data.csv
   [MCP: run_time_series_analysis]

3. User: Were there any anomalies detected?
   [MCP reads response and reports anomalies]
```

## 📦 Deployment

### Production Deployment

```bash
# Run as a system service
sudo cp deploy/mcp-server.service /etc/systemd/system/
sudo systemctl start mcp-server
sudo systemctl enable mcp-server
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY mcp_server.py .
COPY backend/.env ./backend/

CMD ["python", "mcp_server.py"]
```

## 🔗 Related Documentation

- [API Documentation](API_DOCUMENTATION.md) - Backend API reference
- [Setup Guide](SETUP_GUIDE.md) - Installation instructions
- [Database Schema](DATABASE_SCHEMA.md) - MongoDB structure

## 🆘 Support

For MCP-related issues:
1. Check MCP SDK documentation
2. Verify backend is running
3. Check Claude Desktop logs
4. Test with Python script first

---

**MCP Server Version**: 1.0.0
**Protocol**: Model Context Protocol (MCP)
**Last Updated**: 2025-01-03
