-- ================================================================
-- TEST DATASETS FOR PROMISE AI - MYSQL VERSION
-- Run this script in MySQL (testdb database)
-- ================================================================

USE testdb;

-- ================================================================
-- SMALL DATASET: employees_small (100 rows)
-- ================================================================
DROP TABLE IF EXISTS employees_small;
CREATE TABLE employees_small (
    id INT AUTO_INCREMENT PRIMARY KEY,
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

-- Create stored procedure to insert data
DELIMITER $$
DROP PROCEDURE IF EXISTS insert_employees_small$$
CREATE PROCEDURE insert_employees_small()
BEGIN
    DECLARE i INT DEFAULT 1;
    WHILE i <= 100 DO
        INSERT INTO employees_small (name, age, department, salary, hire_date, years_experience, performance_score, city, country)
        VALUES (
            CONCAT('Employee ', i),
            20 + (i % 40),
            CASE (i % 5)
                WHEN 0 THEN 'Engineering'
                WHEN 1 THEN 'Marketing'
                WHEN 2 THEN 'Sales'
                WHEN 3 THEN 'HR'
                ELSE 'Finance'
            END,
            50000 + (i * 1000),
            DATE_ADD('2010-01-01', INTERVAL (i * 30) DAY),
            (i % 15) + 1,
            3.0 + (i % 20) * 0.1,
            CASE (i % 10)
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
            END,
            'USA'
        );
        SET i = i + 1;
    END WHILE;
END$$
DELIMITER ;

CALL insert_employees_small();

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

CALL insert_sales_medium();

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

DELIMITER $$
DROP PROCEDURE IF EXISTS insert_transactions_large$$
CREATE PROCEDURE insert_transactions_large()
BEGIN
    DECLARE i INT DEFAULT 1;
    DECLARE unit_p DECIMAL(10, 2);
    DECLARE qty INT;
    DECLARE disc DECIMAL(5, 2);
    
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
        SET i = i + 1;
    END WHILE;
END$$
DELIMITER ;

CALL insert_transactions_large();

-- ================================================================
-- DEPARTMENTS TABLE (for JOIN examples)
-- ================================================================
DROP TABLE IF EXISTS departments;
CREATE TABLE departments (
    dept_id INT AUTO_INCREMENT PRIMARY KEY,
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

DELIMITER $$
DROP PROCEDURE IF EXISTS insert_customer_info$$
CREATE PROCEDURE insert_customer_info()
BEGIN
    DECLARE i INT DEFAULT 1;
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
        SET i = i + 1;
    END WHILE;
END$$
DELIMITER ;

CALL insert_customer_info();

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
/*
SELECT e.name, e.salary, d.dept_name, d.budget
FROM employees_small e
JOIN departments d ON e.department = d.dept_name
WHERE e.salary > 70000;
*/

-- Example 2: Complex aggregation
/*
SELECT 
    department,
    COUNT(*) as employee_count,
    AVG(salary) as avg_salary,
    MAX(salary) as max_salary,
    MIN(years_experience) as min_experience
FROM employees_small
GROUP BY department
HAVING AVG(salary) > 60000;
*/

-- Example 3: Multi-table JOIN with aggregation
/*
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
LIMIT 50;
*/

-- Example 4: Date-based analysis
/*
SELECT 
    DATE_FORMAT(transaction_date, '%Y-%m') as month,
    product_category,
    SUM(final_amount) as monthly_revenue,
    COUNT(*) as order_count
FROM transactions_large
WHERE transaction_date >= '2023-06-01'
GROUP BY DATE_FORMAT(transaction_date, '%Y-%m'), product_category
ORDER BY month, monthly_revenue DESC;
*/
