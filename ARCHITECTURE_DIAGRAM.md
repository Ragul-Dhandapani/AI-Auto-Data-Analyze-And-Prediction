# PROMISE AI - Architecture & Data Flow

## System Architecture

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
│  │  • Data Upload UI                                     │  │
│  │  • Dashboard & Visualizations                         │  │
│  │  • Interactive Chat Interface                         │  │
│  │  • Workspace Management                               │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST API
                         │ (axios requests)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   BACKEND (FastAPI)                          │
│                  http://localhost:8001                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  API Endpoints:                                       │  │
│  │  • /api/datasource/upload-file                       │  │
│  │  • /api/analysis/holistic                            │  │
│  │  • /api/analysis/chat-action                         │  │
│  │  • /api/analysis/save-state                          │  │
│  │  • /api/datasource/test-connection                   │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Services:                                            │  │
│  │  • Data Processing (pandas, numpy)                   │  │
│  │  • ML Models (sklearn, xgboost, tensorflow)          │  │
│  │  • Visualization (plotly)                            │  │
│  │  • AI Chat (LLM integration)                         │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────┬──────────────────────────┬─────────────────────┘
           │                          │
           │ MongoDB Driver           │ LLM API
           ▼                          ▼
┌──────────────────────┐    ┌────────────────────────┐
│   MongoDB Database    │    │   Emergent LLM Key     │
│  (localhost:27017)    │    │   or Provider Keys     │
│                       │    │                        │
│  Collections:         │    │  Supports:             │
│  • datasets           │    │  • OpenAI GPT-4o       │
│  • analysis_states    │    │  • Claude Sonnet 4     │
│  • fs.files (GridFS)  │    │  • Gemini              │
│  • fs.chunks          │    │  • GPT-Image-1         │
└──────────────────────┘    └────────────────────────┘
```

---

## Data Flow: Upload to Analysis

```
1. USER UPLOADS FILE
   ├─ Frontend: File selected via drag-drop
   ├─ Chunk upload (if >5MB)
   └─ POST /api/datasource/upload-file
        │
        ▼
2. BACKEND PROCESSING
   ├─ File validation (CSV/Excel)
   ├─ pandas DataFrame creation
   ├─ Data profiling
   │   ├─ Row/column counts
   │   ├─ Data types detection
   │   ├─ Missing values analysis
   │   └─ Summary statistics
   └─ Storage decision:
        ├─ Small (<5MB): Direct MongoDB
        └─ Large (≥5MB): GridFS
             │
             ▼
3. MONGODB STORAGE
   ├─ datasets collection
   │   ├─ Metadata (id, name, columns)
   │   └─ Data preview (first 10 rows)
   └─ GridFS (for large files)
        ├─ fs.files (metadata)
        └─ fs.chunks (actual data)
             │
             ▼
4. AUTOMATIC ANALYSIS
   ├─ ML Model Training
   │   ├─ Linear Regression
   │   ├─ Random Forest
   │   ├─ XGBoost
   │   └─ Decision Tree
   ├─ Chart Generation (up to 15)
   │   ├─ Histograms
   │   ├─ Box plots
   │   ├─ Scatter plots
   │   ├─ Bar charts
   │   └─ Correlation heatmap
   └─ AI Insights Generation
        └─ LLM API call for summaries
             │
             ▼
5. RESULTS TO FRONTEND
   ├─ JSON response with:
   │   ├─ Model scores (R², RMSE)
   │   ├─ Chart data (Plotly JSON)
   │   ├─ AI insights (text)
   │   └─ Recommendations
   └─ Frontend renders:
        ├─ Dashboard with metrics
        ├─ Interactive charts
        └─ Chat interface
```

---

## Workspace Save/Load Flow

```
USER CLICKS "SAVE"
   │
   ▼
Frontend collects state:
   ├─ All analysis data
   ├─ Chart configurations
   ├─ Chat history
   └─ Model results
   │
   ▼
POST /api/analysis/save-state
   │
   ├─ Calculate data size
   │
   ├─ IF size < 10MB:
   │   └─ Store directly in analysis_states collection
   │
   └─ IF size ≥ 10MB:
       ├─ Store data in GridFS
       └─ Store only metadata in analysis_states
   │
   ▼
MongoDB Storage
   ├─ analysis_states (metadata)
   │   ├─ id, dataset_id, state_name
   │   ├─ storage_type (direct/gridfs)
   │   ├─ created_at, updated_at
   │   └─ Data (if small) or gridfs_file_id (if large)
   │
   └─ GridFS (if large)
        ├─ Workspace data as JSON
        └─ Chunked for streaming
   │
   ▼
Return to Frontend
   └─ Success + state_id + storage_type + size_mb
```

---

## Database Connection Flow

```
USER ENTERS DB CREDENTIALS
   │
   ▼
