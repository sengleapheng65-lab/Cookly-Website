USE cookly_db;

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
