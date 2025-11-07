# PROMISE AI - Backend Documentation

## ⚙️ Backend Architecture Overview

PROMISE AI's backend is built with FastAPI (Python), providing a high-performance, async API for data analysis, ML model training, and AI-powered insights.

---

## 📦 Technology Stack

- **Framework**: FastAPI 0.115.5 (Python 3.11+)
- **Server**: Uvicorn 0.32.1 (ASGI)
- **Databases**: Oracle RDS 19c, MongoDB
- **ML Libraries**: scikit-learn, XGBoost, LightGBM, CatBoost, Prophet
- **Deep Learning**: TensorFlow/Keras (LSTM)
- **AI/LLM**: Azure OpenAI (gpt-4o)
- **Data Processing**: pandas, numpy
- **Explainability**: SHAP, LIME

---

## 🏗️ Project Structure

```
backend/
├── app/
│   ├── main.py                          # FastAPI app entry point
│   ├── config.py                        # Configuration management
│   ├── database/
│   │   ├── connections.py               # Database connection management
│   │   ├── mongodb.py                   # MongoDB client
│   │   ├── oracle_schema.sql            # Oracle schema definition
│   │   ├── adapters/
│   │   │   ├── base.py                  # Abstract base adapter
│   │   │   ├── oracle_adapter.py        # Oracle database adapter
│   │   │   ├── mongodb_adapter.py       # MongoDB database adapter
│   │   │   └── factory.py               # Database factory pattern
│   │   └── db_helper.py                 # Helper functions
│   ├── models/
│   │   └── pydantic_models.py           # Request/response models
│   ├── routes/
│   │   ├── analysis.py                  # Analysis endpoints
│   │   ├── datasource.py                # Dataset management
│   │   ├── training.py                  # Training metadata
│   │   ├── config.py                    # Configuration endpoints
│   │   └── models.py                    # Model management
│   └── services/
│       ├── ml_service_enhanced.py       # ML training (35+ models)
│       ├── azure_openai_service.py      # Azure OpenAI integration
│       ├── chat_service.py              # AI chat
│       ├── data_service.py              # Data profiling
│       ├── visualization_service_v2.py  # Chart generation
│       ├── feature_selection_service.py # Feature importance
│       ├── time_series_service.py       # Forecasting
│       ├── nlp_service.py               # NLP/text processing
│       ├── hyperparameter_service.py    # Hyperparameter tuning
│       ├── feedback_service.py          # User feedback
│       ├── relational_service.py        # Multi-table joins
│       ├── analytics_tracking_service.py# Training metadata tracking
│       ├── ai_insights_service.py       # AI insights generation
│       ├── chart_intelligence_service.py# Chart recommendations
│       ├── model_explainability_service.py # SHAP/LIME
│       ├── variable_intelligence_service.py # Variable recommendations
│       ├── llm_chart_intelligence.py    # LLM-powered chart generation
│       └── enhanced_chart_intelligence.py # Enhanced chart insights
├── .env                                 # Environment variables
├── requirements.txt                     # Python dependencies
├── server.py                            # Server startup
├── init_oracle_schema.py                # Oracle schema initialization
└── create_indexes.py                    # Database indexing
```

---

## 🚀 API Endpoints

### 1. **Datasource Management**

**Base Path**: `/api/datasource`

#### Upload CSV File
```http
POST /api/datasource/upload
Content-Type: multipart/form-data

Body:
  file: <CSV file>

Response:
{
  "id": "uuid",
  "name": "dataset.csv",
  "row_count": 1000,
  "column_count": 15,
  "columns": ["col1", "col2", ...],
  "dtypes": {"col1": "int64", "col2": "float64"},
  "preview": [[row1], [row2], ...]
}
```

