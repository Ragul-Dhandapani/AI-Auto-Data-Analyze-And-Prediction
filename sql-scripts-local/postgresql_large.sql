-- ================================================================
-- POSTGRESQL - LARGE DATASET (10,000 rows + 5,000 reference rows)
-- Good for testing large data handling and GridFS
-- ================================================================

-- ================================================================
-- LARGE DATASET: transactions_large (10,000 rows)
-- ================================================================
DROP TABLE IF EXISTS transactions_large CASCADE;
CREATE TABLE transactions_large (
    id SERIAL PRIMARY KEY,
    transaction_date TIMESTAMP,
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

-- Insert 10,000 rows (this takes about 5-10 seconds)
INSERT INTO transactions_large (
    transaction_date, customer_id, product_id, product_category,
    quantity, unit_price, total_amount, discount_percent, final_amount,
    payment_status, shipping_cost, delivery_days, customer_rating, return_flag
)
SELECT
    TIMESTAMP '2023-01-01 00:00:00' + (generate_series * INTERVAL '1 hour') AS transaction_date,
    1000 + (generate_series % 5000) AS customer_id,
    100 + (generate_series % 200) AS product_id,
    CASE (generate_series % 8)
        WHEN 0 THEN 'Electronics'
        WHEN 1 THEN 'Clothing'
        WHEN 2 THEN 'Food & Beverage'
        WHEN 3 THEN 'Books'
        WHEN 4 THEN 'Furniture'
        WHEN 5 THEN 'Sports'
        WHEN 6 THEN 'Toys'
        ELSE 'Home & Garden'
    END AS product_category,
    (generate_series % 10) + 1 AS quantity,
    5 + (generate_series % 100) * 2.5 AS unit_price,
    ((generate_series % 10) + 1) * (5 + (generate_series % 100) * 2.5) AS total_amount,
    (generate_series % 4) * 5 AS discount_percent,
    ((generate_series % 10) + 1) * (5 + (generate_series % 100) * 2.5) * (1 - (generate_series % 4) * 0.05) AS final_amount,
    CASE (generate_series % 3)
        WHEN 0 THEN 'Completed'
        WHEN 1 THEN 'Pending'
        ELSE 'Failed'
    END AS payment_status,
    5 + (generate_series % 20) AS shipping_cost,
    2 + (generate_series % 10) AS delivery_days,
    (generate_series % 5) + 1 AS customer_rating,
    (generate_series % 20) = 0 AS return_flag
FROM generate_series(1, 10000);

-- ================================================================
-- CUSTOMER_INFO TABLE (5,000 rows - for JOIN with transactions)
-- ================================================================
DROP TABLE IF EXISTS customer_info CASCADE;
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

-- Insert 5,000 customers (takes about 3-5 seconds)
INSERT INTO customer_info (customer_id, full_name, email, phone, address, membership_level, total_purchases, lifetime_value)
SELECT
    1000 + generate_series AS customer_id,
    'Customer ' || generate_series AS full_name,
    'customer' || generate_series || '@email.com' AS email,
    '555-' || LPAD((generate_series % 10000)::TEXT, 4, '0') AS phone,
    generate_series || ' Main Street, City, State' AS address,
    CASE (generate_series % 3)
        WHEN 0 THEN 'Gold'
        WHEN 1 THEN 'Silver'
        ELSE 'Bronze'
    END AS membership_level,
    (generate_series % 50) + 1 AS total_purchases,
    (generate_series % 50 + 1) * 250.50 AS lifetime_value
FROM generate_series(1, 5000);

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
--     DATE_TRUNC('month', transaction_date) as month,
--     product_category,
--     COUNT(*) as order_count,
--     SUM(final_amount) as monthly_revenue,
--     AVG(customer_rating) as avg_rating
-- FROM transactions_large
-- WHERE transaction_date >= '2023-06-01'
-- GROUP BY DATE_TRUNC('month', transaction_date), product_category
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
