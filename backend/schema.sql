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

CREATE TABLE IF NOT EXISTS recipes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    catergory_id INT NOT NULL,
    cuisine_id INT NOT NULL,
    diet_type_id INT NOT NULL,
    original_recipe_id INT NULL, --empty for normal recipes, filled when the recipe is a variation so it links back to orig
    title VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    difficulty ENUM('Easy', 'Medium', 'Hard') NOT NULL, --set levels it accepts
    cooking_time_minutes INT NOT NULL,
    serving_size INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, title),
    INDEX (title),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (catergory_id) REFERENCES categories(id),
    FOREIGN KEY (cuisine_id) REFERENCES cuisines(id),
    FOREIGN KEY (diet_type_id) REFERENCES diet_types(id),
    FOREIGN KEY (original_recipe_id) REFERENCES recipes(id) ON DELETE SET NULL
);