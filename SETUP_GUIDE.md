# PROMISE AI - Complete Setup Guide

**Quick Reference:** Need just the basics? Jump to [Quick Start](#quick-start)

---

## Table of Contents
1. [Quick Start](#quick-start) - Get running in 5 minutes
2. [Local Development Setup](#local-development-setup)
3. [Docker Deployment](#docker-deployment)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [Configuration](#configuration)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Minimum Requirements
- Python 3.9+
- Node.js 18+
- MongoDB (any option below)

### 3 Steps to Run:

**Step 1: Start MongoDB** (choose ONE)
```bash
# Option A: MongoDB Atlas (FREE cloud - easiest)
# → Sign up at mongodb.com/cloud/atlas
# → Get connection string

# Option B: Local MongoDB
brew install mongodb-community  # macOS
sudo apt install mongodb-org    # Linux

# Option C: Docker
docker run -d -p 27017:27017 mongo:7.0
```

**Step 2: Configure** (2 lines only)
```bash
# Edit /app/backend/.env
MONGO_URL=mongodb://localhost:27017  # or your Atlas URL
EMERGENT_LLM_KEY=your_key_here      # for AI features
```

**Step 3: Start Application**
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

**Done!** Open http://localhost:3000 🎉

### What Happens Automatically:
✅ Database created on first upload
✅ Collections created automatically
✅ GridFS configured for large files
✅ No manual setup needed

---

## Local Development Setup

### Prerequisites

**Required:**
- Python 3.9 or higher
- Node.js 18 or higher
- MongoDB (see options below)
- Git

**Optional:**
- Docker (for containerized MongoDB)
- Virtual environment tool (venv, conda)

### Database Setup - 3 Options

#### Option 1: MongoDB Atlas (Cloud - Recommended)
✅ **Easiest** - No installation, 5-minute setup, FREE tier

1. **Sign up:** https://www.mongodb.com/cloud/atlas
2. **Create cluster:** Free M0 tier (no credit card)
3. **Get connection string:**
   ```
   mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/
   ```
4. **Configure:** Update `/app/backend/.env`

**Pros:** Cloud-hosted, automatic backups, accessible anywhere

#### Option 2: Local MongoDB (Full Control)

**macOS:**
```bash
brew tap mongodb/brew
brew install mongodb-community@7.0
brew services start mongodb-community@7.0

# Connection: mongodb://localhost:27017
```

**Linux (Ubuntu/Debian):**
```bash
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org
sudo systemctl start mongod
sudo systemctl enable mongod

# Connection: mongodb://localhost:27017
```

**Windows:**
- Download installer from https://www.mongodb.com/try/download/community
- Install as Windows Service
- Connection: `mongodb://localhost:27017`

**Pros:** Full control, fast local access, no internet dependency

#### Option 3: Docker MongoDB (Isolated)

```bash
docker run -d \
  --name promise-mongodb \
  -p 27017:27017 \
  -v mongodb_data:/data/db \
  mongo:7.0

# Connection: mongodb://localhost:27017
```

**With authentication:**
```bash
docker run -d \
  --name promise-mongodb \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=password123 \
  mongo:7.0

# Connection: mongodb://admin:password123@localhost:27017/?authSource=admin
```

**Pros:** Isolated environment, easy cleanup, version control

### Configuration Files

#### Backend: `/app/backend/.env`
```env
# Database Configuration
MONGO_URL=mongodb://localhost:27017
DB_NAME=promise_ai

# AI Features (Required for chat and insights)
EMERGENT_LLM_KEY=your_emergent_llm_key_here

# Optional: Direct Provider Keys
# OPENAI_API_KEY=your_openai_key
# ANTHROPIC_API_KEY=your_anthropic_key
```

#### Frontend: `/app/frontend/.env`
```env
# Backend API URL (already configured)
REACT_APP_BACKEND_URL=http://localhost:8001
```

**Note:** Only update `MONGO_URL` and `EMERGENT_LLM_KEY` in most cases

### Getting Your Emergent LLM Key

**If on Emergent Platform:**
```bash
# Key is available in environment
echo $EMERGENT_LLM_KEY
```

**If Running Locally:**
1. Go to Emergent Dashboard
2. Profile → Universal Key
3. Copy and paste in `.env`

**Alternative - Direct Provider Keys:**
```env
# Use instead of EMERGENT_LLM_KEY
OPENAI_API_KEY=sk-proj-xxxxx
# or
ANTHROPIC_API_KEY=sk-ant-xxxxx
```

**What works without LLM key:**
- ✅ File upload
- ✅ Data profiling
- ✅ ML model training
- ✅ Chart generation
- ❌ AI chat (requires key)
- ❌ AI insights (requires key)

### Installation & Running

#### Backend
```bash
cd /app/backend

# Optional: Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start server
python server.py
# Or with uvicorn:
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

**Backend runs on:** http://localhost:8001

#### Frontend
```bash
cd /app/frontend

# Install dependencies
yarn install
# or: npm install

# Start development server
yarn start
# or: npm start
```

**Frontend opens at:** http://localhost:3000

### Verification

**Backend Health:**
```bash
curl http://localhost:8001/api/
# Expected: {"message":"AutoPredict API","version":"1.0"}
```

**MongoDB Connection:**
```bash
mongosh --eval "db.serverStatus()"
# Or with Docker:
docker exec promise-mongodb mongosh --eval "db.serverStatus()"
```

**Frontend Health:**
- Open http://localhost:3000
- Should see PROMISE AI homepage

---

## Docker Deployment

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- 20GB disk space

### Quick Deploy

1. **Clone repository**
```bash
git clone <your-repo-url>
cd promise-ai
```

2. **Configure environment**
```bash
echo "EMERGENT_LLM_KEY=your_key" > .env
```

3. **Start all services**
```bash
docker-compose up -d
```

4. **Verify**
```bash
docker-compose ps
# All services should be "Up"
```

5. **Access**
- Frontend: http://localhost:3000
- Backend: http://localhost:8001/api
- MongoDB: mongodb://localhost:27017

### Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f
docker-compose logs -f backend  # Specific service

# Restart service
docker-compose restart backend

# Rebuild images
docker-compose build --no-cache

# Scale backend (load balancing)
docker-compose up -d --scale backend=3

# Remove all (including volumes)
docker-compose down -v
```

### Build Individual Images

**Backend:**
```bash
cd backend
docker build -t promise-ai-backend:latest .
```

**Frontend:**
```bash
cd frontend
docker build -t promise-ai-frontend:latest .
```

---

## Kubernetes Deployment

### Prerequisites
- Kubernetes cluster 1.24+
- kubectl configured
- 8GB RAM minimum
- 50GB disk space

### Deploy to Kubernetes

1. **Create namespace**
```bash
kubectl apply -f k8s/namespace.yaml
```

2. **Configure secrets**
```bash
# Edit k8s/configmap.yaml first
kubectl apply -f k8s/configmap.yaml
```

3. **Deploy MongoDB**
```bash
kubectl apply -f k8s/mongodb.yaml
kubectl wait --for=condition=ready pod -l app=mongodb -n promise-ai --timeout=300s
```

4. **Deploy Backend**
```bash
kubectl apply -f k8s/backend.yaml
kubectl wait --for=condition=ready pod -l app=backend -n promise-ai --timeout=300s
```

5. **Deploy Frontend**
```bash
kubectl apply -f k8s/frontend.yaml
```

6. **Setup Ingress (optional)**
```bash
# Update k8s/ingress.yaml with your domain
kubectl apply -f k8s/ingress.yaml
```

### Kubernetes Management

```bash
# View all resources
kubectl get all -n promise-ai

# View logs
kubectl logs -f deployment/backend -n promise-ai

# Scale deployments
kubectl scale deployment backend --replicas=5 -n promise-ai

# Port forwarding
kubectl port-forward svc/frontend-service 3000:3000 -n promise-ai

# Restart deployment
kubectl rollout restart deployment/backend -n promise-ai

# View events
kubectl get events -n promise-ai --sort-by='.lastTimestamp'
```

### Update Secrets

```bash
# Create secret
kubectl create secret generic promise-ai-secrets \
  --from-literal=EMERGENT_LLM_KEY=your_key \
  --from-literal=MONGO_URL=mongodb://mongodb:27017 \
  -n promise-ai

# Update secret
kubectl delete secret promise-ai-secrets -n promise-ai
kubectl create secret generic promise-ai-secrets \
  --from-literal=EMERGENT_LLM_KEY=new_key \
  -n promise-ai
```

---

## Configuration

### Environment Variables

#### Backend Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MONGO_URL` | Yes | `mongodb://localhost:27017` | MongoDB connection string |
| `DB_NAME` | No | `promise_ai` | Database name |
| `EMERGENT_LLM_KEY` | For AI | - | Universal LLM key |
| `OPENAI_API_KEY` | Alternative | - | Direct OpenAI key |
| `ANTHROPIC_API_KEY` | Alternative | - | Direct Anthropic key |

#### Frontend Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `REACT_APP_BACKEND_URL` | Yes | `http://localhost:8001` | Backend API URL |

### What You DON'T Need to Configure

❌ No manual database setup required
❌ No pre-created collections needed
❌ No schema imports
❌ No initial data
❌ No GridFS configuration
❌ No index setup
❌ CORS already configured
❌ Ports already configured

✅ **Only configure:**
1. MongoDB connection URL
2. LLM key (for AI features)

---

## Troubleshooting

### Common Issues

#### 1. Backend Won't Start - MongoDB Connection Error

**Error:** `ServerSelectionTimeoutError: Connection refused`

**Solution:**
```bash
# Check MongoDB status
mongosh --eval "db.serverStatus()"  # Should show server info

# Start MongoDB
brew services start mongodb-community  # macOS
sudo systemctl start mongod            # Linux
docker start promise-mongodb           # Docker

# Verify MongoDB running
ps aux | grep mongod
```

#### 2. LLM Features Not Working

**Error:** `EMERGENT_LLM_KEY not set` or AI responses fail

**Solution:**
1. Check key in `.env` file: `cat backend/.env | grep EMERGENT_LLM_KEY`
2. Verify no extra spaces or quotes
3. Restart backend after adding key
4. Test key validity

#### 3. Frontend Can't Connect to Backend

**Error:** `Network Error` or `ERR_CONNECTION_REFUSED`

**Solution:**
```bash
# Verify backend running
curl http://localhost:8001/api/

# Check REACT_APP_BACKEND_URL
cat frontend/.env

# Restart frontend after .env changes
cd frontend && yarn start
```

#### 4. Large File Upload Fails

**Error:** `413 Payload Too Large`

**Solution:**
- GridFS already handles this automatically
- If using nginx, increase: `client_max_body_size 100M;`

#### 5. Port Already in Use

**Error:** `Address already in use`

**Solution:**
```bash
# Find process using port
lsof -i:8001  # Backend
lsof -i:3000  # Frontend

# Kill process
kill -9 <PID>
```

### View Logs

**Local Development:**
```bash
# Backend logs (terminal output)
cd backend && python server.py

# Frontend logs (browser console)
# Press F12 → Console tab
```

**Docker:**
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

**Kubernetes:**
```bash
kubectl logs -f deployment/backend -n promise-ai
kubectl logs -f deployment/frontend -n promise-ai
```

**Supervisor (if used):**
```bash
tail -f /var/log/supervisor/backend.err.log
tail -f /var/log/supervisor/frontend.out.log
```

### Health Checks

```bash
# Backend API
curl http://localhost:8001/api/
# Expected: {"message":"AutoPredict API"}

# Frontend
curl http://localhost:3000/
# Expected: HTML page

# MongoDB
mongosh --eval "db.adminCommand('ping')"
# Expected: { ok: 1 }
```

---

## First Time Usage

### 1. Access Application
Open browser: http://localhost:3000

### 2. Upload Your First Dataset
1. Click "Get Started"
2. Choose "File Upload" tab
3. Drag & drop CSV or Excel file
4. Wait for processing (few seconds)

### 3. What Happens Automatically:
✅ Database `promise_ai` created
✅ Collection `datasets` created
✅ Data stored (direct or GridFS)
✅ Data profiled automatically
✅ Ready for analysis

### 4. Explore Features
- **Data Profiler:** View statistics, missing values, duplicates
- **Predictive Analysis:** Train 6 ML models, generate 15+ charts
- **Visualization:** Create custom charts
- **Chat:** Ask AI about your data (requires LLM key)

---

## Production Considerations

### Security
```env
# Use strong MongoDB credentials
MONGO_URL=mongodb://user:strongpass@host:27017/

# Restrict CORS
CORS_ORIGINS=["https://yourdomain.com"]

# Use HTTPS
```

### Performance
- Use MongoDB Atlas for production
- Enable authentication
- Set up backups
- Configure connection pooling
- Enable monitoring

### Monitoring
- Set up logging aggregation
- Monitor API endpoints
- Track database performance
- Alert on errors

### Backup
```bash
# MongoDB backup
mongodump --uri="$MONGO_URL" --out=/backup

# Restore
mongorestore --uri="$MONGO_URL" /backup
```

---

## Summary

### Minimum Setup Checklist:
- [ ] MongoDB running (Atlas/Local/Docker)
- [ ] Backend `.env` configured (MONGO_URL + EMERGENT_LLM_KEY)
- [ ] Frontend `.env` verified (usually default is fine)
- [ ] Dependencies installed (`pip install`, `yarn install`)
- [ ] Services started (backend + frontend)
- [ ] Application accessible (http://localhost:3000)

### Zero Database Setup:
✅ No manual database creation
✅ No schema setup
✅ No initial data
✅ Just upload CSV and start!

### Support:
- Full docs: `/app/README.md`
- Database details: `/app/DATABASE_SETUP.md`
- Architecture: `/app/ARCHITECTURE.md`
- Testing: `/app/test_result.md`

---

**You're ready to analyze data in 5 minutes!** 🚀
