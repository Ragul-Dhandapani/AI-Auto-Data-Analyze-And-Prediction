-- ================================================================
-- APPLICATION PERFORMANCE MONITORING (APM) DATASETS
-- Professional observability data for PROMISE AI testing
-- ================================================================

-- ================================================================
-- 1. API REQUEST LOGS (10,000 rows) - Application Latency Data
-- Track API performance, latency, errors
-- ================================================================
DROP TABLE IF EXISTS api_request_logs CASCADE;
CREATE TABLE api_request_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    request_id VARCHAR(50) UNIQUE,
    service_name VARCHAR(100),
    endpoint VARCHAR(200),
    http_method VARCHAR(10),
    http_status INT,
    response_time_ms INT,
    request_size_bytes INT,
    response_size_bytes INT,
    user_id VARCHAR(50),
    client_ip VARCHAR(45),
    user_agent TEXT,
    region VARCHAR(50),
    datacenter VARCHAR(50),
    error_message TEXT,
    error_type VARCHAR(100),
    cache_hit BOOLEAN,
    upstream_service VARCHAR(100),
    upstream_latency_ms INT
);

-- Generate realistic API request data
INSERT INTO api_request_logs (
    timestamp, request_id, service_name, endpoint, http_method, http_status,
    response_time_ms, request_size_bytes, response_size_bytes, user_id, client_ip,
    user_agent, region, datacenter, error_message, error_type, cache_hit,
    upstream_service, upstream_latency_ms
)
SELECT
    TIMESTAMP '2025-01-01 00:00:00' + (generate_series * INTERVAL '30 seconds') AS timestamp,
    'req_' || LPAD(generate_series::TEXT, 10, '0') AS request_id,
    CASE (generate_series % 6)
        WHEN 0 THEN 'api-gateway'
        WHEN 1 THEN 'user-service'
        WHEN 2 THEN 'order-service'
        WHEN 3 THEN 'payment-service'
        WHEN 4 THEN 'notification-service'
        ELSE 'analytics-service'
    END AS service_name,
    CASE (generate_series % 15)
        WHEN 0 THEN '/api/v1/users'
        WHEN 1 THEN '/api/v1/orders'
        WHEN 2 THEN '/api/v1/products'
        WHEN 3 THEN '/api/v1/checkout'
        WHEN 4 THEN '/api/v1/payments'
        WHEN 5 THEN '/api/v1/cart'
        WHEN 6 THEN '/api/v1/search'
        WHEN 7 THEN '/api/v1/recommendations'
        WHEN 8 THEN '/api/v1/notifications'
        WHEN 9 THEN '/api/v1/analytics'
        WHEN 10 THEN '/api/v1/auth/login'
        WHEN 11 THEN '/api/v1/auth/refresh'
        WHEN 12 THEN '/api/v1/profile'
        WHEN 13 THEN '/api/v1/reports'
        ELSE '/api/v1/health'
    END AS endpoint,
    CASE (generate_series % 4)
        WHEN 0 THEN 'GET'
        WHEN 1 THEN 'POST'
        WHEN 2 THEN 'PUT'
        ELSE 'DELETE'
    END AS http_method,
    CASE
        WHEN generate_series % 100 < 85 THEN 200  -- 85% success
        WHEN generate_series % 100 < 92 THEN 400  -- 7% client errors
        WHEN generate_series % 100 < 98 THEN 500  -- 6% server errors
        ELSE 503  -- 2% service unavailable
    END AS http_status,
    CASE
        WHEN generate_series % 100 < 70 THEN 50 + (generate_series % 150)    -- 70% fast (50-200ms)
        WHEN generate_series % 100 < 90 THEN 200 + (generate_series % 300)   -- 20% medium (200-500ms)
        WHEN generate_series % 100 < 97 THEN 500 + (generate_series % 1500)  -- 7% slow (500-2000ms)
        ELSE 2000 + (generate_series % 3000)  -- 3% very slow (2000-5000ms)
    END AS response_time_ms,
    256 + (generate_series % 10000) AS request_size_bytes,
    512 + (generate_series % 50000) AS response_size_bytes,
    'user_' || (1000 + generate_series % 5000) AS user_id,
    '10.' || (generate_series % 255) || '.' || ((generate_series * 7) % 255) || '.' || ((generate_series * 13) % 255) AS client_ip,
    CASE (generate_series % 3)
        WHEN 0 THEN 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)'
        WHEN 1 THEN 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0'
        ELSE 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/605.1'
    END AS user_agent,
    CASE (generate_series % 5)
        WHEN 0 THEN 'us-east-1'
        WHEN 1 THEN 'us-west-2'
        WHEN 2 THEN 'eu-west-1'
        WHEN 3 THEN 'ap-southeast-1'
        ELSE 'ap-northeast-1'
    END AS region,
    CASE (generate_series % 3)
        WHEN 0 THEN 'dc-alpha'
        WHEN 1 THEN 'dc-beta'
        ELSE 'dc-gamma'
    END AS datacenter,
    CASE
        WHEN generate_series % 100 >= 85 THEN
            CASE (generate_series % 5)
                WHEN 0 THEN 'Database connection timeout'
                WHEN 1 THEN 'Invalid authentication token'
                WHEN 2 THEN 'Rate limit exceeded'
                WHEN 3 THEN 'Service temporarily unavailable'
                ELSE 'Internal server error'
            END
        ELSE NULL
    END AS error_message,
    CASE
        WHEN generate_series % 100 >= 85 THEN
            CASE (generate_series % 5)
                WHEN 0 THEN 'TimeoutError'
                WHEN 1 THEN 'AuthenticationError'
                WHEN 2 THEN 'RateLimitError'
                WHEN 3 THEN 'ServiceUnavailable'
                ELSE 'InternalError'
            END
        ELSE NULL
    END AS error_type,
    (generate_series % 4) = 0 AS cache_hit,
    CASE (generate_series % 5)
        WHEN 0 THEN 'database-primary'
        WHEN 1 THEN 'redis-cache'
        WHEN 2 THEN 'elasticsearch'
        WHEN 3 THEN 'message-queue'
        ELSE 'cdn'
    END AS upstream_service,
    10 + (generate_series % 200) AS upstream_latency_ms
