# Database Testing Setup Guide

This guide will help you set up test databases for comprehensive testing of PROMISE AI's database connection functionality.

## Quick Setup with Docker (Recommended)

If you have Docker installed, you can quickly spin up all test databases:

```bash
cd /app
docker compose -f docker-compose-testdbs.yml up -d
```

This will start:
- **Oracle XE** on port 1521
- **PostgreSQL** on port 5432
- **MySQL** on port 3306
- **SQL Server** on port 1433

### Connection Details

#### Oracle
- Host: localhost
- Port: 1521
- Service Name: XEPDB1
- Username: testuser
- Password: testpass

#### PostgreSQL
- Host: localhost
- Port: 5432
- Database: testdb
- Username: testuser
- Password: testpass

#### MySQL
- Host: localhost
- Port: 3306
- Database: testdb
- Username: testuser
- Password: testpass

#### SQL Server
- Host: localhost
- Port: 1433
- Database: master
- Username: sa
- Password: StrongPass123!

## Creating Test Tables

Once connected, you can create sample tables using the provided SQL scripts:

### PostgreSQL / MySQL
```sql
CREATE TABLE employees (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    age INT,
    department VARCHAR(50),
    salary DECIMAL(10, 2),
    hire_date DATE
);

INSERT INTO employees VALUES
(1, 'John Doe', 35, 'Engineering', 95000.00, '2020-01-15'),
(2, 'Jane Smith', 28, 'Marketing', 72000.00, '2021-03-22'),
(3, 'Bob Johnson', 42, 'Engineering', 110000.00, '2018-07-10'),
(4, 'Alice Brown', 31, 'Sales', 85000.00, '2019-11-05'),
(5, 'Charlie Wilson', 38, 'Engineering', 98000.00, '2020-09-18'),
(6, 'Diana Miller', 29, 'Marketing', 68000.00, '2022-01-20'),
(7, 'Eve Davis', 45, 'Sales', 105000.00, '2017-04-12'),
(8, 'Frank Garcia', 33, 'Engineering', 88000.00, '2021-06-30'),
(9, 'Grace Lee', 27, 'Marketing', 65000.00, '2022-08-15'),
(10, 'Henry Martinez', 40, 'Sales', 92000.00, '2019-02-28');

CREATE TABLE sales_data (
    transaction_id INT PRIMARY KEY,
    product VARCHAR(100),
    quantity INT,
    price DECIMAL(10, 2),
    sale_date DATE,
    region VARCHAR(50)
);

INSERT INTO sales_data VALUES
(1, 'Laptop', 5, 1200.00, '2024-01-10', 'North'),
(2, 'Mouse', 25, 25.00, '2024-01-11', 'South'),
(3, 'Keyboard', 15, 75.00, '2024-01-12', 'East'),
(4, 'Monitor', 8, 350.00, '2024-01-13', 'West'),
(5, 'Laptop', 3, 1200.00, '2024-01-14', 'North'),
(6, 'Mouse', 30, 25.00, '2024-01-15', 'South'),
(7, 'Keyboard', 12, 75.00, '2024-01-16', 'East'),
(8, 'Monitor', 6, 350.00, '2024-01-17', 'West'),
(9, 'Laptop', 7, 1200.00, '2024-01-18', 'North'),
(10, 'Mouse', 20, 25.00, '2024-01-19', 'South');
```

### Oracle
```sql
CREATE TABLE employees (
    id NUMBER PRIMARY KEY,
    name VARCHAR2(100),
    age NUMBER,
    department VARCHAR2(50),
    salary NUMBER(10, 2),
    hire_date DATE
);

INSERT INTO employees VALUES (1, 'John Doe', 35, 'Engineering', 95000.00, TO_DATE('2020-01-15', 'YYYY-MM-DD'));
INSERT INTO employees VALUES (2, 'Jane Smith', 28, 'Marketing', 72000.00, TO_DATE('2021-03-22', 'YYYY-MM-DD'));
INSERT INTO employees VALUES (3, 'Bob Johnson', 42, 'Engineering', 110000.00, TO_DATE('2018-07-10', 'YYYY-MM-DD'));
INSERT INTO employees VALUES (4, 'Alice Brown', 31, 'Sales', 85000.00, TO_DATE('2019-11-05', 'YYYY-MM-DD'));
INSERT INTO employees VALUES (5, 'Charlie Wilson', 38, 'Engineering', 98000.00, TO_DATE('2020-09-18', 'YYYY-MM-DD'));
COMMIT;
```

### SQL Server
```sql
CREATE TABLE employees (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    age INT,
    department VARCHAR(50),
    salary DECIMAL(10, 2),
    hire_date DATE
);

INSERT INTO employees VALUES
(1, 'John Doe', 35, 'Engineering', 95000.00, '2020-01-15'),
(2, 'Jane Smith', 28, 'Marketing', 72000.00, '2021-03-22'),
(3, 'Bob Johnson', 42, 'Engineering', 110000.00, '2018-07-10'),
(4, 'Alice Brown', 31, 'Sales', 85000.00, '2019-11-05'),
(5, 'Charlie Wilson', 38, 'Engineering', 98000.00, '2020-09-18');
```

## Testing Workflow

1. **Start the databases** using Docker compose or your own database instances
2. **Wait for databases to be ready** (Oracle can take 2-3 minutes on first start)
3. **Create test tables** using the SQL scripts above
4. **Test connection** in PROMISE AI:
   - Go to Dashboard
   - Select "Database Connection" tab
   - Choose database type
   - Enter connection details or connection string
   - Click "Test Connection"
5. **Load table** once connection is successful
6. **Test all features**:
   - Data Profiler
   - Predictive Analysis
   - Visualization Panel
   - Chat functionality

## Connection String Examples

### PostgreSQL
```
postgresql://testuser:testpass@localhost:5432/testdb
```

### MySQL
```
mysql://testuser:testpass@localhost:3306/testdb
```

### Oracle
```
oracle://testuser:testpass@localhost:1521/XEPDB1
```

### SQL Server
```
mssql://sa:StrongPass123!@localhost:1433/master
```
OR
```
Server=localhost,1433;Database=master;User Id=sa;Password=StrongPass123!;
```

## Troubleshooting

### Oracle Issues
- **Long startup time**: Oracle XE can take 2-3 minutes to fully start
- **Connection refused**: Wait for health check to pass: `docker ps` and check STATUS
- **Service name**: Use XEPDB1 for pluggable database or XE for container database

### SQL Server Issues
- **Password requirements**: Must be strong (uppercase, lowercase, numbers, symbols)
- **Driver not found**: Ensure ODBC Driver 17 for SQL Server is installed
- **Linux setup**: May need to install msodbcsql17

### General
- **Port conflicts**: If ports are already in use, modify docker-compose-testdbs.yml
- **Permission errors**: Ensure Docker daemon is running and user has permissions
- **Network issues**: Use `host.docker.internal` instead of `localhost` on some systems

## Stopping Test Databases

```bash
cd /app
docker compose -f docker-compose-testdbs.yml down
```

To remove data volumes:
```bash
docker compose -f docker-compose-testdbs.yml down -v
```
