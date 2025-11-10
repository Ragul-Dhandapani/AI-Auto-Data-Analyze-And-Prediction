-- ================================================================
-- POSTGRESQL - SMALL DATASET (100 rows + reference tables)
-- Perfect for quick testing
-- ================================================================

-- ================================================================
-- SMALL DATASET: employees_small (100 rows)
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