FROM generate_series(1, 10000);

CREATE INDEX idx_api_timestamp ON api_request_logs(timestamp);
CREATE INDEX idx_api_service ON api_request_logs(service_name);
CREATE INDEX idx_api_status ON api_request_logs(http_status);
CREATE INDEX idx_api_response_time ON api_request_logs(response_time_ms);

-- ================================================================
-- 2. SYSTEM METRICS (5,000 rows) - Infrastructure Monitoring
-- CPU, Memory, Disk, Network metrics
-- ================================================================
DROP TABLE IF EXISTS system_metrics CASCADE;
CREATE TABLE system_metrics (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    host_name VARCHAR(100),
    host_ip VARCHAR(45),
    environment VARCHAR(50),
    cpu_usage_percent DECIMAL(5, 2),
    memory_usage_percent DECIMAL(5, 2),
    memory_used_mb INT,
    memory_available_mb INT,
    disk_usage_percent DECIMAL(5, 2),
    disk_read_mbps DECIMAL(8, 2),
    disk_write_mbps DECIMAL(8, 2),
    network_in_mbps DECIMAL(8, 2),
    network_out_mbps DECIMAL(8, 2),
    active_connections INT,
    process_count INT,
    load_average_1m DECIMAL(5, 2),
    load_average_5m DECIMAL(5, 2),
    load_average_15m DECIMAL(5, 2)
);

