-- ================================================================
-- APPLICATION PERFORMANCE MONITORING (APM) DATASETS - MYSQL VERSION
-- Professional observability data for PROMISE AI testing
-- ================================================================

USE testdb;

-- ================================================================
-- 1. API REQUEST LOGS (10,000 rows) - Application Latency Data
-- Track API performance, latency, errors
-- ================================================================
DROP TABLE IF EXISTS api_request_logs;
CREATE TABLE api_request_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
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
    upstream_latency_ms INT,
    INDEX idx_timestamp (timestamp),
    INDEX idx_service (service_name),
    INDEX idx_status (http_status),
    INDEX idx_response_time (response_time_ms)
);

-- Create stored procedure to insert API request logs
DELIMITER $$
DROP PROCEDURE IF EXISTS insert_api_request_logs$$
CREATE PROCEDURE insert_api_request_logs()
BEGIN
    DECLARE i INT DEFAULT 1;
    
    -- This loop takes about 2-3 minutes for 10,000 rows
    WHILE i <= 10000 DO
        INSERT INTO api_request_logs (
            timestamp, request_id, service_name, endpoint, http_method, http_status,
            response_time_ms, request_size_bytes, response_size_bytes, user_id, client_ip,
            user_agent, region, datacenter, error_message, error_type, cache_hit,
            upstream_service, upstream_latency_ms
        )
        VALUES (
            DATE_ADD('2025-01-01 00:00:00', INTERVAL (i * 30) SECOND),
            CONCAT('req_', LPAD(i, 10, '0')),
            CASE (i % 6)
                WHEN 0 THEN 'api-gateway'
                WHEN 1 THEN 'user-service'
                WHEN 2 THEN 'order-service'
                WHEN 3 THEN 'payment-service'
                WHEN 4 THEN 'notification-service'
                ELSE 'analytics-service'
            END,
            CASE (i % 15)
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
            END,
            CASE (i % 4)
                WHEN 0 THEN 'GET'
                WHEN 1 THEN 'POST'
                WHEN 2 THEN 'PUT'
                ELSE 'DELETE'
            END,
            CASE
                WHEN i % 100 < 85 THEN 200  -- 85% success
                WHEN i % 100 < 92 THEN 400  -- 7% client errors
                WHEN i % 100 < 98 THEN 500  -- 6% server errors
                ELSE 503  -- 2% service unavailable
            END,
            CASE
                WHEN i % 100 < 70 THEN 50 + (i % 150)    -- 70% fast (50-200ms)
                WHEN i % 100 < 90 THEN 200 + (i % 300)   -- 20% medium (200-500ms)
                WHEN i % 100 < 97 THEN 500 + (i % 1500)  -- 7% slow (500-2000ms)
                ELSE 2000 + (i % 3000)  -- 3% very slow (2000-5000ms)
            END,
            256 + (i % 10000),
            512 + (i % 50000),
            CONCAT('user_', (1000 + i % 5000)),
            CONCAT('10.', (i % 255), '.', ((i * 7) % 255), '.', ((i * 13) % 255)),
            CASE (i % 3)
                WHEN 0 THEN 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)'
                WHEN 1 THEN 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0'
                ELSE 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/605.1'
            END,
            CASE (i % 5)
                WHEN 0 THEN 'us-east-1'
                WHEN 1 THEN 'us-west-2'
                WHEN 2 THEN 'eu-west-1'
                WHEN 3 THEN 'ap-southeast-1'
                ELSE 'ap-northeast-1'
            END,
            CASE (i % 3)
                WHEN 0 THEN 'dc-alpha'
                WHEN 1 THEN 'dc-beta'
                ELSE 'dc-gamma'
            END,
            CASE
                WHEN i % 100 >= 85 THEN
                    CASE (i % 5)
                        WHEN 0 THEN 'Database connection timeout'
                        WHEN 1 THEN 'Invalid authentication token'
                        WHEN 2 THEN 'Rate limit exceeded'
                        WHEN 3 THEN 'Service temporarily unavailable'
                        ELSE 'Internal server error'
                    END
                ELSE NULL
            END,
            CASE
                WHEN i % 100 >= 85 THEN
                    CASE (i % 5)
                        WHEN 0 THEN 'TimeoutError'
                        WHEN 1 THEN 'AuthenticationError'
                        WHEN 2 THEN 'RateLimitError'
                        WHEN 3 THEN 'ServiceUnavailable'
                        ELSE 'InternalError'
                    END
                ELSE NULL
            END,
            (i % 4) = 0,
            CASE (i % 5)
                WHEN 0 THEN 'database-primary'
                WHEN 1 THEN 'redis-cache'
                WHEN 2 THEN 'elasticsearch'
                WHEN 3 THEN 'message-queue'
                ELSE 'cdn'
            END,
            10 + (i % 200)
        );
        
        -- Progress indicator (every 1000 rows)
        IF i % 1000 = 0 THEN
            SELECT CONCAT('API Logs: Inserted ', i, ' / 10000 rows...') AS progress;
        END IF;
        
        SET i = i + 1;
    END WHILE;
