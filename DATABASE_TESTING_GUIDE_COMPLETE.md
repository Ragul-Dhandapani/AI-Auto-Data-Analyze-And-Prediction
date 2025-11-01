# PROMISE AI - Database Testing Guide
**Date:** November 2025  
**Status:** ✅ Ready for Testing - Custom SQL Query Feature Implemented

---

## 🎯 What's New

### Custom SQL Query Feature ✨
**Just Implemented!** Users can now:
- Write complex SQL queries (JOINs, aggregations, WHERE clauses, etc.)
- Execute queries directly from the UI
- Load query results for full analysis (Data Profiling, ML Models, Visualizations)
- Works with all 5 database types

---

## 🗄️ Your Database Connection Details

Based on your local Docker setup:

### PostgreSQL
```
Host: localhost (or 0.0.0.0)
Port: 5432
Username: testuser
Password: testpass
Database: testdb
```

**Connection String:**
```
postgresql://testuser:testpass@localhost:5432/testdb
```

### MySQL
```
Host: localhost
Port: 3306
Username: testuser
Password: testpass
Database: testdb
```

**Connection String:**
```
mysql://testuser:testpass@localhost:3306/testdb
```

### SQL Server
```
Host: localhost
Port: 1433
Username: sa
Password: StrongPass123!
Database: master
```

**Connection String:**
```
mssql://sa:StrongPass123!@localhost:1433/master
```

### Oracle
```
Host: localhost
Port: 1521
Username: testuser
Password: testpass
Service Name: XEPDB1
```

**Connection String:**
```
oracle://testuser:testpass@localhost:1521/XEPDB1
```

---

## 📊 Test Datasets Setup

I've created SQL scripts to set up 3 datasets (small, medium, large) + 2 reference tables.

### Step 1: Load Test Data into PostgreSQL

```bash
# From your machine where Docker is running
psql -h localhost -U testuser -d testdb -f /path/to/test_datasets_setup.sql

# If prompted for password: testpass
```

### Step 2: Load Test Data into MySQL

```bash
# From your machine
mysql -h localhost -u testuser -p testdb < /path/to/test_datasets_mysql.sql

# Password: testpass
```

### What Gets Created:

| Table Name | Rows | Purpose | Key Features |
|------------|------|---------|--------------|
| **employees_small** | 100 | Small dataset | Quick testing, salary correlations |
| **sales_medium** | 1,000 | Medium dataset | Category analysis, regional patterns |
| **transactions_large** | 10,000 | Large dataset | GridFS testing, time-series data |
| **departments** | 5 | Reference table | For JOIN examples |
| **customer_info** | 5,000 | Reference table | For JOIN with transactions |

---

## 🧪 Testing Scenarios

### Test 1: Connection Testing ✅

**What to Test:**
- Test connection with individual parameters
- Test connection with connection string
- Verify all 4 database types

**Steps:**
1. Go to Dashboard → "Database Connection" tab
2. Select database type (e.g., PostgreSQL)
3. Enter connection details
4. Click "Test Connection"
5. ✅ Should see "Connected" with green checkmark

**Expected Result:** Connection successful for all database types

---

### Test 2: Table Listing ✅

**What to Test:**
- List tables from each database
- Verify all 5 tables appear

**Steps:**
1. After successful connection test
2. Click "List Tables"
3. ✅ Should see dropdown with:
   - employees_small
   - sales_medium
   - transactions_large
   - departments
   - customer_info

**Expected Result:** All tables listed correctly

---

### Test 3: Simple Table Load ✅

**What to Test:**
- Load a small table (100 rows)
- Verify data preview
- Run full analysis

**Steps:**
1. Select "employees_small" from dropdown
2. Click "Load Table"
3. ✅ Should see:
   - Success toast: "Data loaded successfully!"
   - Row count: 100
   - Column count: 10
   - Data preview (first 10 rows)
4. Navigate to "Data Profiler" tab
5. ✅ Should see:
   - Summary statistics
   - Missing values (should be 0)
   - Column analysis
6. Click "Predictive Analysis"
7. ✅ Should run full ML analysis with charts

**Expected Result:** Complete analysis pipeline works with database data

---

### Test 4: Medium Table Load (GridFS Test) ✅

**What to Test:**
- Load medium dataset (1,000 rows)
- Verify storage type

**Steps:**
1. Load "sales_medium" table
2. ✅ Check response for `storage_type: "direct"` (under 10MB)
3. Verify full analysis works

**Expected Result:** Data loaded directly (not GridFS), analysis works perfectly

---

### Test 5: Large Table Load (GridFS Test) ✅

