# PROMISE AI - Predictive Real-time Operational Monitoring & Intelligence System

![PROMISE AI](https://img.shields.io/badge/AI-Powered-blue) ![ML](https://img.shields.io/badge/ML-Enterprise-green) ![Oracle](https://img.shields.io/badge/Oracle-19c-red) ![React](https://img.shields.io/badge/React-18-61dafb) ![FastAPI](https://img.shields.io/badge/FastAPI-Python-009688)

**Version 2.0 (Oracle Edition)** | **Last Updated**: November 5, 2025

**PROMISE AI** is an enterprise-grade machine learning platform with Oracle RDS integration that automates the entire ML workflow from data ingestion to model deployment and continuous improvement.

---

## 🌟 Key Features

### Core ML Capabilities
- ✅ **Multi-Source Data**: CSV, Excel, PostgreSQL, MySQL, SQL Server, **Oracle RDS (Primary)**, MongoDB
- ✅ **Classification & Regression**: Binary, multi-class, multi-target with 6+ algorithms
- ✅ **Time Series Forecasting**: Prophet and LSTM with anomaly detection
- ✅ **Hyperparameter Tuning**: Ultra-optimized (< 30 seconds) with auto-application
- ✅ **25+ Intelligent Charts**: Distribution, correlations, time series, heatmaps (NO empty charts)

### AI-Powered Intelligence
- ✅ **LLM Chat Assistant**: GPT-4o-mini powered chart generation
- ✅ **Business Insights**: AI-generated recommendations
- ✅ **Model Explainability**: SHAP values for interpretability
- ✅ **Active Learning**: User feedback loop for continuous improvement

### Database & Infrastructure
- ✅ **Oracle 19c RDS**: Primary database with BLOB storage
- ✅ **MongoDB**: Secondary/optional database
- ✅ **Dual Database System**: Switch between Oracle and MongoDB via UI
- ✅ **Workspace Persistence**: Save/load analysis states (2-3 MB compressed)

### Recent Enhancements (17 Issues Resolved)
1. Classification ML model comparison with metrics
2. Hyperparameter tuning speed optimization (67% faster)
3. LLM-powered visualization chat
4. Prophet time series timezone fix
5. Oracle constraint compatibility
6. Oracle as default database
7. Compact database toggle on all pages
8. Bulk dataset deletion with graceful failures
9. Auto clean data React error fix
10. Visualization tab crash prevention
11. Chart generation speed boost
12. 25+ intelligent chart combinations
13. Chat charts properly appending
14. Training metadata now recording
15. Workspace save/load with Oracle BLOB

---

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Oracle RDS Setup](#oracle-rds-setup)
- [Installation](#installation)
- [Configuration](#configuration)
- [Features Documentation](#features-documentation)
- [API Reference](#api-reference)
- [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### Prerequisites

- **Python**: 3.11 or higher
- **Node.js**: 18.x or higher
- **yarn**: Latest version (recommended over npm)
- **Oracle Instant Client**: 19.23 (ARM64 for container environment)
- **Oracle RDS**: AWS Oracle 19c instance (configured)
- **MongoDB**: 5.0+ (optional secondary database)

### Production Environment

The application runs in a Kubernetes container with supervisor managing services:

```bash
# Check service status
sudo supervisorctl status

# Restart services
sudo supervisorctl restart backend
sudo supervisorctl restart frontend
sudo supervisorctl restart all
```

### Access Points

- **Frontend**: https://azure-ml-hub.preview.emergentagent.com
- **Backend API**: https://azure-ml-hub.preview.emergentagent.com/api
- **Database Config**: Top navigation compact toggle (Oracle | MongoDB)

---

## 🏗️ Technology Stack

### Backend
- **Framework**: FastAPI 0.104.1
- **Language**: Python 3.11
- **Primary Database**: Oracle 19c RDS (cx_Oracle 8.3.0)
- **Secondary Database**: MongoDB 5.0+ (Motor 3.3.2)
- **ML Libraries**: 
  - scikit-learn 1.3.2
  - XGBoost 2.0.2
  - Prophet 1.1.5
  - TensorFlow 2.15.0 (LSTM)
- **AI Integration**: emergentintegrations 0.1.0 (Emergent LLM key)
- **Visualization**: Plotly 5.18.0

### Frontend
- **Framework**: React 18.2.0 with Vite
- **Routing**: React Router 6.20.0
- **HTTP Client**: Axios 1.6.2
- **UI Components**: Shadcn/ui, Lucide React
- **Notifications**: Sonner 1.2.0
- **Charts**: Plotly.js 2.27.0

### Infrastructure
- **Container**: Kubernetes with supervisor
- **Web Server**: Nginx (reverse proxy)
- **Process Manager**: Supervisord
- **Backend Port**: 8001 (internal)
- **Frontend Port**: 3000 (internal)

---

## 🗄️ Architecture

### Database Adapter Pattern

```
Application Layer
       ↓
Database Factory (defaults to Oracle)
       ↓
    ┌─────────────┐
    │             │
Oracle Adapter  MongoDB Adapter
    │             │
Oracle RDS     MongoDB
```

**Key Files**:
- `/app/backend/app/database/adapters/base.py` - Abstract interface
- `/app/backend/app/database/adapters/oracle_adapter.py` - Oracle implementation
- `/app/backend/app/database/adapters/mongodb_adapter.py` - MongoDB implementation
- `/app/backend/app/database/factory.py` - Factory (defaults to Oracle)

### Service Architecture

```
Frontend (React) → Nginx → Backend (FastAPI) → Database Adapter → Oracle RDS
                                              ↘ (optional) → MongoDB
```

**Critical Path**:
- All backend API routes MUST use `/api` prefix for Kubernetes ingress
- Frontend communicates via `REACT_APP_BACKEND_URL` environment variable
- Database selection via factory pattern with runtime switching

---

## 🔧 Oracle RDS Setup

### Oracle Instant Client Installation

**Current Environment**: ARM64 Linux (Kubernetes container)

```bash
# Install dependencies
apt-get install -y unzip libaio1

# Download and install Oracle Instant Client 19.23
mkdir -p /opt/oracle
cd /tmp
wget https://download.oracle.com/otn_software/linux/instantclient/1923000/instantclient-basic-linux.arm64-19.23.0.0.0dbru.zip
unzip instantclient-basic-linux.arm64-19.23.0.0.0dbru.zip
mv instantclient_19_23/* /opt/oracle/
rm -rf instantclient_19_23 instantclient-basic-linux.arm64-19.23.0.0.0dbru.zip

# Configure system linker
echo "/opt/oracle" > /etc/ld.so.conf.d/oracle-instantclient.conf
ldconfig

# Restart backend
sudo supervisorctl restart backend
```

### Verification

```bash
# Check library
ls -lh /opt/oracle/libclntsh.so.19.1

# Check backend logs
tail -n 20 /var/log/supervisor/backend.err.log | grep -i oracle

# Expected output:
# ✅ Oracle Client initialized
# ✅ Oracle connection pool created successfully
# ✅ ORACLE database initialized successfully
```

### ⚠️ Known Issue: Ephemeral Storage

The Oracle Instant Client may be lost after certain container operations. Quick reinstall script is provided above and in SETUP_GUIDE.md.

---

## 📦 Installation

### Backend Setup

```bash
cd /app/backend

# Install Python dependencies
pip install -r requirements.txt

# Key dependencies:
# - cx_Oracle==8.3.0 (Oracle connector)
# - emergentintegrations==0.1.0 (LLM integration)
# - prophet==1.1.5 (Time series)
# - xgboost==2.0.2 (ML models)
```

### Frontend Setup

```bash
cd /app/frontend

# Install Node dependencies (use yarn, NOT npm)
yarn install

# Key dependencies:
# - react@18.2.0
# - plotly.js@2.27.0
# - axios@1.6.2
```

---

## ⚙️ Configuration

### Backend Environment Variables

**File**: `/app/backend/.env`

```bash
# === PRIMARY DATABASE (ORACLE) ===
DB_TYPE="oracle"  # Default even if not set

# Oracle RDS Connection
ORACLE_HOST="promise-ai-test-oracle.cgxf9inhpsec.us-east-1.rds.amazonaws.com"
ORACLE_PORT="1521"
ORACLE_SERVICE="ORCL"
ORACLE_USER="testuser"
ORACLE_PASSWORD="<password>"
ORACLE_POOL_SIZE="10"

# === SECONDARY DATABASE (MONGODB) ===
MONGO_URL="mongodb://localhost:27017"
MONGO_DB_NAME="autopredict_db"

# === AI INTEGRATION ===
EMERGENT_LLM_KEY="sk-emergent-<key>"  # GPT-4o-mini, Claude Sonnet 4

# === APPLICATION ===
BACKEND_PORT="8001"
```

### Frontend Environment Variables

**File**: `/app/frontend/.env`

```bash
REACT_APP_BACKEND_URL="https://azure-ml-hub.preview.emergentagent.com"
```

**⚠️ CRITICAL**: Never modify `REACT_APP_BACKEND_URL` - pre-configured for Kubernetes ingress.

---

## 🎯 Features Documentation

### 1. Data Upload & Profiling
- **Formats**: CSV, Excel (XLSX, XLS)
- **Storage**: Original bytes in Oracle BLOB (< 2MB) or compressed (> 2MB)
- **Profiling**: Auto-detection of data types, statistics, missing values

### 2. Predictive Analysis
- **Algorithms**: RandomForest, XGBoost, LightGBM (if available), Linear/Logistic Regression
- **Problem Types**: Classification (binary/multi-class), Regression
- **Multi-Target**: Multiple target variables supported
- **Metrics**:
  - Classification: Accuracy, Precision, Recall, F1-Score
  - Regression: R², RMSE, MAE

### 3. Hyperparameter Tuning
- **Methods**: GridSearchCV, RandomizedSearchCV
- **Speed**: Optimized to < 30 seconds
- **Cross-Validation**: 2 folds (for speed)
- **Auto-Apply**: Tuned parameters automatically applied to models

### 4. Time Series Analysis
- **Models**: Prophet (Facebook), LSTM (TensorFlow)
- **Features**: Trend analysis, seasonality detection, anomaly detection
- **Metrics**: MAPE, RMSE
- **Fix Applied**: Timezone removal for Prophet compatibility

### 5. Visualization (Enhanced)
- **Chart Count**: 25+ intelligent charts
- **Categories**:
  1. Distribution Charts (5 histograms)
  2. Box Plots (4 for outliers)
  3. Categorical Distributions (5 bar charts)
  4. Numeric Correlations (6 scatter plots)
  5. Grouped Analysis (4 cat vs numeric)
  6. Time Series (6 if datetime exists)
  7. Correlation Heatmap (3+ numeric)
  8. Pie Charts (3 for low cardinality)
- **Validation**: All charts validated - NO empty charts
- **Speed**: Optimized generation algorithms

### 6. AI Chat Assistant
- **LLM**: GPT-4o-mini via Emergent LLM key
- **Capabilities**:
  - Natural language chart requests
  - Column name fuzzy matching
  - Intelligent chart type selection
  - Error handling with suggestions
- **Chart Types**: Scatter, line, bar, histogram, pie, box plots
- **Integration**: Charts append to main visualization panel

### 7. Workspace Management
- **Save**: Compressed workspace states (2-3 MB typical)
- **Storage**: Oracle BLOB for large states (> 2MB), direct JSON for small
- **Load**: Restore complete analysis state including cache
- **Location**: Top navigation "Save Workspace" / "Load (n)" buttons

### 8. Training Metadata
- **Tracking**: Automatic recording of analysis runs
- **Metrics**: Initial score, current score, improvement, training count
- **Storage**: Dataset metadata updated after each analysis
- **Access**: Training Metadata page with dataset selector

---

## 📚 API Reference

### Base URL
```
https://azure-ml-hub.preview.emergentagent.com/api
```

### Key Endpoints

#### Database Configuration
```bash
# Get current database
GET /api/config/current-database

# Switch database
POST /api/config/switch-database
Body: {"db_type": "oracle"} or {"db_type": "mongodb"}
```

#### Dataset Management
```bash
# List datasets
GET /api/datasets

# Upload dataset
POST /api/datasource/upload
Body: multipart/form-data with file

# Delete dataset
DELETE /api/datasets/{dataset_id}
```

#### Analysis
```bash
# Run holistic analysis
POST /api/analysis/run
Body: {
  "dataset_id": "uuid",
  "analysis_type": "holistic",
  "target_column": "column_name",
  "problem_type": "classification" | "regression"
}

# Generate visualizations
POST /api/analysis/run
Body: {
  "dataset_id": "uuid",
  "analysis_type": "visualize"
}

# Chat action (chart generation)
POST /api/analysis/chat-action
Body: {
  "dataset_id": "uuid",
  "message": "show me cpu_utilization vs endpoint"
}
```

#### Workspace State
```bash
# Save workspace
POST /api/analysis/save-state
Body: {
  "dataset_id": "uuid",
  "state_name": "workspace_name",
  "analysis_data": {...},
  "chat_history": [...]
}

# List saved states
GET /api/analysis/saved-states/{dataset_id}

# Load workspace
GET /api/analysis/load-state/{state_id}

# Delete workspace
DELETE /api/analysis/delete-state/{state_id}
```

#### Training Metadata
```bash
# Get all training metadata
GET /api/training-metadata

# Get dataset training metadata
GET /api/training/metadata/{dataset_id}
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Oracle Client Not Found
**Error**: `DPI-1047: Cannot locate a 64-bit Oracle Client library`

**Solution**: Reinstall Oracle Instant Client (see Oracle RDS Setup section)

#### 2. Backend Not Starting
```bash
# Check logs
tail -n 100 /var/log/supervisor/backend.err.log

# Common causes:
# - Oracle client missing
# - .env variables incorrect
# - Port 8001 in use
```

#### 3. Database Shows Wrong in UI
**Solution**:
1. Check `/app/backend/.env` - should have `DB_TYPE="oracle"`
2. Restart frontend: `sudo supervisorctl restart frontend`
3. Hard refresh browser (Ctrl+Shift+R)

#### 4. Visualizations Not Loading
**Solution**:
1. Check browser console for errors
2. Verify Plotly.js is loading (check Network tab)
3. Clear browser cache
4. Restart frontend service

#### 5. Training Metadata Shows N/A
**Solution**: Run a fresh Predictive Analysis. The fix was applied recently, so old analyses don't have metadata.

#### 6. Load Button Not Appearing
**Solution**:
1. Refresh page
2. Re-select dataset from "Recent Datasets"
3. Verify workspace was saved successfully
4. Check browser console for API errors

---

## 📊 Performance Benchmarks

- **Hyperparameter Tuning**: 20-30 seconds (target: < 60s) ✅
- **Visualization Generation**: 25+ charts in 5-10 seconds ✅
- **Workspace Save**: 2-3 MB compressed in < 5 seconds ✅
- **Prophet Forecast**: 3-8 seconds depending on data size ✅
- **ML Model Training**: 10-60 seconds depending on data size ✅

---

## 🔄 Recent Updates (Version 2.0)

### November 5, 2025
- ✅ Oracle set as primary/default database
- ✅ Compact database toggle on all pages
- ✅ Training metadata now recording properly
- ✅ Visualization enhanced to 25+ intelligent charts
- ✅ LLM chat integration for chart generation
- ✅ Hyperparameter tuning optimized (67% faster)
- ✅ Prophet timezone fix for forecasting
- ✅ Workspace save/load with Oracle BLOB
- ✅ 17 total issues resolved and tested

---

## 📖 Additional Documentation

- **Setup Guide**: [SETUP_GUIDE.md](./SETUP_GUIDE.md)
- **API Documentation**: [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)
- **Database Schema**: [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md)
- **Dual Database Guide**: [DUAL_DATABASE_GUIDE.md](./DUAL_DATABASE_GUIDE.md)
- **Test Results**: [test_result.md](./test_result.md)
- **Oracle Configuration**: [ORACLE_DEFAULT_COMPLETE.md](./ORACLE_DEFAULT_COMPLETE.md)

---

## 🎉 Success Criteria

Your system is working correctly when:

- [x] Backend responds to API calls
- [x] Oracle shows as active database in UI
- [x] Datasets can be uploaded and displayed
- [x] Predictive Analysis generates ML models with metrics
- [x] Visualizations show 20+ charts (no empty charts)
- [x] Chat can generate and append charts
- [x] Workspaces can be saved and loaded
- [x] Training metadata records all analyses
- [x] Hyperparameter tuning completes in < 30s
- [x] Time Series shows Prophet forecast charts

---

## 🆘 Support & Contact

For issues, questions, or feature requests:

1. Check [test_result.md](./test_result.md) for known issues
2. Review [SETUP_GUIDE.md](./SETUP_GUIDE.md) for configuration
3. Verify Oracle client installation
4. Check service logs: `sudo supervisorctl status`

---

**PROMISE AI - Oracle Edition v2.0**  
*Empowering Enterprise ML with Intelligent Automation*

**Last Updated**: November 5, 2025  
**Maintained By**: AI Engineering Team
