# Complete AI Prompt for PROMISE AI Platform Recreation

This document serves as a comprehensive prompt for an AI to recreate the entire PROMISE AI Platform - a full-stack web application for AI-powered data analysis and predictive analytics with dual-database support.

---

## PROJECT OVERVIEW

**Project Name**: PROMISE AI Platform  
**Version**: 2.0.0  
**Purpose**: AI-powered predictive analytics platform that enables users to upload datasets, perform comprehensive data analysis, train machine learning models, generate intelligent visualizations, and interact with an AI chat assistant.

**Key Features**:
- Multi-database support (MongoDB and Oracle) with seamless switching
- File upload (CSV, Excel) and direct database connections
- Comprehensive data profiling and cleaning
- 35+ machine learning models (regression and classification)
- 28+ intelligent chart types across 8 categories
- AI-powered chat assistant with Azure OpenAI integration
- Workspace save/load functionality
- Training metadata management
- Model explainability (SHAP values, feature importance)
- Auto feature engineering and hyperparameter tuning

---

## ARCHITECTURE OVERVIEW

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND LAYER                            │
│              React 19 + Vite + Tailwind CSS                  │
│  - HomePage, DashboardPage, TrainingMetadataPage            │
│  - DataSourceSelector, DataProfiler, PredictiveAnalysis    │
│  - VisualizationPanel, EnhancedChatAssistant                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    API Gateway (Axios)
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND LAYER                             │
│              FastAPI + Python 3.11                           │
│  - Routes: datasource, analysis, training, config           │
│  - Services: ML, Visualization, Chat, Data Processing       │
└─────────────────────────────────────────────────────────────┘
                            ↓
        ┌───────────────────┴───────────────────┐
        ↓                                       ↓
