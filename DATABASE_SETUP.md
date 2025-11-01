# PROMISE AI - Database Setup Guide

**Quick Reference:** PROMISE AI supports 5 database types and MongoDB for application data

---

## Table of Contents
1. [MongoDB Setup (Application Database)](#mongodb-setup-application-database)
2. [Supported External Databases](#supported-external-databases)
3. [Test Database Setup](#test-database-setup)
4. [Connection Examples](#connection-examples)
5. [Test Data Scripts](#test-data-scripts)
6. [Troubleshooting](#troubleshooting)

---

## MongoDB Setup (Application Database)

MongoDB is used for storing PROMISE AI's application data (datasets, workspaces, training metadata).

### Option 1: MongoDB Atlas (Cloud - Recommended)
✅ **Easiest - Free tier, no installation**

1. **Sign up:** https://www.mongodb.com/cloud/atlas
2. **Create cluster:** Free M0 tier
3. **Get connection string:**
   ```
   mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/
   ```
4. **Configure:** Update `/app/backend/.env`:
   ```env
   MONGO_URL=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/
   ```

**Pros:** Cloud-hosted, automatic backups, accessible anywhere

### Option 2: Local MongoDB

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

### Option 3: Docker MongoDB

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

### What Gets Created Automatically:

When you upload your first dataset, MongoDB automatically creates:

- **Database:** `promise_ai`
- **Collections:**
  - `datasets` - Uploaded data (direct or GridFS reference)
  - `saved_states` - Saved workspaces
  - `fs.files` & `fs.chunks` - GridFS for large files (>10MB)

**No manual setup required!**

---

## Supported External Databases

PROMISE AI can connect to these external databases to load data for analysis:

| Database | Port | Connection Format | Driver |
|----------|------|-------------------|--------|
| **PostgreSQL** | 5432 | URL or parameters | psycopg2-binary |
| **MySQL** | 3306 | URL or parameters | pymysql |
| **Oracle** | 1521 | URL or parameters | cx_Oracle |
| **SQL Server** | 1433 | URL or key-value | pyodbc |
| **MongoDB** | 27017 | URL | pymongo |

### Connection Methods

**Method 1: Connection String (URL Format)**
```
postgresql://user:pass@host:port/database
mysql://user:pass@host:port/database
oracle://user:pass@host:port/service_name
mssql://user:pass@host:port/database
mongodb://user:pass@host:port/database
```

**Method 2: Individual Parameters**
- Host
- Port
- Username
- Password
- Database/Service Name

**Method 3: Key-Value (SQL Server)**
```
Server=host,port;Database=db;User Id=user;Password=pass;
```

---

## Test Database Setup

### Quick Setup with Docker (All 4 Databases)

```bash
cd /app
docker compose -f docker-compose-testdbs.yml up -d
```

This starts:
- **Oracle XE** on port 1521
- **PostgreSQL** on port 5432
- **MySQL** on port 3306
- **SQL Server** on port 1433

### Connection Details

#### Oracle
```
Host: localhost
Port: 1521
Service Name: XEPDB1
Username: testuser
Password: testpass

Connection String:
oracle://testuser:testpass@localhost:1521/XEPDB1
```

#### PostgreSQL
```
Host: localhost
Port: 5432
Database: testdb
Username: testuser
Password: testpass

Connection String:
postgresql://testuser:testpass@localhost:5432/testdb
```

#### MySQL
```
Host: localhost
Port: 3306
Database: testdb
Username: testuser
Password: testpass

Connection String:
mysql://testuser:testpass@localhost:3306/testdb
```

#### SQL Server
```
Host: localhost
Port: 1433
Database: master
Username: sa
Password: StrongPass123!

Connection String:
mssql://sa:StrongPass123!@localhost:1433/master

OR Key-Value:
Server=localhost,1433;Database=master;User Id=sa;Password=StrongPass123!;
```

### Waiting for Databases to Start

```bash
# Check status
docker compose -f docker-compose-testdbs.yml ps

# View logs
docker compose -f docker-compose-testdbs.yml logs -f

# Wait for health checks to pass (especially Oracle - 2-3 mins)
```

---

## Connection Examples

### Using PROMISE AI UI

1. Go to Dashboard
2. Click "Database Connection" tab
3. Select database type from dropdown
4. Choose connection method:
   - **Use Connection String:** Paste full URL
   - **Individual Parameters:** Fill in form
5. Click "Test Connection"
6. If successful, click "List Tables"
7. Select table and click "Load Data"

### Testing via CLI

**PostgreSQL:**
```bash
psql -h localhost -p 5432 -U testuser -d testdb
```

**MySQL:**
```bash
mysql -h localhost -P 3306 -u testuser -p testdb
```

**Oracle:**
```bash
sqlplus testuser/testpass@localhost:1521/XEPDB1
```

**SQL Server:**
```bash
sqlcmd -S localhost,1433 -U sa -P StrongPass123! -d master
```

---

## Test Data Scripts

### Quick Load (All Tables)

The file `/app/test_data_postgres_mysql.sql` contains ready-to-use test data.

**For PostgreSQL:**
```bash
psql -h localhost -U testuser -d testdb -f /app/test_data_postgres_mysql.sql
```

**For MySQL:**
```bash
mysql -h localhost -u testuser -p testdb < /app/test_data_postgres_mysql.sql
```

### What Gets Created:

**1. employees table (15 records)**
- Strong correlation: age ↔ salary ↔ years_experience
- Columns: id, name, age, department, salary, hire_date, years_experience, performance_score

**2. sales_data table (15 records)**
- Columns: transaction_id, product, quantity, price, sale_date, region, customer_age, satisfaction_score

**3. customer_analytics table (15 records)**
- Strong correlations: annual_income ↔ spending_score ↔ avg_purchase_value
- Columns: customer_id, age, annual_income, spending_score, membership_years, total_purchases, avg_purchase_value, region

### Manual SQL Scripts

#### PostgreSQL / MySQL

```sql
-- Create employees table
CREATE TABLE IF NOT EXISTS employees (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    age INT,
    department VARCHAR(50),
    salary DECIMAL(10, 2),
    hire_date DATE,
    years_experience INT,
    performance_score DECIMAL(3, 2)
);

-- Insert sample data
INSERT INTO employees VALUES
(1, 'John Doe', 35, 'Engineering', 95000.00, '2020-01-15', 12, 4.5),
(2, 'Jane Smith', 28, 'Marketing', 72000.00, '2021-03-22', 5, 4.2),
(3, 'Bob Johnson', 42, 'Engineering', 110000.00, '2018-07-10', 18, 4.8),
(4, 'Alice Brown', 31, 'Sales', 85000.00, '2019-11-05', 8, 4.3),
(5, 'Charlie Wilson', 38, 'Engineering', 98000.00, '2020-09-18', 14, 4.6);

-- Verify
SELECT COUNT(*) FROM employees;
```

#### Oracle

```sql
-- Create employees table
CREATE TABLE employees (
    id NUMBER PRIMARY KEY,
    name VARCHAR2(100),
    age NUMBER,
    department VARCHAR2(50),
    salary NUMBER(10, 2),
    hire_date DATE
);

-- Insert sample data
INSERT INTO employees VALUES (1, 'John Doe', 35, 'Engineering', 95000.00, TO_DATE('2020-01-15', 'YYYY-MM-DD'));
INSERT INTO employees VALUES (2, 'Jane Smith', 28, 'Marketing', 72000.00, TO_DATE('2021-03-22', 'YYYY-MM-DD'));
INSERT INTO employees VALUES (3, 'Bob Johnson', 42, 'Engineering', 110000.00, TO_DATE('2018-07-10', 'YYYY-MM-DD'));
COMMIT;

-- Verify
SELECT COUNT(*) FROM employees;
```

#### SQL Server

```sql
-- Create employees table
CREATE TABLE employees (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    age INT,
    department VARCHAR(50),
    salary DECIMAL(10, 2),
    hire_date DATE
);

-- Insert sample data
INSERT INTO employees VALUES
(1, 'John Doe', 35, 'Engineering', 95000.00, '2020-01-15'),
(2, 'Jane Smith', 28, 'Marketing', 72000.00, '2021-03-22'),
(3, 'Bob Johnson', 42, 'Engineering', 110000.00, '2018-07-10');

-- Verify
SELECT COUNT(*) FROM employees;
```

---

## Troubleshooting

### Common Issues

#### MongoDB Issues

**1. Connection Refused**
```bash
# Check if MongoDB is running
mongosh --eval "db.serverStatus()"

# Start MongoDB
brew services start mongodb-community  # macOS
sudo systemctl start mongod            # Linux
docker start promise-mongodb           # Docker
```

**2. Authentication Failed**
```bash
# Verify credentials in connection string
# Check username/password have no special characters that need encoding
```

#### Oracle Issues

**1. Long Startup Time**
- Oracle XE can take 2-3 minutes to fully start
- Wait for Docker health check to pass

**2. Service Name Issues**
- Use `XEPDB1` for pluggable database
- Or `XE` for container database
- Check with: `lsnrctl status`

**3. Connection Refused**
```bash
# Check container status
docker ps | grep oracle

# View logs
docker logs <container_name>
```

#### SQL Server Issues

**1. Password Requirements**
- Must be strong: uppercase, lowercase, numbers, symbols
- Minimum 8 characters
- Example: `StrongPass123!`

**2. Driver Not Found (Linux)**
```bash
# Install ODBC Driver 17
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql17
```

**3. Connection Issues**
```bash
# Verify SQL Server is running
docker ps | grep mssql

# Test connection
sqlcmd -S localhost,1433 -U sa -P StrongPass123!
```

#### PostgreSQL Issues

**1. Authentication Failed**
```bash
# Check pg_hba.conf allows connections
# Or use Docker container which is pre-configured
```

**2. Database Not Found**
```bash
# Create database first
psql -U postgres -c "CREATE DATABASE testdb;"
```

#### MySQL Issues

**1. Access Denied**
```bash
# Check user privileges
mysql -u root -p
> GRANT ALL PRIVILEGES ON testdb.* TO 'testuser'@'%';
> FLUSH PRIVILEGES;
```

**2. Connection Issues**
```bash
# Verify MySQL is running
docker ps | grep mysql

# Check logs
docker logs <mysql_container>
```

### General Troubleshooting

**Port Conflicts:**
```bash
# Check if port is in use
lsof -i:5432  # PostgreSQL
lsof -i:3306  # MySQL
lsof -i:1521  # Oracle
lsof -i:1433  # SQL Server

# Change ports in docker-compose-testdbs.yml if needed
```

**Network Issues:**
- Try `host.docker.internal` instead of `localhost` on Mac/Windows
- Check firewall settings
- Verify Docker network: `docker network ls`

**Test Connection via Python:**
```python
# PostgreSQL
import psycopg2
conn = psycopg2.connect("postgresql://testuser:testpass@localhost:5432/testdb")
print("PostgreSQL connected!")

# MySQL
import pymysql
conn = pymysql.connect(host='localhost', user='testuser', password='testpass', database='testdb')
print("MySQL connected!")

# MongoDB
from pymongo import MongoClient
client = MongoClient("mongodb://localhost:27017")
print(client.list_database_names())
```

---

## Testing Workflow

1. **Start databases** (Docker or local)
2. **Wait for ready state** (check `docker ps` status)
3. **Create test tables** (use SQL scripts above)
4. **Test in PROMISE AI:**
   - Dashboard → Database Connection
   - Select database type
   - Enter connection details
   - Test Connection → List Tables → Load Data
5. **Analyze data:**
   - Data Profiler
   - Predictive Analysis
   - Visualizations

---

## Stopping Test Databases

```bash
# Stop all test databases
cd /app
docker compose -f docker-compose-testdbs.yml down

# Stop and remove data
docker compose -f docker-compose-testdbs.yml down -v
```

---

## Summary

### MongoDB (Application Database):
- ✅ Required for PROMISE AI
- ✅ Auto-creates database and collections
- ✅ Use Atlas (cloud) or local/Docker

### External Databases (Optional):
- ✅ 5 types supported
- ✅ Use for loading external data
- ✅ Test setup via Docker available

### Quick Test:
```bash
# Start test databases
docker compose -f docker-compose-testdbs.yml up -d

# Load test data
psql -h localhost -U testuser -d testdb -f /app/test_data_postgres_mysql.sql

# Test in PROMISE AI UI
```

**All database setups are designed for minimal configuration - just provide connection details and start analyzing!**