END$$
DELIMITER ;

-- Execute the procedure (takes 2-3 minutes)
SELECT 'Starting API request logs insert - this will take 2-3 minutes...' AS status;
CALL insert_api_request_logs();
SELECT 'API request logs insert complete!' AS status;

-- Clean up
DROP PROCEDURE insert_api_request_logs;

-- ================================================================
-- 2. SYSTEM METRICS (5,000 rows) - Infrastructure Monitoring
-- CPU, Memory, Disk, Network metrics
-- ================================================================
DROP TABLE IF EXISTS system_metrics;
CREATE TABLE system_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
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
    load_average_15m DECIMAL(5, 2),
    INDEX idx_timestamp (timestamp),
    INDEX idx_hostname (host_name)
);

-- Create stored procedure to insert system metrics
DELIMITER $$
DROP PROCEDURE IF EXISTS insert_system_metrics$$
CREATE PROCEDURE insert_system_metrics()
BEGIN
    DECLARE i INT DEFAULT 1;
    
    WHILE i <= 5000 DO
        INSERT INTO system_metrics (
            timestamp, host_name, host_ip, environment, cpu_usage_percent,
            memory_usage_percent, memory_used_mb, memory_available_mb,
            disk_usage_percent, disk_read_mbps, disk_write_mbps,
            network_in_mbps, network_out_mbps, active_connections,
            process_count, load_average_1m, load_average_5m, load_average_15m
        )
        VALUES (
            DATE_ADD('2025-01-01 00:00:00', INTERVAL i MINUTE),
            CASE (i % 10)
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
            END,
            CONCAT('172.16.', ((i % 10) + 1), '.', ((i % 250) + 1)),
            CASE (i % 3)
                WHEN 0 THEN 'production'
                WHEN 1 THEN 'staging'
                ELSE 'development'
            END,
            CASE
                WHEN i % 100 < 60 THEN 20 + (i % 30)    -- 60% normal (20-50%)
                WHEN i % 100 < 85 THEN 50 + (i % 30)    -- 25% medium (50-80%)
                ELSE 80 + (i % 15)   -- 15% high (80-95%)
            END,
            CASE
                WHEN i % 100 < 70 THEN 30 + (i % 30)
                WHEN i % 100 < 90 THEN 60 + (i % 20)
                ELSE 80 + (i % 15)
            END,
            3000 + (i % 10000),
            2000 + (i % 6000),
            40 + (i % 50),
            5 + (i % 100),
            3 + (i % 80),
            10 + (i % 500),
            5 + (i % 300),
            50 + (i % 950),
            100 + (i % 400),
            0.5 + (i % 100) / 20,
            0.4 + (i % 80) / 20,
            0.3 + (i % 60) / 20
        );
        
        -- Progress indicator (every 500 rows)
        IF i % 500 = 0 THEN
            SELECT CONCAT('System Metrics: Inserted ', i, ' / 5000 rows...') AS progress;
        END IF;
        
        SET i = i + 1;
    END WHILE;
END$$
DELIMITER ;

-- Execute the procedure (takes 1-2 minutes)
SELECT 'Starting system metrics insert - this will take 1-2 minutes...' AS status;
CALL insert_system_metrics();
SELECT 'System metrics insert complete!' AS status;

-- Clean up
DROP PROCEDURE insert_system_metrics;

-- ================================================================
-- 3. ERROR TRACKING (2,000 rows) - Application Errors
-- ================================================================
DROP TABLE IF EXISTS error_logs;
CREATE TABLE error_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
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
    first_seen DATETIME,
    last_seen DATETIME,
    resolved BOOLEAN,
    assigned_to VARCHAR(100),
    INDEX idx_timestamp (timestamp),
    INDEX idx_severity (severity)
);

