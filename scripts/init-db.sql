-- Purpose: Database initialization script for the demo PostgreSQL instance.
-- Creates the core schema (users, products, orders) and seeds it with sample data.
-- Automatically executed by the demo-postgres container on first startup.

-- Users Table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    age INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products Table
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    price DECIMAL(10, 2),
    category VARCHAR(50),
    stock_quantity INT
);

-- Orders Table
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    total_price DECIMAL(10, 2),
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample Data
INSERT INTO users (name, email, age) VALUES
('Alice Johnson', 'alice@example.com', 28),
('Bob Smith', 'bob@example.com', 34),
('Charlie Brown', 'charlie@example.com', 22),
('Diana Prince', 'diana@example.com', 30);

INSERT INTO products (name, price, category, stock_quantity) VALUES
('Laptop', 1200.00, 'Electronics', 15),
('Smartphone', 800.00, 'Electronics', 30),
('Coffee Maker', 50.00, 'Home Appliances', 50),
('Desk Chair', 150.00, 'Furniture', 10),
('Backpack', 40.00, 'Accessories', 25);

INSERT INTO orders (user_id, total_price, status) VALUES
(1, 1250.00, 'shipped'),
(2, 800.00, 'processing'),
(3, 50.00, 'delivered'),
(1, 40.00, 'pending');
