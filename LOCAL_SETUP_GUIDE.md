# PROMISE AI - Local Machine Setup Guide

## 🎯 Quick Answers to Your Questions

### 1️⃣ Database Setup - What You Need to Do

**Short Answer**: Just provide a MongoDB connection URL. That's it!

**You Have 3 Easy Options**:

#### Option A: MongoDB Atlas (Recommended - Easiest)
```
✅ FREE cloud database
✅ No installation needed
✅ 5 minutes setup

Steps:
1. Go to mongodb.com/cloud/atlas
2. Sign up (free, no credit card)
3. Create cluster
4. Copy connection string
5. Paste in /app/backend/.env
```

#### Option B: Local MongoDB
```bash
# Install on your machine
brew install mongodb-community  # macOS
sudo apt install mongodb-org    # Linux

# Connection URL (already configured):
mongodb://localhost:27017
```

#### Option C: Docker
```bash
docker run -d -p 27017:27017 mongo:7.0
```

**Do you need to create the database?** 
❌ **NO!** Database is created automatically when you upload your first file.

**Do you need to upload data first?**
❌ **NO!** The application STARTS FRESH. Just upload any CSV/Excel file and start analyzing.

---

### 2️⃣ Configuration - What You Need to Set

**You ONLY need to configure 2 things**:

#### A. Database Connection (1 line)
Edit `/app/backend/.env`:
```env
MONGO_URL=mongodb://localhost:27017
# Or your Atlas connection string:
# MONGO_URL=mongodb+srv://user:pass@cluster.mongodb.net/
```

#### B. LLM Key for AI Features (1 line)
Same file `/app/backend/.env`:
```env
EMERGENT_LLM_KEY=your_key_here
```

**Where to get Emergent LLM Key?**
- From your Emergent dashboard → Profile → Universal Key
- OR use direct provider keys (OpenAI, Anthropic, Google)

**What if you don't have a key yet?**
- Basic features still work (file upload, ML models, charts)
- AI chat and insights won't work without it

---

### 3️⃣ What Else to Configure?

**Nothing else!** 

Frontend configuration (`/app/frontend/.env`) is already set:
```env
REACT_APP_BACKEND_URL=http://localhost:8001  # ✅ Already correct
```

---

## 🚀 Complete Setup in 3 Steps

### Step 1: Get MongoDB Running
```bash
# Choose ONE:

# Atlas (cloud):
# → Sign up at mongodb.com/cloud/atlas
# → Get connection string

# OR Local:
brew install mongodb-community && brew services start mongodb-community

# OR Docker:
docker run -d -p 27017:27017 --name mongodb mongo:7.0
```

### Step 2: Update Configuration
```bash
# Edit /app/backend/.env
MONGO_URL=mongodb://localhost:27017  # or your Atlas URL
EMERGENT_LLM_KEY=your_key_here      # for AI features
```

### Step 3: Start Application
```bash
# Terminal 1 - Backend
cd /app/backend
pip install -r requirements.txt
python server.py

# Terminal 2 - Frontend
cd /app/frontend
yarn install
yarn start
```

**Open**: http://localhost:3000 🎉

---

## 📊 First Time Usage

### When You Start the App:
1. ✅ MongoDB is running (empty database)
2. ✅ Application loads successfully
3. ✅ No data exists yet

### Upload Your First Dataset:
1. Click "Get Started"
2. Drag & drop any CSV/Excel file
3. **Magic happens**:
   - Database `promise_ai` created automatically
   - Collection `datasets` created
   - Your data is stored
   - Analysis runs automatically
   - Charts generated
   - ML models trained

### That's it! No manual database setup needed.

---

## 🎯 What You DON'T Need

❌ Pre-create database  
❌ Create tables/collections  
❌ Import schema  
❌ Set up indexes  
❌ Configure GridFS manually  
❌ Upload initial data  
❌ Database migrations  
❌ Seed data  
❌ Configure CORS (already set)  
❌ Configure ports (already set)  
❌ Install MongoDB drivers (in requirements.txt)  

---

## Overview
This guide will help you run PROMISE AI on your local machine with minimal setup.

---

## Prerequisites

### Required Software
1. **Python 3.11+** - Backend runtime
2. **Node.js 18+** - Frontend runtime
3. **MongoDB** - Database (multiple options below)
4. **Git** - Version control

---

## Database Setup (3 Options)

### Option 1: MongoDB Atlas (Cloud - Recommended for Beginners)
**Easiest option - No local installation needed**

1. **Create Free Account**:
   - Go to https://www.mongodb.com/cloud/atlas
   - Sign up for free (no credit card required)
   - Create a new cluster (Free tier M0 is sufficient)

2. **Get Connection String**:
   - Click "Connect" on your cluster
   - Choose "Connect your application"
   - Copy the connection string (looks like):
   ```
   mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/
   ```

