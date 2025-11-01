# PROMISE AI - Technical Documentation

## Architecture Overview

### Backend Structure (Refactored)

```
backend/
├── app/                          # Main application package
│   ├── __init__.py
│   ├── config.py                 # Configuration and environment settings
│   ├── models/                   # Pydantic models
│   │   ├── __init__.py
│   │   └── pydantic_models.py   # Request/Response models
│   ├── database/                 # Database connections
│   │   ├── __init__.py
│   │   ├── mongodb.py           # MongoDB connection & GridFS
│   │   └── connections.py       # External DB connectors (Oracle, MySQL, etc.)
│   ├── services/                 # Business logic (ready for implementation)
│   │   ├── __init__.py
│   │   ├── data_service.py      # Data processing & profiling
│   │   ├── ml_service.py        # ML training & prediction
│   │   ├── visualization_service.py  # Chart generation
│   │   └── chat_service.py      # Chat logic
│   ├── routes/                   # API endpoints (ready for implementation)
│   │   ├── __init__.py
│   │   ├── datasource.py        # Data source endpoints
│   │   ├── analysis.py          # Analysis endpoints
│   │   └── training.py          # Training metadata endpoints
│   └── utils/                    # Utility functions
│       └── __init__.py
├── tests/                        # Test suite
│   ├── __init__.py
│   └── test_backend_comprehensive.py  # Complete backend tests
├── server.py                     # Legacy monolithic server (still functional)
├── requirements.txt              # Python dependencies
└── pytest.ini                    # Pytest configuration

```

### Frontend Structure

```
frontend/
├── src/
│   ├── components/              # React components
│   │   ├── DataSourceSelector.jsx
│   │   ├── PredictiveAnalysis.jsx
│   │   ├── VisualizationPanel.jsx
│   │   ├── PlotlyChart.jsx
│   │   ├── DataProfiler.jsx
│   │   └── TrainingMetadataDashboard.jsx
│   ├── pages/                   # Page components
│   │   ├── HomePage.jsx
│   │   ├── DashboardPage.jsx
│   │   └── TrainingMetadataPage.jsx
│   ├── tests/                   # Test files
│   │   └── comprehensive.test.tsx
│   ├── setupTests.ts            # Test setup
│   └── App.js                   # Main app component
├── test-config.json             # Jest configuration
└── package.json                 # Dependencies

```

### MCP Server

```
mcp_server/
├── autopredict_mcp.py          # Complete MCP server with 6 tools
└── README.md                    # MCP documentation

```

## Features Implemented

### 1. Multi-Database Support ✅
- **Supported Databases**: PostgreSQL, MySQL, Oracle, SQL Server, MongoDB
- **Connection Methods**: 
  - Individual parameters (host, port, username, password)
  - Connection strings (URL format)
- **Features**:
  - Connection testing
  - Table/collection listing
  - Data loading with pandas
  - Connection string parsing

### 2. Data Analysis Pipeline ✅
- **Data Profiling**: 
  - Row/column counts
  - Missing values analysis
  - Data type detection
  - Summary statistics
- **ML Models**:
  - Linear Regression
  - Random Forest
  - XGBoost
  - Decision Tree
  - LSTM (for time series)
- **Visualizations**:
  - Histograms
  - Box plots
  - Scatter plots
  - Correlation heatmaps
  - Bar charts
  - Line charts
  - Pie charts

### 3. Interactive Features ✅
- **Chat Interface**:
  - Natural language queries
  - Dynamic chart generation (scatter, pie, bar, line)
  - Analysis customization
  - Full chat controls (Clear, New Chat, End Chat with confirmations)
  - Save reminders for unsaved conversations
- **Workspace Management**:
  - Save analysis states
  - Load previous workspaces
  - Chat history persistence
  - Training metadata tracking
  - GridFS for large workspace states

### 4. Training Metadata Dashboard ✅
- **Dataset-wise View**: Shows all datasets with training history
- **Workspace-wise View**: Shows workspaces grouped by dataset
- **Metrics Tracked**:
  - Training count
  - Initial vs current scores
  - Model improvements
  - Last trained timestamp

### 5. MCP Server Tools ✅
1. **upload_dataset**: Upload & profile datasets
2. **get_data_profile**: Comprehensive data profiling
3. **train_ml_models**: Train multiple ML models
4. **generate_visualizations**: Create charts
5. **analyze_correlations**: Correlation analysis
6. **list_datasets**: Dataset management

## Testing Framework

### Backend Tests
**Location**: `/app/backend/tests/test_backend_comprehensive.py`

**Test Coverage**:
- ✅ Data source endpoints (connection string parsing, database connections)
- ✅ File upload (CSV, Excel, duplicate handling, large files)
- ✅ Analysis endpoints (holistic analysis, profiling)
- ✅ Chat functionality (pie charts, correlations, bar charts)
- ✅ State management (save/load workspaces)
- ✅ Training metadata retrieval
- ✅ Data validation and error handling
- ✅ Missing values and edge cases

**Run Tests**:
```bash
cd /app/backend
pytest tests/test_backend_comprehensive.py -v
pytest tests/test_backend_comprehensive.py --cov=app --cov-report=html
```

### Frontend Tests
**Location**: `/app/frontend/src/tests/comprehensive.test.tsx`

