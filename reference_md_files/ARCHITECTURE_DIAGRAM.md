# PROMISE AI Platform - Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         PROMISE AI PLATFORM                          │
│              AI-Powered Predictive Analytics Platform                │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│                           FRONTEND LAYER                              │
│                     (React.js + Vite + Tailwind)                     │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐   │
│  │  HomePage  │  │ Dashboard  │  │  Training  │  │    Docs    │   │
│  │            │  │    Page    │  │  Metadata  │  │    Page    │   │
│  └────────────┘  └────────────┘  └────────────┘  └────────────┘   │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    CORE COMPONENTS                            │   │
│  ├──────────────────────────────────────────────────────────────┤   │
│  │ • DataSourceSelector    • PredictiveAnalysis                 │   │
│  │ • DataProfiler          • VisualizationPanel (28+ charts)    │   │
│  │ • TrainingMetadata      • EnhancedChatAssistant              │   │
│  │ • ModelSelector         • DatabaseSwitcher                   │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  State Management: React Context + Local State                       │
│  Caching: In-memory + Backend BLOB storage                          │
└──────────────────────────────────────────────────────────────────────┘
                                    ↓
                              API Gateway
                    (axios → REACT_APP_BACKEND_URL)
                                    ↓
┌──────────────────────────────────────────────────────────────────────┐
│                           BACKEND LAYER                               │
│                     (FastAPI + Python 3.11)                          │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                      API ROUTES                               │   │
│  ├──────────────────────────────────────────────────────────────┤   │
│  │ /api/datasource    - File upload, DB connections, tables     │   │
│  │ /api/analysis      - Holistic analysis, profiling, viz       │   │
│  │ /api/training      - Metadata, model training                │   │
│  │ /api/config        - Database switching                      │   │
│  │ /api/models        - Model management                        │   │
│  │ /api/enhanced-chat - AI chat assistant                       │   │
│  │ /api/migration     - Data migration utilities                │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                   CORE SERVICES                               │   │
│  ├──────────────────────────────────────────────────────────────┤   │
│  │ • IntelligentVisualizationService (28+ chart types)          │   │
│  │ • MLService (35+ models: regression, classification)         │   │
│  │ • EnhancedChatService (Azure OpenAI integration)             │   │
│  │ • DataService (profiling, cleaning)                          │   │
│  │ • FeatureSelectionService (auto feature engineering)         │   │
│  │ • HyperparameterService (auto-tuning)                        │   │
│  │ • ModelExplainabilityService (SHAP, feature importance)      │   │
│  │ • TimeSeriesService (forecasting, seasonality)               │   │
│  │ • AzureOpenAIService (GPT-4o integration)                    │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
                          ↓                ↓
                   ┌──────────┐    ┌──────────┐
                   │ MongoDB  │    │  Oracle  │
                   │ Adapter  │    │  Adapter │
                   └──────────┘    └──────────┘
                          ↓                ↓
┌──────────────────────────────────────────────────────────────────────┐
│                        DATABASE LAYER                                 │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────────────────┐      ┌─────────────────────────┐       │
│  │      MongoDB Atlas       │      │   Oracle RDS 19c        │       │
│  │   (Document Database)    │      │ (Relational Database)   │       │
│  ├─────────────────────────┤      ├─────────────────────────┤       │
│  │ • Datasets Collection    │      │ • DATASETS Table        │       │
│  │ • Training Metadata      │      │ • TRAINING_METADATA     │       │
│  │ • Workspaces             │      │ • WORKSPACE_STATES      │       │
│  │ • GridFS (BLOB storage)  │      │ • LARGE_DATASETS (BLOB) │       │
│  └─────────────────────────┘      └─────────────────────────┘       │
│                                                                       │
│  Abstract Database Factory Pattern                                   │
│  ✓ Seamless switching between MongoDB and Oracle                    │
│  ✓ Unified adapter interface                                        │
└──────────────────────────────────────────────────────────────────────┘
                                    ↓
┌──────────────────────────────────────────────────────────────────────┐
│                      EXTERNAL INTEGRATIONS                            │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │ Azure OpenAI (GPT-4o)                                       │     │
│  │ • Enhanced chat assistance                                  │     │
│  │ • AI insights generation                                    │     │
│  │ • Natural language chart creation                           │     │
│  │ • Context-aware follow-ups                                  │     │
│  └────────────────────────────────────────────────────────────┘     │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │ ML Libraries                                                │     │
│  │ • scikit-learn (35+ models, PCA, clustering)               │     │
│  │ • pandas, numpy (data processing)                          │     │
│  │ • plotly (interactive visualizations)                       │     │
│  │ • scipy (statistical analysis)                             │     │
│  └────────────────────────────────────────────────────────────┘     │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

## Data Flow Architecture

