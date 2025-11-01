-- ================================================================
-- MYSQL - MEDIUM DATASET (1,000 rows)
-- Good for testing performance
-- ================================================================

USE testdb;

-- ================================================================
-- MEDIUM DATASET: sales_medium (1,000 rows)
-- ================================================================
DROP TABLE IF EXISTS sales_medium;
CREATE TABLE sales_medium (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(100),
    category VARCHAR(50),
    quantity INT,
    price DECIMAL(10, 2),
    sale_date DATE,
    region VARCHAR(50),
    customer_age INT,
    customer_gender VARCHAR(10),
    payment_method VARCHAR(20),
    satisfaction_score INT
);

-- Create stored procedure to insert data
DELIMITER $$
DROP PROCEDURE IF EXISTS insert_sales_medium$$
CREATE PROCEDURE insert_sales_medium()
BEGIN
    DECLARE i INT DEFAULT 1;
    WHILE i <= 1000 DO
        INSERT INTO sales_medium (product_name, category, quantity, price, sale_date, region, customer_age, customer_gender, payment_method, satisfaction_score)
        VALUES (
            CONCAT('Product ', (i % 50)),
            CASE (i % 5)
                WHEN 0 THEN 'Electronics'
                WHEN 1 THEN 'Clothing'
                WHEN 2 THEN 'Food'
                WHEN 3 THEN 'Books'
                ELSE 'Furniture'
            END,
            (i % 10) + 1,
            10 + (i % 100) * 5,
            DATE_ADD('2023-01-01', INTERVAL (i % 365) DAY),
            CASE (i % 4)
                WHEN 0 THEN 'North'
                WHEN 1 THEN 'South'
                WHEN 2 THEN 'East'
                ELSE 'West'
            END,
            18 + (i % 60),
            CASE (i % 2)
                WHEN 0 THEN 'Male'
                ELSE 'Female'
            END,
            CASE (i % 3)
                WHEN 0 THEN 'Credit Card'
                WHEN 1 THEN 'Cash'
                ELSE 'Debit Card'
            END,
            (i % 5) + 1
        );
        SET i = i + 1;
    END WHILE;
END$$
DELIMITER ;

-- Execute the procedure
CALL insert_sales_medium();

-- Clean up
DROP PROCEDURE insert_sales_medium;

-- ================================================================
-- VERIFICATION
-- ================================================================
SELECT 'sales_medium' AS table_name, COUNT(*) AS row_count FROM sales_medium;

-- ================================================================
-- EXAMPLE QUERIES TO TEST
-- ================================================================

-- Example 1: Sales by category
-- SELECT category, COUNT(*) as sales_count, SUM(price * quantity) as total_revenue
-- FROM sales_medium
-- GROUP BY category
-- ORDER BY total_revenue DESC;

-- Example 2: Monthly sales trend
-- SELECT 
--     DATE_FORMAT(sale_date, '%Y-%m') as month,
--     COUNT(*) as orders,
--     SUM(price * quantity) as revenue
-- FROM sales_medium
-- WHERE sale_date >= '2023-06-01'
-- GROUP BY DATE_FORMAT(sale_date, '%Y-%m')
-- ORDER BY month;

-- Example 3: Regional performance
-- SELECT region, AVG(satisfaction_score) as avg_satisfaction, COUNT(*) as total_sales
-- FROM sales_medium
-- GROUP BY region
-- ORDER BY avg_satisfaction DESC;