-- Generate realistic system metrics
INSERT INTO system_metrics (
    timestamp, host_name, host_ip, environment, cpu_usage_percent,
    memory_usage_percent, memory_used_mb, memory_available_mb,
    disk_usage_percent, disk_read_mbps, disk_write_mbps,
    network_in_mbps, network_out_mbps, active_connections,
    process_count, load_average_1m, load_average_5m, load_average_15m
)
SELECT
    TIMESTAMP '2025-01-01 00:00:00' + (generate_series * INTERVAL '1 minute') AS timestamp,
    CASE (generate_series % 10)
        WHEN 0 THEN 'web-server-01'
        WHEN 1 THEN 'web-server-02'
        WHEN 2 THEN 'app-server-01'
        WHEN 3 THEN 'app-server-02'
        WHEN 4 THEN 'db-server-01'
        WHEN 5 THEN 'db-server-02'
        WHEN 6 THEN 'cache-server-01'
        WHEN 7 THEN 'queue-server-01'
        WHEN 8 THEN 'worker-server-01'
        ELSE 'lb-server-01'
    END AS host_name,
    '172.16.' || ((generate_series % 10) + 1) || '.' || ((generate_series % 250) + 1) AS host_ip,
    CASE (generate_series % 3)
        WHEN 0 THEN 'production'
        WHEN 1 THEN 'staging'
        ELSE 'development'
    END AS environment,
    CASE
        WHEN generate_series % 100 < 60 THEN 20 + (generate_series % 30)::DECIMAL    -- 60% normal (20-50%)
        WHEN generate_series % 100 < 85 THEN 50 + (generate_series % 30)::DECIMAL    -- 25% medium (50-80%)
        ELSE 80 + (generate_series % 15)::DECIMAL   -- 15% high (80-95%)
    END AS cpu_usage_percent,
    CASE
        WHEN generate_series % 100 < 70 THEN 30 + (generate_series % 30)::DECIMAL
        WHEN generate_series % 100 < 90 THEN 60 + (generate_series % 20)::DECIMAL
        ELSE 80 + (generate_series % 15)::DECIMAL
    END AS memory_usage_percent,
    3000 + (generate_series % 10000) AS memory_used_mb,
    2000 + (generate_series % 6000) AS memory_available_mb,
    40 + (generate_series % 50)::DECIMAL AS disk_usage_percent,
    5 + (generate_series % 100)::DECIMAL AS disk_read_mbps,
    3 + (generate_series % 80)::DECIMAL AS disk_write_mbps,
    10 + (generate_series % 500)::DECIMAL AS network_in_mbps,
    5 + (generate_series % 300)::DECIMAL AS network_out_mbps,
    50 + (generate_series % 950) AS active_connections,
    100 + (generate_series % 400) AS process_count,
    0.5 + (generate_series % 100)::DECIMAL / 20 AS load_average_1m,
    0.4 + (generate_series % 80)::DECIMAL / 20 AS load_average_5m,
    0.3 + (generate_series % 60)::DECIMAL / 20 AS load_average_15m
FROM generate_series(1, 5000);

CREATE INDEX idx_sys_timestamp ON system_metrics(timestamp);
CREATE INDEX idx_sys_hostname ON system_metrics(host_name);

-- ================================================================
-- 3. ERROR TRACKING (2,000 rows) - Application Errors
-- ================================================================
DROP TABLE IF EXISTS error_logs CASCADE;
CREATE TABLE error_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    error_id VARCHAR(50) UNIQUE,
    service_name VARCHAR(100),
    environment VARCHAR(50),
    severity VARCHAR(20),
    error_type VARCHAR(100),
    error_message TEXT,
    stack_trace TEXT,
    user_id VARCHAR(50),
    request_id VARCHAR(50),
    endpoint VARCHAR(200),
    occurrences INT,
    first_seen TIMESTAMP,
    last_seen TIMESTAMP,
    resolved BOOLEAN,
    assigned_to VARCHAR(100)
);

