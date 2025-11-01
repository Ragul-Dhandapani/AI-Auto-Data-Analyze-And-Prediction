# 🚀 PROMISE AI - Quick Setup Reference Card

## Minimum Configuration Needed

### 1️⃣ Database Setup (Pick ONE option)

#### Option A: MongoDB Atlas (Cloud - Easiest)
```
✅ FREE - No installation
✅ 5 minutes setup
✅ Always accessible

Steps:
1. Sign up: https://www.mongodb.com/cloud/atlas
2. Create free cluster
3. Get connection string
4. Paste in backend/.env
```

#### Option B: Local MongoDB
```bash
# macOS
brew install mongodb-community@7.0
brew services start mongodb-community@7.0

# Linux
sudo apt-get install mongodb-org
sudo systemctl start mongod

# Connection already configured:
mongodb://localhost:27017
```

#### Option C: Docker
```bash
docker run -d --name mongodb -p 27017:27017 mongo:7.0
# Connection: mongodb://localhost:27017
```

---

### 2️⃣ Configuration Files

#### Backend: `/app/backend/.env`
```env
# Database (choose from above)
MONGO_URL=mongodb://localhost:27017
DB_NAME=promise_ai

# AI Features (required)
EMERGENT_LLM_KEY=your_key_here
```

#### Frontend: `/app/frontend/.env`
```env
# Already configured - no changes needed
REACT_APP_BACKEND_URL=http://localhost:8001
```

---

### 3️⃣ Start Application

```bash
# Terminal 1 - Backend
cd backend
pip install -r requirements.txt
python server.py

# Terminal 2 - Frontend  
cd frontend
yarn install
yarn start
```

---

## That's It! 🎉

### What Happens Automatically:
✅ Database created on first upload  
✅ Collections created automatically  
✅ GridFS configured for large files  
✅ No manual setup needed  

### First Use:
1. Open http://localhost:3000
2. Upload any CSV/Excel file
3. Start analyzing!

---

## Get Your Emergent LLM Key

### If Running on Emergent Platform:
```bash
# Use this tool to get your key:
emergent_integrations_manager

# Or check your environment:
echo $EMERGENT_LLM_KEY
```

### If Running Locally:
1. Go to Emergent Dashboard
2. Profile → Universal Key
3. Copy and paste in backend/.env

### Alternative: Use Direct Provider Keys
```env
# Instead of EMERGENT_LLM_KEY, use:
OPENAI_API_KEY=sk-proj-xxxxx
# or
ANTHROPIC_API_KEY=sk-ant-xxxxx
```

---

## Quick Troubleshooting

### Backend won't start?
```bash
# Check MongoDB running:
mongosh --eval "db.serverStatus()"

# Check logs:
tail -f /var/log/supervisor/backend.err.log
```

### Can't connect to backend?
```bash
# Verify backend running:
curl http://localhost:8001/api/

# Check .env files configured correctly
```

### AI features not working?
```bash
# Verify key set:
cat backend/.env | grep EMERGENT_LLM_KEY

# Restart backend after setting key
```

---

## File Locations

```
📁 Configuration:
   backend/.env        ← MongoDB + LLM key
   frontend/.env       ← Backend URL (default OK)

📁 Logs:
   /var/log/supervisor/backend.*.log
   /var/log/supervisor/frontend.*.log

📁 Data Storage:
   MongoDB database    ← Created automatically
   GridFS              ← For files >5MB
```

---

## Key Points

❌ **NOT Needed**:
- Manual database creation
- Pre-loaded data
- Schema setup
- Table creation
- Initial configuration beyond 2 .env files

✅ **Only Need**:
- MongoDB connection URL (1 line)
- Emergent LLM key (1 line)

🎯 **Zero Database Setup**:
- Upload CSV → Database created
- Collections auto-generated
- Ready to analyze immediately!

---

## Support

📖 **Full Guide**: See `/app/LOCAL_SETUP_GUIDE.md`  
📖 **Technical Docs**: See `/app/TECHNICAL_DOCUMENTATION.md`  
📖 **Database Testing**: See `/app/DATABASE_TESTING_GUIDE.md`

---

**You're ready to go with just 2 configuration lines!** 🚀