### 1. Data Upload Flow
```
User → File Upload/DB Connection
    ↓
DataSource API → Parse & Validate
    ↓
Data Service → Profile & Clean
    ↓
Database Adapter → Store (Direct or BLOB)
    ↓
Frontend → Display in Data Profiler
```

### 2. Predictive Analysis Flow
```
User → Select Variables → Train Models
    ↓
Analysis API → Holistic Analysis Service
    ↓
ML Service → Train 35+ Models in Parallel
    ↓
Feature Selection → Auto-detect best features
    ↓
Model Explainability → SHAP, Feature Importance
    ↓
Results → Cache + Store in Database
    ↓
Frontend → Display Model Comparison
```

### 3. Intelligent Visualization Flow
```
User → Click "Generate Charts"
    ↓
Analysis API (visualize) → IntelligentVisualizationService
    ↓
Deep Data Profiling → Detect patterns, types, relationships
    ↓
Smart Chart Recommendation → 28+ chart types across 8 categories
    ↓
Azure OpenAI → Generate insights (5 key findings)
    ↓
Response → Charts + Insights + Skipped messages
    ↓
Frontend → Display categorized visualizations
```

### 4. Enhanced Chat Flow
```
User → Type message in Chat Assistant
    ↓
Enhanced Chat API → Parse intent
    ↓
Azure OpenAI → Semantic understanding + Context
    ↓
Conversation History → Context-aware responses
    ↓
Action Handler → Execute (chart creation, analysis, etc.)
    ↓
Response → Natural language + Action data
    ↓
Frontend → Display response + Generated chart
```

### 5. Workspace Save/Load Flow
```
User → Save Workspace
    ↓
Dashboard → Collect all cached state
    ↓
Analysis API → Optimize for storage
    ↓
Large Data (>5MB) → BLOB storage
    ↓
Metadata → Database (workspace_name, dataset_id)
    ↓
Load Workspace → Retrieve from database
    ↓
Frontend → Restore all cached state
```

## Technology Stack

### Frontend
- **Framework**: React 18.x with Vite
- **UI Library**: Tailwind CSS + shadcn/ui
- **State Management**: React Context + useState/useRef
- **Data Visualization**: Plotly.js (interactive charts)
- **API Client**: Axios
- **Routing**: React Router v6
- **Notifications**: Sonner (toast notifications)

### Backend
- **Framework**: FastAPI 0.100+
- **Language**: Python 3.11
- **ML Libraries**: 
  - scikit-learn (models, clustering, PCA)
  - pandas, numpy (data processing)
  - scipy (statistics)
- **Visualization**: plotly (chart generation)
- **AI Integration**: Azure OpenAI (GPT-4o)
- **Database Drivers**:
  - motor (MongoDB async)
  - cx_Oracle (Oracle 19c)
  - pymongo (MongoDB sync)

### Databases
- **Primary**: Oracle RDS 19c (AWS)
- **Alternative**: MongoDB Atlas
- **BLOB Storage**: GridFS (MongoDB) / BLOB (Oracle)

### Deployment
- **Container**: Docker + Kubernetes
- **Process Manager**: Supervisor (frontend, backend)
- **Reverse Proxy**: Nginx
- **Hot Reload**: Enabled for development

## Security Architecture

### Authentication & Authorization
- Database credentials stored in environment variables
- Azure OpenAI API keys secured in .env
- No hardcoded credentials in code

### Data Security
- Sensitive data stored in BLOB with encryption
- Connection strings not exposed to frontend
- CORS enabled for specific origins

### Input Validation
- File upload validation (CSV, Excel)
- SQL injection prevention (parameterized queries)
- XSS protection (input sanitization)

## Scalability Features

### Backend
- Async/await pattern for non-blocking operations
- Database connection pooling (Oracle: 10 connections)
- Parallel model training (35+ models)
- Efficient data sampling for large datasets

### Frontend
- Component-level caching
- Lazy loading of charts
- Pagination for large data previews
- WebGL context cleanup for memory management

### Database
- BLOB storage for datasets >5MB
- Indexed queries for fast retrieval
- Abstract adapter pattern for database switching

## Performance Optimizations

1. **BLOB Storage**: Datasets >5MB stored separately
2. **Chart Sampling**: Large datasets sampled (e.g., 500 rows for heatmaps)
3. **Model Caching**: Training results cached in-memory
4. **Workspace Optimization**: Large payloads compressed before storage
5. **Parallel Processing**: Multiple models trained simultaneously
6. **WebGL Management**: Charts destroyed and recreated to prevent memory leaks

## High Availability

- Database connection retry logic
- Graceful error handling with user-friendly messages
- Fallback mechanisms for AI services
- Automatic reconnection for dropped connections

## Monitoring & Logging

- Comprehensive logging (INFO, WARNING, ERROR levels)
- Service status endpoints (/health, /api/)
- Supervisor process monitoring
- Error tracking with detailed stack traces
