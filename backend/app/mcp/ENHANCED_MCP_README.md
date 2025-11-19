# Enhanced Intelligent Prediction MCP

## 🎯 What's Different from Basic MCP?

### Basic MCP (prediction_mcp.py)
- ✅ Load data and make predictions with **pre-trained** models
- ✅ Batch predictions on GB-scale data
- ❌ Cannot train new models
- ❌ No forecasting or insights

### Enhanced MCP (intelligent_prediction_mcp.py)
- ✅ **User prompt**: Describe what you want to predict in natural language
- ✅ **Model selection**: Choose which models to train (Random Forest, XGBoost, etc.)
- ✅ **Auto-training**: Trains models on your data automatically
- ✅ **Predictions**: Makes predictions after training
- ✅ **Forecasting**: Generates trend analysis and forecasts
- ✅ **AI Insights**: Provides domain-adaptive insights
- ✅ **Feature importance**: Shows what drives predictions
- ✅ **Model comparison**: Compares multiple models and picks best

---

## 🚀 Quick Start

### Example 1: Customer Churn Prediction

**Request**:
```python
from app.mcp.intelligent_prediction_mcp import IntelligentPredictionMCP

mcp = IntelligentPredictionMCP()

result = mcp.train_and_predict(
    data_source={
        'type': 'file',
        'path': '/data/customers.csv'
    },
    user_prompt="I want to predict which customers will churn based on their purchase behavior and support tickets. Help me identify high-risk customers so we can run retention campaigns.",
    target_column='churned',
    feature_columns=['purchase_frequency', 'support_tickets', 'account_age_days', 'days_since_last_purchase'],
    models_to_train=['random_forest', 'xgboost', 'logistic_regression'],
    include_forecasting=True,
    include_insights=True
)

print(result)
```

**Response**:
```json
{
    "training_summary": {
        "rows": 500000,
        "problem_type": "classification",
        "domain": "ecommerce",
        "user_prompt": "I want to predict which customers will churn..."
    },
    "predictions": [0, 1, 0, 0, 1, ...],
    "model_comparison": [
        {
            "model_name": "random_forest",
            "score": 0.9245,
            "metrics": {
                "accuracy": 0.9245
            },
            "training_time": 12.3
        },
        {
            "model_name": "xgboost",
            "score": 0.9187,
            "metrics": {
                "accuracy": 0.9187
            },
            "training_time": 8.7
        },
        {
            "model_name": "logistic_regression",
            "score": 0.8523,
            "metrics": {
                "accuracy": 0.8523
            },
            "training_time": 2.1
        }
    ],
    "best_model": {
        "model_name": "random_forest",
        "score": 0.9245,
        "metrics": {
            "accuracy": 0.9245
        }
    },
    "feature_importance": {
        "days_since_last_purchase": 0.423,
        "purchase_frequency": 0.312,
        "support_tickets": 0.187,
        "account_age_days": 0.078
    },
    "forecasting": {
        "summary": "Trend increasing by 12.3%",
        "statistics": {
            "predicted_mean": 0.287,
            "predicted_median": 0.0,
            "trend_direction": "increasing",
            "trend_magnitude_percent": 12.3
        },
        "alerts": [
            {
                "level": "warning",
                "message": "Significant increasing trend detected"
            }
        ]
    },
    "insights": {
        "summary": "Best model: random_forest (score: 0.9245)",
        "key_findings": [
            "Top features: days_since_last_purchase (42.3%), purchase_frequency (31.2%), support_tickets (18.7%)",
            "Prediction quality: High",
            "Trend: Trend increasing by 12.3%"
        ],
        "domain": "ecommerce",
        "user_prompt": "I want to predict which customers will churn..."
    },
    "execution_time": 45.8
}
```

---

### Example 2: Server Latency Prediction from Oracle

