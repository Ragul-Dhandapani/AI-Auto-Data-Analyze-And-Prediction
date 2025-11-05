# PROMISE AI - Complete Setup Guide (Oracle Edition)

**Last Updated**: November 5, 2025  
**Version**: 2.0 (Oracle Primary Database)

This guide provides detailed step-by-step instructions for setting up PROMISE AI with Oracle RDS as the primary database.

---

## 📋 Overview

PROMISE AI is a full-stack AI/ML platform featuring:
- **Backend**: FastAPI (Python 3.11)
- **Frontend**: React.js with Vite
- **Primary Database**: Oracle 19c RDS (AWS)
- **Secondary Database**: MongoDB (optional)
- **AI Integration**: Emergent LLM key (GPT-4o-mini, Claude Sonnet 4)
- **ML Libraries**: scikit-learn, XGBoost, Prophet, LSTM

---

## 🎯 Quick Start (Production Environment)

The application is already deployed and running in a Kubernetes container with:
- ✅ Backend: FastAPI on port 8001
- ✅ Frontend: React on port 3000
- ✅ Oracle RDS: Connected and operational
- ✅ Oracle Instant Client: Pre-installed (may need reinstallation after restarts)

### Service Management

```bash
# Check status
sudo supervisorctl status

# Restart services
sudo supervisorctl restart backend
sudo supervisorctl restart frontend
sudo supervisorctl restart all

# View logs
tail -n 100 /var/log/supervisor/backend.err.log
tail -n 100 /var/log/supervisor/frontend.err.log
```

---

## 🔧 Oracle Instant Client Setup

### Current Configuration

**Location**: `/opt/oracle/`  
**Version**: Oracle Instant Client 19.23 (ARM64)  
**Main Library**: `libclntsh.so.19.1` (50 MB)

### Installation Script

```bash
# Install dependencies
apt-get install -y unzip libaio1

# Create directory
mkdir -p /opt/oracle

# Download Oracle Instant Client
cd /tmp
wget https://download.oracle.com/otn_software/linux/instantclient/1923000/instantclient-basic-linux.arm64-19.23.0.0.0dbru.zip

# Extract and install
unzip instantclient-basic-linux.arm64-19.23.0.0.0dbru.zip
mv instantclient_19_23/* /opt/oracle/
rmdir instantclient_19_23
rm instantclient-basic-linux.arm64-19.23.0.0.0dbru.zip

# Configure system linker
echo "/opt/oracle" > /etc/ld.so.conf.d/oracle-instantclient.conf
ldconfig

# Restart backend
sudo supervisorctl restart backend
```

### Verification

```bash
# Check if library exists
ls -lh /opt/oracle/libclntsh.so.19.1

# Check system linker
ldconfig -p | grep oracle

# Check backend logs
tail -n 20 /var/log/supervisor/backend.err.log | grep -i oracle
```

**Expected Output**:
```
✅ Oracle Client initialized
✅ Oracle connection pool created successfully
✅ ORACLE database initialized successfully
```

---

## 🗄️ Database Configuration

### Oracle RDS (Primary Database)

**File**: `/app/backend/.env`

```bash
# Database Type (PRIMARY)
DB_TYPE="oracle"

# Oracle RDS Configuration
ORACLE_HOST="promise-ai-test-oracle.cgxf9inhpsec.us-east-1.rds.amazonaws.com"
ORACLE_PORT="1521"
ORACLE_SERVICE="ORCL"
ORACLE_USER="testuser"
ORACLE_PASSWORD="<your-password>"
ORACLE_POOL_SIZE="10"
```

### MongoDB (Secondary/Optional)

```bash
# MongoDB Configuration (when DB_TYPE=mongodb)
MONGO_URL="mongodb://localhost:27017"
MONGO_DB_NAME="autopredict_db"
```

### Switching Databases

**Via UI**: Use the compact database toggle (top navigation bar)

**Via Backend**:
```bash
# Change DB_TYPE in .env
nano /app/backend/.env

# Set to oracle or mongodb
DB_TYPE="oracle"

# Restart backend
sudo supervisorctl restart backend
```

**Note**: Oracle is now the default database. Even without DB_TYPE in .env, the system defaults to Oracle.

---

## 🚀 Application Architecture

### Backend Structure