┌───────────────┐                      ┌───────────────┐
│   MongoDB     │                      │    Oracle    │
│   Atlas       │                      │    RDS 19c   │
└───────────────┘                      └───────────────┘
```

### Data Flow

1. **Data Upload**: User uploads file → Backend parses → Stores in database (direct or BLOB)
2. **Analysis**: User selects variables → Backend trains 35+ models → Returns results
3. **Visualization**: User clicks "Generate Charts" → Backend analyzes data → Generates 28+ charts → Returns with AI insights
4. **Chat**: User sends message → Azure OpenAI processes → Returns response + optional chart/action

---

## TECHNOLOGY STACK

### Frontend
- **Framework**: React 19.0.0 with Vite
- **UI Library**: Tailwind CSS 3.4.17 + shadcn/ui (Radix UI components)
- **State Management**: React Context + useState/useRef
- **Routing**: React Router DOM 7.5.1
- **Data Visualization**: Plotly.js 3.2.0 + react-plotly.js 2.6.0
- **HTTP Client**: Axios 1.8.4
- **Forms**: React Hook Form 7.56.2 + Zod 3.24.4
- **Notifications**: Sonner 2.0.3
- **Build Tool**: CRACO 5.9.0 (Create React App Configuration Override)

### Backend
- **Framework**: FastAPI 0.110.1
- **Language**: Python 3.11+
- **ASGI Server**: Uvicorn 0.38.0
- **ML Libraries**:
  - scikit-learn 1.3.2 (35+ models)
  - XGBoost 3.1.1
  - LightGBM 4.6.0
  - SHAP 0.49.1 (model explainability)
  - Prophet 1.2.1 (time series)
- **Data Processing**:
  - pandas 2.3.3
  - numpy 1.26.4
  - scipy 1.11.4
- **Visualization**: plotly 6.3.1
- **AI Integration**: 
  - openai 1.99.9 (Azure OpenAI SDK)
- **Database Drivers**:
  - motor 3.3.1 (MongoDB async)
  - pymongo 4.5.0 (MongoDB sync)
  - cx_Oracle 8.3.0 (Oracle)
  - psycopg2-binary 2.9.11 (PostgreSQL)
  - PyMySQL 1.1.1 (MySQL)
- **Utilities**:
  - python-dotenv 1.2.1
  - pydantic 2.12.3
  - python-multipart 0.0.20

### Databases
- **Primary**: Oracle RDS 19c (AWS)
- **Alternative**: MongoDB Atlas
- **BLOB Storage**: GridFS (MongoDB) / BLOB (Oracle)

### Deployment
- **Containerization**: Docker
- **Orchestration**: Kubernetes (optional)
- **Reverse Proxy**: Nginx
- **Process Manager**: Supervisor

---

## DATABASE SCHEMAS

### MongoDB Schema

#### Collection: `datasets`
```javascript
{
  "_id": ObjectId("..."),
  "id": "uuid-string",  // Primary key
  "name": "dataset.csv",
  "row_count": 10000,
  "column_count": 12,
  "columns": ["col1", "col2", ...],
  "dtypes": {"col1": "float64", "col2": "object"},
  "data_preview": [{...}, {...}],  // First 1000 rows
  "storage_type": "blob" | "direct",
  "gridfs_file_id": ObjectId("..."),  // If storage_type=blob
  "data": [...],  // If storage_type=direct (<5MB)
  "source_type": "file_upload" | "oracle" | "postgresql" | "mysql" | "mongodb",
  "source_table": "table_name",
  "source_config": {...},
  "created_at": ISODate("..."),
  "updated_at": ISODate("..."),
  "storage_format": "csv"
}
```

**Indexes**:
- `{ "id": 1 }` (unique)
- `{ "name": 1 }`
- `{ "created_at": -1 }`

#### Collection: `training_metadata`
```javascript
{
  "_id": ObjectId("..."),
  "id": "uuid-string",
  "dataset_id": "uuid-string",
  "workspace_name": "workspace_name",
  "model_name": "Random Forest",
  "model_type": "regression" | "classification",
  "problem_type": "regression" | "classification",
  "target_variable": "target_col",
  "features": ["feat1", "feat2", ...],
  "metrics": {
    "r2_score": 0.8567,
    "mse": 123.45,
    "rmse": 11.11,
    "mae": 8.92,
    "accuracy": 0.95,  // For classification
    "f1_score": 0.92
  },
  "hyperparameters": {...},
  "feature_importance": {...},
  "training_time": 12.5,
  "is_best": true,
  "created_at": ISODate("..."),
  "analysis_type": "holistic",
  "feedback": {
    "rating": 5,
    "comments": "Excellent model"
  }
}
```

**Indexes**:
- `{ "id": 1 }` (unique)
- `{ "dataset_id": 1 }`
- `{ "workspace_name": 1 }`
- `{ "dataset_id": 1, "workspace_name": 1 }`
- `{ "created_at": -1 }`

#### Collection: `workspace_states`
```javascript
{
  "_id": ObjectId("..."),
  "id": "uuid-string",
  "workspace_name": "workspace_name",
  "dataset_id": "uuid-string",
  "predictive_analysis": {...},
  "visualization": {...},
  "variable_selection": {...},
  "large_data_blob_id": ObjectId("..."),  // If >5MB
  "created_at": ISODate("..."),
  "updated_at": ISODate("...")
}
```

**Indexes**:
- `{ "workspace_name": 1, "dataset_id": 1 }` (unique)
- `{ "dataset_id": 1 }`

#### GridFS Collections: `fs.files` & `fs.chunks`
For storing large datasets (>5MB) and large workspace states.

### Oracle Schema

#### Table: `DATASETS`
```sql
CREATE TABLE DATASETS (
    id VARCHAR2(255) PRIMARY KEY,
    name VARCHAR2(500) NOT NULL,
    row_count NUMBER DEFAULT 0,
    column_count NUMBER DEFAULT 0,
    columns CLOB CHECK (columns IS JSON),
    dtypes CLOB CHECK (dtypes IS JSON),
    data_preview CLOB CHECK (data_preview IS JSON),
    storage_type VARCHAR2(50) DEFAULT 'direct',
    gridfs_file_id VARCHAR2(255),
    source_type VARCHAR2(100),
    source_table VARCHAR2(255),
    source_config CLOB CHECK (source_config IS JSON),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    storage_format VARCHAR2(50)
);

