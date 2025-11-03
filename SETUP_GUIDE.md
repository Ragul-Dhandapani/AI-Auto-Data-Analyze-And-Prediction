# PROMISE AI - Complete Setup Guide

This guide provides detailed step-by-step instructions for setting up PROMISE AI on your local machine.

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

### Required Software

| Software | Version | Download Link | Verification Command |
|----------|---------|---------------|----------------------|
| Python | 3.11.x or higher | [python.org](https://www.python.org/downloads/) | `python --version` |
| pip | 23.0 or higher | Included with Python | `pip --version` |
| Node.js | 18.x or higher | [nodejs.org](https://nodejs.org/) | `node --version` |
| npm | 9.x or higher | Included with Node.js | `npm --version` |
| yarn | 1.22.x or higher | `npm install -g yarn` | `yarn --version` |
| MongoDB | 5.0 or higher | [mongodb.com](https://www.mongodb.com/try/download/community) | `mongod --version` |
| Git | Latest | [git-scm.com](https://git-scm.com/) | `git --version` |

### Optional Software

- **Docker**: For containerized deployment
- **MongoDB Compass**: GUI for MongoDB
- **Postman**: API testing

## 🔧 System Requirements

### Minimum Requirements
- **OS**: Linux (Ubuntu 20.04+), macOS (10.15+), Windows 10+
- **RAM**: 8 GB
- **Storage**: 10 GB free space
- **CPU**: 4 cores

### Recommended Requirements
- **OS**: Linux (Ubuntu 22.04+), macOS (12+)
- **RAM**: 16 GB or more
- **Storage**: 50 GB free space
- **CPU**: 8 cores or more

## 📥 Installation Steps

### Step 1: Install Python 3.11

#### On Ubuntu/Debian:
```bash
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev

# Verify installation
python3.11 --version
```

#### On macOS:
```bash
# Using Homebrew
brew install python@3.11

# Verify installation
python3.11 --version
```

#### On Windows:
1. Download Python 3.11 installer from [python.org](https://www.python.org/downloads/)
2. Run installer and check "Add Python to PATH"
3. Verify: `python --version`

### Step 2: Install pip (Latest Version)

```bash
# Upgrade pip
python3.11 -m pip install --upgrade pip

# Verify
pip --version
# Should show: pip 23.x or higher
```

### Step 3: Install Node.js 18.x

#### On Ubuntu/Debian:
```bash
# Using NodeSource
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify
node --version  # Should show v18.x.x
npm --version
```

#### On macOS:
```bash
# Using Homebrew
brew install node@18

# Verify
node --version
npm --version
```

#### On Windows:
1. Download Node.js 18.x LTS from [nodejs.org](https://nodejs.org/)
2. Run installer
3. Verify in Command Prompt: `node --version`

### Step 4: Install Yarn

```bash
# Install globally via npm
npm install -g yarn

# Verify
yarn --version
# Should show: 1.22.x or higher
```

### Step 5: Install MongoDB

#### On Ubuntu/Debian:
```bash
# Import MongoDB public key
wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | sudo apt-key add -

# Add MongoDB repository
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/5.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-5.0.list

# Install MongoDB
sudo apt-get update
sudo apt-get install -y mongodb-org

# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# Verify
sudo systemctl status mongod
mongod --version
```

#### On macOS:
```bash
# Using Homebrew
brew tap mongodb/brew
brew install mongodb-community@5.0

# Start MongoDB
brew services start mongodb-community@5.0

# Verify
mongosh --version
```

#### On Windows:
1. Download MongoDB Community Server from [mongodb.com](https://www.mongodb.com/try/download/community)
2. Run installer (choose "Complete" installation)
3. Install as Windows Service
4. Verify: Open Command Prompt and run `mongod --version`

## 🚀 Project Setup

### Step 1: Clone Repository

```bash
# Clone the repository
git clone <your-repository-url>
cd promise-ai
```

### Step 2: Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create Python virtual environment
python3.11 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Upgrade pip in virtual environment
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt

# This will install:
# - fastapi==0.104.1
# - uvicorn[standard]==0.24.0
# - motor==3.3.2
# - pandas==2.1.3
# - numpy==1.26.2
# - scikit-learn==1.3.2
# - xgboost==2.0.2
# - tensorflow==2.15.0
# - prophet==1.1.5
# - shap==0.43.0
# - lime==0.2.0.1
# - And many more...
```

### Step 3: Backend Configuration

```bash
# Create .env file
cp .env.example .env

# Edit .env file with your settings
nano .env  # or use any text editor
```

**Backend .env Configuration:**
```env
# MongoDB Configuration
MONGO_URL=mongodb://localhost:27017
DB_NAME=autopredict_db

# LLM Configuration (Optional - for AI insights)
EMERGENT_LLM_KEY=your_emergent_llm_key_here
LLM_PROVIDER=emergent
LLM_MODEL=gpt-4

# Server Configuration
PORT=8001
HOST=0.0.0.0

# Environment
ENV=development
LOG_LEVEL=INFO
```

### Step 4: Create MongoDB Indexes

```bash
# Still in backend directory with venv activated
python create_indexes.py

# Expected output:
# 🔧 Creating MongoDB indexes for performance optimization...
# 📊 Creating indexes for 'datasets' collection...
#    ✅ Created indexes on: id, created_at, name
# ...
# ✨ All indexes created successfully!
```

### Step 5: Frontend Setup

```bash
# Open new terminal, navigate to frontend
cd frontend

# Install dependencies using yarn (recommended)
yarn install

# OR using npm
npm install

# This will install:
# - react@18.2.0
# - vite@5.0.0
# - axios@1.6.2
# - plotly.js@2.27.1
# - And many more...
```

### Step 6: Frontend Configuration

```bash
# Create .env file
cp .env.example .env

# Edit .env file
nano .env
```

**Frontend .env Configuration:**
```env
# Backend API URL
REACT_APP_BACKEND_URL=http://localhost:8001

# Optional: Other configurations
VITE_APP_NAME=PROMISE AI
```

## ▶️ Running the Application

### Start Backend

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate  # Activate venv
python server.py

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8001
# INFO:     Application startup complete.
```

**Backend will be available at:** `http://localhost:8001`

### Start Frontend

```bash
# Terminal 2: Frontend
cd frontend
yarn dev  # or npm run dev

# Expected output:
# VITE v5.0.0  ready in 1234 ms
# ➜  Local:   http://localhost:3000/
```

**Frontend will be available at:** `http://localhost:3000`

### Verify Installation

1. **Check Backend API:**
   ```bash
   curl http://localhost:8001/api/datasets
   # Should return: {"datasets": []}
   ```

2. **Check Frontend:**
   - Open browser: `http://localhost:3000`
   - You should see PROMISE AI homepage

3. **Check MongoDB:**
   ```bash
   mongosh
   use autopredict_db
   show collections
   ```

## 🔍 Troubleshooting

### Python Issues

**Problem:** `python3.11: command not found`
```bash
# Solution: Verify Python installation
which python3.11
python3 --version

# Try using python3 instead
python3 -m venv venv
```

**Problem:** `ModuleNotFoundError`
```bash
# Solution: Ensure venv is activated and reinstall
source venv/bin/activate
pip install -r requirements.txt
```

### Node.js Issues

**Problem:** `node: command not found`
```bash
# Solution: Verify Node installation
which node
node --version

# Add Node to PATH (on Linux/macOS)
export PATH="$PATH:/usr/local/bin"
```

**Problem:** `yarn: command not found`
```bash
# Solution: Install yarn globally
npm install -g yarn
```

### MongoDB Issues

**Problem:** `Connection refused to MongoDB`
```bash
# Solution 1: Start MongoDB
sudo systemctl start mongod  # Linux
brew services start mongodb-community  # macOS

# Solution 2: Check MongoDB status
sudo systemctl status mongod

# Solution 3: Check MongoDB logs
sudo tail -f /var/log/mongodb/mongod.log
```

**Problem:** `Authentication failed`
```bash
# Solution: If you have authentication enabled
# Update MONGO_URL in .env:
MONGO_URL=mongodb://username:password@localhost:27017/autopredict_db
```

### Port Already in Use

**Problem:** `Address already in use: 8001`
```bash
# Solution: Kill process using port
# On Linux/macOS:
lsof -ti:8001 | xargs kill -9

# On Windows:
netstat -ano | findstr :8001
taskkill /PID <PID> /F
```

### Frontend Not Loading

**Problem:** Blank page or errors in browser
```bash
# Solution 1: Clear cache
# Chrome: Ctrl+Shift+Del, clear cache

# Solution 2: Check backend URL in .env
# frontend/.env should have correct REACT_APP_BACKEND_URL

# Solution 3: Rebuild frontend
cd frontend
rm -rf node_modules
yarn install
yarn dev
```

## 🎯 Quick Start Script

Create `start.sh` in project root:

```bash
#!/bin/bash

# Start MongoDB
if ! pgrep -x "mongod" > /dev/null
then
    echo "Starting MongoDB..."
    sudo systemctl start mongod
fi

# Start Backend
echo "Starting Backend..."
cd backend
source venv/bin/activate
python server.py &
BACKEND_PID=$!

# Wait for backend
sleep 3

# Start Frontend
echo "Starting Frontend..."
cd ../frontend
yarn dev &
FRONTEND_PID=$!

echo "✅ PROMISE AI is running!"
echo "Frontend: http://localhost:3000"
echo "Backend: http://localhost:8001"
echo ""
echo "Press Ctrl+C to stop"

# Wait and cleanup on exit
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT TERM
wait
```

Make it executable and run:
```bash
chmod +x start.sh
./start.sh
```

## 📦 Production Deployment

### Using Docker

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d
```

### Using Supervisor (Linux)

```bash
# Install supervisor
sudo apt install supervisor

# Copy config files
sudo cp deploy/backend.conf /etc/supervisor/conf.d/
sudo cp deploy/frontend.conf /etc/supervisor/conf.d/

# Reload supervisor
sudo supervisorctl reread
sudo supervisorctl update

# Start services
sudo supervisorctl start backend
sudo supervisorctl start frontend
```

## ✅ Verification Checklist

- [ ] Python 3.11+ installed and verified
- [ ] pip 23.0+ installed and verified
- [ ] Node.js 18.x+ installed and verified
- [ ] npm 9.x+ installed and verified
- [ ] yarn 1.22.x+ installed and verified
- [ ] MongoDB 5.0+ installed and running
- [ ] Backend dependencies installed
- [ ] Frontend dependencies installed
- [ ] MongoDB indexes created
- [ ] .env files configured
- [ ] Backend running on port 8001
- [ ] Frontend running on port 3000
- [ ] Can access application in browser
- [ ] Can upload dataset and run analysis

## 🎓 Next Steps

After successful setup:

1. Read [API Documentation](API_DOCUMENTATION.md) for backend API reference
2. Review [Database Schema](DATABASE_SCHEMA.md) for data structure
3. Explore [MCP Server](MCP_SERVER.md) for AI assistant integration
4. Upload a sample dataset and run your first analysis!

## 📞 Support

If you encounter any issues:
1. Check this guide's troubleshooting section
2. Review application logs
3. Check GitHub issues
4. Contact support team

---

**Happy Analyzing! 🚀**