Frontend collects:
   ├─ Database type (PostgreSQL/MySQL/Oracle/SQL Server/MongoDB)
   ├─ Connection details OR
   └─ Connection string
   │
   ▼
POST /api/datasource/test-connection
   │
   ├─ IF connection string provided:
   │   └─ POST /api/datasource/parse-connection-string
   │       └─ Parse to individual parameters
   │
   └─ Test connection with appropriate driver:
        ├─ PostgreSQL: psycopg2
        ├─ MySQL: pymysql
        ├─ Oracle: cx_Oracle
        ├─ SQL Server: pyodbc
        └─ MongoDB: motor
   │
   ▼
IF successful:
   ├─ POST /api/datasource/list-tables
   │   └─ Get list of tables/collections
   │
   └─ User selects table
        │
        ▼
   POST /api/datasource/load-table
        ├─ Execute SELECT * FROM table
        ├─ Load into pandas DataFrame
        ├─ Store in MongoDB (same as file upload)
        └─ Proceed with analysis
```

---

## Configuration Dependencies

```
┌─────────────────────────────────────┐
│         ENVIRONMENT SETUP            │
└─────────────────────────────────────┘
                 │
    ┌────────────┴────────────┐
    ▼                         ▼
┌─────────┐            ┌──────────────┐
│ MongoDB │            │ Emergent Key │
│         │            │  or LLM Keys │
└────┬────┘            └──────┬───────┘
     │                        │
     │ Required               │ Required for
     │ for ALL features       │ AI features only
     │                        │
     ├─ Data storage          ├─ AI insights
     ├─ Workspace save        ├─ Chat interface
     ├─ Analysis results      └─ Smart summaries
     └─ Training metadata

┌─────────────────────────────────────┐
│       OPTIONAL FEATURES              │
└─────────────────────────────────────┘
                 │
    ┌────────────┴────────────┐
    ▼                         ▼
┌──────────────┐      ┌──────────────┐
│ External DBs │      │ MCP Server   │
│ (for testing)│      │ (for agents) │
└──────────────┘      └──────────────┘
     │                        │
     └─ Oracle/MySQL/etc      └─ External AI agents
        (not required)           (not required)
```

---

## Minimum vs Full Setup

### Minimum Setup (Basic Functionality)
```
✅ MongoDB (local or Atlas)
✅ Backend .env with MONGO_URL
✅ Frontend .env (default is fine)

Features Available:
• File upload ✅
• Data profiling ✅
• ML model training ✅
• Chart generation ✅
• Workspace save/load ✅
• Training metadata ✅

Features Limited:
• AI insights ⚠️ (needs LLM key)
• Chat interface ⚠️ (needs LLM key)
```

### Full Setup (All Features)
```
✅ MongoDB
✅ Emergent LLM Key

All Features Available:
• File upload ✅
• Data profiling ✅
• ML model training ✅
• Chart generation ✅
• AI insights ✅
• Chat interface ✅
• Workspace save/load ✅
• Training metadata ✅
• Database connections ✅
```

---

## Storage Architecture

```
MongoDB Database
├─ datasets                    (Collection)
│  ├─ id: UUID
│  ├─ name: String
│  ├─ columns: Array
│  ├─ row_count: Number
│  ├─ data_preview: Array      (First 10 rows)
│  └─ created_at: DateTime
│
├─ analysis_states            (Collection)
│  ├─ id: UUID
│  ├─ dataset_id: UUID
│  ├─ state_name: String
│  ├─ storage_type: "direct" | "gridfs"
│  ├─ analysis_data: Object   (if direct)
│  ├─ gridfs_file_id: ObjectId (if gridfs)
│  ├─ chat_history: Array
│  └─ created_at: DateTime
│
└─ GridFS
   ├─ fs.files                (File metadata)
   │  ├─ _id: ObjectId
   │  ├─ filename: String
   │  ├─ length: Number
   │  └─ metadata: Object
   │
   └─ fs.chunks               (File chunks)
      ├─ files_id: ObjectId
      ├─ n: Number (chunk index)
      └─ data: Binary
```

---

## Scalability Notes

### Current Limits
- File upload: 100MB (configurable)
- GridFS threshold: 5MB
- Workspace size: Unlimited (via GridFS)
- Max charts per analysis: 15
- MongoDB document: 16MB (handled via GridFS)

### Scaling Options
1. **Horizontal Scaling**:
   - Add more backend instances
   - Use load balancer
   - MongoDB replica sets

2. **Vertical Scaling**:
   - Increase server resources
   - Optimize MongoDB indexes
   - Cache frequently accessed data

3. **Cloud Deployment**:
   - MongoDB Atlas (auto-scaling)
   - AWS/GCP/Azure
   - Container orchestration (Kubernetes)

---

**This architecture is designed for easy local setup while being production-ready for scaling!**
