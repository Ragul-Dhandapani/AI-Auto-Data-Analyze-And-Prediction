# Prediction MCP Tool - Quick Start Guide

## 📍 Model Path Explanation

### Where Does `model_path` Come From?

When you train models in PROMISE AI, the system saves the trained models to disk. The path follows this pattern:

```
/app/backend/models/{dataset_id}/{model_name}.pkl
```

**Example**:
- Dataset ID: `5621a093-501c-45c6-b7d3-ea5f0ea33e43`
- Best Model: `Random Forest`
- Model Path: `/app/backend/models/5621a093-501c-45c6-b7d3-ea5f0ea33e43/random_forest.pkl`

### How to Get Model Path

**Option 1: From Analysis Results**
```python
# After running analysis, the response includes model info
analysis_result = {
    "ml_models": [
        {
            "model_name": "Random Forest",
            "model_path": "/app/backend/models/{dataset_id}/random_forest.pkl",
            "r2_score": 0.89
        }
    ]
}
```

**Option 2: List Available Models**
```bash
# List all trained models for a dataset
ls /app/backend/models/{dataset_id}/
```

**Option 3: Use Best Model Automatically**
```python
# The MCP tool can auto-detect the best model
from app.mcp.prediction_mcp import PredictionMCP

mcp = PredictionMCP()
best_model_path = mcp.get_best_model_path(dataset_id="your-dataset-id")
```

---

## 🚀 Quick Start Examples

### Example 1: Predict from CSV File

**Request**:
```python
from app.mcp.prediction_mcp import PredictionMCP

mcp = PredictionMCP()

result = mcp.predict_from_file(
    file_path="/app/backend/uploads/new_data.csv",
    model_path="/app/backend/models/5621a093-501c-45c6-b7d3-ea5f0ea33e43/random_forest.pkl",
    num_threads=8,
    output_path="/app/backend/predictions/output.csv"
)

print(result)
```

**Response**:
```json
{
    "predictions": [125.3, 142.8, 98.7, 156.2, 110.5],
    "confidence_scores": [0.89, 0.92, 0.85, 0.88, 0.91],
    "processing_time_seconds": 45.3,
    "rows_processed": 500000,
    "throughput_rows_per_second": 11037,
    "model_features": ["memory_usage_mb", "cpu_utilization"],
    "timestamp": "2025-11-18T12:30:00"
}
```

---

### Example 2: Predict from Oracle Database

**Request**:
```python
from app.mcp.prediction_mcp import PredictionMCP

mcp = PredictionMCP()

result = mcp.predict_from_database(
    db_type="oracle",
    connection_config={
        'host': 'promise-ai-test-oracle.cgxf9inhpsec.us-east-1.rds.amazonaws.com',
        'port': '1521',
        'service_name': 'ORCL',
        'username': 'testuser',
        'password': 'DbPasswordTest'
    },
    table_name="prediction_data",
    model_path="/app/backend/models/5621a093-501c-45c6-b7d3-ea5f0ea33e43/xgboost.pkl",
    batch_size=100000
)

print(result)
```

**Response**:
```json
{
    "predictions": [125.3, 142.8, 98.7, ...],
    "confidence_scores": [0.89, 0.92, 0.85, ...],
    "processing_time_seconds": 320.5,
    "rows_processed": 2000000,
    "batches_processed": 20,
    "throughput_rows_per_second": 6241,
    "model_features": ["memory_usage_mb", "cpu_utilization"],
    "timestamp": "2025-11-18T12:35:00"
}
```

---

### Example 3: Predict from PostgreSQL

**Request**:
```python
result = mcp.predict_from_database(
    db_type="postgresql",
    connection_config={
        'host': 'localhost',
        'port': '5432',
        'database': 'analytics',
        'username': 'postgres',
        'password': 'password'
    },
    query="SELECT * FROM customers WHERE last_purchase_date > '2024-01-01'",
    model_path="/app/backend/models/{dataset_id}/linear_regression.pkl",
    batch_size=50000
)
```

**Response**:
```json
{
    "predictions": [0.87, 0.23, 0.91, ...],
    "confidence_scores": [0.94, 0.78, 0.96, ...],
    "processing_time_seconds": 180.2,
    "rows_processed": 1500000,
    "batches_processed": 30,
    "throughput_rows_per_second": 8321,
    "model_features": ["purchase_frequency", "account_age_days", "support_tickets"],
    "timestamp": "2025-11-18T12:40:00"
}
```