-- Generate error logs
INSERT INTO error_logs (
    timestamp, error_id, service_name, environment, severity, error_type,
    error_message, stack_trace, user_id, request_id, endpoint,
    occurrences, first_seen, last_seen, resolved, assigned_to
)
SELECT
    TIMESTAMP '2025-01-01 00:00:00' + (generate_series * INTERVAL '2 minutes') AS timestamp,
    'err_' || LPAD(generate_series::TEXT, 8, '0') AS error_id,
    CASE (generate_series % 6)
        WHEN 0 THEN 'api-gateway'
        WHEN 1 THEN 'user-service'
        WHEN 2 THEN 'order-service'
        WHEN 3 THEN 'payment-service'
        WHEN 4 THEN 'notification-service'
        ELSE 'analytics-service'
    END AS service_name,
    CASE (generate_series % 3)
        WHEN 0 THEN 'production'
        WHEN 1 THEN 'staging'
        ELSE 'development'
    END AS environment,
    CASE (generate_series % 10)
        WHEN 0 THEN 'critical'
        WHEN 1 THEN 'critical'
        WHEN 2 THEN 'error'
        WHEN 3 THEN 'error'
        WHEN 4 THEN 'error'
        ELSE 'warning'
    END AS severity,
    CASE (generate_series % 8)
        WHEN 0 THEN 'NullPointerException'
        WHEN 1 THEN 'DatabaseConnectionError'
        WHEN 2 THEN 'TimeoutException'
        WHEN 3 THEN 'AuthenticationError'
        WHEN 4 THEN 'ValidationError'
        WHEN 5 THEN 'OutOfMemoryError'
        WHEN 6 THEN 'NetworkError'
        ELSE 'UnexpectedError'
    END AS error_type,
    CASE (generate_series % 8)
        WHEN 0 THEN 'Null pointer exception in user validation'
        WHEN 1 THEN 'Failed to connect to database: connection timeout'
        WHEN 2 THEN 'Request timeout after 5000ms'
        WHEN 3 THEN 'Invalid or expired authentication token'
        WHEN 4 THEN 'Validation failed: missing required field'
        WHEN 5 THEN 'Heap space exhausted during query execution'
        WHEN 6 THEN 'Network connection lost to upstream service'
        ELSE 'Unexpected error occurred during request processing'
    END AS error_message,
    'at com.example.service.Handler.process(Handler.java:' || (100 + generate_series % 400) || ')' AS stack_trace,
    'user_' || (1000 + generate_series % 3000) AS user_id,
    'req_' || LPAD(generate_series::TEXT, 10, '0') AS request_id,
    '/api/v1/' || CASE (generate_series % 5)
        WHEN 0 THEN 'users'
        WHEN 1 THEN 'orders'
        WHEN 2 THEN 'payments'
        WHEN 3 THEN 'products'
        ELSE 'checkout'
    END AS endpoint,
    1 + (generate_series % 50) AS occurrences,
    TIMESTAMP '2025-01-01 00:00:00' + (generate_series * INTERVAL '2 minutes') AS first_seen,
    TIMESTAMP '2025-01-01 00:00:00' + (generate_series * INTERVAL '2 minutes') + INTERVAL '1 hour' AS last_seen,
    (generate_series % 3) = 0 AS resolved,
    CASE (generate_series % 5)
        WHEN 0 THEN 'john.doe@company.com'
        WHEN 1 THEN 'jane.smith@company.com'
        WHEN 2 THEN 'mike.johnson@company.com'
        ELSE NULL
    END AS assigned_to
FROM generate_series(1, 2000);

CREATE INDEX idx_err_timestamp ON error_logs(timestamp);
CREATE INDEX idx_err_severity ON error_logs(severity);

-- ================================================================
-- 4. DISTRIBUTED TRACING (3,000 rows) - Microservices Traces
-- ================================================================
DROP TABLE IF EXISTS distributed_traces CASCADE;
CREATE TABLE distributed_traces (
    id SERIAL PRIMARY KEY,
    trace_id VARCHAR(50),
    span_id VARCHAR(50) UNIQUE,
    parent_span_id VARCHAR(50),
    service_name VARCHAR(100),
    operation_name VARCHAR(200),
    start_time TIMESTAMP,
    duration_ms INT,
    status VARCHAR(20),
    tags JSONB,
    logs JSONB
);

