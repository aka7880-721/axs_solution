DROP TABLE IF EXISTS sales;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    city VARCHAR(100),
    age INT
);

CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(100),
    joining_date DATE
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(100),
    price NUMERIC(10,2)
);

CREATE TABLE sales (
    id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(id),
    employee_id INT REFERENCES employees(id),
    product_id INT REFERENCES products(id),
    quantity INT NOT NULL,
    sale_amount NUMERIC(10,2) NOT NULL,
    sale_date DATE NOT NULL
);