-- Create stored procedure to insert error logs
DELIMITER $$
DROP PROCEDURE IF EXISTS insert_error_logs$$
CREATE PROCEDURE insert_error_logs()
BEGIN
    DECLARE i INT DEFAULT 1;
    
    WHILE i <= 2000 DO
        INSERT INTO error_logs (
            timestamp, error_id, service_name, environment, severity, error_type,
            error_message, stack_trace, user_id, request_id, endpoint,
            occurrences, first_seen, last_seen, resolved, assigned_to
        )
        VALUES (
            DATE_ADD('2025-01-01 00:00:00', INTERVAL (i * 2) MINUTE),
            CONCAT('err_', LPAD(i, 8, '0')),
            CASE (i % 6)
                WHEN 0 THEN 'api-gateway'
                WHEN 1 THEN 'user-service'
                WHEN 2 THEN 'order-service'
                WHEN 3 THEN 'payment-service'
                WHEN 4 THEN 'notification-service'
                ELSE 'analytics-service'
            END,
            CASE (i % 3)
                WHEN 0 THEN 'production'
                WHEN 1 THEN 'staging'
                ELSE 'development'
            END,
            CASE (i % 10)
                WHEN 0 THEN 'critical'
                WHEN 1 THEN 'critical'
                WHEN 2 THEN 'error'
                WHEN 3 THEN 'error'
                WHEN 4 THEN 'error'
                ELSE 'warning'
            END,
            CASE (i % 8)
                WHEN 0 THEN 'NullPointerException'
                WHEN 1 THEN 'DatabaseConnectionError'
                WHEN 2 THEN 'TimeoutException'
                WHEN 3 THEN 'AuthenticationError'
                WHEN 4 THEN 'ValidationError'
                WHEN 5 THEN 'OutOfMemoryError'
                WHEN 6 THEN 'NetworkError'
                ELSE 'UnexpectedError'
            END,
            CASE (i % 8)
                WHEN 0 THEN 'Null pointer exception in user validation'
                WHEN 1 THEN 'Failed to connect to database: connection timeout'
                WHEN 2 THEN 'Request timeout after 5000ms'
                WHEN 3 THEN 'Invalid or expired authentication token'
                WHEN 4 THEN 'Validation failed: missing required field'
                WHEN 5 THEN 'Heap space exhausted during query execution'
                WHEN 6 THEN 'Network connection lost to upstream service'
                ELSE 'Unexpected error occurred during request processing'
            END,
            CONCAT('at com.example.service.Handler.process(Handler.java:', (100 + i % 400), ')'),
            CONCAT('user_', (1000 + i % 3000)),
            CONCAT('req_', LPAD(i, 10, '0')),
            CONCAT('/api/v1/', CASE (i % 5)
                WHEN 0 THEN 'users'
                WHEN 1 THEN 'orders'
                WHEN 2 THEN 'payments'
                WHEN 3 THEN 'products'
                ELSE 'checkout'
            END),
            1 + (i % 50),
            DATE_ADD('2025-01-01 00:00:00', INTERVAL (i * 2) MINUTE),
            DATE_ADD('2025-01-01 00:00:00', INTERVAL (i * 2 + 60) MINUTE),
            (i % 3) = 0,
            CASE (i % 5)
                WHEN 0 THEN 'john.doe@company.com'
                WHEN 1 THEN 'jane.smith@company.com'
                WHEN 2 THEN 'mike.johnson@company.com'
                ELSE NULL
            END
        );
        
        -- Progress indicator (every 500 rows)
        IF i % 500 = 0 THEN
            SELECT CONCAT('Error Logs: Inserted ', i, ' / 2000 rows...') AS progress;
        END IF;
        
        SET i = i + 1;
    END WHILE;
END$$
DELIMITER ;

-- Execute the procedure
SELECT 'Starting error logs insert - this will take about 1 minute...' AS status;
CALL insert_error_logs();
SELECT 'Error logs insert complete!' AS status;

-- Clean up
DROP PROCEDURE insert_error_logs;

-- ================================================================
-- 4. DISTRIBUTED TRACING (3,000 rows) - Microservices Traces
-- ================================================================
DROP TABLE IF EXISTS distributed_traces;
CREATE TABLE distributed_traces (
    id INT AUTO_INCREMENT PRIMARY KEY,
    trace_id VARCHAR(50),
    span_id VARCHAR(50) UNIQUE,
    parent_span_id VARCHAR(50),
    service_name VARCHAR(100),
    operation_name VARCHAR(200),
    start_time DATETIME,
    duration_ms INT,
    status VARCHAR(20),
    tags JSON,
    logs JSON,
    INDEX idx_trace_id (trace_id),
    INDEX idx_start_time (start_time)
);

