USE cookly_db;

-- Safe to rerun. Adds amount columns when recipe_ingredients already exists.
SET @has_quantity = (
    SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'recipe_ingredients' AND COLUMN_NAME = 'quantity'
);
SET @sql = IF(@has_quantity = 0,
    'ALTER TABLE recipe_ingredients ADD COLUMN quantity DECIMAL(10, 2) NULL',
    'SELECT 1');
PREPARE add_quantity FROM @sql;
EXECUTE add_quantity;
DEALLOCATE PREPARE add_quantity;

SET @has_unit = (
    SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'recipe_ingredients' AND COLUMN_NAME = 'unit'
);
SET @sql = IF(@has_unit = 0,
    'ALTER TABLE recipe_ingredients ADD COLUMN unit VARCHAR(40) NULL',
    'SELECT 1');
PREPARE add_unit FROM @sql;
EXECUTE add_unit;
DEALLOCATE PREPARE add_unit;

SET @has_notes = (
    SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'recipe_ingredients' AND COLUMN_NAME = 'notes'
);
SET @sql = IF(@has_notes = 0,
    'ALTER TABLE recipe_ingredients ADD COLUMN notes VARCHAR(255) NULL',
    'SELECT 1');
PREPARE add_notes FROM @sql;
EXECUTE add_notes;
DEALLOCATE PREPARE add_notes;

SET @has_line_number = (
    SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'recipe_ingredients' AND COLUMN_NAME = 'line_number'
);
SET @sql = IF(@has_line_number = 0,
    'ALTER TABLE recipe_ingredients ADD COLUMN line_number INT NOT NULL DEFAULT 1',
    'SELECT 1');
PREPARE add_line_number FROM @sql;
EXECUTE add_line_number;
DEALLOCATE PREPARE add_line_number;