---

### Example 4: Predict from MongoDB

**Request**:
```python
result = mcp.predict_from_database(
    db_type="mongodb",
    connection_config={
        'connection_string': 'mongodb://localhost:27017',
        'database': 'ecommerce'
    },
    table_name="user_sessions",
    model_path="/app/backend/models/{dataset_id}/lstm_neural_network.pkl",
    batch_size=50000
)
```

**Response**:
```json
{
    "predictions": [1, 0, 1, 0, 1, ...],
    "confidence_scores": [0.88, 0.92, 0.85, 0.79, 0.94, ...],
    "processing_time_seconds": 420.8,
    "rows_processed": 3000000,
    "batches_processed": 60,
    "throughput_rows_per_second": 7129,
    "model_features": ["session_duration", "pages_viewed", "cart_items"],
    "timestamp": "2025-11-18T12:45:00"
}
```

---

### Example 5: Predict from MySQL

**Request**:
```python
result = mcp.predict_from_database(
    db_type="mysql",
    connection_config={
        'host': 'localhost',
        'port': '3306',
        'database': 'sales',
        'username': 'root',
        'password': 'password'
    },
    table_name="transactions",
    model_path="/app/backend/models/{dataset_id}/decision_tree.pkl",
    batch_size=100000
)
```

**Response**:
```json
{
    "predictions": [245.67, 189.34, 567.89, ...],
    "confidence_scores": null,
    "processing_time_seconds": 215.7,
    "rows_processed": 1200000,
    "batches_processed": 12,
    "throughput_rows_per_second": 5563,
    "model_features": ["product_category", "customer_segment", "season"],
    "timestamp": "2025-11-18T12:50:00"
}
```

---

## 🔧 How to Call the MCP Tool

### Method 1: Direct Python Import

```python
# In your Python script or Jupyter notebook
from app.mcp.prediction_mcp import PredictionMCP

mcp = PredictionMCP()
result = mcp.predict_from_file(...)
```

### Method 2: REST API Endpoint (Coming Soon)

```bash
curl -X POST https://model-wizard-2.preview.emergentagent.com/api/mcp/predict \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "file",
    "file_path": "/uploads/data.csv",
    "model_path": "/models/{dataset_id}/random_forest.pkl"
  }'
```

### Method 3: Command Line Interface

```bash
cd /app/backend
python -m app.mcp.prediction_mcp \
  --file "/uploads/data.csv" \
  --model "/models/{dataset_id}/random_forest.pkl" \
  --output "/predictions/results.csv"
```

---

## 📊 Complete Workflow Example

### Step 1: Train Models in PROMISE AI

```
1. Upload dataset (CSV, Excel, or connect to database)
2. Select target variable: "latency_ms"
3. Select features: ["memory_usage_mb", "cpu_utilization"]
4. Click "Train Models"
5. Wait for analysis (5-30 minutes)
6. Review results → Best Model: Random Forest (R² = 0.89)
7. Note the model path: /app/backend/models/{dataset_id}/random_forest.pkl
```

### Step 2: Use MCP for Batch Predictions

```python
from app.mcp.prediction_mcp import PredictionMCP

# Initialize MCP
mcp = PredictionMCP()

# Scenario: You have 10GB of new data in Oracle
result = mcp.predict_from_database(
    db_type="oracle",
    connection_config={
        'host': 'your-oracle-host.rds.amazonaws.com',
        'port': '1521',
        'service_name': 'ORCL',
        'username': 'testuser',
        'password': 'password'
    },
    table_name="new_server_metrics",
    model_path="/app/backend/models/{dataset_id}/random_forest.pkl",
    batch_size=100000
)

# Results
print(f"✅ Predicted latency for {result['rows_processed']:,} servers")
print(f"⏱️  Processing time: {result['processing_time_seconds']/60:.1f} minutes")
print(f"⚠️  High latency servers: {sum(1 for p in result['predictions'] if p > 150):,}")

# Example output:
# ✅ Predicted latency for 50,000,000 servers
# ⏱️  Processing time: 35.2 minutes
# ⚠️  High latency servers: 3,245,678
```

### Step 3: Take Action