#### Connect to Database
```http
POST /api/datasource/connect
Content-Type: application/json

Body:
{
  "source_type": "postgresql",  // or mysql, oracle, sqlserver, mongodb
  "host": "localhost",
  "port": 5432,
  "database": "mydb",
  "username": "user",
  "password": "pass",
  "table_name": "customers",
  "use_kerberos": false
}

Response:
{
  "id": "uuid",
  "name": "customers",
  "source": "postgresql",
  "row_count": 5000,
  "column_count": 20
}
```

#### Get Recent Datasets
```http
GET /api/datasource/recent?limit=10

Response:
{
  "datasets": [
    {
      "id": "uuid",
      "name": "sales_data.csv",
      "row_count": 1000,
      "training_count": 5,
      "last_trained_at": "2025-01-15T10:30:00Z",
      "created_at": "2025-01-10T09:00:00Z"
    }
  ]
}
```

#### Get Dataset Details
```http
GET /api/datasource/{dataset_id}

Response:
{
  "id": "uuid",
  "name": "dataset.csv",
  "columns": ["col1", "col2", ...],
  "dtypes": {"col1": "int64"},
  "preview": [[row1], [row2]],
  "statistics": {
    "col1": {"mean": 50.5, "std": 10.2}
  }
}
```

#### Delete Dataset
```http
DELETE /api/datasource/{dataset_id}

Response:
{
  "message": "Dataset deleted successfully"
}
```

---

### 2. **Analysis & ML Training**

**Base Path**: `/api/analysis`

#### Holistic ML Analysis (35+ Models)
```http
POST /api/analysis/holistic
Content-Type: application/json

Body:
{
  "dataset_id": "uuid",
  "target_variables": ["price"],
  "feature_variables": ["sqft", "bedrooms", "age"],
  "problem_type": "regression",  // or "classification", "auto"
  "selected_models": ["random_forest", "xgboost", "linear_regression"],
  "test_size": 0.2
}

Response:
{
  "ml_models": [
    {
      "model_name": "XGBoost",
      "r2_score": 0.92,
      "rmse": 15000,
      "mae": 12000,
      "training_time": 2.5,
      "is_best": true
    },
    {
      "model_name": "Random Forest",
      "r2_score": 0.89,
      "rmse": 18000,
      "mae": 14000,
      "training_time": 3.1,
      "is_best": false
    }
  ],
  "feature_importance": {
    "sqft": 0.65,
    "age": 0.25,
    "bedrooms": 0.10
  },
  "correlation_matrix": {...},
  "ai_summary": "XGBoost performed best with R² of 0.92..."
}
```

#### AI Chat for Insights
```http
POST /api/analysis/chat
Content-Type: application/json

Body:
{
  "dataset_id": "uuid",
  "message": "Show me a scatter plot of price vs sqft",
  "conversation_history": [
    {"role": "user", "content": "previous message"},
    {"role": "assistant", "content": "previous response"}
  ]
}

Response:
{
  "action": "chart",  // or "message"
  "chart_data": {
    "type": "scatter",
    "x": [1000, 1500, 2000],
    "y": [200000, 300000, 400000],
    "title": "Price vs Square Footage"
  },
  "message": "I've generated a scatter plot showing the relationship between price and square footage."
}
```

#### Time Series Forecasting
```http
POST /api/analysis/timeseries
Content-Type: application/json

Body:
{
  "dataset_id": "uuid",
  "date_column": "date",
  "target_column": "sales",
  "forecast_periods": 30,  // days
  "method": "both"  // or "prophet", "lstm"
}

Response:
{
  "prophet_forecast": {
    "forecast": [100, 105, 110, ...],
    "lower_bound": [90, 95, 100, ...],
    "upper_bound": [110, 115, 120, ...],
    "mape": 5.2
  },
  "lstm_forecast": {...},
  "anomalies": {
    "count": 5,
    "percentage": 2.1,
    "indices": [10, 25, 50, 78, 92]
  },
  "trend_components": {
    "trend": [...],
    "seasonality": [...]
  }
}
```