**Request**:
```python
result = mcp.train_and_predict(
    data_source={
        'type': 'oracle',
        'config': {
            'host': 'promise-ai-test-oracle.cgxf9inhpsec.us-east-1.rds.amazonaws.com',
            'port': '1521',
            'service_name': 'ORCL',
            'username': 'testuser',
            'password': 'DbPasswordTest'
        },
        'table': 'server_metrics'
    },
    user_prompt="Predict server latency to prevent SLO breaches. Focus on resource utilization patterns that lead to performance degradation.",
    target_column='latency_ms',
    feature_columns=['memory_usage_mb', 'cpu_utilization', 'disk_io_ops', 'network_bandwidth_mbps'],
    models_to_train=['random_forest', 'xgboost'],  # User chooses specific models
    include_forecasting=True,
    include_insights=True
)
```

**Response**:
```json
{
    "training_summary": {
        "rows": 2000000,
        "problem_type": "regression",
        "domain": "it_infrastructure",
        "user_prompt": "Predict server latency to prevent SLO breaches..."
    },
    "predictions": [125.3, 142.8, 98.7, 156.2, ...],
    "model_comparison": [
        {
            "model_name": "xgboost",
            "score": 0.8934,
            "metrics": {
                "r2_score": 0.8934,
                "rmse": 15.7,
                "mae": 12.3
            },
            "training_time": 45.2
        },
        {
            "model_name": "random_forest",
            "score": 0.8721,
            "metrics": {
                "r2_score": 0.8721,
                "rmse": 17.2,
                "mae": 13.8
            },
            "training_time": 32.1
        }
    ],
    "best_model": {
        "model_name": "xgboost",
        "score": 0.8934
    },
    "feature_importance": {
        "memory_usage_mb": 0.563,
        "cpu_utilization": 0.287,
        "disk_io_ops": 0.098,
        "network_bandwidth_mbps": 0.052
    },
    "forecasting": {
        "summary": "Trend increasing by 23.7%",
        "statistics": {
            "predicted_mean": 142.8,
            "predicted_median": 138.5,
            "trend_direction": "increasing",
            "trend_magnitude_percent": 23.7
        },
        "alerts": [
            {
                "level": "warning",
                "message": "Significant increasing trend detected"
            }
        ]
    },
    "insights": {
        "summary": "Best model: xgboost (score: 0.8934)",
        "key_findings": [
            "Top features: memory_usage_mb (56.3%), cpu_utilization (28.7%), disk_io_ops (9.8%)",
            "Prediction quality: High",
            "Trend: Trend increasing by 23.7%"
        ],
        "domain": "it_infrastructure",
        "user_prompt": "Predict server latency to prevent SLO breaches..."
    },
    "execution_time": 128.5
}
```

---

## 📊 Parameters Explained

### `data_source` (Dict)
Where to load data from:

**File**:
```python
{
    'type': 'file',
    'path': '/path/to/data.csv'  # CSV, Excel, Parquet, JSON
}
```

**Oracle**:
```python
{
    'type': 'oracle',
    'config': {
        'host': 'your-host.com',
        'port': '1521',
        'service_name': 'ORCL',
        'username': 'user',
        'password': 'pass'
    },
    'table': 'table_name'  # or use 'query': 'SELECT * FROM ...'
}
```

### `user_prompt` (String)
Natural language description of what you want to predict.

**Good Examples**:
- "I want to predict customer churn to run retention campaigns"
- "Predict server latency to prevent SLO breaches and identify bottlenecks"
- "Forecast sales revenue to optimize inventory and staffing"

**Bad Examples**:
- "Predict" (too vague)
- "Machine learning" (not specific)

### `target_column` (String)
The column you want to predict (e.g., 'churned', 'latency_ms', 'revenue')

### `feature_columns` (List[String])
Columns to use as features (e.g., ['memory_mb', 'cpu_util', 'disk_io'])

### `models_to_train` (List[String], optional)
Which models to train. Default: trains Random Forest and XGBoost (if available).

**Available Models**:
- Regression: `['linear_regression', 'random_forest', 'decision_tree', 'xgboost']`
- Classification: `['logistic_regression', 'random_forest', 'decision_tree', 'xgboost']`