```python
# Filter high-risk predictions
high_risk_indices = [i for i, p in enumerate(result['predictions']) if p > 150]

# Export for investigation
with open('/output/high_risk_servers.txt', 'w') as f:
    for idx in high_risk_indices:
        f.write(f"Server {idx}: Predicted latency {result['predictions'][idx]:.1f}ms\n")

print(f"✅ Exported {len(high_risk_indices):,} high-risk servers for review")
```

---

## 🎯 Common Use Cases

### Use Case 1: Daily Batch Scoring

```python
# Run this script daily via cron
import schedule
import time

def daily_prediction():
    mcp = PredictionMCP()
    result = mcp.predict_from_database(
        db_type="oracle",
        connection_config=oracle_config,
        query="SELECT * FROM customers WHERE last_scored_date < SYSDATE - 1",
        model_path="/app/backend/models/{dataset_id}/churn_predictor.pkl"
    )
    print(f"✅ Scored {result['rows_processed']:,} customers")

schedule.every().day.at("02:00").do(daily_prediction)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### Use Case 2: Real-Time File Processing

```python
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class PredictionHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.endswith('.csv'):
            mcp = PredictionMCP()
            result = mcp.predict_from_file(
                file_path=event.src_path,
                model_path="/app/backend/models/{dataset_id}/model.pkl",
                output_path=event.src_path.replace('.csv', '_predictions.csv')
            )
            print(f"✅ Processed {event.src_path}")

# Monitor /uploads directory
observer = Observer()
observer.schedule(PredictionHandler(), path='/app/backend/uploads', recursive=False)
observer.start()
```

### Use Case 3: Multi-Database Aggregation

```python
# Combine predictions from multiple data sources
results = []

# Source 1: Oracle production database
result1 = mcp.predict_from_database(
    db_type="oracle",
    connection_config=oracle_config,
    table_name="prod_data",
    model_path="/app/backend/models/{dataset_id}/model.pkl"
)
results.extend(result1['predictions'])

# Source 2: PostgreSQL analytics database
result2 = mcp.predict_from_database(
    db_type="postgresql",
    connection_config=postgres_config,
    table_name="analytics_data",
    model_path="/app/backend/models/{dataset_id}/model.pkl"
)
results.extend(result2['predictions'])

# Source 3: CSV export from third-party system
result3 = mcp.predict_from_file(
    file_path="/imports/external_data.csv",
    model_path="/app/backend/models/{dataset_id}/model.pkl"
)
results.extend(result3['predictions'])

print(f"✅ Total predictions: {len(results):,}")
```

---

## 🔍 Troubleshooting

### Issue 1: Model Not Found

**Error**: `FileNotFoundError: No such file or directory: '/app/backend/models/...'`

**Solution**:
```python
import os

# Check if model exists
model_path = "/app/backend/models/{dataset_id}/random_forest.pkl"
if not os.path.exists(model_path):
    print(f"❌ Model not found at {model_path}")
    print("Available models:")
    for model_file in os.listdir(os.path.dirname(model_path)):
        print(f"  - {model_file}")
```

### Issue 2: Connection Failed

**Error**: `cx_Oracle.DatabaseError: ORA-12545: Connect failed`

**Solution**:
```python
# Test connection first
import cx_Oracle

try:
    dsn = cx_Oracle.makedsn('host', '1521', service_name='ORCL')
    conn = cx_Oracle.connect(user='testuser', password='password', dsn=dsn)
    print("✅ Connection successful")
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

### Issue 3: Memory Error

**Error**: `MemoryError: Unable to allocate array`

**Solution**:
```python
# Reduce chunk size
mcp = PredictionMCP(chunk_size=50000)  # Instead of default 100K
```

---

## 📚 Additional Resources

- **Full API Documentation**: `/app/MCP_DOCUMENTATION.md`
- **Performance Guide**: `/app/SCALABILITY_GUIDE.md`
- **Application Overview**: `/app/APPLICATION_PURPOSE.md`
- **Source Code**: `/app/backend/app/mcp/prediction_mcp.py`

---

## 🚀 Next Steps

1. **Train a model** in PROMISE AI web interface
2. **Note the model path** from analysis results
3. **Prepare your data** (file or database)
4. **Run predictions** using examples above
5. **Deploy in production** with scheduling/monitoring

Need help? Check the documentation files or examine the example code!