-- Create stored procedure to insert distributed traces
DELIMITER $$
DROP PROCEDURE IF EXISTS insert_distributed_traces$$
CREATE PROCEDURE insert_distributed_traces()
BEGIN
    DECLARE i INT DEFAULT 1;
    DECLARE trace_num INT;
    DECLARE parent_span VARCHAR(50);
    
    WHILE i <= 3000 DO
        SET trace_num = FLOOR((i - 1) / 5) + 1;
        
        -- Calculate parent span ID (NULL for first span in trace)
        IF (i % 5) = 1 THEN
            SET parent_span = NULL;
        ELSE
            SET parent_span = CONCAT('span_', LPAD((i - (i % 5)), 8, '0'));
        END IF;
        
        INSERT INTO distributed_traces (
            trace_id, span_id, parent_span_id, service_name, operation_name,
            start_time, duration_ms, status, tags, logs
        )
        VALUES (
            CONCAT('trace_', trace_num),
            CONCAT('span_', LPAD(i, 8, '0')),
            parent_span,
            CASE ((i % 5))
                WHEN 1 THEN 'api-gateway'
                WHEN 2 THEN 'user-service'
                WHEN 3 THEN 'order-service'
                WHEN 4 THEN 'payment-service'
                ELSE 'notification-service'
            END,
            CASE ((i % 5))
                WHEN 1 THEN 'http.request'
                WHEN 2 THEN 'db.query'
                WHEN 3 THEN 'cache.get'
                WHEN 4 THEN 'http.call'
                ELSE 'message.send'
            END,
            DATE_ADD('2025-01-01 00:00:00', INTERVAL (trace_num * 60) SECOND),
            10 + (i % 500),
            CASE WHEN i % 20 = 0 THEN 'error' ELSE 'success' END,
            JSON_OBJECT(
                'http.method', 'POST',
                'http.url', '/api/v1/orders',
                'user.id', CONCAT('user_', (1000 + i % 1000))
            ),
            JSON_ARRAY(
                JSON_OBJECT('timestamp', NOW(), 'message', 'Processing request')
            )
        );
        
        -- Progress indicator (every 500 rows)
        IF i % 500 = 0 THEN
            SELECT CONCAT('Distributed Traces: Inserted ', i, ' / 3000 rows...') AS progress;
        END IF;
        
        SET i = i + 1;
    END WHILE;
END$$
DELIMITER ;

-- Execute the procedure
SELECT 'Starting distributed traces insert - this will take about 1 minute...' AS status;
CALL insert_distributed_traces();
SELECT 'Distributed traces insert complete!' AS status;

-- Clean up
DROP PROCEDURE insert_distributed_traces;

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

-- Query 1: API latency percentiles by endpoint
/*
SELECT 
    endpoint,
    COUNT(*) as request_count,
    AVG(response_time_ms) as avg_latency,
    MIN(response_time_ms) as min_latency,
    MAX(response_time_ms) as max_latency
FROM api_request_logs
WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 1 HOUR)
GROUP BY endpoint
ORDER BY avg_latency DESC
LIMIT 20;
*/

-- Query 2: Error rate by service
/*
SELECT 
    service_name,
    COUNT(*) as total_requests,
    SUM(CASE WHEN http_status >= 500 THEN 1 ELSE 0 END) as server_errors,
    ROUND(100.0 * SUM(CASE WHEN http_status >= 500 THEN 1 ELSE 0 END) / COUNT(*), 2) as error_rate_percent
FROM api_request_logs
GROUP BY service_name
ORDER BY error_rate_percent DESC;
*/

-- Query 3: System resource correlation
/*
SELECT 
    host_name,
    environment,
    AVG(cpu_usage_percent) as avg_cpu,
    AVG(memory_usage_percent) as avg_memory,
    MAX(cpu_usage_percent) as max_cpu,
    MAX(memory_usage_percent) as max_memory
FROM system_metrics
GROUP BY host_name, environment
ORDER BY avg_cpu DESC;
*/

-- Query 4: Critical errors timeline
/*
SELECT 
    DATE_FORMAT(timestamp, '%Y-%m-%d %H:00:00') as hour,
    COUNT(*) as error_count,
    COUNT(DISTINCT error_type) as unique_errors
FROM error_logs
WHERE severity = 'critical'
GROUP BY hour
ORDER BY hour;
*/

-- Query 5: Service latency correlation with errors (JOIN)
/*
SELECT 
    a.service_name,
    COUNT(a.id) as total_requests,
    AVG(a.response_time_ms) as avg_latency,
    COUNT(e.id) as error_count,
    ROUND(100.0 * COUNT(e.id) / COUNT(a.id), 2) as error_rate
FROM api_request_logs a
LEFT JOIN error_logs e ON a.request_id = e.request_id
GROUP BY a.service_name
ORDER BY error_rate DESC;
*/

-- Query 6: Infrastructure alerts (high resource usage)
/*
SELECT 
    host_name,
    timestamp,
    cpu_usage_percent,
    memory_usage_percent,
    load_average_1m
FROM system_metrics
WHERE cpu_usage_percent > 80 OR memory_usage_percent > 80
ORDER BY timestamp DESC
LIMIT 50;
*/
