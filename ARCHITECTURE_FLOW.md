# PROMISE AI - Architecture & Data Flow

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          CLIENT LAYER                                │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  React.js Frontend (Port 3000)                                │  │
│  │  - Components: Dashboard, Analysis, Visualization             │  │
│  │  - State Management: React Hooks + localStorage              │  │
│  │  - UI Library: shadcn/ui + Tailwind CSS                       │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                  ↕ HTTP/REST
┌─────────────────────────────────────────────────────────────────────┐
│                        API GATEWAY LAYER                             │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  FastAPI Backend (Port 8001)                                  │  │
│  │  - Routes: /api/datasets, /api/analysis, /api/models         │  │
│  │  - Middleware: CORS, Error Handling                           │  │
│  │  - Validation: Pydantic Models                                │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                  ↕
┌─────────────────────────────────────────────────────────────────────┐
│                        SERVICE LAYER                                 │
│  ┌────────────────────┐  ┌──────────────────┐  ┌─────────────────┐ │
│  │  ML Service        │  │  Azure OpenAI    │  │  Data Service   │ │
│  │  - 35+ Models      │  │  - Insights      │  │  - Profiling    │ │
│  │  - Training        │  │  - Chat          │  │  - Cleaning     │ │
│  │  - Evaluation      │  │  - Recommenda-   │  │  - Transform    │ │
│  │                    │  │    tions          │  │                 │ │
│  └────────────────────┘  └──────────────────┘  └─────────────────┘ │
│                                                                      │
│  ┌────────────────────┐  ┌──────────────────┐  ┌─────────────────┐ │
│  │  Visualization     │  │  Feature         │  │  Analytics      │ │
│  │  Service           │  │  Selection       │  │  Tracking       │ │
│  │  - Charts          │  │  - Importance    │  │  - Metadata     │ │
│  │  - Insights        │  │  - Correlation   │  │  - Metrics      │ │
│  └────────────────────┘  └──────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                  ↕
┌─────────────────────────────────────────────────────────────────────┐
│                      DATA ACCESS LAYER                               │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Database Factory Pattern                                     │  │
│  │  ┌────────────────────┐        ┌──────────────────────────┐  │  │
│  │  │  Oracle Adapter    │        │  MongoDB Adapter         │  │  │
│  │  │  - BLOB Storage    │        │  - GridFS Storage        │  │  │
│  │  │  - Connection Pool │        │  - Document Store        │  │  │
│  │  └────────────────────┘        └──────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                  ↕
┌─────────────────────────────────────────────────────────────────────┐
│                        DATABASE LAYER                                │
│  ┌──────────────────────┐                ┌──────────────────────┐  │
│  │  Oracle RDS 19c      │       OR       │  MongoDB             │  │
│  │  - Primary DB        │                │  - Alternative DB    │  │
│  │  - BLOB for Files    │                │  - GridFS for Files  │  │
│  │  - 4 Core Tables     │                │  - 4 Collections     │  │
│  └──────────────────────┘                └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      EXTERNAL SERVICES                               │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Azure OpenAI                                                 │  │
│  │  - Endpoint: https://your-resource.openai.azure.com/         │  │
│  │  - Deployment: gpt-4o                                         │  │
│  │  - API Version: 2024-12-01-preview                            │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow Diagrams

### 1. Dataset Upload & Analysis Flow

```
User Uploads CSV
      ↓
[Frontend] File Upload Component
      ↓ POST /api/datasets/upload
[Backend] Dataset Route
      ↓
[Service] Data Service
      ├─→ Validate CSV
      ├─→ Generate Profile
      ├─→ Detect Data Types
      └─→ Store in Database
            ↓
[Database Adapter] Oracle/MongoDB
      ├─→ Save metadata to 'datasets' table
      └─→ Store file in BLOB/GridFS
            ↓
[Response] Dataset ID + Profile
      ↓
[Frontend] Display in Dashboard
```

### 2. ML Model Training Flow

