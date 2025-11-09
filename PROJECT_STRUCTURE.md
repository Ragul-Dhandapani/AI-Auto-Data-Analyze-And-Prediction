# PROMISE AI Platform - Project Structure

Complete project structure documentation with file descriptions and API endpoints.

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Directory Structure](#directory-structure)
3. [Backend Structure](#backend-structure)
4. [Frontend Structure](#frontend-structure)
5. [API Endpoints](#api-endpoints)
6. [Configuration Files](#configuration-files)

---

## Project Overview

```
/app
├── backend/          # FastAPI backend (Python 3.11)
├── frontend/         # React frontend (Vite + Tailwind)
├── mcp_server/       # MCP server for AI integration
├── docs/             # Documentation files
└── scripts/          # Utility scripts
```

---

## Directory Structure

```
/app/
├── ARCHITECTURE_DIAGRAM.md       # System architecture documentation
├── LOCAL_SETUP.md                # Setup guide for Windows/Mac/Linux
├── DEPLOYMENT.md                 # Production deployment guide
├── DATABASE_STRUCTURE.md         # Complete database schema documentation
├── PROJECT_STRUCTURE.md          # This file
├── README.md                     # Project overview
├── test_result.md                # Testing results and protocols
│
├── backend/                      # Backend application
│   ├── .env                      # Environment variables (not in git)
│   ├── requirements.txt          # Python dependencies
│   ├── server.py                 # FastAPI application entry point
│   │
│   ├── app/                      # Main application package
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI app initialization, CORS, routes
│   │   ├── config.py             # Configuration management
│   │   │
│   │   ├── database/             # Database layer
│   │   │   ├── __init__.py
│   │   │   ├── connections.py   # Database connection utilities
│   │   │   ├── db_helper.py     # Database helper functions
│   │   │   ├── mongodb.py       # MongoDB specific utilities
│   │   │   ├── oracle_schema.sql # Oracle database schema
│   │   │   │
│   │   │   └── adapters/        # Abstract database adapters
│   │   │       ├── __init__.py
│   │   │       ├── base.py      # Base adapter interface
│   │   │       ├── factory.py   # Adapter factory pattern
│   │   │       ├── mongodb_adapter.py  # MongoDB implementation
│   │   │       └── oracle_adapter.py   # Oracle implementation
│   │   │
│   │   ├── models/               # Data models
│   │   │   ├── __init__.py
│   │   │   └── pydantic_models.py # Request/response models
│   │   │
│   │   ├── routes/               # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── analysis.py      # Analysis & profiling endpoints
│   │   │   ├── datasource.py    # Data upload & connections
│   │   │   ├── training.py      # Training metadata management
│   │   │   ├── config.py        # Configuration endpoints
│   │   │   ├── models.py        # Model management
│   │   │   ├── enhanced_chat.py # AI chat assistant
│   │   │   └── migration.py     # Data migration utilities
│   │   │
│   │   └── services/             # Business logic services
│   │       ├── __init__.py
│   │       ├── data_service.py  # Data profiling & cleaning
│   │       ├── ml_service.py    # ML model training (35+ models)
│   │       ├── intelligent_visualization_service.py  # 28+ chart types
│   │       ├── enhanced_chat_service.py  # AI chat with Azure OpenAI
│   │       ├── azure_openai_service.py   # Azure OpenAI integration
│   │       ├── feature_selection_service.py  # Auto feature engineering
│   │       ├── hyperparameter_service.py  # Auto hyperparameter tuning
│   │       ├── model_explainability_service.py  # SHAP, feature importance
│   │       ├── time_series_service.py    # Forecasting & seasonality
│   │       ├── visualization_service.py  # Chart generation
│   │       ├── analytics_tracking_service.py  # Usage analytics
│   │       └── feedback_service.py       # User feedback collection
│   │
│   ├── init_oracle_schema.py    # Oracle schema initialization
│   ├── create_indexes.py        # MongoDB index creation
│   ├── migrate_workspace_column.py  # Migration utility
│   └── tests/                   # Test files
│       └── test_backend_comprehensive.py
│
├── frontend/                     # Frontend application
│   ├── .env                      # Frontend environment variables
│   ├── package.json              # Node.js dependencies
│   ├── yarn.lock                 # Yarn lock file
│   ├── vite.config.js            # Vite configuration
│   ├── tailwind.config.js        # Tailwind CSS configuration
│   ├── postcss.config.js         # PostCSS configuration
│   │
│   ├── public/                   # Static assets
│   │   ├── index.html            # HTML template
│   │   └── favicon.ico
│   │
│   └── src/                      # Source code
│       ├── index.js              # Application entry point
│       ├── App.js                # Root component with routing
│       │
│       ├── pages/                # Page components
│       │   ├── HomePage.jsx      # Landing page
│       │   ├── DashboardPage.jsx # Main analysis dashboard
│       │   ├── TrainingMetadataPage.jsx  # Training history viewer
│       │   └── DocumentationPage.jsx     # API documentation
│       │
│       ├── components/           # Reusable components
│       │   ├── DataSourceSelector.jsx    # File/DB upload
│       │   ├── DataProfiler.jsx          # Data profiling display
│       │   ├── PredictiveAnalysis.jsx    # ML model training & results
│       │   ├── VisualizationPanel.jsx    # 28+ chart types display
│       │   ├── TrainingMetadataDashboard.jsx  # Training history UI
│       │   ├── ModelSelector.jsx         # ML model selection
│       │   ├── AnalysisTabs.jsx          # Tab navigation
│       │   ├── HyperparameterTuning.jsx  # Hyperparameter UI
│       │   ├── FeedbackPanel.jsx         # User feedback
│       │   ├── DatabaseSwitcher.jsx      # DB switching UI
│       │   └── CompactDatabaseToggle.jsx # Compact DB toggle
│       │
│       ├── utils/                # Utility functions
│       │   └── storageManager.js # LocalStorage management
│       │
│       ├── hooks/                # Custom React hooks
│       │   └── use-toast.js      # Toast notification hook
│       │
│       └── lib/                  # Third-party library configs
│           └── utils.js          # Utility functions
│
└── mcp_server/                   # MCP Server (AI Integration)
    ├── promise_ai_mcp_v2.py      # Latest MCP server implementation
    └── autopredict_mcp.py        # Legacy MCP server
```

---

## Backend Structure

### Core Services

#### 1. **data_service.py** - Data Profiling & Cleaning
```python
# Purpose: Profile datasets, detect data types, clean data
# Key Functions:
- generate_data_profile(df)      # Generate comprehensive data profile
- detect_column_types(df)        # Auto-detect numeric/categorical/datetime
- clean_missing_values(df)       # Handle missing data
- detect_outliers(df, col)       # Identify outliers using IQR
```

#### 2. **ml_service.py** - Machine Learning (35+ Models)
```python
# Purpose: Train and evaluate ML models
# Models Supported:
# Regression (20): Linear, Ridge, Lasso, ElasticNet, Decision Tree, 
#                  Random Forest, Gradient Boosting, XGBoost, LightGBM,
#                  Support Vector, KNN, AdaBoost, etc.
# Classification (15): Logistic, Random Forest, XGBoost, SVM, KNN,
#                      Naive Bayes, Decision Tree, etc.
# Key Functions:
- train_holistic_models(X, y, problem_type)  # Train all applicable models
- evaluate_model(model, X_test, y_test)      # Calculate metrics
- get_feature_importance(model)              # Extract feature importance
```

#### 3. **intelligent_visualization_service.py** - 28+ Chart Types
```python
# Purpose: Generate intelligent visualizations across 8 categories
# Categories:
# 1. Distribution (6): Histogram, Box Plot, Violin, Density, ECDF, Pie
# 2. Relationships (5): Scatter, Heatmap, Bubble, Pair Plot, Hexbin
# 3. Categorical (4): Bar, Stacked Bar, Grouped Bar, Count Plot
# 4. Time Series (5): Line, Rolling Average, Seasonality, Lag, Calendar
# 5. Data Quality (4): Missing Heatmap, Missing %, Type Distribution, Duplicates
# 6. Clustering (4): PCA, K-Means, Dendrogram, Silhouette
# 7. Dashboard (2): KPI Cards, Radar Chart
# 8. Custom: AI-generated charts
# Key Functions:
- analyze_and_generate(df)       # Main entry point
- _profile_data()                # Deep data profiling
- _generate_distribution_charts() # Category 1 charts
- _generate_ai_insights()        # Azure OpenAI insights
```

#### 4. **enhanced_chat_service.py** - AI Chat Assistant
```python
# Purpose: Context-aware chat with Azure OpenAI integration
# Features:
- Natural language chart creation
- Data analysis queries
- Context-aware follow-ups (conversation history)
- Chart recommendations
# Key Functions:
- process_message(message, dataset, results, history)
- _handle_chart_request()
- _handle_general_query()
- _handle_interpretation()
```

#### 5. **azure_openai_service.py** - Azure OpenAI Integration
```python
# Purpose: Interface with Azure OpenAI GPT-4o
# Key Functions:
- generate_completion(prompt, max_tokens, temperature)
- is_available()                 # Check if service is configured
- _create_client()               # Initialize OpenAI client
```

#### 6. **feature_selection_service.py** - Auto Feature Engineering
```python
# Purpose: Automatic feature selection and engineering
# Key Functions:
- select_features(X, y, problem_type)
- create_interaction_features(X)
- create_polynomial_features(X)
```

#### 7. **hyperparameter_service.py** - Auto Hyperparameter Tuning
```python
# Purpose: Optimize model hyperparameters
# Key Functions:
- tune_hyperparameters(model, X, y, problem_type)
- get_param_grid(model_name)
- grid_search_cv()
```

#### 8. **model_explainability_service.py** - Model Interpretability
```python
# Purpose: Explain model predictions (SHAP values, feature importance)
# Key Functions:
- calculate_shap_values(model, X)
- get_feature_importance(model)
- generate_explanation(prediction)
```

#### 9. **time_series_service.py** - Time Series Analysis
```python
# Purpose: Forecasting and seasonality detection
# Key Functions:
- detect_seasonality(df, datetime_col)
- forecast(df, periods)
- decompose_time_series(df)
```

---

## Frontend Structure

### Page Components

#### 1. **HomePage.jsx** - Landing Page
```jsx
// Purpose: Welcome page with project overview
// Features:
- Project introduction
- Quick start guide
- Database status indicator
- Navigation to Dashboard
```

#### 2. **DashboardPage.jsx** - Main Analysis Dashboard
```jsx
// Purpose: Central hub for all analysis features
// Features:
- Dataset upload/selection
- Analysis tabs (Data Profile, Predictions, Visualizations)
- Workspace save/load
- State management for all cached results
// State Management:
- analysisCache (predictive analysis results)
- visualizationCache (generated charts)
- dataProfileCache (data profiling results)
```

#### 3. **TrainingMetadataPage.jsx** - Training History
```jsx
// Purpose: View historical model training results
// Features:
- Summary statistics (datasets, workspaces, models)
- Search and filter functionality
- Model comparison
- Workspace-based organization
- Delete training records
```

#### 4. **DocumentationPage.jsx** - API Documentation
```jsx
// Purpose: API documentation and guides
// Features:
- Endpoint documentation
- Request/response examples
- Feature explanations
- Getting started guide
```

### Core Components

#### 5. **DataSourceSelector.jsx** - Data Upload
```jsx
// Purpose: Handle file uploads and database connections
// Features:
- File upload (CSV, Excel)
- Database connections (Oracle, PostgreSQL, MySQL, MongoDB)
- Table loading from databases
- Connection testing
```

#### 6. **DataProfiler.jsx** - Data Profiling Display
```jsx
// Purpose: Display comprehensive data profile
// Features:
- Dataset overview (rows, columns, types)
- Data preview with pagination (1000 rows)
- Column statistics
- Missing value analysis
- Data type distribution
```

#### 7. **PredictiveAnalysis.jsx** - ML Training & Results
```jsx
// Purpose: Train ML models and display results
// Features:
- Variable selection (target + features)
- 35+ ML models
- Model comparison table
- Feature importance charts
- Model metrics display
- Merge new models with existing
// State:
- analysisResults (current results)
- previousResultsRef (for merging)
```

#### 8. **VisualizationPanel.jsx** - Chart Generation
```jsx
// Purpose: Display 28+ intelligent visualizations
// Features:
- Generate charts button
- Categorized chart display (8 categories)
- Skipped charts with reasons
- AI insights display
- Chart export
```

---

## API Endpoints

### Base URL
```
Production: https://api.yourdomain.com/api
Development: http://localhost:8001/api
```

---

### 1. Data Source Endpoints (`/api/datasource`)

#### POST `/api/datasource/upload`
**Purpose**: Upload CSV or Excel files

**Request**:
```bash
Content-Type: multipart/form-data

file: <binary-file>
```

**Response**:
```json
{
  "success": true,
  "dataset_id": "uuid-string",
  "dataset": {
    "id": "uuid-string",
    "name": "application_latency.csv",
    "row_count": 10000,
    "column_count": 12,
    "columns": ["timestamp", "latency_ms", ...],
    "data_preview": [{...}, {...}]
  }
}
```

**Limitations**:
- Max file size: 500MB
- Supported formats: CSV, XLSX, XLS
- Duplicate filenames auto-renamed

---

#### POST `/api/datasource/parse-connection-string`
**Purpose**: Parse database connection string

**Request**:
```json
{
  "source_type": "postgresql",
  "connection_string": "postgresql://user:pass@host:5432/db"
}
```

**Response**:
```json
{
  "success": true,
  "config": {
    "host": "localhost",
    "port": 5432,
    "database": "testdb",
    "username": "user",
    "password": "pass"
  }
}
```

---

#### POST `/api/datasource/test-connection`
**Purpose**: Test database connection

**Request**:
```json
{
  "source_type": "oracle",
  "config": {
    "host": "oracle-rds.amazonaws.com",
    "port": 1521,
    "service_name": "ORCL",
    "username": "admin",
    "password": "password"
  }
}
```

**Response**:
```json
{
  "success": true,
  "message": "Connection successful"
}
```

---

#### POST `/api/datasource/list-tables`
**Purpose**: Get list of tables from database

**Request**:
```json
{
  "source_type": "oracle",
  "config": {...}
}
```

**Response**:
```json
{
  "tables": ["USERS", "ORDERS", "PRODUCTS"]
}
```

---

#### POST `/api/datasource/load-table?table_name=USERS`
**Purpose**: Load data from database table

**Request**:
```json
{
  "source_type": "oracle",
  "config": {...},
  "limit": 1000
}
```

**Response**:
```json
{
  "success": true,
  "dataset_id": "uuid-string",
  "dataset": {
    "id": "uuid-string",
    "name": "USERS_oracle.csv",
    "row_count": 1000,
    "columns": [...],
    "data_preview": [...]
  }
}
```

---

#### GET `/api/datasource/list?limit=50`
**Purpose**: List all uploaded datasets

**Response**:
```json
{
  "datasets": [
    {
      "id": "uuid-1",
      "name": "dataset1.csv",
      "row_count": 5000,
      "created_at": "2024-11-09T10:00:00Z"
    }
  ]
}
```

---

#### DELETE `/api/datasource/{dataset_id}`
**Purpose**: Delete a dataset

**Response**:
```json
{
  "success": true,
  "message": "Dataset deleted successfully"
}
```

---

### 2. Analysis Endpoints (`/api/analysis`)

#### POST `/api/analysis/run`
**Purpose**: Run analysis (profiling, holistic, visualization)

**Request**:
```json
{
  "dataset_id": "uuid-string",
  "analysis_type": "holistic",  // "profile", "holistic", "visualize"
  "target_variable": "latency_ms",
  "feature_variables": ["cpu_usage", "memory_usage"],
  "problem_type": "auto",  // "auto", "regression", "classification"
  "models": ["Random Forest", "XGBoost"]  // Optional
}
```

**Response (holistic)**:
```json
{
  "dataset_profile": {
    "total_rows": 10000,
    "total_columns": 12,
    "numeric_columns": 8,
    "categorical_columns": 4
  },
  "ml_models": [
    {
      "model_name": "Random Forest",
      "model_type": "regression",
      "r2_score": 0.8567,
      "rmse": 11.11,
      "feature_importance": {...},
      "is_best": true
    }
  ],
  "auto_charts": [
    {
      "title": "Distribution: latency_ms",
      "type": "histogram",
      "description": "...",
      "data": {...}  // Plotly JSON
    }
  ]
}
```

**Response (visualize)**:
```json
{
  "charts": [
    {
      "title": "Histogram: latency_ms",
      "type": "histogram",
      "category": "distribution",
      "description": "Shows how latency_ms values are distributed...",
      "data": {...}  // Plotly JSON
    }
  ],
  "skipped": [
    {
      "category": "clustering",
      "message": "Dendrogram: Dataset too large (max 100 rows)"
    }
  ],
  "insights": [
    "Dataset contains 10,000 rows with 12 columns",
    "Strong correlation between cpu_usage and memory_usage"
  ],
  "total_charts": 34,
  "total_skipped": 3
}
```

**Limitations**:
- Max execution time: 600 seconds
- Model training: All 35+ models trained in parallel
- Visualization: 28+ charts generated automatically

---

#### GET `/api/analysis/saved-states?dataset_id=uuid`
**Purpose**: Get all saved workspaces for a dataset

**Response**:
```json
{
  "workspaces": [
    {
      "workspace_name": "latency_analysis_nov3",
      "dataset_id": "uuid-string",
      "created_at": "2024-11-09T10:00:00Z"
    }
  ]
}
```

---

#### POST `/api/analysis/save-state`
**Purpose**: Save workspace state

**Request**:
```json
{
  "workspace_name": "latency_analysis_nov3",
  "dataset_id": "uuid-string",
  "state": {
    "predictive_analysis": {...},
    "visualization": {...},
    "variable_selection": {...}
  }
}
```

**Response**:
```json
{
  "success": true,
  "message": "Workspace saved successfully"
}
```

---

#### POST `/api/analysis/load-state`
**Purpose**: Load workspace state

**Request**:
```json
{
  "workspace_name": "latency_analysis_nov3",
  "dataset_id": "uuid-string"
}
```

**Response**:
```json
{
  "workspace": {
    "workspace_name": "latency_analysis_nov3",
    "dataset_id": "uuid-string",
    "predictive_analysis": {...},
    "visualization": {...}
  }
}
```

---

### 3. Training Metadata Endpoints (`/api/training`)

#### GET `/api/training/metadata/by-workspace?workspace_name=name`
**Purpose**: Get training metadata for a workspace

**Response**:
```json
{
  "metadata": [
    {
      "id": "uuid-string",
      "model_name": "Random Forest",
      "metrics": {...},
      "created_at": "2024-11-09T10:00:00Z"
    }
  ]
}
```

---

#### GET `/api/training/metadata/all`
**Purpose**: Get all training metadata

**Response**:
```json
{
  "metadata": [...]
}
```

---

#### DELETE `/api/training/metadata/delete/{dataset_id}/{workspace_name}`
**Purpose**: Delete specific training metadata

**Response**:
```json
{
  "success": true,
  "message": "Training metadata deleted"
}
```

---

### 4. Enhanced Chat Endpoints (`/api/enhanced-chat`)

#### POST `/api/enhanced-chat/message`
**Purpose**: Send message to AI chat assistant

**Request**:
```json
{
  "message": "Show me outliers",
  "dataset_id": "uuid-string",
  "analysis_results": {...},
  "conversation_history": [
    {"role": "user", "message": "Previous message"},
    {"role": "assistant", "response": "Previous response"}
  ]
}
```

**Response**:
```json
{
  "response": "I've identified 42 outliers in latency_ms...",
  "action": "chart",  // "chart", "message", "analysis"
  "data": {
    "chart": {...}  // Plotly chart data
  },
  "suggestions": [
    "Show me the distribution",
    "What's causing these outliers?"
  ]
}
```

---

### 5. Config Endpoints (`/api/config`)

#### GET `/api/config/current-db`
**Purpose**: Get current database configuration

**Response**:
```json
{
  "db_type": "oracle",
  "connection_info": {
    "host": "oracle-rds.amazonaws.com",
    "port": 1521
  }
}
```

---

#### POST `/api/config/switch-db`
**Purpose**: Switch between MongoDB and Oracle

**Request**:
```json
{
  "db_type": "mongodb"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Switched to MongoDB"
}
```

---

### 6. Model Endpoints (`/api/models`)

#### GET `/api/models/available`
**Purpose**: Get list of available ML models

**Response**:
```json
{
  "regression": [
    "Linear Regression",
    "Ridge Regression",
    "Random Forest",
    ...
  ],
  "classification": [
    "Logistic Regression",
    "Random Forest Classifier",
    ...
  ]
}
```

---

## Configuration Files

### Backend Configuration

#### `.env`
```bash
# Database
DB_TYPE="oracle"  # or "mongodb"
ORACLE_USER="admin"
ORACLE_PASSWORD="password"
ORACLE_DSN="host:1521/ORCL"

# AI Provider
AI_PROVIDER="azure_openai"
AZURE_OPENAI_API_KEY="your-key"
AZURE_OPENAI_ENDPOINT="https://resource.openai.azure.com/"
```

#### `requirements.txt`
```
fastapi==0.100.0
uvicorn[standard]==0.23.0
pandas==2.0.3
numpy==1.24.3
scikit-learn==1.3.0
plotly==5.15.0
cx-Oracle==8.3.0
motor==3.3.0
pymongo==4.5.0
openai==1.0.0
scipy==1.11.0
...
```

### Frontend Configuration

#### `.env`
```bash
REACT_APP_BACKEND_URL=http://localhost:8001
```

#### `package.json`
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-router-dom": "^6.15.0",
    "axios": "^1.5.0",
    "plotly.js": "^2.26.0",
    "tailwindcss": "^3.3.0"
  }
}
```

---

For setup instructions, see [LOCAL_SETUP.md](LOCAL_SETUP.md)

For API testing, visit: `http://localhost:8001/docs` (Interactive Swagger UI)
