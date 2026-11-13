# Cookly Entity-Relationship Diagram

```mermaid
erDiagram
    USERS ||--o{ RECIPES : creates
    USERS ||--o{ COMMENTS : writes
    USERS ||--o{ SAVED_RECIPES : saves
    USERS ||--o{ RECIPE_LIKES : likes
    USERS ||--o{ COLLECTIONS : owns
    RECIPES }o--|| CATEGORIES : classified_as
    RECIPES }o--|| CUISINES : uses
    RECIPES }o--|| DIET_TYPES : supports
    RECIPES }o--o| SOURCES : attributed_to
    RECIPES ||--o{ COMMENTS : receives
    RECIPES ||--o{ SAVED_RECIPES : saved_as
    RECIPES ||--o{ RECIPE_LIKES : receives
    RECIPES ||--o{ RECIPE_INGREDIENTS : contains
    INGREDIENTS ||--o{ RECIPE_INGREDIENTS : used_in
    RECIPES ||--o{ INSTRUCTION_STEPS : has
    INGREDIENTS ||--o{ INGREDIENT_ALLERGIES : maps
    ALLERGIES ||--o{ INGREDIENT_ALLERGIES : includes
    COLLECTIONS ||--o{ COLLECTION_RECIPES : contains
    RECIPES ||--o{ COLLECTION_RECIPES : grouped_in

    USERS {
        int id PK
        varchar full_name
        varchar email UK
        enum role
        boolean is_suspended
    }
    RECIPES {
        int id PK
        int user_id FK
        int category_id FK
        int cuisine_id FK
        int diet_type_id FK
        int source_id FK
        varchar title
    }
    INGREDIENTS {
        int id PK
        varchar name UK
    }
    RECIPE_INGREDIENTS {
        int recipe_id PK,FK
        int ingredient_id PK,FK
        decimal quantity
        varchar unit
    }
    INSTRUCTION_STEPS {
        int recipe_id PK,FK
        int step_number PK
        text instruction
    }
    ALLERGIES {
        int id PK
        varchar name UK
    }
    INGREDIENT_ALLERGIES {
        int ingredient_id PK,FK
        int allergy_id PK,FK
    }
    COLLECTIONS {
        int id PK
        int user_id FK
        varchar name
    }
    COLLECTION_RECIPES {
        int collection_id PK,FK
        int recipe_id PK,FK
    }
```

The existing `catergory_id` spelling is retained for compatibility with the current application and database. It should be renamed to `category_id` in a future cleanup migration.
