# Cookly Normalization Notes

Cookly separates independent facts into separate relations and uses junction tables for many-to-many relationships.

- `users`, `recipes`, `categories`, `cuisines`, `diet_types`, and `sources` store facts about one entity type.
- `recipe_ingredients` resolves the many-to-many relationship between recipes and reusable ingredients.
- `instruction_steps` stores one ordered instruction per recipe and step number.
- `ingredient_allergies` resolves the many-to-many relationship between ingredients and allergies.
- `collections` stores a user's named collection; `collection_recipes` resolves the many-to-many relationship between collections and recipes.
- `saved_recipes`, `comments`, and `recipe_likes` store user interactions with recipes.

Primary keys identify each row, while foreign keys enforce referential integrity. Unique constraints prevent duplicate emails, recipe titles per user, ingredient names, allergy names, and collection names per user. Cascading deletes remove dependent interaction and junction rows while preserving reusable ingredient and allergy records.

The legacy `recipes.ingredients` and `recipes.instructions` text fields remain temporarily for backward compatibility with the existing forms. New recipe writes also populate the normalized tables. The normalized tables are the target design for future recipe-detail queries.
