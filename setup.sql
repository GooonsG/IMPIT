CREATE DATABASE IF NOT EXISTS inventory_database;
USE inventory_database;

CREATE TABLE IF NOT EXISTS Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS Products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    quantity_available INT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS Orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    product_id INT,
    quantity INT,
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (product_id) REFERENCES Products(product_id)
);

INSERT INTO Users (username, password_hash) VALUES
('admin', 'admin123');

INSERT INTO Products (name, description, quantity_available) VALUES
('Sample Product 1', 'Description for product 1', 10),
('Sample Product 2', 'Description for product 2', 20);
