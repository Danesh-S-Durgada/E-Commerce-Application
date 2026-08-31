CREATE DATABASE IF NOT EXISTS ecommerce;
USE ecommerce;

CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    description VARCHAR(500),
    price DECIMAL(10,2) NOT NULL,
    image_url VARCHAR(500),
    category VARCHAR(100),
    stock INT DEFAULT 0
);

INSERT INTO products (name, description, price, image_url, category, stock)
SELECT 'Laptop', 'High performance laptop', 65000,
'https://via.placeholder.com/300x200?text=Laptop', 'Electronics', 10
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name='Laptop');

INSERT INTO products (name, description, price, image_url, category, stock)
SELECT 'Smartphone', 'Latest Android smartphone', 30000,
'https://via.placeholder.com/300x200?text=Smartphone', 'Electronics', 20
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name='Smartphone');

INSERT INTO products (name, description, price, image_url, category, stock)
SELECT 'Headphones', 'Wireless noise cancelling headphones', 5000,
'https://via.placeholder.com/300x200?text=Headphones', 'Accessories', 30
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name='Headphones');
