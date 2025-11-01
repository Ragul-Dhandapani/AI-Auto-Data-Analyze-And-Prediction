-- ================================================================
-- TEST DATASETS FOR PROMISE AI DATABASE TESTING
-- Run this script in both PostgreSQL and MySQL
-- ================================================================

-- ================================================================
-- SMALL DATASET: employees_small (100 rows)
-- Good for quick testing
-- ================================================================
DROP TABLE IF EXISTS employees_small CASCADE;
CREATE TABLE employees_small (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    age INT,
    department VARCHAR(50),
    salary DECIMAL(10, 2),
    hire_date DATE,
    years_experience INT,
    performance_score DECIMAL(3, 2),
    city VARCHAR(50),
    country VARCHAR(50)
);

-- Insert 100 rows
INSERT INTO employees_small (name, age, department, salary, hire_date, years_experience, performance_score, city, country)
SELECT
    'Employee ' || generate_series AS name,
    20 + (generate_series % 40) AS age,
    CASE (generate_series % 5)
        WHEN 0 THEN 'Engineering'
        WHEN 1 THEN 'Marketing'
        WHEN 2 THEN 'Sales'
        WHEN 3 THEN 'HR'
        ELSE 'Finance'
    END AS department,
    50000 + (generate_series * 1000) AS salary,
    DATE '2010-01-01' + (generate_series * 30 || ' days')::INTERVAL AS hire_date,
    (generate_series % 15) + 1 AS years_experience,
    3.0 + (generate_series % 20) * 0.1 AS performance_score,
    CASE (generate_series % 10)
        WHEN 0 THEN 'New York'
        WHEN 1 THEN 'San Francisco'
        WHEN 2 THEN 'Chicago'
        WHEN 3 THEN 'Boston'
        WHEN 4 THEN 'Seattle'
        WHEN 5 THEN 'Austin'
        WHEN 6 THEN 'Denver'
        WHEN 7 THEN 'Portland'
        WHEN 8 THEN 'Miami'
        ELSE 'Atlanta'
    END AS city,
    'USA' AS country
FROM generate_series(1, 100);

-- ================================================================
-- MEDIUM DATASET: sales_medium (1,000 rows)
-- Good for testing performance
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
-- LARGE DATASET: transactions_large (10,000 rows)
-- Good for testing large data handling and GridFS
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

-- Insert 10,000 rows
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
-- DEPARTMENTS TABLE (for JOIN examples)
-- ================================================================
DROP TABLE IF EXISTS departments CASCADE;
CREATE TABLE departments (
    dept_id SERIAL PRIMARY KEY,
    dept_name VARCHAR(50),
    dept_head VARCHAR(100),
    budget DECIMAL(15, 2),
    location VARCHAR(50)
);

INSERT INTO departments (dept_name, dept_head, budget, location) VALUES
('Engineering', 'John Smith', 5000000, 'San Francisco'),
('Marketing', 'Sarah Johnson', 2000000, 'New York'),
('Sales', 'Mike Brown', 3000000, 'Chicago'),
('HR', 'Emily Davis', 1000000, 'Boston'),
('Finance', 'Robert Wilson', 1500000, 'Seattle');

-- ================================================================
-- CUSTOMER_INFO TABLE (for JOIN with sales)
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

-- Insert 5000 customers
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
-- VERIFICATION QUERIES
-- ================================================================
SELECT 'employees_small' AS table_name, COUNT(*) AS row_count FROM employees_small
UNION ALL
SELECT 'sales_medium', COUNT(*) FROM sales_medium
UNION ALL
SELECT 'transactions_large', COUNT(*) FROM transactions_large
UNION ALL
SELECT 'departments', COUNT(*) FROM departments
UNION ALL
SELECT 'customer_info', COUNT(*) FROM customer_info;

-- ================================================================
-- EXAMPLE QUERIES FOR TESTING CUSTOM SQL FEATURE
-- ================================================================

-- Example 1: Simple JOIN
-- SELECT e.name, e.salary, d.dept_name, d.budget
-- FROM employees_small e
-- JOIN departments d ON e.department = d.dept_name
-- WHERE e.salary > 70000;

-- Example 2: Complex aggregation
-- SELECT 
--     department,
--     COUNT(*) as employee_count,
--     AVG(salary) as avg_salary,
--     MAX(salary) as max_salary,
--     MIN(years_experience) as min_experience
-- FROM employees_small
-- GROUP BY department
-- HAVING AVG(salary) > 60000;

-- Example 3: Multi-table JOIN with aggregation
-- SELECT 
--     t.product_category,
--     c.membership_level,
--     COUNT(*) as transaction_count,
--     SUM(t.final_amount) as total_revenue,
--     AVG(t.customer_rating) as avg_rating
-- FROM transactions_large t
-- JOIN customer_info c ON t.customer_id = c.customer_id
-- WHERE t.payment_status = 'Completed'
-- GROUP BY t.product_category, c.membership_level
-- ORDER BY total_revenue DESC;

-- Example 4: Date-based analysis
-- SELECT 
--     DATE_TRUNC('month', transaction_date) as month,
--     product_category,
--     SUM(final_amount) as monthly_revenue,
--     COUNT(*) as order_count
-- FROM transactions_large
-- WHERE transaction_date >= '2023-06-01'
-- GROUP BY DATE_TRUNC('month', transaction_date), product_category
-- ORDER BY month, monthly_revenue DESC;
