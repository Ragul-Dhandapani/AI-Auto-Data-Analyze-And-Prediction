-- ================================================================
-- MYSQL - LARGE DATASET (10,000 rows + 5,000 reference rows)
-- Good for testing large data handling and GridFS
-- WARNING: This script takes 2-5 minutes to complete
-- ================================================================

USE testdb;

-- ================================================================
-- LARGE DATASET: transactions_large (10,000 rows)
-- ================================================================
DROP TABLE IF EXISTS transactions_large;
CREATE TABLE transactions_large (
    id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_date DATETIME,
    customer_id INT,
    product_id INT,
    product_category VARCHAR(50),
    quantity INT,
    unit_price DECIMAL(10, 2),
    total_amount DECIMAL(12, 2),
    discount_percent DECIMAL(5, 2),
    final_amount DECIMAL(12, 2),
    payment_status VARCHAR(20),
    shipping_cost DECIMAL(8, 2),
    delivery_days INT,
    customer_rating INT,
    return_flag BOOLEAN
);

-- Create stored procedure to insert data
DELIMITER $$
DROP PROCEDURE IF EXISTS insert_transactions_large$$
CREATE PROCEDURE insert_transactions_large()
BEGIN
    DECLARE i INT DEFAULT 1;
    DECLARE unit_p DECIMAL(10, 2);
    DECLARE qty INT;
    DECLARE disc DECIMAL(5, 2);
    
    -- This loop takes about 2-3 minutes
    WHILE i <= 10000 DO
        SET qty = (i % 10) + 1;
        SET unit_p = 5 + (i % 100) * 2.5;
        SET disc = (i % 4) * 5;
        
        INSERT INTO transactions_large (
            transaction_date, customer_id, product_id, product_category,
            quantity, unit_price, total_amount, discount_percent, final_amount,
            payment_status, shipping_cost, delivery_days, customer_rating, return_flag
        )
        VALUES (
            DATE_ADD('2023-01-01 00:00:00', INTERVAL i HOUR),
            1000 + (i % 5000),
            100 + (i % 200),
            CASE (i % 8)
                WHEN 0 THEN 'Electronics'
                WHEN 1 THEN 'Clothing'
                WHEN 2 THEN 'Food & Beverage'
                WHEN 3 THEN 'Books'
                WHEN 4 THEN 'Furniture'
                WHEN 5 THEN 'Sports'
                WHEN 6 THEN 'Toys'
                ELSE 'Home & Garden'
            END,
            qty,
            unit_p,
            qty * unit_p,
            disc,
            qty * unit_p * (1 - disc / 100),
            CASE (i % 3)
                WHEN 0 THEN 'Completed'
                WHEN 1 THEN 'Pending'
                ELSE 'Failed'
            END,
            5 + (i % 20),
            2 + (i % 10),
            (i % 5) + 1,
            (i % 20) = 0
        );
        
        -- Progress indicator (every 1000 rows)
        IF i % 1000 = 0 THEN
            SELECT CONCAT('Inserted ', i, ' / 10000 rows...') AS progress;
        END IF;
        
        SET i = i + 1;
    END WHILE;
END$$
DELIMITER ;

-- Execute the procedure (takes 2-3 minutes)
SELECT 'Starting large dataset insert - this will take 2-3 minutes...' AS status;
CALL insert_transactions_large();
SELECT 'Large dataset insert complete!' AS status;

-- Clean up
DROP PROCEDURE insert_transactions_large;

-- ================================================================
-- CUSTOMER_INFO TABLE (5,000 rows - for JOIN with transactions)
-- ================================================================
DROP TABLE IF EXISTS customer_info;
CREATE TABLE customer_info (
    customer_id INT PRIMARY KEY,
    full_name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    address VARCHAR(200),
    membership_level VARCHAR(20),
    total_purchases INT,
    lifetime_value DECIMAL(12, 2)
);