```
/app/backend/
├── .env                          # Environment variables (Oracle config)
├── requirements.txt              # Python dependencies
├── server.py                     # FastAPI entry point
├── app/
│   ├── main.py                   # Application initialization
│   ├── config.py                 # Configuration management
│   ├── database/
│   │   ├── adapters/
│   │   │   ├── base.py          # Abstract database interface
│   │   │   ├── oracle_adapter.py # Oracle RDS implementation
│   │   │   └── mongodb_adapter.py # MongoDB implementation
│   │   ├── factory.py           # Database adapter factory (defaults to Oracle)
│   │   └── oracle_schema.sql   # Oracle DDL (19c compatible)
│   ├── routes/
│   │   ├── analysis.py          # ML analysis endpoints
│   │   ├── datasource.py        # Dataset upload/management
│   │   ├── training.py          # Training metadata
│   │   └── config.py            # Database switching API
│   └── services/
│       ├── ml_service.py        # Machine learning models
│       ├── visualization_service_v2.py # Chart generation (25+ charts)
│       ├── llm_chart_intelligence.py   # LLM-powered chat
│       ├── hyperparameter_service.py   # Tuning (optimized)
│       └── time_series_service.py      # Prophet & LSTM
```

### Frontend Structure

```
/app/frontend/
├── .env                          # REACT_APP_BACKEND_URL
├── package.json                  # Node dependencies
├── src/
│   ├── App.js                   # Main application
│   ├── components/
│   │   ├── CompactDatabaseToggle.jsx  # Database switcher
│   │   ├── DataProfiler.jsx           # Data profiling
│   │   ├── PredictiveAnalysis.jsx     # ML models
│   │   ├── VisualizationPanel.jsx     # Charts (25+ intelligent)
│   │   ├── TimeSeriesAnalysis.jsx     # Forecasting
│   │   └── HyperparameterTuning.jsx   # Model tuning
│   └── pages/
│       ├── HomePage.jsx                # Landing page
│       ├── DashboardPage.jsx          # Main dashboard
│       └── TrainingMetadataPage.jsx   # Metrics tracking
```

---

## 📦 Dependencies

### Backend Python Packages

```txt
# Core Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# Database
cx_Oracle==8.3.0              # Oracle RDS connector
motor==3.3.2                  # MongoDB async driver
pymongo==4.6.0

# Machine Learning
scikit-learn==1.3.2
xgboost==2.0.2
prophet==1.1.5
tensorflow==2.15.0            # For LSTM

# Data Processing
pandas==2.1.3
numpy==1.26.2
plotly==5.18.0

# AI Integration
emergentintegrations==0.1.0   # Emergent LLM key support

# Utilities
python-dotenv==1.0.0
pydantic==2.5.0
```

### Frontend Node Packages

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "axios": "^1.6.2",
    "plotly.js": "^2.27.0",
    "sonner": "^1.2.0",
    "lucide-react": "^0.294.0"
  }
}
```

---

## 🔐 Environment Variables

### Backend (.env)

```bash
# === DATABASE CONFIGURATION ===
DB_TYPE="oracle"                    # PRIMARY: oracle | mongodb

# Oracle RDS (PRIMARY)
ORACLE_HOST="promise-ai-test-oracle.cgxf9inhpsec.us-east-1.rds.amazonaws.com"
ORACLE_PORT="1521"
ORACLE_SERVICE="ORCL"
ORACLE_USER="testuser"
ORACLE_PASSWORD="<password>"
ORACLE_POOL_SIZE="10"

# MongoDB (SECONDARY)
MONGO_URL="mongodb://localhost:27017"
MONGO_DB_NAME="autopredict_db"

# === AI INTEGRATION ===
EMERGENT_LLM_KEY="sk-emergent-<key>"  # Universal key for GPT-4o-mini, Claude

