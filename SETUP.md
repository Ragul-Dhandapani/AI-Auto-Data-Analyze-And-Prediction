# PROMISE AI - Local Machine Setup Guide

## 🚀 Quick Start

PROMISE AI is an enterprise-grade AI/ML platform for data analysis and prediction with Oracle RDS 19c and Azure OpenAI integration.

---

## 📋 Prerequisites

### Required Software
- **Python**: 3.11+
- **Node.js**: 18.x or 20.x
- **Yarn**: 1.22+
- **Oracle Instant Client**: 19.23 (ARM64)
- **Database**: Oracle RDS 19c or MongoDB

### System Requirements
- **OS**: Linux (Ubuntu 22.04+), macOS, or Windows WSL2
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **Architecture**: ARM64 or x86_64

---

## 🔧 Installation Steps

### 1. Clone Repository
```bash
git clone <repository-url>
cd promise-ai
```

### 2. Backend Setup

#### 2.1 Install Oracle Instant Client (for Oracle DB)

**For Linux ARM64:**
```bash
# Download Oracle Instant Client
cd /tmp
wget https://download.oracle.com/otn_software/linux/instantclient/1923000/instantclient-basic-linux.arm64-19.23.0.0.0dbru.zip

# Install dependencies
sudo apt-get update
sudo apt-get install -y unzip libaio1

# Extract and configure
sudo unzip instantclient-basic-linux.arm64-19.23.0.0.0dbru.zip -d /opt/oracle/
sudo sh -c "echo /opt/oracle/instantclient_19_23 > /etc/ld.so.conf.d/oracle-instantclient.conf"
sudo ldconfig

# Verify installation
ls -la /opt/oracle/instantclient_19_23/libclntsh.so*
```

**For Linux x86_64:**
```bash
wget https://download.oracle.com/otn_software/linux/instantclient/1923000/instantclient-basic-linux.x64-19.23.0.0.0dbru.zip
# Rest is same as ARM64
```

**For macOS:**
```bash
brew install instantclient-basic
```

#### 2.2 Install Python Dependencies
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

#### 2.3 Configure Environment Variables
```bash
cp .env.example .env
nano .env
```

**Required Environment Variables:**
```env
# Database Configuration (Choose ONE)
DB_TYPE="oracle"  # or "mongodb"

# Oracle Database (if DB_TYPE="oracle")
ORACLE_DSN="(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=your-host.rds.amazonaws.com)(PORT=1521))(CONNECT_DATA=(SID=ORCL)))"
ORACLE_USER="admin"
ORACLE_PASSWORD="your-password"
ORACLE_POOL_MIN=2
ORACLE_POOL_MAX=10

# MongoDB (if DB_TYPE="mongodb")
MONGO_URL="mongodb://localhost:27017/promise_ai"

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
AZURE_OPENAI_KEY="your-api-key"
AZURE_OPENAI_API_VERSION="2024-12-01-preview"
AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4o"

# Backend Configuration
REACT_APP_BACKEND_URL="http://localhost:8001"
```

#### 2.4 Initialize Oracle Database Schema
```bash
python init_oracle_schema.py
```

#### 2.5 Start Backend Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8001
INFO:     Application startup complete.
```

---

### 3. Frontend Setup

#### 3.1 Install Dependencies
```bash
cd frontend
yarn install
```

#### 3.2 Configure Environment
```bash
cp .env.example .env
nano .env
```

**Frontend .env:**
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

#### 3.3 Start Frontend Server
```bash
yarn start
```

**Expected Output:**
```
Compiled successfully!
You can now view promise-ai in the browser.
  Local:            http://localhost:3000
```

---

## 🧪 Verify Installation

### Backend Health Check
```bash
curl http://localhost:8001/health
```

**Expected Response:**
```json
{"status":"healthy","version":"2.0.0"}
```

### Database Connection Test
```bash
curl http://localhost:8001/api/datasets
```

**Expected Response:**
```json
{"datasets":[]}
```

### Frontend Access
Open browser: http://localhost:3000

---

## 📦 Key Python Packages

```txt
fastapi==0.115.5
uvicorn==0.32.1
pandas==2.2.3
scikit-learn==1.5.2
xgboost==2.1.2
cx-Oracle==8.3.0
pymongo==4.10.1
openai==1.54.5
prophet==1.1.6
numpy==1.26.4
```

---

## 🔑 API Keys Setup

### Azure OpenAI
1. Go to Azure Portal → Your OpenAI Resource
2. Navigate to "Keys and Endpoint"
3. Copy:
   - Endpoint URL
   - API Key
   - Deployment Name
4. Add to backend/.env

### Oracle RDS
1. AWS Console → RDS → Your Oracle Instance
2. Copy connection details
3. Ensure Security Group allows your IP
4. Test connection: `sqlplus admin/password@your-host:1521/ORCL`

---

## 🐛 Troubleshooting

### Issue: Oracle Client Library Not Found

**Error:**
```
DPI-1047: Cannot locate a 64-bit Oracle Client library
```

**Solution:**
```bash
# Verify library path
ls /opt/oracle/instantclient_19_23/libclntsh.so*

# Update LD config
sudo sh -c "echo /opt/oracle/instantclient_19_23 > /etc/ld.so.conf.d/oracle-instantclient.conf"
sudo ldconfig

# Verify
ldconfig -p | grep oracle
```

### Issue: Backend Not Starting

**Error:** `ModuleNotFoundError: No module named 'cx_Oracle'`

**Solution:**
```bash
cd backend
source .venv/bin/activate
pip install cx_Oracle==8.3.0
```

### Issue: Frontend Build Fails

**Error:** `ERESOLVE unable to resolve dependency tree`

**Solution:**
```bash
rm -rf node_modules yarn.lock
yarn install --network-timeout 100000
```

### Issue: Azure OpenAI 404 Error

**Error:** `DeploymentNotFound: The API deployment for this resource does not exist`

**Solution:**
1. Check Azure Portal → Deployments
2. Verify deployment name exactly matches
3. Update AZURE_OPENAI_DEPLOYMENT_NAME in .env
4. Common names: `gpt-4o`, `gpt-4`, `gpt-35-turbo`

---

## 🚢 Production Deployment

### Using Docker
```bash
docker-compose up -d
```

### Using Supervisor (Linux)
```bash
sudo supervisorctl restart all
```

### Environment-Specific Configs
- **Development**: Use `.env.development`
- **Staging**: Use `.env.staging`
- **Production**: Use `.env.production`

---

## 📊 Default Ports

- **Backend API**: 8001
- **Frontend**: 3000
- **MongoDB**: 27017 (if used)
- **Oracle**: 1521 (if used)

---

## 🎯 Next Steps

After successful setup:
1. Upload your first dataset
2. Run holistic analysis
3. Explore 35+ ML models
4. Try Azure OpenAI chat features
5. Check Training Metadata page

For detailed API documentation, see `BACKEND.md`
