# PROMISE AI Platform - Local Setup Guide

Complete guide for setting up the PROMISE AI platform on Windows, macOS, and Linux.

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Windows Setup](#windows-setup)
3. [macOS Setup](#macos-setup)
4. [Linux Setup](#linux-setup)
5. [Database Configuration](#database-configuration)
6. [Environment Variables](#environment-variables)
7. [Running the Application](#running-the-application)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software (All Platforms)
- **Python 3.11+**: [Download](https://www.python.org/downloads/)
- **Node.js 18+ and npm/yarn**: [Download](https://nodejs.org/)
- **Git**: [Download](https://git-scm.com/)

### Database Options (Choose One or Both)
- **MongoDB Atlas** (Cloud): [Sign up](https://www.mongodb.com/cloud/atlas)
- **Oracle Database 19c** (RDS or Local): [Download](https://www.oracle.com/database/)

### Optional but Recommended
- **Visual Studio Code**: [Download](https://code.visualstudio.com/)
- **Postman**: For API testing
- **MongoDB Compass**: For MongoDB management

---

## Windows Setup

### Step 1: Install Python 3.11

```powershell
# Download and install Python 3.11 from python.org
# During installation, check "Add Python to PATH"

# Verify installation
python --version
pip --version
```

### Step 2: Install Node.js and Yarn

```powershell
# Download and install Node.js from nodejs.org
# Verify installation
node --version
npm --version

# Install Yarn globally
npm install -g yarn
yarn --version
```

### Step 3: Clone the Repository

```powershell
git clone <repository-url>
cd promise-ai-platform
```




### Step 4: Setup Backend

Oracle client installation in windows: 


```powershell
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
copy .env.example .env
# Edit .env with your database credentials
notepad .env
```

### Step 5: Setup Frontend

```powershell
cd ..\frontend

# Install dependencies
yarn install

# Create .env file
copy .env.example .env
# Edit .env with backend URL
notepad .env

cd /app/frontend
yarn dev
# or
npm run dev
```

### Step 6: Oracle Instant Client (If using Oracle)

```powershell
# Download Oracle Instant Client for Windows
# https://www.oracle.com/database/technologies/instant-client/downloads.html

# Extract to C:\oracle\instantclient_19_23
# Add to PATH
setx PATH "%PATH%;C:\oracle\instantclient_19_23"
```

---

## macOS Setup

### Step 1: Install Homebrew (if not installed)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Step 2: Install Python 3.11

```bash
brew install python@3.11

# Verify installation
python3.11 --version
pip3 --version

# Create alias (optional)
echo "alias python=python3.11" >> ~/.zshrc
echo "alias pip=pip3" >> ~/.zshrc
source ~/.zshrc
```

### Step 3: Install Node.js and Yarn

```bash
brew install node
brew install yarn

# Verify installation
node --version
yarn --version
```

### Step 4: Clone the Repository

```bash
git clone <repository-url>
cd promise-ai-platform
```

### Step 5: Setup Backend

```bash
cd backend

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your database credentials
nano .env  # or use vim, code, etc.
```

### Step 6: Setup Frontend

```bash
cd ../frontend

# Install dependencies
yarn install

# Create .env file
cp .env.example .env
# Edit .env with backend URL
nano .env
```

### Step 7: Oracle Instant Client (If using Oracle)

```bash
# Download Oracle Instant Client for macOS (ARM64 for M1/M2/M3)
# https://www.oracle.com/database/technologies/instant-client/downloads.html

# Extract to /opt/oracle/instantclient_23_3
sudo mkdir -p /opt/oracle
sudo unzip instantclient-basic-macos.arm64-19.23.0.0.0dbru.zip -d /opt/oracle/

# Add to PATH
echo 'export PATH="/opt/oracle/instantclient_23_3:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Update library path
echo '/opt/oracle/instantclient_23_3' | sudo tee -a /etc/ld.so.conf.d/oracle-instantclient.conf
sudo ldconfig
```

---

## Linux Setup (Ubuntu/Debian)

### Step 1: Update System

```bash
sudo apt update
sudo apt upgrade -y
```

### Step 2: Install Python 3.11

```bash
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev python3-pip -y

# Verify installation
python3.11 --version
```

### Step 3: Install Node.js and Yarn

```bash
# Install Node.js 18.x
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install Yarn
npm install -g yarn

# Verify installation
node --version
yarn --version
```

### Step 4: Clone the Repository

```bash
git clone <repository-url>
cd promise-ai-platform
```

### Step 5: Setup Backend

```bash
cd backend

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your database credentials
nano .env
```

### Step 6: Setup Frontend

```bash
cd ../frontend

# Install dependencies
yarn install

# Create .env file
cp .env.example .env
# Edit .env with backend URL
nano .env
```

### Step 7: Oracle Instant Client (If using Oracle)

```bash
# Download Oracle Instant Client for Linux (ARM64 or x86_64)
# https://www.oracle.com/database/technologies/instant-client/downloads.html

# Install dependencies
sudo apt install libaio1 unzip -y

# Extract to /opt/oracle
sudo mkdir -p /opt/oracle
sudo unzip instantclient-basic-linux.arm64-19.23.0.0.0dbru.zip -d /opt/oracle/

# Update library path
echo '/opt/oracle/instantclient_23_3' | sudo tee -a /etc/ld.so.conf.d/oracle-instantclient.conf
sudo ldconfig

# Verify
ls -la /opt/oracle/instantclient_23_3/
```

---

## Database Configuration

### MongoDB Atlas Setup

1. Create account at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a new cluster (free tier available)
3. Create database user with read/write permissions
4. Whitelist your IP address (or 0.0.0.0/0 for development)
5. Get connection string: `mongodb+srv://username:password@cluster.mongodb.net/promise_ai`

### Oracle RDS Setup

1. Create Oracle RDS instance on AWS (19c)
2. Configure security group to allow inbound connections (port 1521)
3. Create database user with necessary permissions
4. Get connection details:
   - Host: `your-oracle-rds.region.rds.amazonaws.com`
   - Port: `1521`
   - Service Name: `ORCL`

---

## Environment Variables

### Backend `.env` Configuration

```bash
# Database Configuration (Choose one)
DB_TYPE="oracle"  # or "mongodb"

# MongoDB Configuration
MONGO_URL="mongodb+srv://username:password@cluster.mongodb.net/promise_ai?retryWrites=true&w=majority"

# Oracle Configuration
ORACLE_USER="your_username"
ORACLE_PASSWORD="your_password"
ORACLE_DSN="your-oracle-rds.region.rds.amazonaws.com:1521/ORCL"
ORACLE_HOST="your-oracle-rds.region.rds.amazonaws.com"
ORACLE_PORT="1521"
ORACLE_SERVICE_NAME="ORCL"
ORACLE_POOL_SIZE="10"

# AI Provider Configuration
AI_PROVIDER="azure_openai"  # or "none"

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=""
AZURE_OPENAI_DEPLOYMENT="gpt-4o"
AZURE_OPENAI_API_VERSION="2024-12-01-preview"

# Application Configuration
ENVIRONMENT="development"
DEBUG="true"
```

### Frontend `.env` Configuration

```bash
# Backend URL
REACT_APP_BACKEND_URL=http://localhost:8001

# For production
# REACT_APP_BACKEND_URL=https://your-domain.com
```

---

## Running the Application

### Option 1: Manual Start (Development)

**Terminal 1 - Backend**:
```bash
cd backend
source venv/bin/activate  # Windows: .\venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

**Terminal 2 - Frontend**:
```bash
cd frontend
yarn dev
```

**Access Application**:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8001/api
- API Docs: http://localhost:8001/docs

### Option 2: Using Supervisor (Production-like)

**Install Supervisor** (Linux/macOS):
```bash
sudo apt install supervisor -y  # Ubuntu/Debian
# or
brew install supervisor  # macOS
```

**Start Services**:
```bash
sudo supervisorctl start all
sudo supervisorctl status
```

---

## Database Initialization

### Oracle Schema Setup

```bash
cd backend
source venv/bin/activate
python init_oracle_schema.py
```

This creates all necessary tables:
- `datasets`
- `training_metadata`
- `workspace_states`
- `large_datasets` (BLOB storage)

### MongoDB Indexes

```bash
cd backend
source venv/bin/activate
python create_indexes.py
```

This creates indexes for:
- `datasets.id`
- `training_metadata.dataset_id`
- `workspaces.workspace_name`

---

## Troubleshooting

### Common Issues

#### 1. **Oracle Instant Client Not Found**

**Error**: `DPI-1047: Cannot locate a 64-bit Oracle Client library`

**Solution**:
- Verify Oracle Instant Client is installed
- Check PATH includes the client directory
- Run `ldconfig` (Linux/macOS)
- Restart terminal after PATH changes

#### 2. **MongoDB Connection Failed**

**Error**: `ServerSelectionTimeoutError`

**Solution**:
- Check your IP is whitelisted in MongoDB Atlas
- Verify connection string in .env
- Ensure network allows outbound connections on port 27017

#### 3. **Port Already in Use**

**Error**: `Address already in use`

**Solution**:
```bash
# Find process using port 8001
lsof -i :8001  # macOS/Linux
netstat -ano | findstr :8001  # Windows

# Kill process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

#### 4. **Module Not Found**

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
.\venv\Scripts\activate  # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

#### 5. **CORS Errors in Frontend**

**Solution**:
- Verify `REACT_APP_BACKEND_URL` in frontend/.env
- Check backend CORS configuration in `app/main.py`
- Ensure backend is running

#### 6. **Yarn Install Fails**

**Solution**:
```bash
# Clear yarn cache
yarn cache clean

# Delete node_modules and lock file
rm -rf node_modules yarn.lock

# Reinstall
yarn install
```

---

## Development Tips

### Hot Reload
- Backend: Auto-reloads on file changes (uvicorn --reload)
- Frontend: Auto-reloads on file changes (Vite)

### Debugging
- Backend: Use `print()` or `logging.info()` - visible in terminal
- Frontend: Use browser DevTools Console
- API Testing: Use `/docs` endpoint for interactive API testing

### Code Quality
```bash
# Backend linting
cd backend
pip install ruff
ruff check app/

# Frontend linting
cd frontend
yarn lint
```

### Database Switching
```bash
# Switch to MongoDB
# Edit backend/.env: DB_TYPE="mongodb"

# Switch to Oracle
# Edit backend/.env: DB_TYPE="oracle"

# Restart backend
# Restart backend
sudo supervisorctl restart backend

# Start backend
cd /app/backend
python server.py or
sudo supervisorctl start backend

# Stop backend
sudo supervisorctl stop backend

# Check status
sudo supervisorctl status backend

# View logs
tail -n 100 /var/log/supervisor/backend.*.log
```

---

## Next Steps

1. ✅ Install all prerequisites
2. ✅ Configure databases
3. ✅ Set up environment variables
4. ✅ Run database initialization scripts
5. ✅ Start the application
6. ✅ Access http://localhost:5173
7. ✅ Upload a dataset and explore features!

For deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md)

For architecture details, see [ARCHITECTURE_DIAGRAM.md](ARCHITECTURE_DIAGRAM.md)