# === APPLICATION ===
BACKEND_PORT="8001"
FRONTEND_URL="https://your-domain.preview.emergentagent.com"
```

### Frontend (.env)

```bash
REACT_APP_BACKEND_URL="https://your-domain.preview.emergentagent.com"
```

**⚠️ CRITICAL**: Never modify `REACT_APP_BACKEND_URL` - it's pre-configured for Kubernetes ingress.

---

## 🧪 Testing the Setup

### 1. Backend Health Check

```bash
curl https://your-domain.preview.emergentagent.com/api/config/current-database
```

**Expected Response**:
```json
{
  "current_database": "oracle",
  "available_databases": ["mongodb", "oracle"]
}
```

### 2. Database Connection Test

```bash
# Check backend logs for Oracle connection
tail -n 50 /var/log/supervisor/backend.err.log | grep -E "Oracle|database"
```

**Expected Output**:
```
✅ Oracle Client initialized
✅ Oracle connection pool created successfully
✅ ORACLE database initialized successfully
```

### 3. Upload Test Dataset

1. Navigate to Dashboard
2. Click "Upload File"
3. Select CSV/Excel file
4. Verify dataset appears in "Recent Datasets"

### 4. Run Predictive Analysis

1. Select dataset
2. Click "Predictive Analysis" tab
3. Select target variable
4. Click "Run Analysis"
5. Verify ML models appear

---

## 🐛 Common Issues & Solutions

### Issue 1: Oracle Client Not Found

**Error**: `DPI-1047: Cannot locate a 64-bit Oracle Client library`

**Solution**:
```bash
# Reinstall Oracle Instant Client
apt-get install -y unzip libaio1
mkdir -p /opt/oracle
cd /tmp
wget -q https://download.oracle.com/otn_software/linux/instantclient/1923000/instantclient-basic-linux.arm64-19.23.0.0.0dbru.zip
unzip -q instantclient-basic-linux.arm64-19.23.0.0.0dbru.zip
mv instantclient_19_23/* /opt/oracle/
rm -rf instantclient_19_23 instantclient-basic-linux.arm64-19.23.0.0.0dbru.zip
echo "/opt/oracle" > /etc/ld.so.conf.d/oracle-instantclient.conf
ldconfig
sudo supervisorctl restart backend
```

### Issue 2: Backend Not Starting

**Check logs**:
```bash
tail -n 100 /var/log/supervisor/backend.err.log
```

**Common causes**:
- Oracle client missing
- Environment variables incorrect
- Port 8001 already in use

### Issue 3: Frontend Can't Connect to Backend

**Check**:
1. Backend is running: `sudo supervisorctl status backend`
2. Backend URL in `/app/frontend/.env` is correct
3. All API routes use `/api` prefix

### Issue 4: Database Switching Not Working

**Solution**:
1. Use compact toggle button (top navigation)
2. Wait 15 seconds for backend restart
3. Refresh page if needed

### Issue 5: Training Metadata Shows N/A

**Solution**:
Run a fresh Predictive Analysis after the recent fix. Old analyses didn't save metadata.

---

## 📊 Feature Summary

### ✅ Implemented Features (17 Issues Resolved)

1. **Classification ML Model Comparison** - Shows accuracy, precision, recall, F1-score
2. **Hyperparameter Tuning** - Optimized to <30 seconds, auto-applies to models
3. **LLM Chat Intelligence** - GPT-4o-mini powered chart generation
4. **Prophet Time Series** - Fixed timezone issues, shows forecast charts
5. **Workspace Save/Load** - Compressed storage in Oracle BLOB
6. **Oracle Primary Database** - Defaults to Oracle on restart
7. **Compact Database Toggle** - On all pages for easy switching
8. **Bulk Dataset Deletion** - Graceful failure handling
9. **Auto Clean Data** - Fixed React rendering error
10. **Visualization Enhancements** - 25+ intelligent charts, no empty charts
11. **Training Metadata** - Now properly records all analysis runs
12. **Multi-Target Prediction** - Supports multiple target variables
13. **NLP Support** - Text data analysis capabilities
14. **Feedback Loop** - Active learning integration
15. **Model Explainability** - SHAP values for interpretability

---

## 🔄 Maintenance

### Daily Tasks

```bash
# Check service status
sudo supervisorctl status

# Monitor logs
tail -f /var/log/supervisor/backend.err.log
```

### Weekly Tasks

```bash
# Verify Oracle client
ls -lh /opt/oracle/libclntsh.so.19.1

# Check database connection
curl https://your-domain/api/config/current-database

# Review disk usage
df -h
```

### As-Needed Tasks

```bash
# Reinstall Oracle client (if missing)
# Use script from "Common Issues" section

# Clear browser cache (if UI issues)
# Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)

# Restart all services
sudo supervisorctl restart all
```

---

## 📝 Additional Resources

- **API Documentation**: `/app/API_DOCUMENTATION.md`
- **Database Schema**: `/app/DATABASE_SCHEMA.md`
- **Dual Database Guide**: `/app/DUAL_DATABASE_GUIDE.md`
- **Test Results**: `/app/test_result.md`
- **Oracle Configuration**: `/app/ORACLE_DEFAULT_COMPLETE.md`

---

## 🎉 Success Criteria

Your setup is successful when:

- [x] Backend responds to API calls
- [x] Oracle database shows as "active" in UI toggle
- [x] Datasets can be uploaded
- [x] Predictive Analysis generates ML models
- [x] Visualizations display 20+ charts
- [x] Chat can create and append charts
- [x] Workspaces can be saved and loaded
- [x] Training metadata records analysis runs

---

## 🆘 Support

If you encounter issues not covered in this guide:

1. Check `/app/test_result.md` for known issues and fixes
2. Review backend logs: `tail -n 200 /var/log/supervisor/backend.err.log`
3. Verify Oracle client: `test -f /opt/oracle/libclntsh.so.19.1 && echo "OK" || echo "MISSING"`
4. Check database connection: `curl <backend-url>/api/config/current-database`

---

**Last Updated**: November 5, 2025  
**Maintained By**: AI Engineering Team  
**Version**: 2.0 (Oracle Primary Edition)