**What to Test:**
- Load large dataset (10,000 rows)
- Verify GridFS storage

**Steps:**
1. Load "transactions_large" table
2. ✅ Check if `storage_type: "gridfs"` (if over 10MB)
3. Verify data profiling works
4. Verify ML training works
5. Verify charts generate

**Expected Result:** Large data handled via GridFS, no BSON size errors

---

### Test 6: Custom SQL Query - Simple JOIN 🆕

**What to Test:**
- Execute a SQL query with JOIN
- Verify results load for analysis

**Sample Query (PostgreSQL/MySQL):**
```sql
SELECT e.name, e.salary, e.department, d.dept_head, d.budget
FROM employees_small e
JOIN departments d ON e.department = d.dept_name
WHERE e.salary > 70000
ORDER BY e.salary DESC
```

**Steps:**
1. Go to Dashboard → "Custom SQL Query" tab (NEW!)
2. Select database type (PostgreSQL or MySQL)
3. Enter connection details
4. Click "Test Connection"
5. ✅ Connection successful
6. Enter the SQL query above
7. Click "Execute Query & Load Data"
8. ✅ Should see:
   - Success toast with row count
   - Dataset name: "Query: SELECT e.name..."
   - Data preview showing joined results
9. Navigate to "Data Profiler"
10. ✅ Should see profile of query results
11. Run "Predictive Analysis"
12. ✅ ML models train on query results

**Expected Result:** JOIN query executes, results loaded, full analysis works

---

### Test 7: Custom SQL Query - Complex Aggregation 🆕

**Sample Query (PostgreSQL/MySQL):**
```sql
SELECT 
    department,
    COUNT(*) as employee_count,
    AVG(salary) as avg_salary,
    MAX(salary) as max_salary,
    MIN(years_experience) as min_experience
FROM employees_small
GROUP BY department
HAVING AVG(salary) > 60000
ORDER BY avg_salary DESC
```

**Steps:**
1. Same as Test 6, but use this query
2. ✅ Results show aggregated data by department
3. Verify analysis works on aggregated data

**Expected Result:** Aggregation query works, analysis on grouped data successful

---

### Test 8: Custom SQL Query - Multi-Table JOIN 🆕

**Sample Query (PostgreSQL/MySQL):**
```sql
SELECT 
    t.product_category,
    c.membership_level,
    COUNT(*) as transaction_count,
    SUM(t.final_amount) as total_revenue,
    AVG(t.customer_rating) as avg_rating
FROM transactions_large t
JOIN customer_info c ON t.customer_id = c.customer_id
WHERE t.payment_status = 'Completed'
GROUP BY t.product_category, c.membership_level
ORDER BY total_revenue DESC
LIMIT 100
```

**Steps:**
1. Execute this complex query
2. ✅ Should return ~100 rows (due to LIMIT)
3. Verify columns: product_category, membership_level, transaction_count, total_revenue, avg_rating
4. Run full analysis

**Expected Result:** Complex multi-table JOIN with aggregation works

---

### Test 9: Date-Based Analysis 🆕

**Sample Query (PostgreSQL):**
```sql
SELECT 
    DATE_TRUNC('month', transaction_date) as month,
    product_category,
    SUM(final_amount) as monthly_revenue,
    COUNT(*) as order_count
FROM transactions_large
WHERE transaction_date >= '2023-06-01'
GROUP BY DATE_TRUNC('month', transaction_date), product_category
ORDER BY month, monthly_revenue DESC
```

**MySQL Version:**
```sql
SELECT 
    DATE_FORMAT(transaction_date, '%Y-%m-01') as month,
    product_category,
    SUM(final_amount) as monthly_revenue,
    COUNT(*) as order_count
FROM transactions_large
WHERE transaction_date >= '2023-06-01'
GROUP BY DATE_FORMAT(transaction_date, '%Y-%m-01'), product_category
ORDER BY month, monthly_revenue DESC
```

**Steps:**
1. Execute date-based query
2. ✅ Results show monthly aggregations
3. Run time-series analysis

**Expected Result:** Date functions work, time-series data analyzed

---

### Test 10: Connection String Parsing ✅

**What to Test:**
- Parse connection string into individual fields
- Auto-fill connection details

**Steps:**
1. Click "Use Connection String" checkbox
2. Paste: `postgresql://testuser:testpass@localhost:5432/testdb`
3. (Feature already implemented for connection test)
4. ✅ Should connect successfully

**Expected Result:** Connection string parsed and used correctly

---

### Test 11: Error Handling 🔍

**What to Test:**
- Invalid SQL query
- Wrong credentials
- Non-existent table