```
User Selects Variables & Models
      ↓
[Frontend] ModelSelector Component
      ↓ POST /api/analysis/holistic
      ↓ payload: {dataset_id, problem_type, selected_models}
[Backend] Analysis Route
      ↓
[Service] Load Dataset from Database
      ↓
[Service] Data Preprocessing
      ├─→ Handle NaN values
      ├─→ Select numeric columns
      └─→ Train/Test Split (80/20)
            ↓
[ML Service Enhanced] Train Models
      ├─→ For each selected model:
      │   ├─→ Initialize model
      │   ├─→ Fit on training data
      │   ├─→ Predict on test data
      │   ├─→ Calculate metrics
      │   └─→ Track training time
      └─→ Return results
            ↓
[Analytics Tracking] Record Metadata
      ├─→ Increment training_count
      ├─→ Update last_trained_at
      └─→ Store training metadata
            ↓
[Response] ML Results + Metrics
      ├─→ ml_models: [{model_name, r2_score, rmse, ...}]
      ├─→ feature_importance
      ├─→ correlation_matrix
      └─→ ai_summary
            ↓
[Frontend] Display ML Model Comparison
      ├─→ Save to localStorage
      └─→ Render comparison table + tabs
```

### 3. Azure OpenAI Chat Flow

```
User Sends Chat Message
      ↓
[Frontend] Chat Component
      ↓ POST /api/analysis/chat
      ↓ payload: {dataset_id, message, conversation_history}
[Backend] Chat Endpoint
      ↓
[Service] LLM Chart Intelligence
      ├─→ Parse natural language request
      ├─→ Detect chart type
      └─→ Map to dataset columns
            ↓
[Azure OpenAI Service]
      ├─→ Prepare prompt with data context
      ├─→ Call Azure OpenAI API
      │   └─→ POST https://your-resource.openai.azure.com/
      │       └─→ Headers: api-key, Content-Type
      │       └─→ Body: {model, messages, temperature}
      └─→ Parse response
            ↓
[Service] Generate Visualization
      ├─→ If chart request: Create chart data
      └─→ If question: Return AI response
            ↓
[Response] Chat Result
      ├─→ action: "chart" | "message"
      ├─→ chart_data: {...} (if chart)
      └─→ message: "..." (if text)
            ↓
[Frontend] Render Chat Response
      ├─→ Display message in chat
      └─→ Render chart if provided
```

### 4. Model Selection Flow

```
User Opens ModelSelector
      ↓
[Frontend] ModelSelector Component
      ↓ GET /api/models/available?problem_type=regression
[Backend] Models Route
      ↓
[ML Service] Get Available Models
      ├─→ Load model catalog
      ├─→ Filter by problem type
      └─→ Return model list
            ↓
[Response] Available Models
      └─→ [{key, name, description}]
            ↓
[Frontend] Display Model List
      └─→ User selects models
            ↓
[User Action] Select Models & Click Train
      ↓
[Frontend] POST /api/analysis/holistic
      └─→ payload: {selected_models: [...]}
            ↓
[Backend] Train ONLY Selected Models
      └─→ Results show selected models only
```

---

## 🗄️ Database Schema Flow

### Oracle RDS Structure

```
datasets (Main Table)
  ├─→ id (VARCHAR2 PK)
  ├─→ name, size, row_count, column_count
  ├─→ columns_json, dtypes_json, data_preview_json
  ├─→ created_at, training_count, last_trained_at
  └─→ Links to: file_storage (1:1)

file_storage (BLOB Storage)
  ├─→ id (VARCHAR2 PK)
  ├─→ dataset_id (FK → datasets.id)
  ├─→ file_data (BLOB) - Compressed CSV data
  ├─→ compression_type (gzip/none)
  └─→ created_at

workspaces (Analysis States)
  ├─→ id (VARCHAR2 PK)
  ├─→ dataset_id (FK → datasets.id)
  ├─→ name, workspace_data_json
  ├─→ created_at, updated_at
  └─→ Stores: analysis results, charts, state

training_metadata (ML History)
  ├─→ id (VARCHAR2 PK)
  ├─→ dataset_id (FK → datasets.id)
  ├─→ problem_type, target_variable
  ├─→ model_type, model_params_json
  ├─→ metrics_json (r2_score, accuracy, etc.)
  ├─→ training_duration, created_at
  └─→ Tracks: every ML training run
```

---

## 🔐 Security Flow