#### Hyperparameter Tuning
```http
POST /api/analysis/hyperparameter-tuning
Content-Type: application/json

Body:
{
  "dataset_id": "uuid",
  "target_variable": "price",
  "feature_variables": ["sqft", "bedrooms"],
  "model_name": "random_forest",
  "param_grid": {
    "n_estimators": [100, 200, 300],
    "max_depth": [10, 20, 30],
    "min_samples_split": [2, 5, 10]
  },
  "search_type": "grid",  // or "random"
  "cv_folds": 5
}

Response:
{
  "best_params": {
    "n_estimators": 200,
    "max_depth": 20,
    "min_samples_split": 5
  },
  "best_score": 0.94,
  "all_results": [
    {"params": {...}, "score": 0.92},
    {"params": {...}, "score": 0.94}
  ],
  "duration_seconds": 45.3
}
```

---

### 3. **Model Management**

**Base Path**: `/api/models`

#### Get Available Models
```http
GET /api/models/available?problem_type=regression

Response:
{
  "models": [
    {
      "key": "linear_regression",
      "name": "Linear Regression",
      "description": "Simple linear regression model",
      "category": "linear"
    },
    {
      "key": "xgboost",
      "name": "XGBoost",
      "description": "Gradient boosting with XGBoost",
      "category": "ensemble"
    }
    // ... 35+ models
  ]
}
```

#### Get AI Model Recommendations
```http
POST /api/models/recommend
Content-Type: application/json

Body:
{
  "dataset_id": "uuid",
  "problem_type": "regression"
}

Response:
{
  "recommended_models": [
    "xgboost",
    "random_forest",
    "gradient_boosting"
  ],
  "reasoning": "Based on dataset size and feature types, ensemble methods are recommended."
}
```

---

### 4. **Training Metadata**

**Base Path**: `/api/training`

#### Get Training History
```http
GET /api/training/metadata?dataset_id=uuid

Response:
{
  "metadata": [
    {
      "id": "uuid",
      "dataset_id": "uuid",
      "dataset_name": "sales_data.csv",
      "problem_type": "regression",
      "target_variable": "price",
      "model_type": "XGBoost",
      "metrics": {
        "r2_score": 0.92,
        "rmse": 15000
      },
      "training_duration": 2.5,
      "created_at": "2025-01-15T10:30:00Z"
    }
  ]
}
```

#### Submit Prediction Feedback
```http
POST /api/training/feedback
Content-Type: application/json

Body:
{
  "prediction_id": "uuid",
  "dataset_id": "uuid",
  "model_name": "XGBoost",
  "is_correct": true,
  "prediction": "250000",
  "actual_outcome": "248000",
  "comment": "Very close prediction"
}

Response:
{
  "message": "Feedback recorded successfully",
  "feedback_id": "uuid"
}
```

---

### 5. **Configuration**

**Base Path**: `/api/config`

#### Switch Database
```http
POST /api/config/switch-db
Content-Type: application/json

Body:
{
  "db_type": "oracle"  // or "mongodb"
}

Response:
{
  "message": "Database switched to oracle",
  "current_db": "oracle"
}
```

#### Get Current Database
```http
GET /api/config/current-db

Response:
{
  "current_db": "oracle"
}
```

---

## 🧩 Core Services

### 1. **ml_service_enhanced.py** - ML Training

**Purpose**: Trains 35+ ML models and returns performance metrics.

**Key Functions**:

```python
async def train_and_evaluate_models(
    dataset_id: str,
    target_variables: List[str],
    feature_variables: List[str],
    problem_type: str,
    selected_models: List[str] = None
) -> dict:
    """
    Train multiple ML models and return results
    
    Args:
        dataset_id: UUID of dataset
        target_variables: List of target columns
        feature_variables: List of feature columns
        problem_type: 'regression', 'classification', or 'auto'
        selected_models: Optional list of specific models to train
    
    Returns:
        {
            'ml_models': [model_results],
            'feature_importance': {...},
            'correlation_matrix': {...}
        }
    """
```

