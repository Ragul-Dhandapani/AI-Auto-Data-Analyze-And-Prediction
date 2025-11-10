-- ================================================================
-- POSTGRESQL - MEDIUM DATASET (1,000 rows)
-- Good for testing performance
-- ================================================================

-- ================================================================
-- MEDIUM DATASET: sales_medium (1,000 rows)
-- ================================================================
DROP TABLE IF EXISTS sales_medium CASCADE;
CREATE TABLE sales_medium (
    transaction_id SERIAL PRIMARY KEY,
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

-- Insert 1,000 rows
INSERT INTO sales_medium (product_name, category, quantity, price, sale_date, region, customer_age, customer_gender, payment_method, satisfaction_score)
SELECT
    'Product ' || (generate_series % 50) AS product_name,
    CASE (generate_series % 5)
        WHEN 0 THEN 'Electronics'
        WHEN 1 THEN 'Clothing'
        WHEN 2 THEN 'Food'
        WHEN 3 THEN 'Books'
        ELSE 'Furniture'
    END AS category,
    (generate_series % 10) + 1 AS quantity,
    10 + (generate_series % 100) * 5 AS price,
    DATE '2023-01-01' + (generate_series % 365 || ' days')::INTERVAL AS sale_date,
    CASE (generate_series % 4)
        WHEN 0 THEN 'North'
        WHEN 1 THEN 'South'
        WHEN 2 THEN 'East'
        ELSE 'West'
    END AS region,
    18 + (generate_series % 60) AS customer_age,
    CASE (generate_series % 2)
        WHEN 0 THEN 'Male'
        ELSE 'Female'
    END AS customer_gender,
    CASE (generate_series % 3)
        WHEN 0 THEN 'Credit Card'
        WHEN 1 THEN 'Cash'
        ELSE 'Debit Card'
    END AS payment_method,
    (generate_series % 5) + 1 AS satisfaction_score
FROM generate_series(1, 1000);

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
--     DATE_TRUNC('month', sale_date) as month,
--     COUNT(*) as orders,
--     SUM(price * quantity) as revenue
-- FROM sales_medium
-- WHERE sale_date >= '2023-06-01'
-- GROUP BY DATE_TRUNC('month', sale_date)
-- ORDER BY month;

-- Example 3: Regional performance
-- SELECT region, AVG(satisfaction_score) as avg_satisfaction, COUNT(*) as total_sales
-- FROM sales_medium
-- GROUP BY region
-- ORDER BY avg_satisfaction DESC;
