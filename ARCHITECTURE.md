# PROMISE AI - System Architecture

## Overview

PROMISE AI is a full-stack AI/ML-powered data analysis platform built with:
- **Frontend:** React 18 + Tailwind CSS + Shadcn UI
- **Backend:** FastAPI (Python 3.9+) + Modular Architecture  
- **Database:** MongoDB + GridFS
- **ML/AI:** scikit-learn, XGBoost, TensorFlow, Emergent LLM

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         USER                                 │
│                     (Your Browser)                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                          │
│                  http://localhost:3000                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  • HomePage (Landing)                                 │  │
│  │  • DashboardPage (Main interface)                     │  │
│  │  • TrainingMetadataPage (ML tracking)                 │  │
│  │  • DataProfiler Component                             │  │
│  │  • PredictiveAnalysis Component                       │  │
│  │  • VisualizationPanel Component                       │  │
│  │  • Interactive Chat Interface                         │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST API (axios)
                         │ REACT_APP_BACKEND_URL
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   BACKEND (FastAPI)                          │
│                  http://localhost:8001                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  server.py (Entry Point - 18 lines)                  │  │
│  │  └─→ app/main.py (FastAPI instance)                  │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  app/routes/ (API Endpoints)                         │  │
│  │  ├─ datasource.py                                    │  │
│  │  │   ├─ POST /api/datasource/upload-file            │  │
│  │  │   ├─ POST /api/datasource/test-connection        │  │
│  │  │   ├─ POST /api/datasource/list-tables            │  │
│  │  │   └─ POST /api/datasource/load-table             │  │
│  │  ├─ analysis.py                                      │  │
│  │  │   ├─ POST /api/analysis/run                      │  │
│  │  │   ├─ POST /api/analysis/holistic                 │  │
│  │  │   ├─ POST /api/analysis/chat-action              │  │
│  │  │   ├─ POST /api/analysis/save-state               │  │
│  │  │   └─ GET  /api/analysis/load-state/{id}          │  │
│  │  └─ training.py                                      │  │
│  │      ├─ GET /api/training/metadata                   │  │
│  │      └─ GET /api/training/metadata/download-pdf     │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  app/services/ (Business Logic)                      │  │
│  │  ├─ data_service.py (profiling, cleaning)           │  │
│  │  ├─ ml_service.py (model training)                  │  │
│  │  ├─ visualization_service.py (charts)               │  │
│  │  ├─ chat_service.py (AI interactions)               │  │
│  │  └─ chart_insights.py (AI descriptions)             │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  app/database/ (Data Layer)                          │  │
│  │  ├─ mongodb.py (MongoDB + GridFS)                   │  │
│  │  └─ connections.py (External DBs: Oracle,           │  │
│  │                      PostgreSQL, MySQL,              │  │
│  │                      SQL Server, MongoDB)            │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────┬──────────────────────────┬─────────────────────┘
           │                          │
           │ pymongo                  │ emergentintegrations
           ▼                          ▼
┌──────────────────────┐    ┌────────────────────────┐
│   MongoDB Database    │    │   Emergent LLM API     │
│    (localhost:27017)  │    │                        │
│                       │    │  Unified Access:       │
│  Collections:         │    │  • OpenAI GPT-5        │
│  • datasets           │    │  • Claude Sonnet 4     │
│  • saved_states       │    │  • Gemini 2.0          │
│  • fs.files (GridFS)  │    │  • GPT-Image-1         │
│  • fs.chunks (GridFS) │    └────────────────────────┘
└──────────────────────┘
```

---

## Backend Modular Structure

```
backend/
├── server.py                    # Streamlined entry point (18 lines)
│   └─→ Imports app from app/main.py
│
├── app/
│   ├── main.py                  # FastAPI instance, includes routers
│   ├── config.py                # Environment & settings
│   │
│   ├── routes/                  # API endpoint handlers
│   │   ├── datasource.py        # File upload, DB connections
│   │   ├── analysis.py          # Analysis, chat, workspace
│   │   └── training.py          # Training metadata, PDF
│   │
│   ├── services/                # Business logic layer
│   │   ├── data_service.py      # Profiling, cleaning, validation
│   │   ├── ml_service.py        # ML model training
│   │   ├── visualization_service.py  # Chart generation
│   │   ├── chat_service.py      # Chat command processing
│   │   └── chart_insights.py    # AI-powered insights
│   │
│   ├── database/                # Data access layer
│   │   ├── mongodb.py           # MongoDB + GridFS operations
│   │   └── connections.py       # External DB connectors
│   │
│   ├── models/                  # Data models
│   │   └── pydantic_models.py   # Request/Response schemas
│   │
│   └── utils/                   # Helper functions
│       └── __init__.py
│
└── tests/                       # Test suite
    └── test_backend_comprehensive.py
