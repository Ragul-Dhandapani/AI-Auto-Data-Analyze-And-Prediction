# Professional APM/Observability Datasets - Quick Reference

## 📊 Available SQL Scripts

### PostgreSQL
- `postgresql_small.sql` - 100 rows (employees + departments)
- `postgresql_medium.sql` - 1,000 rows (sales data)
- `postgresql_large.sql` - 10,000 rows (transactions + customers)
- **`postgresql_apm_observability.sql`** - 20,000 rows (4 APM tables) ⭐

### MySQL
- `mysql_small.sql` - 100 rows (employees + departments)
- `mysql_medium.sql` - 1,000 rows (sales data)
- `mysql_large.sql` - 10,000 rows (transactions + customers)
- **`mysql_apm_observability.sql`** - 20,000 rows (4 APM tables) ⭐

---

## 🎯 APM Observability Datasets (Professional)

### 4 Tables with Real-World Monitoring Data

#### 1. **api_request_logs** (10,000 rows)
**Purpose:** API Performance Monitoring
- Request/Response tracking
- Latency measurements (P50, P95, P99)
- Error tracking (4xx, 5xx)
- Regional performance
- Cache hit ratios

**Key Columns:**
- `response_time_ms` - For latency analysis
- `http_status` - Success/error rates
- `service_name`, `endpoint` - Service breakdown
- `region`, `datacenter` - Geographic analysis

#### 2. **system_metrics** (5,000 rows)
**Purpose:** Infrastructure Monitoring
- CPU, Memory, Disk usage
- Network traffic
- Load averages
- Process counts

**Key Columns:**
- `cpu_usage_percent`, `memory_usage_percent`
- `disk_read_mbps`, `disk_write_mbps`
- `network_in_mbps`, `network_out_mbps`
- `load_average_1m`, `load_average_5m`

#### 3. **error_logs** (2,000 rows)
**Purpose:** Error Tracking
- Exception monitoring
- Severity levels (critical/error/warning)
- Error resolution tracking
- Assignment tracking

**Key Columns:**
- `severity` - Critical, error, warning
- `error_type`, `error_message`
- `occurrences` - Frequency
- `resolved` - Status

#### 4. **distributed_traces** (3,000 rows)
**Purpose:** Distributed Tracing
- Microservices call chains
- Service dependencies
- Span relationships
- JSON metadata

**Key Columns:**
- `trace_id`, `span_id`, `parent_span_id`
- `service_name`, `operation_name`
- `duration_ms`, `status`
- `tags` (JSON), `logs` (JSON)

---

## 🚀 How to Load

### PostgreSQL (Your AWS RDS)
```bash
# Set your connection details
PG_HOST="promise-ai-test-postgresql.cgxf9inhpsec.us-east-1.rds.amazonaws.com"
DB_USER="testuser"
DB_PASS="your_password"

# Load APM observability data (~30 seconds)
PGPASSWORD=$DB_PASS psql -h $PG_HOST -U $DB_USER -d testdb -f /app/postgresql_apm_observability.sql
```

### MySQL (Your AWS RDS)
```bash
# Set your connection details
MYSQL_HOST="promise-ai-test-mysql.xxx.us-east-1.rds.amazonaws.com"
DB_USER="testuser"
DB_PASS="your_password"

# Load APM observability data (~3-5 minutes due to stored procedures)
mysql -h $MYSQL_HOST -u $DB_USER -p$DB_PASS testdb < /app/mysql_apm_observability.sql
```

---

## 💡 Testing Scenarios

### 1. Latency Analysis
```sql
-- PostgreSQL
SELECT 
    endpoint,
    COUNT(*) as requests,
    AVG(response_time_ms) as avg_ms,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time_ms) as p95_ms
FROM api_request_logs
GROUP BY endpoint
ORDER BY avg_ms DESC
LIMIT 10;

-- MySQL
SELECT 
    endpoint,
    COUNT(*) as requests,
    AVG(response_time_ms) as avg_ms,
    MAX(response_time_ms) as max_ms
FROM api_request_logs
GROUP BY endpoint
ORDER BY avg_ms DESC
LIMIT 10;
```

### 2. Error Rate by Service
```sql
SELECT 
    service_name,
    COUNT(*) as total,
    SUM(CASE WHEN http_status >= 500 THEN 1 ELSE 0 END) as errors,
    ROUND(100.0 * SUM(CASE WHEN http_status >= 500 THEN 1 ELSE 0 END) / COUNT(*), 2) as error_rate
FROM api_request_logs
GROUP BY service_name
ORDER BY error_rate DESC;
```