-- Generate trace data
INSERT INTO distributed_traces (
    trace_id, span_id, parent_span_id, service_name, operation_name,
    start_time, duration_ms, status, tags, logs
)
SELECT
    'trace_' || ((generate_series - 1) / 5 + 1) AS trace_id,
    'span_' || LPAD(generate_series::TEXT, 8, '0') AS span_id,
    CASE WHEN (generate_series % 5) = 1 THEN NULL
         ELSE 'span_' || LPAD((generate_series - (generate_series % 5))::TEXT, 8, '0')
    END AS parent_span_id,
    CASE ((generate_series % 5))
        WHEN 1 THEN 'api-gateway'
        WHEN 2 THEN 'user-service'
        WHEN 3 THEN 'order-service'
        WHEN 4 THEN 'payment-service'
        ELSE 'notification-service'
    END AS service_name,
    CASE ((generate_series % 5))
        WHEN 1 THEN 'http.request'
        WHEN 2 THEN 'db.query'
        WHEN 3 THEN 'cache.get'
        WHEN 4 THEN 'http.call'
        ELSE 'message.send'
    END AS operation_name,
    TIMESTAMP '2025-01-01 00:00:00' + (((generate_series - 1) / 5) * INTERVAL '1 minute') AS start_time,
    10 + (generate_series % 500) AS duration_ms,
    CASE WHEN generate_series % 20 = 0 THEN 'error' ELSE 'success' END AS status,
    jsonb_build_object(
        'http.method', 'POST',
        'http.url', '/api/v1/orders',
        'user.id', 'user_' || (1000 + generate_series % 1000)
    ) AS tags,
    jsonb_build_array(
        jsonb_build_object('timestamp', NOW(), 'message', 'Processing request')
    ) AS logs
FROM generate_series(1, 3000);

CREATE INDEX idx_trace_id ON distributed_traces(trace_id);
CREATE INDEX idx_trace_time ON distributed_traces(start_time);

-- ================================================================
-- VERIFICATION
-- ================================================================
SELECT 'api_request_logs' AS table_name, COUNT(*) AS row_count FROM api_request_logs
UNION ALL SELECT 'system_metrics', COUNT(*) FROM system_metrics
UNION ALL SELECT 'error_logs', COUNT(*) FROM error_logs
UNION ALL SELECT 'distributed_traces', COUNT(*) FROM distributed_traces;

-- ================================================================
-- EXAMPLE QUERIES FOR APM ANALYSIS
-- ================================================================

-- Query 1: API latency analysis by endpoint
-- SELECT 
--     endpoint,
--     COUNT(*) as request_count,
--     AVG(response_time_ms) as avg_latency,
--     PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY response_time_ms) as p50_latency,
--     PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time_ms) as p95_latency,
--     PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY response_time_ms) as p99_latency
-- FROM api_request_logs
-- WHERE timestamp >= NOW() - INTERVAL '1 hour'
-- GROUP BY endpoint
-- ORDER BY avg_latency DESC;

-- Query 2: Error rate by service
-- SELECT 
--     service_name,
--     COUNT(*) as total_requests,
--     SUM(CASE WHEN http_status >= 500 THEN 1 ELSE 0 END) as server_errors,
--     ROUND(100.0 * SUM(CASE WHEN http_status >= 500 THEN 1 ELSE 0 END) / COUNT(*), 2) as error_rate_percent
-- FROM api_request_logs
-- GROUP BY service_name
-- ORDER BY error_rate_percent DESC;

-- Query 3: System resource correlation
-- SELECT 
--     host_name,
--     AVG(cpu_usage_percent) as avg_cpu,
--     AVG(memory_usage_percent) as avg_memory,
--     MAX(cpu_usage_percent) as max_cpu,
--     MAX(memory_usage_percent) as max_memory
-- FROM system_metrics
-- GROUP BY host_name
-- ORDER BY avg_cpu DESC;

-- Query 4: Critical errors timeline
-- SELECT 
--     DATE_TRUNC('hour', timestamp) as hour,
--     COUNT(*) as error_count,
--     COUNT(DISTINCT error_type) as unique_errors
-- FROM error_logs
-- WHERE severity = 'critical'
-- GROUP BY hour
-- ORDER BY hour;
