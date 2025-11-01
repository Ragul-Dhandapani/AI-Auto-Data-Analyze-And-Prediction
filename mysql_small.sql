-- ================================================================
-- MYSQL - SMALL DATASET (100 rows + reference tables)
-- Perfect for quick testing
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

-- Execute the procedure
CALL insert_employees_small();

-- Clean up
DROP PROCEDURE insert_employees_small;

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
-- VERIFICATION
-- ================================================================
SELECT 'employees_small' AS table_name, COUNT(*) AS row_count FROM employees_small
UNION ALL
SELECT 'departments', COUNT(*) FROM departments;

-- ================================================================
-- EXAMPLE QUERIES TO TEST
-- ================================================================

-- Example 1: Simple query
-- SELECT * FROM employees_small WHERE salary > 70000 ORDER BY salary DESC LIMIT 10;

-- Example 2: JOIN query
-- SELECT e.name, e.salary, d.dept_name, d.budget
-- FROM employees_small e
-- JOIN departments d ON e.department = d.dept_name
-- WHERE e.salary > 70000
-- ORDER BY e.salary DESC;

-- Example 3: Aggregation
-- SELECT department, COUNT(*) as emp_count, AVG(salary) as avg_salary
-- FROM employees_small
-- GROUP BY department
-- ORDER BY avg_salary DESC;