-- Create stored procedure to insert customer data
DELIMITER $$
DROP PROCEDURE IF EXISTS insert_customer_info$$
CREATE PROCEDURE insert_customer_info()
BEGIN
    DECLARE i INT DEFAULT 1;
    
    -- This loop takes about 1-2 minutes
    WHILE i <= 5000 DO
        INSERT INTO customer_info (customer_id, full_name, email, phone, address, membership_level, total_purchases, lifetime_value)
        VALUES (
            1000 + i,
            CONCAT('Customer ', i),
            CONCAT('customer', i, '@email.com'),
            CONCAT('555-', LPAD(i % 10000, 4, '0')),
            CONCAT(i, ' Main Street, City, State'),
            CASE (i % 3)
                WHEN 0 THEN 'Gold'
                WHEN 1 THEN 'Silver'
                ELSE 'Bronze'
            END,
            (i % 50) + 1,
            (i % 50 + 1) * 250.50
        );
        
        -- Progress indicator (every 1000 rows)
        IF i % 1000 = 0 THEN
            SELECT CONCAT('Inserted ', i, ' / 5000 customer records...') AS progress;
        END IF;
        
        SET i = i + 1;
    END WHILE;
END$$
DELIMITER ;

-- Execute the procedure (takes 1-2 minutes)
SELECT 'Starting customer info insert - this will take 1-2 minutes...' AS status;
CALL insert_customer_info();
SELECT 'Customer info insert complete!' AS status;

-- Clean up
DROP PROCEDURE insert_customer_info;

-- ================================================================
-- VERIFICATION
-- ================================================================
SELECT 'transactions_large' AS table_name, COUNT(*) AS row_count FROM transactions_large
UNION ALL
SELECT 'customer_info', COUNT(*) FROM customer_info;

-- ================================================================
-- EXAMPLE QUERIES TO TEST
-- ================================================================

-- Example 1: Sales by category and payment status
-- SELECT 
--     product_category,
--     payment_status,
--     COUNT(*) as transaction_count,
--     SUM(final_amount) as total_revenue
-- FROM transactions_large
-- GROUP BY product_category, payment_status
-- ORDER BY total_revenue DESC
-- LIMIT 20;

-- Example 2: Customer segmentation with transactions (JOIN)
-- SELECT 
--     c.membership_level,
--     COUNT(DISTINCT t.customer_id) as unique_customers,
--     COUNT(t.id) as total_transactions,
--     AVG(t.final_amount) as avg_transaction_value,
--     SUM(t.final_amount) as total_revenue
-- FROM transactions_large t
-- JOIN customer_info c ON t.customer_id = c.customer_id
-- WHERE t.payment_status = 'Completed'
-- GROUP BY c.membership_level
-- ORDER BY total_revenue DESC;

-- Example 3: Monthly trend analysis
-- SELECT 
--     DATE_FORMAT(transaction_date, '%Y-%m') as month,
--     product_category,
--     COUNT(*) as order_count,
--     SUM(final_amount) as monthly_revenue,
--     AVG(customer_rating) as avg_rating
-- FROM transactions_large
-- WHERE transaction_date >= '2023-06-01'
-- GROUP BY DATE_FORMAT(transaction_date, '%Y-%m'), product_category
-- ORDER BY month, monthly_revenue DESC
-- LIMIT 50;

-- Example 4: High-value customers (complex JOIN)
-- SELECT 
--     c.customer_id,
--     c.full_name,
--     c.membership_level,
--     COUNT(t.id) as transaction_count,
--     SUM(t.final_amount) as total_spent,
--     AVG(t.customer_rating) as avg_rating
-- FROM customer_info c
-- JOIN transactions_large t ON c.customer_id = t.customer_id
-- WHERE t.payment_status = 'Completed'
-- GROUP BY c.customer_id, c.full_name, c.membership_level
-- HAVING SUM(t.final_amount) > 10000
-- ORDER BY total_spent DESC
-- LIMIT 100;