**Supported Models**:

**Regression**:
- Linear Regression
- Ridge Regression
- Lasso Regression
- ElasticNet
- SVR (Support Vector Regression)
- Decision Tree
- Random Forest
- Gradient Boosting
- XGBoost
- LightGBM
- CatBoost
- AdaBoost
- Extra Trees
- KNN Regressor
- Bagging Regressor
- HistGradient Boosting
- Huber Regressor
- RANSAC Regressor

**Classification**:
- Logistic Regression
- SVC (Support Vector Classifier)
- Decision Tree
- Random Forest
- Gradient Boosting
- XGBoost
- LightGBM
- CatBoost
- AdaBoost
- Extra Trees
- KNN Classifier
- Naive Bayes (Gaussian)
- Naive Bayes (Multinomial)
- Naive Bayes (Bernoulli)
- Bagging Classifier
- HistGradient Boosting
- Perceptron

**Key Features**:
- NaN handling (fills with median/mode)
- Train/test split (80/20)
- Model training time tracking
- Best model identification
- Feature importance calculation
- Correlation matrix generation

---

### 2. **azure_openai_service.py** - Azure OpenAI Integration

**Purpose**: Interface with Azure OpenAI for AI insights and recommendations.

**Configuration**:
```python
import os
from openai import AzureOpenAI

client = AzureOpenAI(
    api_key=os.getenv('AZURE_OPENAI_KEY'),
    api_version=os.getenv('AZURE_OPENAI_API_VERSION', '2024-12-01-preview'),
    azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT')
)

DEPLOYMENT_NAME = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-4o')
```

**Key Functions**:
```python
async def generate_insights(
    data_summary: dict,
    ml_results: dict,
    context: str = ""
) -> str:
    """
    Generate AI insights from ML results
    
    Args:
        data_summary: Dataset statistics
        ml_results: ML model results
        context: Additional context
    
    Returns:
        AI-generated insights and recommendations
    """
    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[
            {"role": "system", "content": "You are an AI data analyst..."},
            {"role": "user", "content": f"Analyze: {data_summary}"}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content
```

**Environment Variables Required**:
```env
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=your-api-key
AZURE_OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
```

---

### 3. **chat_service.py** - AI Chat

**Purpose**: Handle chat interactions and route to appropriate services.

**Key Functions**:
```python
async def process_chat_message(
    dataset_id: str,
    message: str,
    conversation_history: List[dict]
) -> dict:
    """
    Process user chat message and generate response
    
    Args:
        dataset_id: UUID of dataset
        message: User message
        conversation_history: Previous chat messages
    
    Returns:
        {
            'action': 'chart' | 'message',
            'chart_data': {...},  // if action=chart
            'message': '...'      // AI response
        }
    """
```

**Chat Actions**:
- **Chart Generation**: Detects chart requests and generates visualizations
- **General Queries**: Answers questions about data and insights
- **Model Explanations**: Explains ML model results
- **Recommendations**: Provides business recommendations

---

### 4. **data_service.py** - Data Profiling

**Purpose**: Profile datasets and generate statistics.

**Key Functions**:
```python
async def profile_dataset(df: pd.DataFrame) -> dict:
    """
    Generate comprehensive dataset profile
    
    Returns:
        {
            'row_count': int,
            'column_count': int,
            'missing_values': {...},
            'duplicates': int,
            'statistics': {...},
            'dtypes': {...},
            'correlations': {...}
        }
    """
```

---

### 5. **time_series_service.py** - Forecasting

**Purpose**: Time series forecasting with Prophet and LSTM.

**Key Functions**:
```python
async def forecast_prophet(
    df: pd.DataFrame,
    date_column: str,
    target_column: str,
    periods: int
) -> dict:
    """
    Forecast using Facebook Prophet
    
    Returns:
        {
            'forecast': [...],
            'lower_bound': [...],
            'upper_bound': [...],
            'mape': float,
            'trend': [...],
            'seasonality': [...]
        }
    """

async def forecast_lstm(
    df: pd.DataFrame,
    target_column: str,
    periods: int
) -> dict:
    """
    Forecast using LSTM neural network
    """
```

