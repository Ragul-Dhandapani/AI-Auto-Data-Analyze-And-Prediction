# PROMISE AI - API Documentation

Complete reference for all backend API endpoints.

**Base URL**: `http://localhost:8001/api`

## 📝 Table of Contents

- [Data Source APIs](#data-source-apis)
- [Analysis APIs](#analysis-apis)
- [Training Metadata APIs](#training-metadata-apis)
- [Feedback APIs](#feedback-apis)
- [Error Handling](#error-handling)

## 📊 Data Source APIs

### 1. Upload Dataset

**Endpoint**: `POST /datasource/upload`

**Description**: Upload a CSV/Excel file to the platform

**Request**:
```http
POST /api/datasource/upload
Content-Type: multipart/form-data

file: <binary file data>
```

**Response**:
```json
{
  "id": "uuid-string",
  "name": "dataset.csv",
  "row_count": 1000,
  "column_count": 10,
  "columns": ["col1", "col2"],
  "dtypes": {"col1": "int64", "col2": "float64"},
  "storage_type": "gridfs",
  "message": "Dataset uploaded successfully"
}
```

### 2. List Datasets

**Endpoint**: `GET /datasets`

**Description**: Retrieve list of all uploaded datasets with metadata

**Parameters**:
- `limit` (optional): Maximum number of datasets to return (default: 10)

**Request**:
```http
GET /api/datasets?limit=20
```

**Response**:
```json
{
  "datasets": [
    {
      "id": "uuid-string",
      "name": "sales_data.csv",
      "row_count": 5000,
      "column_count": 15,
      "columns": ["date", "sales", "region"],
      "dtypes": {"sales": "float64"},
      "created_at": "2025-01-01T12:00:00",
      "data_preview": [{"date": "2025-01-01", "sales": 1000}]
    }
  ]
}
```

### 3. Get Dataset by ID

**Endpoint**: `GET /datasets/{dataset_id}`

**Description**: Retrieve specific dataset details

**Request**:
```http
GET /api/datasets/uuid-string
```

**Response**:
```json
{
  "id": "uuid-string",
  "name": "sales_data.csv",
  "row_count": 5000,
  "column_count": 15,
  "columns": ["date", "sales"],
  "dtypes": {"sales": "float64"},
  "data_preview": [{}]
}
```

### 4. Delete Dataset

**Endpoint**: `DELETE /datasets/{dataset_id}`

**Description**: Delete a dataset and all associated analysis data

**Request**:
```http
DELETE /api/datasets/uuid-string
```

**Response**:
```json
{
  "message": "Dataset deleted successfully"
}
```

### 5. Database Connection Test

**Endpoint**: `POST /datasource/test-connection`

**Description**: Test database connection before querying

**Request**:
```json
{
  "db_type": "postgresql",
  "host": "localhost",
  "port": 5432,
  "database": "mydb",
  "username": "user",
  "password": "pass",
  "use_kerberos": false
}
```

**Response**:
```json
{
  "success": true,
  "message": "Connection successful"
}
```

### 6. Execute Custom SQL Query (Preview)

**Endpoint**: `POST /datasource/execute-query-preview`

**Description**: Execute SQL query and return preview (doesn't save)

**Request**:
```json
{
  "db_type": "postgresql",
  "query": "SELECT * FROM sales LIMIT 10",
  "host": "localhost",
  "port": 5432,
  "database": "mydb",
  "username": "user",
  "password": "pass"
}
```

**Response**:
```json
{
  "row_count": 10,
  "column_count": 5,
  "columns": ["id", "name", "value"],
  "data_preview": [{"id": 1, "name": "test"}],
  "message": "Query executed successfully"
}
```

### 7. Save Query Results as Dataset

**Endpoint**: `POST /datasource/save-query-dataset`

**Description**: Execute query and save results as a new dataset

**Request**:
```json
{
  "db_type": "mysql",
  "query": "SELECT * FROM products",
  "dataset_name": "Products Data",
  "host": "localhost",
  "port": 3306,
  "database": "shop",
  "username": "root",
  "password": "password"
}
```

**Response**:
```json
{
  "id": "uuid-string",
  "name": "Products Data",
  "row_count": 1500,
  "column_count": 8,
  "storage_type": "gridfs",
  "message": "Query dataset saved successfully"
}
```

## 🧠 Analysis APIs

### 8. Holistic Analysis

**Endpoint**: `POST /analysis/holistic`

**Description**: Comprehensive ML analysis with data profiling, model training, insights, and visualizations

**Request**:
```json
{
  "dataset_id": "uuid-string",
  "problem_type": "auto",
  "variable_selection": {
    "mode": "manual",
    "targets": [
      {
        "column": "sales",
        "features": ["date", "region", "product"]
      }
    ]
  }
}
```

**Parameters**:
- `problem_type`: "auto", "regression", "classification", "time_series"
- `variable_selection.mode`: "manual", "auto", "ai_suggested", "hybrid"

**Response**:
```json
{
  "profile": {
    "row_count": 5000,
    "column_count": 10,
    "missing_values": {"col1": 5},
    "data_types": {"sales": "numeric"}
  },
  "ml_models": [
    {
      "model_name": "Random Forest",
      "r2_score": 0.85,
      "rmse": 125.5,
      "accuracy": 0.89,
      "f1_score": 0.87,
      "feature_importance": [{"feature": "region", "importance": 0.45}],
      "training_time": 2.5
    }
  ],
  "correlations": {
    "sales": [{"feature": "region", "correlation": 0.78}]
  },
  "auto_charts": [
    {
      "chart_type": "scatter",
      "title": "Sales vs Region",
      "data": {}
    }
  ],
  "ai_insights": [
    {
      "type": "trend",
      "title": "Increasing Sales Pattern",
      "description": "Sales show 15% growth",
      "severity": "info",
      "recommendation": "Focus on high-performing regions"
    }
  ],
  "business_recommendations": [
    {
      "priority": "high",
      "recommendation": "Expand in top 3 regions",
      "expected_impact": "20% revenue increase",
      "implementation_effort": "medium"
    }
  ],
  "explainability": {
    "model_name": "Random Forest",
    "shap_values": []
  },
  "problem_type": "regression",
  "is_sampled": false
}
```

### 9. Time Series Analysis

**Endpoint**: `POST /analysis/time-series`

**Description**: Forecast future values with Prophet/LSTM and detect anomalies

**Request**:
```json
{
  "dataset_id": "uuid-string",
  "time_column": "date",
  "target_column": "sales",
  "forecast_periods": 30,
  "forecast_method": "prophet"
}
```

**Parameters**:
- `forecast_method`: "prophet", "lstm", "both"
- `forecast_periods`: Number of future periods (1-365)

**Response**:
```json
{
  "prophet_forecast": {
    "forecast": [{"ds": "2025-01-01", "yhat": 1500}],
    "metrics": {"mape": 5.2, "rmse": 125.5},
    "trends": {"weekly": {}, "yearly": {}}
  },
  "lstm_forecast": {
    "forecast": [{"date": "2025-01-01", "prediction": 1480}],
    "metrics": {"mape": 5.8, "rmse": 132.1}
  },
  "anomalies": {
    "anomaly_count": 15,
    "anomaly_percentage": 3.2,
    "method": "isolation_forest",
    "anomaly_indices": [45, 67, 89]
  }
}
```

### 10. Hyperparameter Tuning

**Endpoint**: `POST /analysis/hyperparameter-tuning`

**Description**: Optimize model parameters using grid/random search

**Request**:
```json
{
  "dataset_id": "uuid-string",
  "target_column": "sales",
  "model_type": "random_forest",
  "problem_type": "regression",
  "search_type": "grid",
  "param_grid": {
    "n_estimators": [50, 100, 200],
    "max_depth": [5, 10, 20],
    "learning_rate": [0.01, 0.1, 0.2]
  },
  "n_iter": 20
}
```

**Parameters**:
- `model_type`: "random_forest", "xgboost", "lightgbm"
- `search_type`: "grid" (exhaustive), "random" (faster)
- `problem_type`: "regression", "classification"

**Response**:
```json
{
  "best_params": {
    "n_estimators": 100,
    "max_depth": 10,
    "learning_rate": 0.1
  },
  "best_score": 0.89,
  "cv_results": {
    "mean_test_score": [0.85, 0.87, 0.89],
    "n_splits": 5
  }
}
```

### 11. Get Datetime Columns

**Endpoint**: `GET /datetime-columns/{dataset_id}`

**Description**: Detect potential datetime columns in a dataset

**Request**:
```http
GET /api/datetime-columns/uuid-string
```

**Response**:
```json
{
  "datetime_columns": ["order_date", "ship_date", "timestamp"]
}
```

### 12. Save Workspace

**Endpoint**: `POST /analysis/save-state`

**Description**: Save current analysis state as a workspace (optimized with compression)

**Request**:
```json
{
  "dataset_id": "uuid-string",
  "state_name": "Sales Analysis - Q1 2025",
  "analysis_data": {
    "ml_models": [],
    "charts": [],
    "insights": []
  },
  "chat_history": []
}
```

**Response**:
```json
{
  "state_id": "workspace-uuid",
  "message": "Workspace 'Sales Analysis - Q1 2025' saved successfully",
  "storage_type": "gridfs",
  "size_mb": 2.5,
  "optimized": true
}
```

### 13. Load Workspace

**Endpoint**: `GET /analysis/load-state/{state_id}`

**Description**: Load a previously saved workspace

**Request**:
```http
GET /api/analysis/load-state/workspace-uuid
```

**Response**:
```json
{
  "id": "workspace-uuid",
  "dataset_id": "dataset-uuid",
  "state_name": "Sales Analysis - Q1 2025",
  "analysis_data": {},
  "chat_history": [],
  "created_at": "2025-01-01T12:00:00"
}
```

## 📋 Training Metadata APIs

### 14. Get Training Metadata

**Endpoint**: `GET /training/metadata`

**Description**: Retrieve training history and model performance for all datasets

**Request**:
```http
GET /api/training/metadata
```

**Response**:
```json
{
  "metadata": [
    {
      "dataset_id": "uuid-string",
      "dataset_name": "Sales Data",
      "training_count": 5,
      "last_trained": "2025-01-01T12:00:00",
      "initial_score": 0.75,
      "current_score": 0.89,
      "improvement_percentage": 18.67,
      "initial_scores": {
        "Random Forest": 0.75,
        "XGBoost": 0.78
      },
      "current_scores": {
        "Random Forest": 0.89,
        "XGBoost": 0.91
      },
      "workspaces": [
        {
          "workspace_name": "Analysis v1",
          "saved_at": "2025-01-01T12:00:00",
          "workspace_id": "workspace-uuid"
        }
      ]
    }
  ]
}
```

### 15. Download Training Metadata PDF

**Endpoint**: `GET /training/metadata/download-pdf/{dataset_id}`

**Description**: Generate and download PDF report of training metadata

**Request**:
```http
GET /api/training/metadata/download-pdf/uuid-string
```

**Response**: PDF file download

## 👍 Feedback APIs

### 16. Submit Prediction Feedback

**Endpoint**: `POST /feedback/submit`

**Description**: Submit user feedback on model predictions for active learning

**Request**:
```json
{
  "prediction_id": "pred-uuid",
  "is_correct": true,
  "actual_outcome": "1500",
  "comment": "Prediction was very accurate"
}
```

**Response**:
```json
{
  "message": "Feedback submitted successfully",
  "feedback_id": "feedback-uuid"
}
```

### 17. Get Feedback Statistics

**Endpoint**: `GET /feedback/stats/{dataset_id}/{model_name}`

**Description**: Get performance statistics based on user feedback

**Request**:
```http
GET /api/feedback/stats/uuid-string/Random%20Forest
```

**Response**:
```json
{
  "feedback_count": 50,
  "correct_predictions": 42,
  "incorrect_predictions": 8,
  "accuracy": 0.84,
  "feedback_data": [
    {
      "prediction_id": "pred-uuid",
      "is_correct": true,
      "prediction": "1500",
      "actual_outcome": "1480",
      "timestamp": "2025-01-01T12:00:00"
    }
  ]
}
```

### 18. Retrain Model with Feedback

**Endpoint**: `POST /feedback/retrain`

**Description**: Retrain model using accumulated feedback data

**Request**:
```json
{
  "dataset_id": "uuid-string",
  "model_name": "Random Forest",
  "target_column": "sales"
}
```

**Response**:
```json
{
  "message": "Model retrained successfully",
  "feedback_samples": 50,
  "new_score": 0.91,
  "improvement": 0.07
}
```

## ⚠️ Error Handling

### Standard Error Response

All API endpoints return errors in this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request parameters |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Server-side error |
| 502 | Bad Gateway | Backend timeout or unavailable |

### Common Error Examples

**400 Bad Request**:
```json
{
  "detail": "Target column 'sales' not found in dataset"
}
```

**404 Not Found**:
```json
{
  "detail": "Dataset not found"
}
```

**500 Internal Server Error**:
```json
{
  "detail": "Failed to train models: Insufficient data"
}
```

## 🔒 Authentication

Currently, the API does not require authentication. In production, implement:

- JWT tokens
- API keys
- OAuth2

## 📦 Rate Limiting

No rate limiting is currently enforced. Recommended limits for production:

- General endpoints: 100 requests/minute
- Analysis endpoints: 10 requests/minute
- Upload endpoints: 5 requests/minute

## 📊 API Response Times

**Typical Response Times** (with 10MB dataset):

| Endpoint | Average Time | Notes |
|----------|--------------|-------|
| Upload Dataset | 2-5 seconds | Depends on file size |
| List Datasets | <100ms | Cached with indexes |
| Holistic Analysis | 8-15 seconds | 6 models trained |
| Time Series | 5-10 seconds | Prophet + LSTM |
| Hyperparameter Tuning | 15-30 seconds | Grid search |
| Save Workspace | 2-5 seconds | With compression |
| Load Workspace | 1-2 seconds | From GridFS |

## 📝 Notes

1. All timestamps are in ISO 8601 format (UTC)
2. UUIDs are used for all IDs
3. Large datasets (>10MB) are automatically stored in GridFS
4. Workspaces >2MB are compressed with GZIP
5. Analysis results are cached per dataset
6. MongoDB indexes optimize query performance

## 🔗 Related Documentation

- [Setup Guide](SETUP_GUIDE.md)
- [Database Schema](DATABASE_SCHEMA.md)
- [MCP Server](MCP_SERVER.md)

---

**API Version**: 1.0.0
**Last Updated**: 2025-01-03
