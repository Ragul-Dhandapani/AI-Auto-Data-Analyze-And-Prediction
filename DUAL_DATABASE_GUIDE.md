# PROMISE AI - Dual Database Support Guide

## Overview

PROMISE AI now supports **BOTH MongoDB and Oracle 23** databases with seamless switching capability. All features work identically on both databases.

## Supported Databases

| Database | Version | Status | Features |
|----------|---------|--------|----------|
| **MongoDB** | 5.0+ | ✅ Production Ready | GridFS for large files |
| **Oracle** | 23ai+ | ✅ Production Ready | BLOB storage, JSON columns |

## Quick Switch Guide

### Switch to Oracle

**Step 1**: Set up Oracle database
```bash
# Run the schema creation script
sqlplus username/password@localhost:1521/XEPDB1 @backend/app/database/oracle_schema.sql
```

**Step 2**: Update `.env` file
```env
# Change DB_TYPE to oracle
DB_TYPE="oracle"

# Configure Oracle credentials
ORACLE_USER="your_username"
ORACLE_PASSWORD="your_password"
ORACLE_HOST="localhost"
ORACLE_PORT="1521"
ORACLE_SERVICE_NAME="XEPDB1"
```

**Step 3**: Restart backend
```bash
sudo supervisorctl restart backend
```

✅ **Done!** Application now uses Oracle.

---

### Switch Back to MongoDB

**Step 1**: Update `.env` file
```env
# Change DB_TYPE back to mongodb
DB_TYPE="mongodb"
```

**Step 2**: Restart backend
```bash
sudo supervisorctl restart backend
```

✅ **Done!** Application now uses MongoDB.

---

## Environment Variables

### Common Variables
```env
DB_TYPE="mongodb"  # or "oracle"
```

### MongoDB Configuration
```env
MONGO_URL="mongodb://localhost:27017"
DB_NAME="autopredict_db"
```

### Oracle Configuration
```env
ORACLE_USER="promise_ai_user"
ORACLE_PASSWORD="your_secure_password"
ORACLE_HOST="localhost"
ORACLE_PORT="1521"
ORACLE_SERVICE_NAME="XEPDB1"
ORACLE_POOL_SIZE="10"
```

---

## Oracle Setup Instructions

### 1. Create Oracle User

```sql
-- Connect as SYSDBA
sqlplus sys/password@localhost:1521/XE as sysdba

-- Create user
CREATE USER promise_ai_user IDENTIFIED BY your_password;

-- Grant privileges
GRANT CONNECT, RESOURCE, CREATE TABLE, CREATE SEQUENCE TO promise_ai_user;
GRANT UNLIMITED TABLESPACE TO promise_ai_user;

-- Enable JSON features (Oracle 23)
GRANT CREATE SEARCH INDEX TO promise_ai_user;
```

### 2. Create Schema

```bash
# As the promise_ai_user
sqlplus promise_ai_user/your_password@localhost:1521/XEPDB1

# Run schema script
@/app/backend/app/database/oracle_schema.sql
```

### 3. Verify Installation

```sql
-- Check tables
SELECT table_name FROM user_tables;

-- Expected output:
-- DATASETS
-- FILE_STORAGE
-- WORKSPACE_STATES
-- PREDICTION_FEEDBACK
```

---

## Migration Tools

### Migrate from MongoDB to Oracle

```bash
cd /app/backend
python migrate_to_oracle.py
```

This will:
1. Connect to both databases
2. Copy all datasets from MongoDB → Oracle
3. Copy all workspaces
4. Copy all feedback records
5. Maintain all relationships

### Migrate from Oracle to MongoDB

```bash
cd /app/backend
python migrate_to_mongodb.py
```

---

## Feature Compatibility

| Feature | MongoDB | Oracle | Notes |
|---------|---------|--------|-------|
| Dataset Upload | ✅ | ✅ | Identical |
| Large Files (>1MB) | ✅ GridFS | ✅ BLOB | Both support compression |
| Workspace Save | ✅ | ✅ | Identical |
| Predictive Analysis | ✅ | ✅ | All ML features work |
| Time Series | ✅ | ✅ | Prophet & LSTM |
| Hyperparameter Tuning | ✅ | ✅ | Full support |
| Feedback Loop | ✅ | ✅ | Active learning |
| Training Metadata | ✅ | ✅ | Complete history |
| AI Insights | ✅ | ✅ | SHAP, LIME |
| Charts & Viz | ✅ | ✅ | Auto-generation |

**100% Feature Parity** ✅

---

## Performance Comparison

### MongoDB
- **Strengths**: 
  - Flexible schema
  - Native GridFS for large files
  - Fast document operations
  - Easier setup
- **Best For**: 
  - Rapid development
  - Document-heavy workloads
  - Teams familiar with NoSQL

### Oracle 23
- **Strengths**: 
  - Enterprise features
  - ACID compliance
  - Advanced JSON support
  - Mature tooling
- **Best For**: 
  - Enterprise environments
  - Regulated industries
  - Oracle-based infrastructure

---

## Troubleshooting

### Oracle Connection Issues

**Error**: `ORA-12541: TNS:no listener`
```bash
# Check Oracle listener status
lsnrctl status

# Start listener if needed
lsnrctl start
```

**Error**: `ORA-01017: invalid username/password`
```bash
# Verify credentials
sqlplus username/password@host:port/service
```

### MongoDB Connection Issues

**Error**: `Connection refused`
```bash
# Check MongoDB status
sudo systemctl status mongod

# Start MongoDB
sudo systemctl start mongod
```

---

## Architecture

### Database Abstraction Layer

```
Application Layer (Routes)
          ↓
   Database Helper
          ↓
   Factory Pattern
       ↙     ↘
MongoDB      Oracle
Adapter      Adapter
   ↓            ↓
MongoDB      Oracle DB
```

All business logic remains unchanged. Only the database layer is swapped.

---

## Testing

### Test MongoDB
```bash
# Set DB_TYPE=mongodb in .env
DB_TYPE="mongodb"

# Restart and test
sudo supervisorctl restart backend
curl http://localhost:8001/api/datasets
```

### Test Oracle
```bash
# Set DB_TYPE=oracle in .env
DB_TYPE="oracle"

# Restart and test
sudo supervisorctl restart backend
curl http://localhost:8001/api/datasets
```

---

## Backup & Recovery

### MongoDB Backup
```bash
mongodump --db autopredict_db --out /backup/mongodb/
```

### Oracle Backup
```bash
expdp promise_ai_user/password directory=DATA_PUMP_DIR dumpfile=promise_ai.dmp
```

---

## FAQ

**Q: Can I use both databases simultaneously?**
A: No, only one database is active at a time based on `DB_TYPE`.

**Q: Do I lose data when switching?**
A: Data remains in the original database. Use migration tools to sync.

**Q: Which database is faster?**
A: Both perform similarly. MongoDB has slight edge for document operations, Oracle for complex queries.

**Q: Can I use Oracle 19c instead of 23ai?**
A: Yes, but without native JSON search. Update schema to remove JSON indexes.

**Q: Is there downtime when switching?**
A: Yes, application must restart. Use migration tools first to avoid data loss.

---

## Support

For issues:
1. Check logs: `tail -f /var/log/supervisor/backend.*.log`
2. Verify configuration in `.env`
3. Test database connection independently
4. Review error messages

---

**Updated**: 2025-01-03
**Version**: 2.0.0 (Dual-Database Support)