**Test Coverage**:
- ✅ DataSourceSelector component (file upload, database connections)
- ✅ PredictiveAnalysis component (analysis display, chat, save)
- ✅ VisualizationPanel component (chart rendering, collapsible sections)
- ✅ DashboardPage integration (tabs, data loading)
- ✅ Error handling (failed uploads, API errors)
- ✅ Accessibility (ARIA labels, keyboard navigation)
- ✅ Performance benchmarks

**Run Tests**:
```bash
cd /app/frontend
yarn test
yarn test:coverage
```

## API Endpoints

### Data Source Endpoints
- `POST /api/datasource/upload-file` - Upload CSV/Excel files
- `POST /api/datasource/test-connection` - Test database connection
- `POST /api/datasource/list-tables` - List database tables
- `POST /api/datasource/load-table` - Load data from table
- `POST /api/datasource/parse-connection-string` - Parse connection string

### Analysis Endpoints
- `POST /api/analysis/holistic` - Comprehensive analysis
- `POST /api/analysis/chat-action` - Chat-based analysis
- `POST /api/analysis/save-state` - Save workspace
- `GET /api/analysis/load-state/{state_id}` - Load workspace
- `GET /api/analysis/saved-states/{dataset_id}` - List workspaces

### Training Endpoints
- `GET /api/training-metadata` - Get all training metadata

## Configuration

### Environment Variables

**Backend** (`/app/backend/.env`):
```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=autopredict_db
EMERGENT_LLM_KEY=your_llm_key
```

**Frontend** (`/app/frontend/.env`):
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

## Development Workflow

### Starting Services
```bash
# Backend
sudo supervisorctl restart backend

# Frontend  
sudo supervisorctl restart frontend

# All services
sudo supervisorctl restart all
```

### Checking Status
```bash
sudo supervisorctl status
```

### Viewing Logs
```bash
# Backend logs
tail -f /var/log/supervisor/backend.out.log
tail -f /var/log/supervisor/backend.err.log

# Frontend logs
tail -f /var/log/supervisor/frontend.out.log
```

## Database Setup for Testing

### Using Docker Compose
```bash
cd /app
docker compose -f docker-compose-testdbs.yml up -d
```

This will start:
- PostgreSQL on port 5432
- MySQL on port 3306
- Oracle on port 1521
- SQL Server on port 1433

### Connection Details
See `/app/DATABASE_TESTING_GUIDE.md` for complete setup instructions.

## Code Quality

### Backend
- **Linting**: Ruff (Python)
- **Type Checking**: Pydantic models
- **Testing**: Pytest with >60% coverage target
- **Code Structure**: Modular, production-ready

### Frontend
- **Linting**: ESLint
- **Testing**: Jest + React Testing Library
- **Code Structure**: Component-based architecture
- **State Management**: React hooks + context

## Future Enhancements

### Backend Refactoring (In Progress)
- [ ] Move all endpoints to `routes/` modules
- [ ] Implement service layer in `services/`
- [ ] Add comprehensive logging in `utils/`
- [ ] Create database migration system

### Testing
- [x] Backend comprehensive tests created
- [x] Frontend comprehensive tests created
- [ ] Run and validate all tests
- [ ] Achieve 80%+ code coverage
- [ ] Add E2E tests with Playwright

### Features
- [ ] Real-time collaboration
- [ ] Advanced ML model deployment
- [ ] Custom model training workflows
- [ ] Data versioning
- [ ] Scheduled analysis jobs

## Troubleshooting

### Backend Not Starting
```bash
# Check logs
tail -n 50 /var/log/supervisor/backend.err.log

# Common issues:
# - Missing dependencies: pip install -r requirements.txt
# - MongoDB not running: check MONGO_URL
# - Port conflicts: check if 8001 is available
```

### Frontend Build Errors
```bash
# Check for syntax errors
yarn build

# Common issues:
# - Missing dependencies: yarn install
# - ESLint errors: check console output
```

### Database Connection Failures
- Verify database is running
- Check connection credentials
- Ensure network connectivity
- For Oracle: verify service name (XEPDB1 for XE)
- For SQL Server: check ODBC driver installation

## Performance Optimization

### Backend
- GridFS for large files (>5MB)
- MongoDB indexing on frequently queried fields
- Caching analysis results
- Async/await for I/O operations

### Frontend
- React.memo for expensive components
- Lazy loading for charts
- Virtual scrolling for large datasets
- Code splitting by route

## Security Considerations

### Current Implementation
- Environment variables for sensitive data
- CORS configuration
- Input validation with Pydantic
- SQL injection prevention (parameterized queries)

### Production Recommendations
- Add authentication/authorization
- Encrypt database credentials
- Rate limiting on API endpoints
- HTTPS enforcement
- API key rotation
- Audit logging

## Support & Maintenance

### Documentation
- API documentation: This file
- Database setup: `/app/DATABASE_TESTING_GUIDE.md`
- MCP server: `/app/mcp_server/README.md`
- Test results: `/app/test_result.md`

### Monitoring
- Backend health: `GET /api/`
- Service status: `sudo supervisorctl status`
- Database connectivity: Test connection endpoints

---

**Last Updated**: November 2025  
**Version**: 2.0.0  
**Maintainer**: PROMISE AI Development Team