### 3. Infrastructure Correlation
```sql
SELECT 
    host_name,
    AVG(cpu_usage_percent) as avg_cpu,
    AVG(memory_usage_percent) as avg_mem,
    AVG(load_average_1m) as avg_load
FROM system_metrics
WHERE cpu_usage_percent > 80 OR memory_usage_percent > 80
GROUP BY host_name;
```

### 4. Complex JOIN (Latency + Errors)
```sql
SELECT 
    a.service_name,
    COUNT(a.id) as requests,
    AVG(a.response_time_ms) as avg_latency,
    COUNT(e.id) as errors,
    ROUND(100.0 * COUNT(e.id) / COUNT(a.id), 2) as error_pct
FROM api_request_logs a
LEFT JOIN error_logs e ON a.request_id = e.request_id
GROUP BY a.service_name
ORDER BY error_pct DESC;
```

---

## 🧪 What to Test in PROMISE AI

### Via "Database Connection" Tab:
1. Connect to your AWS RDS
2. List Tables → See 4 APM tables
3. Load "api_request_logs" (10,000 rows)
4. Run Data Profiler → See latency distributions
5. Run Predictive Analysis → ML models on latency
6. Save workspace

### Via "Custom SQL Query" Tab:
1. Connect to AWS RDS
2. Run JOIN query (above)
3. Load results into PROMISE AI
4. Analyze query results with ML models
5. Generate charts
6. Chat: "Show correlation between latency and errors"

---

## ✅ Expected Results

### Data Profiler Should Show:
- 10,000 rows with 19 columns (api_request_logs)
- Response time distribution (50-5000ms)
- 85% success rate (status 200)
- 15% errors (status 4xx/5xx)
- No missing values
- Multiple service categories

### Predictive Analysis Should:
- Train 6 ML models
- Generate 15+ charts
- Show correlations:
  - High latency ↔ Errors
  - CPU usage ↔ Memory usage
  - Request volume ↔ Load average
- Provide AI insights on performance patterns

### Visualizations:
- Latency histogram (distribution)
- Error rate by service (bar chart)
- Time-series trends
- Correlation heatmaps
- Scatter plots (latency vs status)

---

## 📈 Real-World Use Cases

1. **SRE Dashboard:** Monitor API latency P95/P99
2. **Capacity Planning:** CPU/Memory trends
3. **Incident Investigation:** Correlate errors with latency spikes
4. **Service Health:** Track error rates by service
5. **Performance Tuning:** Identify slow endpoints
6. **Alerting:** Detect anomalies in metrics

---

## 🎓 Advanced Queries to Try

### Time-Series Analysis (PostgreSQL)
```sql
SELECT 
    DATE_TRUNC('hour', timestamp) as hour,
    service_name,
    AVG(response_time_ms) as avg_latency,
    COUNT(*) as requests
FROM api_request_logs
GROUP BY hour, service_name
ORDER BY hour, avg_latency DESC;
```

### Anomaly Detection
```sql
SELECT * FROM system_metrics
WHERE cpu_usage_percent > 90 
   OR memory_usage_percent > 90
   OR load_average_1m > 8
ORDER BY timestamp DESC;
```

### Service Dependency Map
```sql
SELECT 
    service_name,
    upstream_service,
    COUNT(*) as calls,
    AVG(upstream_latency_ms) as avg_upstream_ms
FROM api_request_logs
WHERE upstream_service IS NOT NULL
GROUP BY service_name, upstream_service;
```

---

## 📊 Data Characteristics

### Realistic Distributions:
- **70%** requests are fast (50-200ms)
- **20%** are medium (200-500ms)
- **7%** are slow (500-2000ms)
- **3%** are very slow (2000-5000ms)

### Error Rates:
- **85%** success (HTTP 200)
- **7%** client errors (HTTP 4xx)
- **6%** server errors (HTTP 500)
- **2%** service unavailable (HTTP 503)

### Services Included:
- api-gateway
- user-service
- order-service
- payment-service
- notification-service
- analytics-service

---

**Start testing with professional-grade observability data!** 🚀

**Next Steps:**
1. Load the APM dataset
2. Test table loading in PROMISE AI
3. Run custom SQL queries
4. Analyze latency patterns with ML
5. Generate insights and charts