3. **Configure Application**:
   - Update `/app/backend/.env`:
   ```env
   MONGO_URL=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/
   DB_NAME=promise_ai
   ```

4. **That's it!** - Database will be created automatically when you upload your first dataset.

**Pros**: 
- ✅ No installation needed
- ✅ Accessible from anywhere
- ✅ Free tier sufficient for testing
- ✅ Automatic backups

---

### Option 2: Local MongoDB (Full Control)

**For users who want local database**

#### macOS Installation:
```bash
# Install via Homebrew
brew tap mongodb/brew
brew install mongodb-community@7.0

# Start MongoDB
brew services start mongodb-community@7.0

# Connection string (already configured)
MONGO_URL=mongodb://localhost:27017
```

#### Linux Installation:
```bash
# Ubuntu/Debian
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org

# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# Connection string
MONGO_URL=mongodb://localhost:27017
```

#### Windows Installation:
```bash
# Download installer from:
https://www.mongodb.com/try/download/community

# Install as Windows Service
# Connection string
MONGO_URL=mongodb://localhost:27017
```

**Pros**:
- ✅ Full control
- ✅ Fast local access
- ✅ No internet dependency

---

### Option 3: Docker MongoDB (Isolated)

**For users familiar with Docker**

```bash
# Run MongoDB in Docker
docker run -d \
  --name promise-mongodb \
  -p 27017:27017 \
  -v mongodb_data:/data/db \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=password123 \
  mongo:7.0

# Connection string
MONGO_URL=mongodb://admin:password123@localhost:27017/?authSource=admin
```

**Pros**:
- ✅ Isolated environment
- ✅ Easy cleanup
- ✅ Version control

---

## Configuration Files

### 1. Backend Configuration (`/app/backend/.env`)

```env
# Database Configuration (Choose one option above)
MONGO_URL=mongodb://localhost:27017
DB_NAME=promise_ai

# LLM Configuration (Required for AI features)
EMERGENT_LLM_KEY=your_emergent_llm_key_here

# Optional: Direct LLM Provider Keys (if not using Emergent)
# OPENAI_API_KEY=your_openai_key
# ANTHROPIC_API_KEY=your_anthropic_key
```

### 2. Frontend Configuration (`/app/frontend/.env`)

```env
# Backend API URL
REACT_APP_BACKEND_URL=http://localhost:8001
```

**Note**: These files already exist with default values. You only need to update:
1. `MONGO_URL` - If not using default localhost MongoDB
2. `EMERGENT_LLM_KEY` - For AI-powered features

---

## Getting Your Emergent LLM Key

### What is Emergent LLM Key?
A universal key that works with:
- OpenAI (GPT-4o, GPT-4o-mini, GPT-Image-1)
- Anthropic (Claude Sonnet 4)
- Google (Gemini, Imagen)

### How to Get It:

**Option A: If you have it already**
- Just paste it in `/app/backend/.env`

**Option B: Get it from Emergent Platform**
1. Go to your Emergent dashboard
2. Navigate to Profile → Universal Key
3. Copy the key
4. Paste in `.env` file

**Option C: Use Alternative LLM Keys**
If you prefer using direct provider keys:

```env
# For OpenAI
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx

# For Anthropic
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx

# For Google
GOOGLE_API_KEY=xxxxxxxxxxxxx
```

**Note**: You'll need to modify the LLM initialization code if using direct provider keys instead of Emergent key.

---

## Installation & Running

### 1. Clone Repository (if not already done)
```bash
git clone <your-repo-url>
cd promise-ai
```

### 2. Backend Setup
```bash
cd /app/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify .env configuration
cat .env

# Start backend
python server.py
# or with uvicorn:
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

Backend will start on: http://localhost:8001

### 3. Frontend Setup
```bash
cd /app/frontend

# Install dependencies
yarn install
# or: npm install

# Verify .env configuration
cat .env