**Test Cases:**

**A) Invalid SQL Syntax:**
```sql
SELECT * FORM employees_small  -- intentional typo
```
✅ Should show error: "Failed to execute query: syntax error..."

**B) Wrong Password:**
- Enter incorrect password
- ✅ Should show: "Connection test failed"

**C) Non-existent Table:**
```sql
SELECT * FROM non_existent_table
```
✅ Should show error: "table does not exist"

**Expected Result:** Graceful error handling with clear messages

---

### Test 12: End-to-End Workflow 🎯

**Complete User Journey:**

1. **Upload File** (existing feature)
   - Upload CSV → Profile → Analyze → Save Workspace

2. **Load Table** (existing feature)
   - Connect DB → List Tables → Load → Analyze → Save Workspace

3. **Custom Query** (NEW feature)
   - Connect DB → Write Query → Execute → Analyze → Save Workspace

4. **Training Metadata**
   - View all 3 datasets in Training Metadata page
   - Download PDF report

**Expected Result:** All 3 data sources (file, table, query) work identically for analysis

---

## 📋 Testing Checklist

### Database Connection Features:
- [ ] Test PostgreSQL connection (password-based)
- [ ] Test MySQL connection (password-based)
- [ ] Test Oracle connection (password-based)
- [ ] Test SQL Server connection (password-based)
- [ ] Test connection string parsing
- [ ] Test individual parameter entry
- [ ] Test connection error handling

### Table Loading:
- [ ] List tables from database
- [ ] Load small dataset (100 rows)
- [ ] Load medium dataset (1,000 rows)
- [ ] Load large dataset (10,000 rows)
- [ ] Verify GridFS for large data
- [ ] Verify data preview display

### Custom SQL Query (NEW):
- [ ] Simple SELECT query
- [ ] Query with JOIN (2 tables)
- [ ] Query with multiple JOINs
- [ ] Query with WHERE clause
- [ ] Query with GROUP BY and HAVING
- [ ] Query with ORDER BY and LIMIT
- [ ] Query with date functions
- [ ] Query with aggregations
- [ ] Invalid SQL query (error handling)

### Analysis Pipeline:
- [ ] Data Profiler works with DB data
- [ ] Data Profiler works with query results
- [ ] ML models train on DB data
- [ ] ML models train on query results
- [ ] Charts generate from DB data
- [ ] Charts generate from query results
- [ ] Chat feature works with DB data
- [ ] Workspace save/load with DB data

---

## 🚀 Quick Start Testing Commands

### PostgreSQL Quick Test:
```bash
# Connect and verify
psql -h localhost -U testuser -d testdb -c "SELECT 'employees_small' AS table_name, COUNT(*) AS row_count FROM employees_small UNION ALL SELECT 'sales_medium', COUNT(*) FROM sales_medium UNION ALL SELECT 'transactions_large', COUNT(*) FROM transactions_large;"
```

### MySQL Quick Test:
```bash
# Connect and verify
mysql -h localhost -u testuser -p testdb -e "SELECT 'employees_small' AS table_name, COUNT(*) AS row_count FROM employees_small UNION ALL SELECT 'sales_medium', COUNT(*) FROM sales_medium UNION ALL SELECT 'transactions_large', COUNT(*) FROM transactions_large;"
```

---

## 🎉 Success Criteria

**All tests pass if:**
1. ✅ All 4 database types connect successfully
2. ✅ Tables list correctly
3. ✅ Small, medium, large datasets load
4. ✅ GridFS handles large data (>10MB)
5. ✅ Custom SQL queries execute (NEW)
6. ✅ JOIN queries work (NEW)
7. ✅ Aggregation queries work (NEW)
8. ✅ Data Profiler works with all sources
9. ✅ ML training works with all sources
10. ✅ Charts generate for all sources
11. ✅ Workspace save/load works
12. ✅ Training metadata tracks all sources

---

## 📞 Support

**Database Connection Issues?**
- Check if Docker containers are running: `docker ps`
- Verify ports are accessible: `telnet localhost 5432`
- Check credentials match docker-compose-testdbs.yml

**Query Execution Issues?**
- Verify SQL syntax for your database type
- Check table names match exactly (case-sensitive in some DBs)
- Use LIMIT to prevent loading too much data

**Feature Not Working?**
- Check backend logs: `tail -f /var/log/supervisor/backend.err.log`
- Check frontend console (F12 → Console)
- Verify services running: `sudo supervisorctl status`

---

**Happy Testing!** 🎊

All database features are now ready including the new Custom SQL Query functionality!
