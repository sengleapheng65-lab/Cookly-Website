CREATE DATABASE IF NOT EXISTS cookly_db;
USE cookly_db;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS cuisines (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS diet_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

INSERT IGNORE INTO categories (name) VALUES
('Breakfast'),
('Lunch'),
('Dinner'),
('Dessert'),
('Soup'),
('Snack'),
('Salad'),
('Drink');

INSERT IGNORE INTO cuisines (name) VALUES
("Italian"),
('Mexican'),
('American'),
('Chinese'),
('Korean'),
('Thai'),
('Indian'),
('Middle Eastern'),
('Caribbean');

INSERT IGNORE INTO diet_types (name) VALUES
('None'),
('Vegetarian'),
('Vegan'),
('Gluten Free'),
('Dairy Free'),
('Nut Free'),
('Keto'),
('Pescatarian'),
('Halal'),
('Low Carb');