**Example**:
```python
models_to_train=['random_forest', 'xgboost']  # Train only these 2
```

### `problem_type` (String, optional)
`'regression'` or `'classification'`. Auto-detected if not specified.

### `include_forecasting` (Boolean, default=True)
Generate trend analysis and forecasts.

### `include_insights` (Boolean, default=True)
Generate AI-powered insights about the predictions.

### `test_size` (Float, default=0.2)
Fraction of data to use for testing (0.2 = 20%).

---

## 🎯 Comparison: Basic vs Enhanced MCP

| Feature | Basic MCP | Enhanced MCP |
|---------|-----------|--------------|
| **Data Loading** | ✅ Files + 4 databases | ✅ Files + 4 databases |
| **Multi-threading** | ✅ Yes | ❌ No (trains sequentially) |
| **Pre-trained Models** | ✅ Yes | ✅ Yes (after training) |
| **Train New Models** | ❌ No | ✅ **YES** |
| **User Prompt** | ❌ No | ✅ **YES** |
| **Model Selection** | ❌ Fixed 5 models | ✅ **User chooses** |
| **Predictions** | ✅ Yes | ✅ Yes |
| **Forecasting** | ❌ No | ✅ **YES** |
| **AI Insights** | ❌ No | ✅ **YES** |
| **Feature Importance** | ❌ No | ✅ **YES** |
| **Model Comparison** | ❌ No | ✅ **YES** |
| **Best Use Case** | Batch predictions with existing models | Explore + Train + Predict in one go |

---

## 💡 When to Use Which?

### Use Basic MCP when:
- ✅ You already have a trained model
- ✅ You need to make predictions on GB-scale data fast
- ✅ You don't need training, just inference
- ✅ Speed is critical (multi-threaded)

### Use Enhanced MCP when:
- ✅ You want to explore different models
- ✅ You need training + prediction + insights in one call
- ✅ You want to understand WHY predictions are made
- ✅ You need forecasting and trend analysis
- ✅ You want domain-specific recommendations

---

## 🔧 Complete Workflow Example

```python
from app.mcp.intelligent_prediction_mcp import IntelligentPredictionMCP

# Initialize
mcp = IntelligentPredictionMCP()

# Train and predict
result = mcp.train_and_predict(
    data_source={'type': 'file', 'path': '/data/sales.csv'},
    user_prompt="Predict monthly sales to optimize inventory levels and prevent stockouts",
    target_column='monthly_sales',
    feature_columns=['historical_sales', 'season', 'promotions', 'competitor_price'],
    models_to_train=['random_forest', 'xgboost', 'linear_regression'],
    include_forecasting=True,
    include_insights=True
)

# Extract results
best_model = result['best_model']['model_name']
score = result['best_model']['score']
predictions = result['predictions']
top_feature = list(result['feature_importance'].keys())[0]
trend = result['forecasting']['statistics']['trend_direction']
insight = result['insights']['summary']

print(f"🏆 Best Model: {best_model} (R² = {score:.4f})")
print(f"📊 Top Feature: {top_feature}")
print(f"📈 Trend: {trend}")
print(f"💡 Insight: {insight}")

# Use predictions
high_sales_months = [i for i, p in enumerate(predictions) if p > 10000]
print(f"⚠️  {len(high_sales_months)} months with sales > $10K predicted")
```

**Output**:
```
🏆 Best Model: xgboost (R² = 0.8756)
📊 Top Feature: historical_sales
📈 Trend: increasing
💡 Insight: Best model: xgboost (score: 0.8756)
⚠️  15 months with sales > $10K predicted
```

---

## 🚀 Next Steps

1. **Try the examples** above with your data
2. **Experiment with different models** using `models_to_train` parameter
3. **Refine your prompt** to get better domain-specific insights
4. **Compare with Basic MCP** for batch predictions on trained models

For Basic MCP (batch predictions): See `/app/backend/app/mcp/README.md`
For Full API docs: See `/app/MCP_DOCUMENTATION.md`
