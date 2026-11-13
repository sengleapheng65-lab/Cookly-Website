USE cookly_db;

CREATE TABLE IF NOT EXISTS sources (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    url VARCHAR(500) NULL,
    UNIQUE (name, url)
);

CREATE TABLE IF NOT EXISTS ingredients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS allergies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(80) NOT NULL UNIQUE
);

INSERT IGNORE INTO allergies (name) VALUES
('Peanuts'), ('Tree Nuts'), ('Dairy'), ('Eggs'), ('Gluten'),
('Shellfish'), ('Soy'), ('Sesame');

-- Safe to rerun against an existing Cookly database.
SET @has_role = (
    SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'users' AND COLUMN_NAME = 'role'
);
SET @sql = IF(@has_role = 0,
    "ALTER TABLE users ADD COLUMN role ENUM('registered', 'moderator') NOT NULL DEFAULT 'registered'",
    'SELECT 1');
PREPARE add_role FROM @sql;
EXECUTE add_role;
DEALLOCATE PREPARE add_role;

SET @has_suspended = (
    SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'users' AND COLUMN_NAME = 'is_suspended'
);
SET @sql = IF(@has_suspended = 0,
    'ALTER TABLE users ADD COLUMN is_suspended BOOLEAN NOT NULL DEFAULT FALSE',
    'SELECT 1');
PREPARE add_suspended FROM @sql;
EXECUTE add_suspended;
DEALLOCATE PREPARE add_suspended;

SET @has_source_id = (
    SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'recipes' AND COLUMN_NAME = 'source_id'
);
SET @sql = IF(@has_source_id = 0,
    'ALTER TABLE recipes ADD COLUMN source_id INT NULL',
    'SELECT 1');
PREPARE add_source_id FROM @sql;
EXECUTE add_source_id;
DEALLOCATE PREPARE add_source_id;

SET @has_source_fk = (
    SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS
    WHERE CONSTRAINT_SCHEMA = DATABASE() AND TABLE_NAME = 'recipes' AND CONSTRAINT_NAME = 'fk_recipes_source'
);
SET @sql = IF(@has_source_fk = 0,
    'ALTER TABLE recipes ADD CONSTRAINT fk_recipes_source FOREIGN KEY (source_id) REFERENCES sources(id) ON DELETE SET NULL',
    'SELECT 1');
PREPARE add_source_fk FROM @sql;
EXECUTE add_source_fk;
DEALLOCATE PREPARE add_source_fk;

CREATE TABLE IF NOT EXISTS recipe_ingredients (
    recipe_id INT NOT NULL,
    ingredient_id INT NOT NULL,
    quantity DECIMAL(10, 2) NULL,
    unit VARCHAR(40) NULL,
    notes VARCHAR(255) NULL,
    PRIMARY KEY (recipe_id, ingredient_id),
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS instruction_steps (
    recipe_id INT NOT NULL,
    step_number INT NOT NULL,
    instruction TEXT NOT NULL,
    PRIMARY KEY (recipe_id, step_number),
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ingredient_allergies (
    ingredient_id INT NOT NULL,
    allergy_id INT NOT NULL,
    PRIMARY KEY (ingredient_id, allergy_id),
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE,
    FOREIGN KEY (allergy_id) REFERENCES allergies(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS recipe_allergies (
    recipe_id INT NOT NULL,
    allergy_id INT NOT NULL,
    PRIMARY KEY (recipe_id, allergy_id),
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
    FOREIGN KEY (allergy_id) REFERENCES allergies(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS collections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, name),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS collection_recipes (
    collection_id INT NOT NULL,
    recipe_id INT NOT NULL,
    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (collection_id, recipe_id),
    FOREIGN KEY (collection_id) REFERENCES collections(id) ON DELETE CASCADE,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    recipe_id INT NOT NULL,
    body VARCHAR(1000) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX (recipe_id, created_at),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
);

SET @has_hidden_comments = (
    SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'comments' AND COLUMN_NAME = 'is_hidden'
);
SET @sql = IF(@has_hidden_comments = 0,
    'ALTER TABLE comments ADD COLUMN is_hidden BOOLEAN NOT NULL DEFAULT FALSE',
    'SELECT 1');
PREPARE add_hidden_comments FROM @sql;
EXECUTE add_hidden_comments;
DEALLOCATE PREPARE add_hidden_comments;

CREATE TABLE IF NOT EXISTS recipe_likes (
    user_id INT NOT NULL,
    recipe_id INT NOT NULL,
    liked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, recipe_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
);
