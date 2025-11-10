-- PostgreSQL / MySQL Test Data Script
-- Run this after connecting to your test database

-- Create employees table
CREATE TABLE IF NOT EXISTS employees (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    age INT,
    department VARCHAR(50),
    salary DECIMAL(10, 2),
    hire_date DATE,
    years_experience INT,
    performance_score DECIMAL(3, 2)
);

-- Insert sample data with good correlation patterns
INSERT INTO employees VALUES
(1, 'John Doe', 35, 'Engineering', 95000.00, '2020-01-15', 12, 4.5),
(2, 'Jane Smith', 28, 'Marketing', 72000.00, '2021-03-22', 5, 4.2),
(3, 'Bob Johnson', 42, 'Engineering', 110000.00, '2018-07-10', 18, 4.8),
(4, 'Alice Brown', 31, 'Sales', 85000.00, '2019-11-05', 8, 4.3),
(5, 'Charlie Wilson', 38, 'Engineering', 98000.00, '2020-09-18', 14, 4.6),
(6, 'Diana Miller', 29, 'Marketing', 68000.00, '2022-01-20', 6, 4.0),
(7, 'Eve Davis', 45, 'Sales', 105000.00, '2017-04-12', 20, 4.7),
(8, 'Frank Garcia', 33, 'Engineering', 88000.00, '2021-06-30', 10, 4.4),
(9, 'Grace Lee', 27, 'Marketing', 65000.00, '2022-08-15', 4, 3.9),
(10, 'Henry Martinez', 40, 'Sales', 92000.00, '2019-02-28', 16, 4.5),
(11, 'Isabel Rodriguez', 36, 'Engineering', 102000.00, '2019-05-12', 13, 4.7),
(12, 'Jack Thompson', 30, 'Marketing', 75000.00, '2020-11-03', 7, 4.1),
(13, 'Karen White', 44, 'Sales', 108000.00, '2017-08-20', 19, 4.8),
(14, 'Leo Anderson', 32, 'Engineering', 91000.00, '2021-02-14', 9, 4.4),
(15, 'Maria Garcia', 26, 'Marketing', 62000.00, '2023-03-10', 3, 3.8)
ON DUPLICATE KEY UPDATE name=name; -- MySQL compatibility

-- Create sales data table
CREATE TABLE IF NOT EXISTS sales_data (
    transaction_id INT PRIMARY KEY,
    product VARCHAR(100),
    quantity INT,
    price DECIMAL(10, 2),
    sale_date DATE,
    region VARCHAR(50),
    customer_age INT,
    satisfaction_score DECIMAL(3, 2)
);

-- Insert sales data
INSERT INTO sales_data VALUES
(1, 'Laptop', 5, 1200.00, '2024-01-10', 'North', 35, 4.5),
(2, 'Mouse', 25, 25.00, '2024-01-11', 'South', 28, 4.2),
(3, 'Keyboard', 15, 75.00, '2024-01-12', 'East', 42, 4.8),
(4, 'Monitor', 8, 350.00, '2024-01-13', 'West', 31, 4.3),
(5, 'Laptop', 3, 1200.00, '2024-01-14', 'North', 38, 4.6),
(6, 'Mouse', 30, 25.00, '2024-01-15', 'South', 29, 4.0),
(7, 'Keyboard', 12, 75.00, '2024-01-16', 'East', 45, 4.7),
(8, 'Monitor', 6, 350.00, '2024-01-17', 'West', 33, 4.4),
(9, 'Laptop', 7, 1200.00, '2024-01-18', 'North', 27, 3.9),
(10, 'Mouse', 20, 25.00, '2024-01-19', 'South', 40, 4.5),
(11, 'Keyboard', 18, 75.00, '2024-01-20', 'East', 36, 4.7),
(12, 'Monitor', 10, 350.00, '2024-01-21', 'West', 30, 4.1),
(13, 'Laptop', 4, 1200.00, '2024-01-22', 'North', 44, 4.8),
(14, 'Mouse', 22, 25.00, '2024-01-23', 'South', 32, 4.4),
(15, 'Keyboard', 14, 75.00, '2024-01-24', 'East', 26, 3.8)
ON DUPLICATE KEY UPDATE product=product; -- MySQL compatibility

-- Create customer analytics table
CREATE TABLE IF NOT EXISTS customer_analytics (
    customer_id INT PRIMARY KEY,
    age INT,
    annual_income DECIMAL(10, 2),
    spending_score INT,
    membership_years INT,
    total_purchases INT,
    avg_purchase_value DECIMAL(10, 2),
    region VARCHAR(50)
);

-- Insert customer data with correlation patterns
INSERT INTO customer_analytics VALUES
(1, 35, 85000.00, 75, 5, 120, 350.50, 'North'),
(2, 28, 62000.00, 60, 2, 65, 280.25, 'South'),
(3, 42, 110000.00, 85, 8, 200, 425.75, 'East'),
(4, 31, 78000.00, 70, 4, 95, 315.00, 'West'),
(5, 38, 95000.00, 80, 6, 150, 380.00, 'North'),
(6, 29, 68000.00, 65, 3, 75, 290.50, 'South'),
(7, 45, 120000.00, 90, 10, 250, 450.00, 'East'),
(8, 33, 82000.00, 72, 5, 110, 330.25, 'West'),
(9, 27, 58000.00, 55, 1, 45, 260.00, 'North'),
(10, 40, 98000.00, 78, 7, 175, 395.50, 'South'),
(11, 36, 88000.00, 76, 5, 130, 360.00, 'East'),
(12, 30, 72000.00, 68, 3, 85, 305.75, 'West'),
(13, 44, 115000.00, 88, 9, 220, 440.00, 'North'),
(14, 32, 80000.00, 71, 4, 100, 320.50, 'South'),
(15, 26, 55000.00, 52, 1, 40, 250.00, 'East')
ON DUPLICATE KEY UPDATE age=age; -- MySQL compatibility

-- Verification queries
SELECT 'Tables created successfully!' AS status;
SELECT COUNT(*) AS employee_count FROM employees;
SELECT COUNT(*) AS sales_count FROM sales_data;
SELECT COUNT(*) AS customer_count FROM customer_analytics;