**Anomaly Detection**:
```python
async def detect_anomalies(
    df: pd.DataFrame,
    column: str
) -> dict:
    """
    Detect anomalies using Isolation Forest and LOF
    
    Returns:
        {
            'anomaly_count': int,
            'anomaly_percentage': float,
            'anomaly_indices': [int]
        }
    """
```

---

### 6. **hyperparameter_service.py** - Hyperparameter Tuning

**Purpose**: Optimize model hyperparameters using Grid Search or Random Search.

**Key Functions**:
```python
async def tune_hyperparameters(
    X_train: np.ndarray,
    y_train: np.ndarray,
    model_name: str,
    param_grid: dict,
    search_type: str = 'grid',
    cv_folds: int = 5
) -> dict:
    """
    Tune hyperparameters and return best params
    
    Args:
        X_train: Training features
        y_train: Training labels
        model_name: Model to tune
        param_grid: Parameter grid
        search_type: 'grid' or 'random'
        cv_folds: Cross-validation folds
    
    Returns:
        {
            'best_params': {...},
            'best_score': float,
            'all_results': [...]
        }
    """
```

---

### 7. **analytics_tracking_service.py** - Training Metadata

**Purpose**: Track and store ML training metadata for reproducibility.

**Key Functions**:
```python
async def record_training_metadata(
    dataset_id: str,
    problem_type: str,
    target_variable: str,
    model_type: str,
    metrics: dict,
    training_duration: float
) -> str:
    """
    Record training metadata
    
    Returns:
        metadata_id: UUID of metadata record
    """

async def get_training_history(
    dataset_id: str = None
) -> List[dict]:
    """
    Retrieve training history
    
    Args:
        dataset_id: Optional filter by dataset
    
    Returns:
        List of training metadata records
    """
```

---

## 🗄️ Database Architecture

### Database Factory Pattern

**File**: `app/database/adapters/factory.py`

```python
from app.database.adapters.base import BaseAdapter
from app.database.adapters.oracle_adapter import OracleAdapter
from app.database.adapters.mongodb_adapter import MongoDBAdapter
import os

_db_adapter: BaseAdapter = None

async def initialize_database():
    """Initialize database adapter based on DB_TYPE"""
    global _db_adapter
    
    db_type = os.getenv('DB_TYPE', 'mongodb')
    
    if db_type == 'oracle':
        _db_adapter = OracleAdapter()
    else:
        _db_adapter = MongoDBAdapter()
    
    await _db_adapter.initialize()

def get_db() -> BaseAdapter:
    """Get current database adapter"""
    if _db_adapter is None:
        raise RuntimeError("Database not initialized")
    return _db_adapter

async def close_database():
    """Close database connection"""
    if _db_adapter:
        await _db_adapter.close()
```

### Base Adapter Interface

**File**: `app/database/adapters/base.py`

```python
from abc import ABC, abstractmethod

class BaseAdapter(ABC):
    @abstractmethod
    async def initialize(self):
        """Initialize database connection"""
        pass
    
    @abstractmethod
    async def save_dataset(self, dataset: dict) -> str:
        """Save dataset metadata"""
        pass
    
    @abstractmethod
    async def get_dataset(self, dataset_id: str) -> dict:
        """Retrieve dataset by ID"""
        pass
    
    @abstractmethod
    async def list_datasets(self, limit: int) -> List[dict]:
        """List recent datasets"""
        pass
    
    @abstractmethod
    async def delete_dataset(self, dataset_id: str):
        """Delete dataset"""
        pass
    
    @abstractmethod
    async def save_training_metadata(self, metadata: dict) -> str:
        """Save training metadata"""
        pass
```

### Oracle Adapter

