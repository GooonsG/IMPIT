# IMPIT
Group-PIT


kung dili mo gana ang sql e manual ug code
CREATE DATABASE  inventory_database;
USE inventory_database;

CREATE TABLE  Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'user') DEFAULT 'user'
);

CREATE TABLE  Products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    quantity_available INT DEFAULT 0
);

CREATE TABLE  Orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    product_id INT,
    quantity INT,
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (product_id) REFERENCES Products(product_id)
);

INSERT INTO Users (username, password_hash, role) VALUES
('admin', 'admin', 'admin'),
('user', 'user', 'user');


