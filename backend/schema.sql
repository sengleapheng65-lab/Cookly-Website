CREATE DATABASE IF NOT EXISTS cookly_db;
USE cookly_db;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('registered', 'moderator') NOT NULL DEFAULT 'registered',
    is_suspended BOOLEAN NOT NULL DEFAULT FALSE,
    profile_image_filename VARCHAR(255) NULL,
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

CREATE TABLE IF NOT EXISTS source (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    author VARCHAR(50) NULL,
    url VARCHAR(255) NULL
);

CREATE TABLE IF NOT EXISTS recipes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    catergory_id INT NOT NULL,
    cuisine_id INT NOT NULL,
    diet_type_id INT NOT NULL,
    source_id INT NULL,
    original_recipe_id INT NULL, -- empty for a normal recipe, filled when this recipe is a variation
    title VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    difficulty ENUM('Easy', 'Medium', 'Hard') NOT NULL,
    prep_time_minutes INT NOT NULL,
    cooking_time_minutes INT NOT NULL,
    serving_size INT NOT NULL,
    ingredients TEXT NOT NULL,
    instructions TEXT NOT NULL,
    image_filename VARCHAR(255) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, title),
    INDEX (title),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (catergory_id) REFERENCES categories(id),
    FOREIGN KEY (cuisine_id) REFERENCES cuisines(id),
    FOREIGN KEY (diet_type_id) REFERENCES diet_types(id),
    FOREIGN KEY (source_id) REFERENCES source(id),
    FOREIGN KEY (original_recipe_id) REFERENCES recipes(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS ingredients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR(255) NULL
);

CREATE TABLE IF NOT EXISTS recipe_ingredients ( -- says which recipe uses that ingredient and how much
    recipe_id INT NOT NULL,
    ingredient_id INT NOT NULL,
    amount VARCHAR(100) NULL,
    PRIMARY KEY (recipe_id, ingredient_id),
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE, -- delete links when recipe is deleted
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(id)
);

CREATE TABLE IF NOT EXISTS instructions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    recipe_id INT NOT NULL,
    step_number INT NOT NULL,
    instruction_text TEXT NOT NULL,
    UNIQUE (recipe_id, step_number),
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS allergies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS ingredient_allergies (
    ingredient_id INT NOT NULL,
    allergy_id INT NOT NULL,
    PRIMARY KEY (ingredient_id, allergy_id),
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(id),
    FOREIGN KEY (allergy_id) REFERENCES allergies(id)
);

INSERT IGNORE INTO allergies (name) VALUES
('Peanuts'),
('Dairy'),
('Shellfish'),
('Eggs'),
('Soy'),
('Wheat'),
('Tree nuts'),
('Fish');

CREATE TABLE IF NOT EXISTS collections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, name),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS collection_recipes (
    collection_id INT NOT NULL,
    recipe_id INT NOT NULL,
    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (collection_id, recipe_id),
    FOREIGN KEY (collection_id) REFERENCES collections(id) ON DELETE CASCADE,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS saved_recipes (
    user_id INT NOT NULL,
    recipe_id INT NOT NULL,
    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, recipe_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    recipe_id INT NOT NULL,
    body VARCHAR(1000) NOT NULL,
    is_hidden BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX (recipe_id, created_at),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS recipe_likes (
    user_id INT NOT NULL,
    recipe_id INT NOT NULL,
    liked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, recipe_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
);