**File**: `app/database/adapters/oracle_adapter.py`

**Key Features**:
- Connection pooling (2-10 connections)
- BLOB storage for large datasets
- JSON columns for flexible schema
- Automatic date format handling

```python
import cx_Oracle
import os

class OracleAdapter(BaseAdapter):
    def __init__(self):
        self.pool = None
    
    async def initialize(self):
        """Initialize Oracle connection pool"""
        dsn = os.getenv('ORACLE_DSN')
        user = os.getenv('ORACLE_USER')
        password = os.getenv('ORACLE_PASSWORD')
        
        self.pool = cx_Oracle.SessionPool(
            user=user,
            password=password,
            dsn=dsn,
            min=2,
            max=10,
            increment=1
        )
    
    async def save_dataset(self, dataset: dict) -> str:
        """Save to Oracle datasets table"""
        conn = self.pool.acquire()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT INTO datasets (id, name, row_count, column_count, 
                                 columns_json, dtypes_json, created_at)
            VALUES (:id, :name, :row_count, :column_count, 
                    :columns_json, :dtypes_json, CURRENT_TIMESTAMP)
            """,
            dataset
        )
        conn.commit()
        cursor.close()
        self.pool.release(conn)
        
        return dataset['id']
```

### MongoDB Adapter

**File**: `app/database/adapters/mongodb_adapter.py`

**Key Features**:
- Async MongoDB operations with Motor
- GridFS for large file storage
- Document-based storage

```python
from motor.motor_asyncio import AsyncIOMotorClient
import os

class MongoDBAdapter(BaseAdapter):
    def __init__(self):
        self.client = None
        self.db = None
    
    async def initialize(self):
        """Initialize MongoDB connection"""
        mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
        self.client = AsyncIOMotorClient(mongo_url)
        self.db = self.client.promise_ai
    
    async def save_dataset(self, dataset: dict) -> str:
        """Save to MongoDB datasets collection"""
        result = await self.db.datasets.insert_one(dataset)
        return str(result.inserted_id)
```

---

## 🔧 Configuration

### Environment Variables

**File**: `backend/.env`

```env
# Database Configuration
DB_TYPE=oracle  # or mongodb

# Oracle Configuration
ORACLE_DSN=(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=host.rds.amazonaws.com)(PORT=1521))(CONNECT_DATA=(SID=ORCL)))
ORACLE_USER=admin
ORACLE_PASSWORD=your_password
ORACLE_POOL_MIN=2
ORACLE_POOL_MAX=10

# MongoDB Configuration
MONGO_URL=mongodb://localhost:27017/promise_ai

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=your_api_key
AZURE_OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o

# Backend Configuration
REACT_APP_BACKEND_URL=http://localhost:8001
```

---

## 🚀 Running the Backend

### Development

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Initialize Oracle schema (if using Oracle)
python init_oracle_schema.py

# Start server
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### Production (Supervisor)

```bash
sudo supervisorctl restart backend
```

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

---

## 📊 Logging

```python
import logging

logger = logging.getLogger(__name__)

# Log levels
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")
```

**Log Files**:
- `/var/log/supervisor/backend.out.log` - Standard output
- `/var/log/supervisor/backend.err.log` - Error output

---

## 🐛 Error Handling

```python
from fastapi import HTTPException

@router.post("/endpoint")
async def endpoint():
    try:
        # Business logic
        result = await some_operation()
        return result
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

---

## 📚 Additional Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com
- **scikit-learn**: https://scikit-learn.org
- **XGBoost**: https://xgboost.readthedocs.io
- **Prophet**: https://facebook.github.io/prophet
- **Azure OpenAI**: https://learn.microsoft.com/en-us/azure/ai-services/openai
- **cx_Oracle**: https://cx-oracle.readthedocs.io
- **Motor (MongoDB)**: https://motor.readthedocs.io

---

For frontend documentation, see `FRONTEND.md`  
For database schema, see `DATABASE.md`