```

**Benefits:**
- ✅ Separation of concerns
- ✅ Easy testing & debugging
- ✅ Reusable components
- ✅ Production-ready
- ✅ Scalable architecture

---

## Data Flow Diagrams

### 1. File Upload Flow

```
┌─────────┐
│  User   │ Drag & drop CSV/Excel
└────┬────┘
     │
     ▼
┌────────────────────────────────────────────────┐
│  Frontend: DataSourceSelector                  │
│  • File validation (type, size)                │
│  • FormData creation                           │
│  • Progress tracking                           │
└────┬───────────────────────────────────────────┘
     │ POST /api/datasource/upload-file
     ▼
┌────────────────────────────────────────────────┐
│  Backend: routes/datasource.py                 │
│  1. Receive file                               │
│  2. Read with pandas                           │
│  3. Profile data (rows, columns, types)        │
│  4. Size check:                                │
│     • <10MB → Direct MongoDB storage          │
│     • ≥10MB → GridFS storage                  │
│  5. Generate preview (first 10 rows)           │
│  6. Save to datasets collection                │
└────┬───────────────────────────────────────────┘
     │
     ▼
┌────────────────────────────────────────────────┐
│  MongoDB: datasets collection                  │
│  {                                             │
│    id: \"uuid\",                                 │
│    name: \"data.csv\",                           │
│    row_count: 1000,                            │
│    column_count: 10,                           │
│    columns: [\"col1\", \"col2\", ...],             │
│    data: [...] or null,  // If <10MB          │
│    storage_type: \"direct\" | \"gridfs\",         │
│    gridfs_file_id: ObjectId or null,          │
│    created_at: ISOString                       │
│  }                                             │
└────┬───────────────────────────────────────────┘
     │
     ▼
┌────────────────────────────────────────────────┐
│  Frontend: Display preview & metadata          │
│  • Show row/column counts                      │
│  • Display column names and types              │
│  • Preview first rows in table                 │
│  • Enable \"Data Profiler\" tab                  │
└────────────────────────────────────────────────┘
```

### 2. Holistic Analysis Flow

```
┌─────────┐
│  User   │ Clicks \"Run Holistic Analysis\"
└────┬────┘
     │
     ▼
┌────────────────────────────────────────────────┐
│  Frontend: PredictiveAnalysis.jsx              │
│  • Show loading (progress bar caps at 90%)     │
│  • Send dataset_id                             │
└────┬───────────────────────────────────────────┘
     │ POST /api/analysis/holistic
     ▼
┌────────────────────────────────────────────────┐
│  Backend: routes/analysis.py                   │
│  1. Load dataset (from MongoDB or GridFS)      │
│  2. Generate data profile                      │
│  3. Train ML models (parallel)                 │
│  4. Generate auto charts (15+)                 │
│  5. Calculate correlations                     │
│  6. Volume analysis                            │
│  7. Generate AI insights                       │
│  8. Package response                           │
└────┬───────────────────────────────────────────┘
     │
     ├─→ services/data_service.py
     │   └─ generate_data_profile()
     │
     ├─→ services/ml_service.py
     │   ├─ Linear Regression
     │   ├─ Random Forest
     │   ├─ XGBoost
     │   ├─ Decision Tree
     │   ├─ LightGBM (optional)
     │   └─ LSTM (optional)
     │
     ├─→ services/visualization_service.py
     │   ├─ Histograms (distributions)
     │   ├─ Box plots (outliers)
     │   ├─ Scatter plots (correlations)
     │   ├─ Bar charts (categorical)
     │   └─ Correlation heatmap
     │
     └─→ services/chat_service.py
         └─ generate_insights() → Emergent LLM
     │
     ▼
┌────────────────────────────────────────────────┐
│  Response:                                     │
│  {                                             │
│    profile: {...},                             │
│    ml_models: [6 models],                      │
│    auto_charts: [15+ charts],                  │
│    correlations: {...},                        │
│    volume_analysis: {...},                     │
│    training_metadata: {...},                   │
│    insights: \"AI-generated text\"              │
│  }                                             │
└────┬───────────────────────────────────────────┘
     │
     ▼
┌────────────────────────────────────────────────┐
│  Frontend: Display Results                     │
│  • ML Model Comparison (tabs)                  │
│  • AI-Generated Charts (2-col grid)            │
│  • Key Correlations section                    │
│  • Volume Analysis breakdown                   │
│  • Training Metadata card                      │
│  • AI Insights summary                         │
└────────────────────────────────────────────────┘
```

### 3. Chat Interaction Flow

```
┌─────────┐
│  User   │ Types: \"Show correlation analysis\"
└────┬────┘
     │
     ▼
┌────────────────────────────────────────────────┐
│  Frontend: Chat Component                      │
│  • Add message to conversation                 │
│  • Show typing indicator                       │
└────┬───────────────────────────────────────────┘
     │ POST /api/analysis/chat-action
     │ { dataset_id, message, conversation_history }
     ▼
┌────────────────────────────────────────────────┐
│  Backend: services/chat_service.py             │
│  1. Analyze message keywords                   │
│  2. Determine action:                          │
│     • \"correlation\" → Generate heatmap         │
│     • \"scatter plot\" → Create scatter chart    │
│     • \"pie/bar/line\" → Generate chart          │
│     • \"remove\" → Delete chart/section          │
│     • Other → Ask LLM                          │
│  3. Execute action                             │
│  4. Return structured response                 │
└────┬───────────────────────────────────────────┘
     │
     ▼
┌────────────────────────────────────────────────┐
│  Response:                                     │
│  {                                             │
│    action: \"add_chart\" | \"remove_section\" |    │
│            \"message\",                           │
│    message: \"Here's the correlation...\",       │
│    chart_data: {                               │
│      type: \"correlation\",                      │
│      title: \"Correlation Heatmap\",             │
│      plotly_data: {...},                       │
│      description: \"Strong correlations...\"     │
│    }                                           │
│  }                                             │
└────┬───────────────────────────────────────────┘
     │
     ▼
┌────────────────────────────────────────────────┐
│  Frontend: Execute Action                      │
│  • action=\"add_chart\" → Append to charts      │
│  • action=\"remove_section\" → Remove display   │
│  • action=\"message\" → Show in chat            │
│  • Render chart with Plotly                    │
│  • Update conversation history                 │
└────────────────────────────────────────────────┘
```

### 4. Workspace Save/Load Flow

```
SAVE:
┌─────────┐
│  User   │ Clicks \"Save Workspace\"
└────┬────┘
     │ Enters workspace name
     ▼
┌────────────────────────────────────────────────┐
│  POST /api/analysis/save-state                 │
│  • Collect all analysis data                   │
│  • Package: profile, models, charts, chat      │
│  • Check size:                                 │
│    - <10MB → Direct MongoDB                   │
│    - ≥10MB → GridFS                           │
│  • Save to saved_states collection             │
│  • Increment dataset.training_count            │
└────┬───────────────────────────────────────────┘
     │
     ▼
┌────────────────────────────────────────────────┐
│  MongoDB: saved_states collection              │
│  {                                             │
│    id: \"uuid\",                                 │
│    dataset_id: \"uuid\",                         │
│    state_name: \"My Analysis 1\",                │
│    analysis_data: {...} or null,               │
│    storage_type: \"direct\" | \"gridfs\",         │
│    gridfs_file_id: ObjectId or null,          │
│    created_at: ISOString                       │
│  }                                             │
└────────────────────────────────────────────────┘

LOAD:
┌─────────┐
│  User   │ Clicks \"Load\" → Selects workspace
└────┬────┘
     │
     ▼
┌────────────────────────────────────────────────┐
│  GET /api/analysis/load-state/{id}             │
│  • Fetch from saved_states                     │
│  • If GridFS, retrieve from fs.files/chunks    │
│  • Return analysis data                        │
└────┬───────────────────────────────────────────┘
     │
     ▼
┌────────────────────────────────────────────────┐
│  Frontend: Restore State                       │
│  • Populate all analysis sections              │
│  • Restore ML models                           │
│  • Render saved charts                         │
│  • Restore chat history                        │
│  • User continues from saved point             │
└────────────────────────────────────────────────┘
```

---

## Technology Stack

### Frontend
| Technology | Purpose | Version |
|-----------|---------|---------|
| React | UI framework | 18.x |
| Tailwind CSS | Styling | 3.x |
| Shadcn UI | Component library | Latest |
| Plotly.js | Charting | Latest |
| Axios | HTTP client | Latest |
| React-Select | Dropdowns | Latest |
| Lucide React | Icons | Latest |
| Sonner | Toast notifications | Latest |

### Backend
| Technology | Purpose | Version |
|-----------|---------|---------|
| FastAPI | Web framework | Latest |
| Python | Language | 3.9+ |
| Pandas | Data processing | Latest |
| NumPy | Numerical computing | Latest |
| scikit-learn | ML algorithms | Latest |
| XGBoost | Gradient boosting | Latest |
| TensorFlow | Deep learning (LSTM) | Latest |
| Plotly | Chart generation | Latest |
| ReportLab | PDF generation | Latest |
| emergentintegrations | LLM integration | Latest |

### Database
| Technology | Purpose | Version |
|-----------|---------|---------|
| MongoDB | Primary database | 7.0+ |
| GridFS | Large file storage | (MongoDB) |
| psycopg2-binary | PostgreSQL driver | Latest |
| pymysql | MySQL driver | Latest |
| cx_Oracle | Oracle driver | Latest |
| pyodbc | SQL Server driver | Latest |

---

## Key Design Decisions

### 1. GridFS for Large Files
**Problem:** MongoDB BSON document limit (16MB)
**Solution:** Automatic GridFS storage for files ≥10MB
**Benefits:** 
- ✅ Supports files up to 16TB
- ✅ Transparent to frontend
- ✅ Efficient streaming
- ✅ Backward compatible

### 2. Modular Backend Architecture
**Problem:** Monolithic 2567-line server.py
**Solution:** Separate concerns into routes/services/database layers
**Benefits:**
- ✅ Easy testing
- ✅ Better maintainability
- ✅ Reusable components
- ✅ Clear separation of concerns

### 3. Progress Bar Intelligence
**Problem:** 100% shown while still processing
**Solution:** Cap at 90% until actual response
**Benefits:**
- ✅ Honest UX
- ✅ Better user expectations
- ✅ Contextual messages

### 4. Chart Validation (4 Layers)
**Problem:** Empty or broken charts
**Solution:** Multiple validation layers
**Benefits:**
- ✅ No empty charts
- ✅ Better error handling
- ✅ Improved UX

### 5. Emergent LLM Integration
**Problem:** Multiple LLM provider integrations
**Solution:** Single universal key
**Benefits:**
- ✅ Simple configuration
- ✅ Multi-provider support
- ✅ Easy switching

---

## Security Considerations

**Implemented:**
- ✅ Environment variables for sensitive data
- ✅ CORS configuration
- ✅ Input validation (Pydantic)
- ✅ SQL injection prevention (parameterized queries)

**Production Recommendations:**
- [ ] Add authentication/authorization
- [ ] Encrypt database credentials
- [ ] Rate limiting on API endpoints
- [ ] HTTPS enforcement
- [ ] API key rotation
- [ ] Audit logging

---

## Scalability

**Current Architecture Supports:**
- Horizontal scaling of backend (stateless)
- MongoDB replica sets
- GridFS for unlimited file sizes
- Kubernetes deployment ready
- Docker containerization

**Future Enhancements:**
- Load balancers
- Caching layer (Redis)
- Message queues for long-running tasks
- Microservices architecture

---

## Summary

PROMISE AI uses a modern, modular architecture designed for:
- ✅ **Maintainability:** Clear separation of concerns
- ✅ **Scalability:** Stateless backend, GridFS, Kubernetes
- ✅ **User Experience:** Intelligent UI, real-time feedback
- ✅ **Flexibility:** Multiple data sources, 6 ML models
- ✅ **Production-Ready:** Docker, Kubernetes, comprehensive testing

**All components work together seamlessly to provide a powerful, user-friendly data analysis platform.**