CREATE INDEX idx_datasets_name ON DATASETS(name);
CREATE INDEX idx_datasets_created_at ON DATASETS(created_at DESC);
```

#### Table: `TRAINING_METADATA`
```sql
CREATE TABLE TRAINING_METADATA (
    id VARCHAR2(255) PRIMARY KEY,
    dataset_id VARCHAR2(255) NOT NULL,
    workspace_name VARCHAR2(500),
    model_name VARCHAR2(255) NOT NULL,
    model_type VARCHAR2(50),
    problem_type VARCHAR2(50),
    target_variable VARCHAR2(255),
    features CLOB CHECK (features IS JSON),
    metrics CLOB CHECK (metrics IS JSON),
    hyperparameters CLOB CHECK (hyperparameters IS JSON),
    feature_importance CLOB CHECK (feature_importance IS JSON),
    training_time NUMBER,
    is_best NUMBER(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    analysis_type VARCHAR2(100),
    feedback CLOB CHECK (feedback IS JSON),
    CONSTRAINT fk_training_dataset FOREIGN KEY (dataset_id) REFERENCES DATASETS(id) ON DELETE CASCADE
);

CREATE INDEX idx_training_dataset_id ON TRAINING_METADATA(dataset_id);
CREATE INDEX idx_training_workspace ON TRAINING_METADATA(workspace_name);
CREATE INDEX idx_training_created_at ON TRAINING_METADATA(created_at DESC);
CREATE INDEX idx_training_composite ON TRAINING_METADATA(dataset_id, workspace_name);
```

#### Table: `WORKSPACE_STATES`
```sql
CREATE TABLE WORKSPACE_STATES (
    id VARCHAR2(255) PRIMARY KEY,
    workspace_name VARCHAR2(500) NOT NULL,
    dataset_id VARCHAR2(255) NOT NULL,
    predictive_analysis CLOB CHECK (predictive_analysis IS JSON),
    visualization CLOB CHECK (visualization IS JSON),
    variable_selection CLOB CHECK (variable_selection IS JSON),
    large_data_blob_id VARCHAR2(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uk_workspace UNIQUE (workspace_name, dataset_id),
    CONSTRAINT fk_workspace_dataset FOREIGN KEY (dataset_id) REFERENCES DATASETS(id) ON DELETE CASCADE
);

CREATE INDEX idx_workspace_dataset ON WORKSPACE_STATES(dataset_id);
```

#### Table: `LARGE_DATASETS`
```sql
CREATE TABLE LARGE_DATASETS (
    id VARCHAR2(255) PRIMARY KEY,
    dataset_id VARCHAR2(255),
    filename VARCHAR2(500),
    file_size NUMBER,
    content_type VARCHAR2(100),
    data_blob BLOB,
    metadata CLOB CHECK (metadata IS JSON),
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_large_dataset FOREIGN KEY (dataset_id) REFERENCES DATASETS(id) ON DELETE CASCADE
);

CREATE INDEX idx_large_dataset_id ON LARGE_DATASETS(dataset_id);
```

---

## BACKEND STRUCTURE

### Directory Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app initialization
│   ├── config.py                  # Configuration management
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connections.py         # Database connection utilities
│   │   ├── db_helper.py          # Helper functions
│   │   ├── mongodb.py            # MongoDB utilities
│   │   ├── oracle_schema.sql     # Oracle schema DDL
│   │   └── adapters/
│   │       ├── __init__.py
│   │       ├── base.py           # Base adapter interface
│   │       ├── factory.py        # Adapter factory pattern
│   │       ├── mongodb_adapter.py
│   │       └── oracle_adapter.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── pydantic_models.py    # Request/response models
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── datasource.py         # File upload, DB connections
│   │   ├── analysis.py           # Analysis & profiling
│   │   ├── training.py           # Training metadata
│   │   ├── config.py             # Database switching
│   │   ├── models.py             # Model management
│   │   ├── enhanced_chat.py      # AI chat assistant
│   │   └── migration.py          # Data migration
│   │
│   └── services/
│       ├── __init__.py
│       ├── data_service.py       # Data profiling & cleaning
│       ├── ml_service.py         # ML model training (35+ models)
│       ├── intelligent_visualization_service.py  # 28+ chart types
│       ├── enhanced_chat_service.py  # AI chat with Azure OpenAI
│       ├── azure_openai_service.py  # Azure OpenAI integration
│       ├── feature_selection_service.py  # Auto feature engineering
│       ├── hyperparameter_service.py  # Auto hyperparameter tuning
│       ├── model_explainability_service.py  # SHAP, feature importance
│       ├── time_series_service.py  # Forecasting & seasonality
│       ├── visualization_service.py  # Chart generation
│       ├── analytics_tracking_service.py  # Usage analytics
│       └── feedback_service.py  # User feedback
│
├── requirements.txt
├── .env                          # Environment variables
├── init_oracle_schema.py         # Oracle schema initialization
├── create_indexes.py             # MongoDB index creation
└── server.py                     # Alternative entry point
```

### Core Services Implementation

#### 1. Database Adapter Pattern

**Base Adapter Interface** (`app/database/adapters/base.py`):
```python
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

class BaseDatabaseAdapter(ABC):
    @abstractmethod
    async def save_dataset(self, dataset: Dict) -> str:
        """Save dataset to database. Returns dataset_id."""
        pass
    
    @abstractmethod
    async def get_dataset(self, dataset_id: str) -> Optional[Dict]:
        """Retrieve dataset by ID."""
        pass
    
    @abstractmethod
    async def list_datasets(self, limit: int = 50) -> List[Dict]:
        """List all datasets."""
        pass
    
    @abstractmethod
    async def delete_dataset(self, dataset_id: str) -> bool:
        """Delete dataset by ID."""
        pass
    
    @abstractmethod
    async def save_training_metadata(self, metadata: Dict) -> str:
        """Save training metadata."""
        pass
    
    @abstractmethod
    async def get_training_metadata(self, dataset_id: str, workspace_name: Optional[str] = None) -> List[Dict]:
        """Get training metadata."""
        pass
    
    @abstractmethod
    async def save_workspace_state(self, workspace: Dict) -> str:
        """Save workspace state."""
        pass
    
    @abstractmethod
    async def get_workspace_state(self, workspace_name: str, dataset_id: str) -> Optional[Dict]:
        """Get workspace state."""
        pass
    
    @abstractmethod
    async def list_workspaces(self, dataset_id: str) -> List[Dict]:
        """List all workspaces for a dataset."""
        pass
```

**Factory Pattern** (`app/database/adapters/factory.py`):
```python
from app.database.adapters.mongodb_adapter import MongoDBAdapter
from app.database.adapters.oracle_adapter import OracleAdapter
from app.database.adapters.base import BaseDatabaseAdapter
import os

_adapter: Optional[BaseDatabaseAdapter] = None

async def initialize_database():
    global _adapter
    db_type = os.getenv('DB_TYPE', 'mongodb').lower()
    
    if db_type == 'mongodb':
        _adapter = MongoDBAdapter()
    elif db_type == 'oracle':
        _adapter = OracleAdapter()
    else:
        raise ValueError(f"Unsupported DB_TYPE: {db_type}")
    
    await _adapter.connect()

def get_adapter() -> BaseDatabaseAdapter:
    if _adapter is None:
        raise RuntimeError("Database not initialized")
    return _adapter
```

#### 2. ML Service (`app/services/ml_service.py`)

**Key Functions**:
```python
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.svm import SVR, SVC
from sklearn.neighbors import KNeighborsRegressor, KNeighborsClassifier
from sklearn.ensemble import GradientBoostingRegressor, GradientBoostingClassifier
from sklearn.ensemble import AdaBoostRegressor, AdaBoostClassifier
from sklearn.linear_model import Ridge, Lasso, ElasticNet
from sklearn.naive_bayes import GaussianNB
from xgboost import XGBRegressor, XGBClassifier
from lightgbm import LGBMRegressor, LGBMClassifier
# ... 35+ models total

async def train_holistic_models(
    X: pd.DataFrame,
    y: pd.Series,
    problem_type: str,  # "regression" or "classification"
    models: Optional[List[str]] = None
) -> List[Dict]:
    """
    Train all applicable models in parallel.
    Returns list of model results with metrics.
    """
    # Implementation: Train models, evaluate, return results
    pass

def get_available_models(problem_type: str) -> Dict[str, List[str]]:
    """Return list of available models by problem type."""
    pass
```

**Models Supported**:
- **Regression (20)**: Linear, Ridge, Lasso, ElasticNet, Decision Tree, Random Forest, Gradient Boosting, XGBoost, LightGBM, SVR, KNN, AdaBoost, etc.
- **Classification (15)**: Logistic, Random Forest, XGBoost, SVM, KNN, Naive Bayes, Decision Tree, etc.

#### 3. Intelligent Visualization Service (`app/services/intelligent_visualization_service.py`)

**Chart Categories (28+ charts)**:
1. **Distribution (6)**: Histogram, Box Plot, Violin Plot, Density Plot, ECDF, Pie Chart
2. **Relationships (5)**: Scatter Plot, Correlation Heatmap, Bubble Chart, Pair Plot, Hexbin
3. **Categorical (4)**: Bar Chart, Stacked Bar, Grouped Bar, Count Plot
4. **Time Series (5)**: Line Chart, Rolling Average, Seasonality, Lag Plot, Calendar Heatmap
5. **Data Quality (4)**: Missing Value Heatmap, Missing Percentage, Type Distribution, Duplicates
6. **Clustering (4)**: PCA, K-Means, Dendrogram, Silhouette Plot
7. **Dashboard (2)**: KPI Cards, Radar Chart
8. **Custom**: AI-generated charts

**Key Function**:
```python
async def analyze_and_generate(
    df: pd.DataFrame,
    dataset_id: str
) -> Dict:
    """
    Analyze dataset and generate intelligent visualizations.
    Returns:
    {
        "charts": [...],  # List of chart objects
        "skipped": [...],  # Charts that couldn't be generated
        "insights": [...],  # AI-generated insights (5 key findings)
        "total_charts": 34,
        "total_skipped": 3
    }
    """
    # Deep data profiling
    # Smart chart recommendation
    # Generate charts using plotly
    # Generate AI insights using Azure OpenAI
    pass
```

#### 4. Enhanced Chat Service (`app/services/enhanced_chat_service.py`)

**Key Function**:
```python
async def process_message(
    message: str,
    dataset_id: str,
    analysis_results: Optional[Dict] = None,
    conversation_history: List[Dict] = []
) -> Dict:
    """
    Process user message and return AI response.
    Returns:
    {
        "response": "Natural language response",
        "action": "chart" | "message" | "analysis",
        "data": {...},  # Optional chart/analysis data
        "suggestions": [...]  # Follow-up suggestions
    }
    """
    # Parse intent
    # Call Azure OpenAI with context
    # Handle chart creation requests
    # Return response
    pass
```

### API Routes

#### `/api/datasource`
- `POST /api/datasource/upload` - Upload CSV/Excel file
- `POST /api/datasource/parse-connection-string` - Parse DB connection string
- `POST /api/datasource/test-connection` - Test database connection
- `POST /api/datasource/list-tables` - List tables from database
- `POST /api/datasource/load-table` - Load data from database table
- `GET /api/datasource/list` - List all datasets
- `GET /api/datasource/{dataset_id}` - Get dataset by ID
- `DELETE /api/datasource/{dataset_id}` - Delete dataset

#### `/api/analysis`
- `POST /api/analysis/run` - Run analysis (profile/holistic/visualize)
- `GET /api/analysis/saved-states` - Get saved workspaces
- `POST /api/analysis/save-state` - Save workspace state
- `POST /api/analysis/load-state` - Load workspace state

#### `/api/training`
- `GET /api/training/metadata/by-workspace` - Get training metadata by workspace
- `GET /api/training/metadata/all` - Get all training metadata
- `DELETE /api/training/metadata/delete/{dataset_id}/{workspace_name}` - Delete training metadata

#### `/api/enhanced-chat`
- `POST /api/enhanced-chat/message` - Send message to AI chat assistant

#### `/api/config`
- `GET /api/config/current-db` - Get current database
- `POST /api/config/switch-db` - Switch database (MongoDB/Oracle)

#### `/api/models`
- `GET /api/models/available` - Get available ML models
- `POST /api/models/recommend` - Get model recommendations

### Environment Variables (Backend)

```bash
# Database Configuration
DB_TYPE="oracle"  # or "mongodb"
MONGO_URL="mongodb+srv://user:pass@cluster.mongodb.net/promise_ai"
ORACLE_USER="username"
ORACLE_PASSWORD="password"
ORACLE_DSN="host:1521/ORCL"
ORACLE_HOST="host"
ORACLE_PORT="1521"
ORACLE_SERVICE_NAME="ORCL"
ORACLE_POOL_SIZE="10"

# AI Provider
AI_PROVIDER="azure_openai"
AZURE_OPENAI_ENDPOINT="https://resource.openai.azure.com/"
AZURE_OPENAI_DEPLOYMENT="gpt-4o"
AZURE_OPENAI_API_VERSION="2024-12-01-preview"
AZURE_OPENAI_KEY="your-api-key"

# Application
ENVIRONMENT="development"
DEBUG="true"
ALLOWED_ORIGINS="*"
```

---

## FRONTEND STRUCTURE

### Directory Structure
```
frontend/
├── public/
│   └── index.html
│
├── src/
│   ├── index.js                 # Entry point
│   ├── App.js                   # Root component with routing
│   ├── App.css
│   ├── index.css
│   │
│   ├── pages/
│   │   ├── HomePage.jsx         # Landing page
│   │   ├── DashboardPage.jsx   # Main analysis dashboard
│   │   ├── TrainingMetadataPage.jsx  # Training history
│   │   └── DocumentationPage.jsx     # API docs
│   │
│   ├── components/
│   │   ├── DataSourceSelector.jsx    # File/DB upload
│   │   ├── DataProfiler.jsx          # Data profiling display
│   │   ├── PredictiveAnalysis.jsx   # ML training & results
│   │   ├── VisualizationPanel.jsx    # Chart display
│   │   ├── TrainingMetadataDashboard.jsx  # Training history UI
│   │   ├── ModelSelector.jsx         # Model selection
│   │   ├── AnalysisTabs.jsx          # Tab navigation
│   │   ├── HyperparameterTuning.jsx   # Hyperparameter UI
│   │   ├── FeedbackPanel.jsx         # User feedback
│   │   ├── DatabaseSwitcher.jsx      # DB switching UI
│   │   ├── CompactDatabaseToggle.jsx # Compact DB toggle
│   │   └── EnhancedChatAssistant.jsx  # AI chat component
│   │
│   ├── utils/
│   │   └── storageManager.js    # LocalStorage management
│   │
│   ├── hooks/
│   │   └── use-toast.js         # Toast notifications
│   │
│   └── lib/
│       └── utils.js             # Utility functions
│
├── package.json
├── tailwind.config.js
├── postcss.config.js
├── craco.config.js
└── .env
```

### Key Components

#### DashboardPage.jsx
**Purpose**: Central hub for all analysis features

**State Management**:
```javascript
const [analysisCache, setAnalysisCache] = useState(null);
const [visualizationCache, setVisualizationCache] = useState(null);
const [dataProfileCache, setDataProfileCache] = useState(null);
const [selectedDataset, setSelectedDataset] = useState(null);
const [workspaceName, setWorkspaceName] = useState("");
```

**Key Features**:
- Dataset upload/selection
- Analysis tabs (Data Profile, Predictions, Visualizations)
- Workspace save/load
- State caching for performance

#### PredictiveAnalysis.jsx
**Purpose**: ML model training and results display

**Key Features**:
- Variable selection (target + features)
- Train 35+ models
- Model comparison table
- Feature importance charts
- Merge new models with existing results

#### VisualizationPanel.jsx
**Purpose**: Display 28+ intelligent visualizations

**Key Features**:
- Generate charts button
- Categorized chart display (8 categories)
- Skipped charts with reasons
- AI insights display
- Chart export functionality

#### EnhancedChatAssistant.jsx
**Purpose**: AI chat interface

**Key Features**:
- Natural language queries
- Context-aware responses
- Chart creation from chat
- Conversation history
- Follow-up suggestions

### Environment Variables (Frontend)

```bash
REACT_APP_BACKEND_URL=http://localhost:8001
```

### API Client Setup

```javascript
// src/utils/api.js
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;
```

---

## DEPENDENCIES

### Backend (`requirements.txt`)
```
fastapi==0.110.1
uvicorn==0.38.0
pandas==2.3.3
numpy==1.26.4
scikit-learn==1.3.2
plotly==6.3.1
cx_Oracle==8.3.0
motor==3.3.1
pymongo==4.5.0
openai==1.99.9
scipy==1.11.4
shap==0.49.1
xgboost==3.1.1
lightgbm==4.6.0
prophet==1.2.1
python-dotenv==1.2.1
pydantic==2.12.3
python-multipart==0.0.20
psycopg2-binary==2.9.11
PyMySQL==1.1.1
```

### Frontend (`package.json`)
```json
{
  "dependencies": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "react-router-dom": "^7.5.1",
    "axios": "^1.8.4",
    "plotly.js": "^3.2.0",
    "react-plotly.js": "^2.6.0",
    "tailwindcss": "^3.4.17",
    "@radix-ui/react-*": "^1.x.x",
    "react-hook-form": "^7.56.2",
    "zod": "^3.24.4",
    "sonner": "^2.0.3"
  }
}
```

---

## SETUP INSTRUCTIONS

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm/yarn
- MongoDB Atlas account OR Oracle RDS instance
- Azure OpenAI account (optional, for AI features)

### Backend Setup

1. **Create virtual environment**:
```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

4. **Initialize database**:
```bash
# For Oracle
python init_oracle_schema.py

# For MongoDB
python create_indexes.py
```

5. **Run backend**:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### Frontend Setup

1. **Install dependencies**:
```bash
cd frontend
yarn install
```

2. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with backend URL
```

3. **Run frontend**:
```bash
yarn dev
```

### Access Application
- Frontend: http://localhost:5173
- Backend API: http://localhost:8001/api
- API Docs: http://localhost:8001/docs

---

## KEY IMPLEMENTATION PATTERNS

### 1. Database Adapter Pattern
- Abstract base class for database operations
- Factory pattern for adapter selection
- Seamless switching between MongoDB and Oracle
- Unified interface for all database operations

### 2. Service Layer Pattern
- Business logic separated from routes
- Reusable services across routes
- Easy testing and maintenance

### 3. Async/Await Pattern
- All database operations are async
- Non-blocking I/O for better performance
- Parallel model training

### 4. BLOB Storage Pattern
- Datasets >5MB stored in GridFS (MongoDB) or BLOB (Oracle)
- Metadata stored in main collections
- Efficient retrieval and storage

### 5. Caching Pattern
- Frontend caches analysis results
- Workspace states cached in memory
- Reduces database queries

### 6. Error Handling
- Comprehensive error handling at all layers
- User-friendly error messages
- Detailed logging for debugging

---

## DEPLOYMENT

### Docker Deployment

**Backend Dockerfile**:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

**Frontend Dockerfile**:
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package.json yarn.lock .
RUN yarn install
COPY . .
RUN yarn build
CMD ["yarn", "start"]
```

### Kubernetes Deployment

See `k8s/` directory for:
- `namespace.yaml`
- `configmap.yaml`
- `backend.yaml`
- `frontend.yaml`
- `ingress.yaml`
- `mongodb.yaml`

---

## TESTING

### Backend Tests
```bash
cd backend
pytest tests/test_backend_comprehensive.py
```

### Frontend Tests
```bash
cd frontend
yarn test
```

---

## SECURITY CONSIDERATIONS

1. **Environment Variables**: Never commit `.env` files
2. **Input Validation**: All user inputs validated
3. **SQL Injection**: Parameterized queries only
4. **CORS**: Configure allowed origins
5. **Rate Limiting**: Implement in production
6. **Authentication**: Add if needed for production

---

## PERFORMANCE OPTIMIZATIONS

1. **BLOB Storage**: Datasets >5MB stored separately
2. **Chart Sampling**: Large datasets sampled for visualization
3. **Model Caching**: Training results cached
4. **Parallel Processing**: Multiple models trained simultaneously
5. **Connection Pooling**: Database connections pooled
6. **Lazy Loading**: Frontend components loaded on demand

---

## ADDITIONAL FEATURES TO IMPLEMENT

1. **User Authentication**: JWT-based authentication
2. **Multi-tenancy**: Support for multiple users/organizations
3. **Scheduled Jobs**: Automated model retraining
4. **Export Functionality**: Export models, charts, reports
5. **Real-time Updates**: WebSocket support for live updates
6. **Advanced Analytics**: More statistical tests and visualizations

---

## NOTES FOR AI IMPLEMENTATION

1. **Start with Database Layer**: Implement adapters first
2. **Then Services**: Implement core services (data, ML, visualization)
3. **Then Routes**: Implement API routes using services
4. **Then Frontend**: Build React components
5. **Test Incrementally**: Test each layer as you build
6. **Follow Patterns**: Use the patterns described above
7. **Error Handling**: Implement comprehensive error handling
8. **Logging**: Add logging at all levels
9. **Documentation**: Document all functions and classes
10. **Performance**: Optimize for large datasets

---

## CONCLUSION

This prompt provides complete specifications for recreating the PROMISE AI Platform. Follow the architecture, implement the services, create the database schemas, build the frontend components, and deploy using the provided instructions. The system is designed to be scalable, maintainable, and feature-rich.

For additional details, refer to:
- `ARCHITECTURE_DIAGRAM.md` - System architecture
- `DATABASE_STRUCTURE.md` - Complete database schemas
- `PROJECT_STRUCTURE.md` - Detailed project structure
- `LOCAL_SETUP.md` - Setup instructions
- `DEPLOYMENT.md` - Deployment guide

Good luck building the application!