# Start frontend
yarn start
# or: npm start
```

Frontend will open at: http://localhost:3000

---

## First Time Usage

### 1. Access Application
Open browser: http://localhost:3000

### 2. Upload Your First Dataset
1. Click "Get Started"
2. Choose "File Upload" tab
3. Drag & drop a CSV or Excel file
4. Wait for processing

### 3. Explore Features
- **Data Profiler**: View statistics and data quality
- **Predictive Analysis**: Train ML models
- **Visualization**: Generate charts
- **Chat**: Ask AI about your data

### Database is Created Automatically!
- No manual database setup needed
- Collections created on first upload:
  - `datasets` - Your uploaded data
  - `analysis_states` - Saved workspaces
  - `fs.files` / `fs.chunks` - GridFS for large files

---

## What You DON'T Need to Configure

❌ **No need to**:
- Create database manually
- Create tables/collections
- Import schema
- Set up indexes (created automatically)
- Configure GridFS (auto-configured)
- Upload initial data (start fresh!)

✅ **Just configure**:
1. MongoDB connection URL
2. Emergent LLM Key (for AI features)

---

## Verification Checklist

### Backend Health Check
```bash
curl http://localhost:8001/api/
# Expected: {"message":"AutoPredict API","version":"1.0"}
```

### MongoDB Connection Check
```bash
# Check if MongoDB is running
mongosh --eval "db.serverStatus()" 
# or if using Docker:
docker exec promise-mongodb mongosh --eval "db.serverStatus()"
```

### Frontend Health Check
- Open http://localhost:3000
- Should see PROMISE AI homepage

---

## Common Issues & Solutions

### Issue 1: Backend fails to start - MongoDB connection error
**Error**: `ServerSelectionTimeoutError: localhost:27017: [Errno 61] Connection refused`

**Solution**:
```bash
# Check if MongoDB is running
brew services list | grep mongodb  # macOS
systemctl status mongod            # Linux
docker ps | grep mongo             # Docker

# Start MongoDB
brew services start mongodb-community  # macOS
sudo systemctl start mongod            # Linux
docker start promise-mongodb           # Docker
```

### Issue 2: LLM features not working
**Error**: `EMERGENT_LLM_KEY not set` or AI responses fail

**Solution**:
1. Verify key in `.env` file
2. Restart backend after adding key
3. Check key is valid (no extra spaces)

### Issue 3: Frontend can't connect to backend
**Error**: `Network Error` or `ERR_CONNECTION_REFUSED`

**Solution**:
1. Verify backend is running on port 8001
2. Check `REACT_APP_BACKEND_URL` in frontend/.env
3. Restart frontend after changing .env

### Issue 4: Large file upload fails
**Error**: `413 Payload Too Large`

**Solution**: Already handled via GridFS, but if issues persist:
```bash
# Increase nginx limits (if using nginx)
client_max_body_size 100M;
```

---

## File Structure Reference

```
promise-ai/
├── backend/
│   ├── .env                    # ← Configure MongoDB & LLM key
│   ├── requirements.txt
│   ├── server.py
│   └── app/                    # Modular structure
│       ├── config.py
│       ├── models/
│       ├── database/
│       └── services/
├── frontend/
│   ├── .env                    # ← Configure backend URL
│   ├── package.json
│   └── src/
└── mcp_server/
```

---

## Production Deployment Notes

### For Production, Additionally Configure:

1. **Security**:
   ```env
   # Strong MongoDB password
   MONGO_URL=mongodb://user:strongpassword@host:27017/
   
   # CORS restrictions
   CORS_ORIGINS=["https://yourdomain.com"]
   ```

2. **Environment Variables**:
   - Use environment-specific .env files
   - Never commit .env to git
   - Use secrets management (AWS Secrets Manager, etc.)

3. **Database**:
   - Use MongoDB Atlas for production
   - Enable authentication
   - Set up backups
   - Configure connection pooling

4. **Monitoring**:
   - Set up logging
   - Monitor API endpoints
   - Track database performance

---

## Quick Start Summary

### Absolute Minimum to Get Running:

1. **Install MongoDB** (choose any option above)
2. **Update .env files**:
   ```bash
   # backend/.env
   MONGO_URL=mongodb://localhost:27017  # or your Atlas URL
   EMERGENT_LLM_KEY=your_key_here
   
   # frontend/.env (already correct)
   REACT_APP_BACKEND_URL=http://localhost:8001
   ```
3. **Start services**:
   ```bash
   # Terminal 1 - Backend
   cd backend && python server.py
   
   # Terminal 2 - Frontend
   cd frontend && yarn start
   ```
4. **Upload your first CSV file** - Database will be created automatically!

---

## Support & Troubleshooting

### Get MongoDB Connection String:
- **Local**: `mongodb://localhost:27017`
- **Atlas**: From Atlas dashboard → Connect → Connection String
- **Docker**: `mongodb://admin:password@localhost:27017`

### Test Database Connection:
```python
from pymongo import MongoClient
client = MongoClient("your_connection_string")
print(client.list_database_names())  # Should list databases
```

### Need Help?
- Check logs in `/var/log/supervisor/` (if using supervisor)
- Or check terminal output for error messages
- MongoDB logs: `/var/log/mongodb/mongod.log`

---

## Summary

✅ **You ONLY need to configure**:
1. MongoDB connection URL (one line in .env)
2. Emergent LLM key (one line in .env)

✅ **You DON'T need**:
- Pre-created database
- Initial data
- Manual schema setup
- Complex configuration

✅ **First use**:
- Upload any CSV/Excel file
- Database & collections created automatically
- Start analyzing immediately!

**The application is designed to be zero-setup for the database - just provide the connection URL and you're ready to go!**