```
Client Request
      ↓
[CORS Middleware] Validate Origin
      ↓
[Pydantic Validation] Validate Request Body
      ↓
[Business Logic] Process Request
      ↓
[Database Adapter] Sanitize SQL/Queries
      ↓
[Error Handler] Catch & Log Errors
      ↓
[Response] Return JSON
```

**Security Measures:**
- ✅ CORS configured for allowed origins
- ✅ Input validation with Pydantic
- ✅ Parameterized queries (no SQL injection)
- ✅ Error messages sanitized (no stack traces to client)
- ✅ API keys stored in environment variables
- ✅ Connection pooling with limits

---

## 📊 Component Relationships

### Frontend Component Hierarchy

```
App.js
├─→ HomePage
│   └─→ Hero, Features, CTA
├─→ DashboardPage
│   ├─→ DatasetList
│   │   └─→ DatasetCard × N
│   ├─→ DataSourceSelector
│   └─→ AnalysisTabs
│       ├─→ DataProfiler
│       ├─→ PredictiveAnalysis
│       │   ├─→ ModelSelector
│       │   ├─→ VariableSelectionModal
│       │   └─→ MLModelComparison
│       ├─→ VisualizationPanel
│       ├─→ TimeSeriesAnalysis
│       └─→ HyperparameterTuning
└─→ TrainingMetadataPage
    └─→ TrainingHistory
```

### Backend Service Dependencies

```
main.py (FastAPI App)
├─→ routes/
│   ├─→ analysis.py
│   │   ├─→ services/ml_service_enhanced.py
│   │   ├─→ services/azure_openai_service.py
│   │   ├─→ services/data_service.py
│   │   ├─→ services/visualization_service_v2.py
│   │   └─→ services/chat_service.py
│   ├─→ datasource.py
│   │   ├─→ services/data_service.py
│   │   └─→ database/factory.py
│   ├─→ models.py
│   │   └─→ services/ml_service_enhanced.py
│   └─→ training.py
│       └─→ database/factory.py
└─→ database/
    ├─→ factory.py
    ├─→ adapters/
    │   ├─→ oracle_adapter.py
    │   └─→ mongodb_adapter.py
    └─→ connections.py
```

---

## ⚡ Performance Optimizations

### 1. Database Connection Pooling
```python
# Oracle Pool: 2-10 connections
pool = cx_Oracle.SessionPool(
    min=2,
    max=10,
    increment=1
)
```

### 2. Data Compression
```python
# Files compressed before storage
import gzip
compressed_data = gzip.compress(csv_data.encode())
```

### 3. Frontend Caching
```javascript
// Analysis results cached in localStorage
localStorage.setItem(`analysis_${dataset.id}`, JSON.stringify(results));
```

### 4. Lazy Loading
- Charts loaded on-demand
- Models trained only when requested
- Dataset preview limited to 100 rows

---

## 🔄 State Management

### Frontend State (React)
```javascript
// Component State
const [analysisResults, setAnalysisResults] = useState(null);
const [loading, setLoading] = useState(false);

// Persistent State (localStorage)
localStorage.setItem('analysis_${datasetId}', JSON.stringify(results));

// Prop Drilling
DashboardPage → AnalysisTabs → PredictiveAnalysis
```

### Backend State
```python
# Stateless API (no session storage)
# All state in database or passed in requests

# Connection pools maintained
oracle_pool = get_connection_pool()
```

---

## 📈 Scalability Considerations

### Horizontal Scaling
- ✅ Stateless backend (can run multiple instances)
- ✅ Database connection pooling
- ✅ Frontend served via CDN

### Vertical Scaling
- ✅ Oracle RDS can scale to larger instances
- ✅ ML training can use more CPU/RAM
- ✅ Azure OpenAI handles load automatically

### Caching Strategy
- **Frontend**: localStorage for analysis results
- **Backend**: No caching (always fresh data)
- **Database**: Oracle query result cache
- **CDN**: Static assets (JS, CSS, images)

---

## 🎯 Key Design Patterns

1. **Factory Pattern**: Database adapter selection
2. **Adapter Pattern**: Uniform interface for Oracle/MongoDB
3. **Strategy Pattern**: Different ML algorithms
4. **Singleton Pattern**: Azure OpenAI service instance
5. **Repository Pattern**: Data access layer abstraction

---

For detailed API specifications, see `BACKEND.md`
For database schema, see `DATABASE.md`
