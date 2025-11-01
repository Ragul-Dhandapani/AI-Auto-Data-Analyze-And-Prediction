# PROMISE AI - Complete System Documentation
**Version:** 2.0 (Post-Refactoring + UI/UX Enhancements)  
**Last Updated:** November 2025  
**Status:** Production Ready - All Features Verified

---

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Backend Structure](#backend-structure)
4. [Frontend Structure](#frontend-structure)
5. [API Endpoints](#api-endpoints)
6. [Database Collections](#database-collections)
7. [Data Flow](#data-flow)
8. [Features](#features)
9. [Setup & Deployment](#setup--deployment)
10. [MCP Server Integration](#mcp-server-integration)

---

## System Overview

PROMISE AI is an AI/ML-powered data analysis platform that:
- Accepts CSV/Excel file uploads and database connections
- Automatically cleans, prepares, and analyzes data
- Trains multiple ML models (Linear Regression, Random Forest, XGBoost, Decision Tree, LSTM)
- Generates intelligent visualizations and insights
- Provides chat interface for custom analysis
- Manages workspaces for saving analysis states
- Tracks training metadata across sessions

**Tech Stack:**
- **Backend:** FastAPI (Python 3.9+)
- **Frontend:** React 18 with Tailwind CSS
- **Database:** MongoDB with GridFS
- **ML:** scikit-learn, XGBoost, LightGBM, TensorFlow (LSTM)
- **Visualization:** Plotly.js
- **AI:** Emergent LLM Integration

---

## Architecture

### High-Level Architecture
```
┌─────────────┐
│   Browser   │
│  (React)    │
└──────┬──────┘
       │ HTTP/REST
       ▼
┌─────────────┐
│   Nginx     │
│  (Reverse   │
│   Proxy)    │
└──────┬──────┘
       │
       ├──────────────────┐
       │                  │
       ▼                  ▼
┌─────────────┐    ┌─────────────┐
│  Frontend   │    │  Backend    │
│  (Port 3000)│    │ (Port 8001) │
└─────────────┘    └──────┬──────┘
                          │
                          ▼
                   ┌─────────────┐
                   │  MongoDB    │
                   │ + GridFS    │
                   └─────────────┘
```

### Service Communication
- **Frontend → Backend:** via `REACT_APP_BACKEND_URL` with `/api` prefix
- **Backend → MongoDB:** via `MONGO_URL` environment variable
- **Backend → Emergent LLM:** via `EMERGENT_LLM_KEY`

---

## Backend Structure

### Refactored Modular Architecture
```
backend/
├── server.py                    # Entry point (18 lines)
├── requirements.txt
├── pytest.ini
├── app/
│   ├── __init__.py
│   ├── config.py               # Configuration
│   ├── main.py                 # Main FastAPI app
│   ├── database/
│   │   ├── __init__.py
│   │   ├── mongodb.py          # MongoDB & GridFS
│   │   └── connections.py      # External DB connectors
│   ├── models/
│   │   ├── __init__.py
│   │   └── pydantic_models.py  # Request/Response models
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── datasource.py       # File upload, DB connections
│   │   ├── analysis.py         # Analysis, chat, workspace
│   │   └── training.py         # Training metadata, PDF
│   ├── services/
│   │   ├── __init__.py
│   │   ├── data_service.py     # Data profiling, cleaning
│   │   ├── ml_service.py       # ML model training
│   │   ├── visualization_service.py  # Chart generation
│   │   ├── chat_service.py     # Chat actions
│   │   └── chart_insights.py   # AI-powered insights
│   └── utils/
│       └── __init__.py
└── tests/
    └── test_backend_comprehensive.py
```

### Key Backend Files

#### **server.py** (Entry Point)
- Imports and runs the main FastAPI app from `app.main`
- Minimal wrapper for clean separation

#### **app/main.py** (Core Application)
- Creates FastAPI app instance
- Includes all routers (datasource, analysis, training)
- Defines backward compatibility routes
- Configures CORS

#### **app/routes/datasource.py** (Data Source Management)
**Endpoints:**
- `POST /datasource/upload-file` - Upload CSV/Excel files
- `POST /datasource/test-connection` - Test database connections
- `POST /datasource/list-tables` - List tables from database
- `POST /datasource/load-table` - Load data from database table
- `POST /datasource/parse-connection-string` - Parse connection strings
- `DELETE /datasource/datasets/{id}` - Delete dataset

**Supported Databases:**
- PostgreSQL
- MySQL
- Oracle
- SQL Server
- MongoDB

#### **app/routes/analysis.py** (Core Analysis)
**Endpoints:**
- `POST /analysis/run` - Run specific analysis (profile, clean, visualize, insights)
- `POST /analysis/holistic` - Complete analysis with ML models
- `POST /analysis/chat-action` - Handle chat requests
- `POST /analysis/save-state` - Save workspace
- `GET /analysis/load-state/{id}` - Load workspace
- `GET /analysis/saved-states/{dataset_id}` - Get all workspaces for dataset
- `DELETE /analysis/delete-state/{id}` - Delete workspace

#### **app/routes/training.py** (Training Metadata)
**Endpoints:**
- `GET /training/metadata` - Get training metadata for all datasets
- `GET /training/metadata/download-pdf/{dataset_id}` - Download PDF report

#### **app/services/ml_service.py** (ML Training)
**Models Trained:**
1. Linear Regression
2. Random Forest
3. XGBoost
4. Decision Tree
5. LightGBM (optional)
6. LSTM Neural Network (optional, requires TensorFlow)

**Features:**
- Automatic target column selection
- Train/test split (80/20)
- Feature importance calculation
- Confidence levels (High/Medium/Low)
- R² score and RMSE metrics

#### **app/services/visualization_service.py** (Chart Generation)
**Chart Types:**
- Histograms (distribution analysis)
- Box plots (outlier detection)
- Scatter plots (correlation)
- Bar charts (categorical distribution)
- Correlation heatmap

**Features:**
- Automatic chart recommendation
- AI-powered descriptions
- Validation to prevent empty charts
- Responsive sizing (no fixed widths)

#### **app/services/chat_service.py** (Interactive Chat)
**Supported Commands:**
- "show correlation analysis"
- "create scatter plot of X vs Y"
- "add pie chart"
- "show bar chart"
- "add line chart"
- "remove correlation"
- "remove [chart_type]"

**Response Types:**
- `add_chart` - Add new visualization
- `remove_section` - Remove existing chart
- `message` - Text response

---

## Frontend Structure

### React Component Architecture
```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── App.js                  # Main app component
│   ├── App.css
│   ├── index.js
│   ├── index.css
│   ├── components/
│   │   ├── DataSourceSelector.jsx      # File/DB upload
│   │   ├── DataProfiler.jsx            # Data profiling
│   │   ├── PredictiveAnalysis.jsx      # ML analysis & chat
│   │   ├── VisualizationPanel.jsx      # Visualization tab
│   │   ├── PlotlyChart.jsx             # Plotly chart wrapper
│   │   ├── TrainingMetadataDashboard.jsx
│   │   └── ui/                         # Shadcn components
│   ├── pages/
│   │   ├── HomePage.jsx                # Landing page
│   │   ├── DashboardPage.jsx           # Main dashboard
│   │   └── TrainingMetadataPage.jsx    # Training metadata
│   ├── setupTests.ts
│   └── tests/
│       └── comprehensive.test.tsx
├── package.json
├── tailwind.config.js
├── postcss.config.js
└── test-config.json
```

### Key Frontend Components

#### **DashboardPage.jsx**
- Recent datasets display with grid layout
- Multi-select delete functionality
- Load/delete dataset actions
- Quick stats display

#### **DataSourceSelector.jsx**
- File upload (drag & drop)
- Database connection form
- Support for 5 database types
- Connection string parser

#### **DataProfiler.jsx**
- Summary statistics cards (Total Rows, Columns, Missing Values, Duplicates)
- **Missing Values Details** section with 2-liner explanation:
  - "Shows columns with incomplete data (null, NaN, empty, or undefined values)"
  - "Missing data can affect analysis accuracy and model performance - consider cleaning or imputing these values"
- Column-level analysis with accordion view
- Data cleaning actions with before/after comparison
- AI insights generation
- Expand/Collapse all sections functionality

#### **PredictiveAnalysis.jsx**
- Holistic analysis trigger
- ML Model Comparison (5+ models)
- Auto-generated charts (11-15)
- Custom charts via chat
- Key correlations display
- Volume analysis
- Training metadata
- Workspace save/load

#### **TrainingMetadataPage.jsx**
- Modern dropdown navigation with react-select
- Dataset selection dropdown
- Multi-select workspaces dropdown
- Model performance comparison (Initial vs Current scores)
- Improvement percentage display
- PDF download (complete & filtered reports)

---

## API Endpoints

### Complete API Reference

#### **Data Source Endpoints**
```
POST   /api/datasource/upload-file
POST   /api/datasource/test-connection
POST   /api/datasource/list-tables
POST   /api/datasource/load-table
POST   /api/datasource/parse-connection-string
DELETE /api/datasource/datasets/{id}
```

#### **Analysis Endpoints**
```
POST   /api/analysis/run
POST   /api/analysis/holistic
POST   /api/analysis/chat-action
POST   /api/analysis/save-state
GET    /api/analysis/load-state/{id}
GET    /api/analysis/saved-states/{dataset_id}
DELETE /api/analysis/delete-state/{id}
```

#### **Training Metadata Endpoints**
```
GET /api/training/metadata
GET /api/training/metadata/download-pdf/{dataset_id}
```

#### **Backward Compatibility**
```
GET    /api/datasets
DELETE /api/datasets/{id}
GET    /api/training-metadata
```

### API Request/Response Examples

#### Upload File
```bash
POST /api/datasource/upload-file
Content-Type: multipart/form-data

Response:
{
  "id": "uuid-here",
  "name": "data.csv",
  "row_count": 1000,
  "column_count": 10,
  "columns": ["col1", "col2", ...],
  "preview": [...],
  "created_at": "2025-11-01T12:00:00Z"
}
```

#### Holistic Analysis
```bash
POST /api/analysis/holistic
{
  "dataset_id": "uuid-here"
}

Response:
{
  "profile": {...},
  "ml_models": [{model_name, r2_score, rmse, confidence, ...}, ...],
  "auto_charts": [{title, description, plotly_data, ...}, ...],
  "correlations": {correlations: [...], matrix: {...}},
  "volume_analysis": {...},
  "training_metadata": {...},
  "insights": "AI-generated insights..."
}
```

#### Chat Action
```bash
POST /api/analysis/chat-action
{
  "dataset_id": "uuid-here",
  "message": "show correlation analysis",
  "conversation_history": []
}

Response:
{
  "action": "add_chart",
  "message": "Here's the correlation analysis",
  "chart_data": {
    "type": "correlation",
    "title": "Correlation Heatmap",
    "plotly_data": {...},
    "description": "...",
    "correlations": [...]
  }
}
```

---

## Database Collections

### MongoDB Schema

#### **datasets** Collection
```javascript
{
  id: String (UUID),
  name: String,
  row_count: Number,
  column_count: Number,
  columns: [String],
  data: [Object] | null,  // Direct storage for small files
  storage_type: "direct" | "gridfs",
  gridfs_file_id: ObjectId | null,  // For large files
  source_type: "file" | "database",
  created_at: ISOString,
  updated_at: ISOString,
  training_count: Number
}
```

#### **saved_states** Collection
```javascript
{
  id: String (UUID),
  dataset_id: String,
  state_name: String,
  analysis_data: {
    profile: Object,
    ml_models: [Object],
    auto_charts: [Object],
    custom_charts: [Object],
    correlations: Object,
    conversation_history: [Object]
  },
  created_at: ISOString,
  storage_type: "direct" | "gridfs",
  gridfs_file_id: ObjectId | null
}
```

#### **fs.files** & **fs.chunks** (GridFS)
Used for storing large files (>10MB) and large workspace states (>10MB)

---

## Data Flow

### Complete User Journey

#### 1. File Upload Flow
```
User uploads CSV → Frontend sends to /api/datasource/upload-file
                 ↓
Backend reads file → Checks size
                 ↓
If <10MB: Store in datasets.data
If ≥10MB: Store in GridFS, save gridfs_file_id
                 ↓
Generate preview → Return metadata to frontend
                 ↓
Frontend displays preview and column info
```

#### 2. Holistic Analysis Flow
```
User clicks Predictive Analysis → POST /api/analysis/holistic
                                ↓
Backend loads dataset (direct or GridFS)
                                ↓
1. Generate data profile
2. Train ML models (5-6 models)
3. Generate auto charts (11-15 charts)
4. Calculate correlations
5. Generate volume analysis
6. Create AI insights
                                ↓
Return complete analysis to frontend
                                ↓
Frontend renders:
- ML Model Comparison tabs
- Auto-generated charts (2-column grid)
- Key Correlations section
- Volume Analysis
- Training Metadata
- AI Insights
```

#### 3. Chat Interaction Flow
```
User types message → POST /api/analysis/chat-action
                  ↓
Backend analyzes message keywords
                  ↓
Match action type:
- Correlation → Generate heatmap
- Scatter → Create scatter plot
- Pie/Bar/Line → Generate chart
- Remove → Identify chart to remove
- General → LLM response
                  ↓
Return action + chart_data
                  ↓
Frontend executes action:
- add_chart → Append to custom charts
- remove_section → Remove from display
- message → Show in chat
```

#### 4. Workspace Save Flow
```
User clicks Save Workspace → Enters name → POST /api/analysis/save-state
                           ↓
Backend collects:
- Current analysis_data
- ML models
- All charts (auto + custom)
- Conversation history
                           ↓
Check size:
If <10MB: Save in saved_states.analysis_data
If ≥10MB: Save to GridFS, store gridfs_file_id
                           ↓
Increment dataset.training_count
                           ↓
Return success
                           ↓
Frontend shows success toast
```

#### 5. Training Metadata Flow
```
User opens Training Metadata page → GET /api/training-metadata
                                  ↓
Backend:
1. Fetch all datasets
2. Fetch all saved_states
3. Group states by dataset_id
4. Calculate:
   - training_count (# of workspaces)
   - last_trained (latest workspace date)
   - initial_scores (first workspace models)
   - current_scores (latest workspace models)
   - improvement_percentage
                                  ↓
Return metadata array
                                  ↓
Frontend displays:
- Dropdown 1: Select dataset
- Dropdown 2: Multi-select workspaces
- Model Performance comparison
- PDF download buttons
```

---

## Features

### Core Features

#### 1. Multi-Source Data Ingestion
- CSV/Excel file upload
- Database connections (5 types)
- Connection string parsing
- GridFS for large files (>10MB)
- Drag & drop interface

#### 2. Automatic Data Analysis
- Data profiling (row/column counts, missing values, duplicates)
- Data cleaning with reports
- Outlier detection
- Distribution analysis
- AI-powered insights

#### 3. ML Model Training
- Automatic target selection
- 5-6 models trained simultaneously
- Performance metrics (R², RMSE, confidence)
- Feature importance
- Model comparison interface

#### 4. Intelligent Visualizations
- 11-15 auto-generated charts
- Correlation heatmaps
- Interactive Plotly charts
- Responsive design (no overflow)
- AI-generated descriptions

#### 5. Interactive Chat
- Natural language queries
- Custom chart generation (scatter, pie, bar, line)
- Chart removal commands
- Conversation history
- Context-aware responses
- Chat controls: Clear, New Chat, End Chat
- Save reminder when closing chat with unsaved messages

#### 6. Workspace Management
- Save analysis states
- Load previous analyses
- Named workspaces
- Chat history persistence
- GridFS for large states

#### 7. Training Metadata Tracking
- Dataset-level tracking
- Workspace-level tracking
- Model performance history
- Improvement trends
- PDF report generation

### Advanced Features

#### GridFS Integration
- Automatic size detection
- Transparent storage/retrieval
- Supports files up to 16TB
- Backward compatible

#### Chart Validation & Overflow Fix
- Prevents empty charts with multi-layer validation
- Validates plotly_data structure
- Filters invalid charts
- Tracks skipped charts
- **PERMANENT FIX for chart overflow issues:**
  - Charts use responsive containers (no fixed widths)
  - PlotlyChart.jsx enforces container boundaries
  - Backend removes fixed width/height from layouts
  - All charts fit within UI containers perfectly

#### Boolean Column Handling
- Excludes from numeric operations
- Treats as categorical
- Prevents numpy errors

#### AI-Powered Insights
- Emergent LLM integration
- Data quality analysis
- Pattern detection
- Actionable recommendations
- Chart-specific insights generation

#### UI/UX Enhancements
- **Progress Bar Intelligence:** Caps at 90% until completion (prevents misleading 100%)
- **Chat Controls:** Clear, New Chat, End Chat buttons with confirmations
- **Model Descriptions:** Info icon tooltips with proper text wrapping
- **Missing Values Clarity:** 2-liner description explaining impact and recommendations
- **Recent Datasets:** Multi-select delete functionality with grid layout
- **Training Metadata:** Modern dropdowns with multi-select using react-select
- **Consistent Branding:** All instances updated to \"PROMISE AI\"

---

## Setup & Deployment

### Environment Variables

#### Backend (.env)
```bash
MONGO_URL=mongodb://localhost:27017/promise_ai
EMERGENT_LLM_KEY=sk-emergent-xxxxx
```

#### Frontend (.env)
```bash
REACT_APP_BACKEND_URL=http://your-backend-url
```

### Installation

#### Backend
```bash
cd backend
pip install -r requirements.txt
python server.py
```

#### Frontend
```bash
cd frontend
yarn install
yarn start
```

#### Using Docker
```bash
docker-compose up -d
```

### Dependencies

#### Backend Key Dependencies
- fastapi
- uvicorn
- pymongo
- motor
- pandas
- numpy
- scikit-learn
- xgboost
- lightgbm (optional)
- tensorflow (optional, for LSTM)
- plotly
- emergentintegrations
- reportlab (for PDF)
- cx_Oracle
- psycopg2-binary
- pymysql
- pyodbc

#### Frontend Key Dependencies
- react
- react-router-dom
- axios
- plotly.js
- tailwindcss
- shadcn/ui
- lucide-react
- react-select
- sonner (toast notifications)

---

## MCP Server Integration

### Purpose
Exposes PROMISE AI functionality to other AI agents for:
- Automated data analysis
- Programmatic access
- Agent-to-agent communication
- External integrations

### Available Tools
(See mcp_server/README.md for complete API)

---

## Troubleshooting

### Common Issues

#### Frontend not loading
```bash
# Check if port 3000 is free
lsof -i:3000
# Kill process if needed
kill -9 <PID>
# Restart
sudo supervisorctl restart frontend
```

#### Backend errors
```bash
# Check logs
tail -f /var/log/supervisor/backend.err.log
# Restart
sudo supervisorctl restart backend
```

#### Charts overflowing
- Already fixed in current version
- Charts use responsive containers
- No fixed widths in backend chart generation

#### Boolean column errors
- Already fixed in current version
- Boolean columns excluded from numeric operations

---

## Version History

### v2.0 (November 1, 2025) - Current
- Complete backend refactoring to modular structure
- Training Metadata redesign with dropdown navigation
- Multi-select delete for datasets
- Chart overflow fixes (4-layer solution)
- Boolean column handling
- LSTM model integration
- AI insights with Emergent LLM
- PDF report generation
- GridFS for large files
- Comprehensive documentation

### v1.0 (Original)
- Monolithic backend (2567 lines)
- Basic analysis and visualization
- File upload only
- Simple workspace management

---

## Future Enhancements

### Planned Features
- Real-time collaboration
- Advanced ML model tuning
- Custom model upload
- Data versioning
- Scheduled analysis
- Email reports
- API rate limiting
- User authentication

---

## Support & Contact

For issues, questions, or contributions:
- Check this documentation first
- Review test_result.md for recent changes
- Check backend logs for errors
- Use MCP server for automated access

---

**END OF DOCUMENTATION**

*This is a living document. Update as features are added or changed.*
