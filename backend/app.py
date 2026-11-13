# backend/app.py
import os
import uuid
import mysql.connector
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from db import get_db_connection

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

# Map Flask to the Presentation Tier directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, '../frontend/templates')
STATIC_DIR = os.path.join(BASE_DIR, '../frontend/static')

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.secret_key = os.getenv("FLASK_SECRET_KEY")
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

UPLOAD_DIR = os.path.join(STATIC_DIR, 'uploads')
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}


def sync_structured_recipe_data(cursor, recipe_id, ingredients_text, instructions_text):
    """Keep normalized ingredient and instruction tables in sync with legacy form text."""
    cursor.execute('DELETE FROM recipe_ingredients WHERE recipe_id = %s', (recipe_id,))
    cursor.execute('DELETE FROM instruction_steps WHERE recipe_id = %s', (recipe_id,))

    ingredient_lines = [
        line.strip().lstrip('-•*').strip()
        for line in ingredients_text.splitlines()
        if line.strip().lstrip('-•*').strip()
    ]
    for ingredient_name in ingredient_lines:
        cursor.execute(
            'INSERT IGNORE INTO ingredients (name) VALUES (%s)',
            (ingredient_name[:150],),
        )
        cursor.execute('SELECT id FROM ingredients WHERE name = %s', (ingredient_name[:150],))
        ingredient = cursor.fetchone()
        ingredient_id = ingredient[0] if not isinstance(ingredient, dict) else ingredient['id']
        cursor.execute(
            'INSERT IGNORE INTO recipe_ingredients (recipe_id, ingredient_id) VALUES (%s, %s)',
            (recipe_id, ingredient_id),
        )
        link_ingredient_to_allergies(cursor, ingredient_id, ingredient_name)

    instruction_lines = [line.strip() for line in instructions_text.splitlines() if line.strip()]
    for step_number, instruction in enumerate(instruction_lines, start=1):
        cursor.execute(
            'INSERT INTO instruction_steps (recipe_id, step_number, instruction) VALUES (%s, %s, %s)',
            (recipe_id, step_number, instruction),
        )


def sync_recipe_allergies(cursor, recipe_id, allergy_names):
    cursor.execute('DELETE FROM recipe_allergies WHERE recipe_id = %s', (recipe_id,))
    for allergy_name in allergy_names:
        cursor.execute('SELECT id FROM allergies WHERE name = %s', (allergy_name,))
        allergy = cursor.fetchone()
        if allergy:
            allergy_id = allergy[0] if not isinstance(allergy, dict) else allergy['id']
            cursor.execute(
                'INSERT IGNORE INTO recipe_allergies (recipe_id, allergy_id) VALUES (%s, %s)',
                (recipe_id, allergy_id),
            )


def singular_word(word):
    return word[:-1] if word.endswith("s") else word


def link_ingredient_to_allergies(cursor, ingredient_id, ingredient_name):
    cursor.execute("SELECT id, name FROM allergies")
    ingredient_words = {singular_word(word) for word in ingredient_name.lower().split()}
    for allergy in cursor.fetchall():
        allergy_id = allergy[0] if not isinstance(allergy, dict) else allergy['id']
        allergy_name = allergy[1] if not isinstance(allergy, dict) else allergy['name']
        allergy_words = [singular_word(word) for word in allergy_name.lower().split()]
        if allergy_words and all(word in ingredient_words for word in allergy_words):
            cursor.execute(
                "INSERT IGNORE INTO ingredient_allergies (ingredient_id, allergy_id) VALUES (%s, %s)",
                (ingredient_id, allergy_id),
            )


@app.route('/')
def home():
    conn = get_db_connection()
    popular_recipes = []

    if conn:
        cursor = conn.cursor(dictionary=True)
        current_user_id = session.get('user_id', 0)
        cursor.execute(
            """
            SELECT r.id, r.title, r.cooking_time_minutes, r.image_filename,
                   r.created_at, c.name AS category_name,
                   COUNT(DISTINCT weekly_saves.user_id) AS weekly_saves,
                   COUNT(DISTINCT recipe_likes.user_id) AS like_count,
                   (SELECT COUNT(*) FROM comments all_comments
                    WHERE all_comments.recipe_id = r.id
                      AND all_comments.is_hidden = FALSE) AS comment_count,
                   CASE WHEN user_saves.recipe_id IS NULL THEN 0 ELSE 1 END AS is_saved,
                   CASE WHEN user_likes.recipe_id IS NULL THEN 0 ELSE 1 END AS is_liked
            FROM recipes r
            LEFT JOIN categories c ON r.catergory_id = c.id
            LEFT JOIN saved_recipes weekly_saves
              ON weekly_saves.recipe_id = r.id
             AND weekly_saves.saved_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            LEFT JOIN saved_recipes user_saves
              ON user_saves.recipe_id = r.id
             AND user_saves.user_id = %s
            LEFT JOIN recipe_likes recipe_likes
              ON recipe_likes.recipe_id = r.id
            LEFT JOIN recipe_likes user_likes
              ON user_likes.recipe_id = r.id
             AND user_likes.user_id = %s
            GROUP BY r.id, r.title, r.cooking_time_minutes, r.image_filename,
                     r.created_at, c.name, user_saves.recipe_id, user_likes.recipe_id
            ORDER BY weekly_saves DESC, r.created_at DESC
            LIMIT 3
            """,
            (current_user_id, current_user_id),
        )
        popular_recipes = cursor.fetchall()
        cursor.close()
        conn.close()

    return render_template('home.html', popular_recipes=popular_recipes)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        conn = get_db_connection()
        if not conn:
            flash('Database connection failed. Please check MySQL settings.', 'error')
            return redirect(url_for('login'))

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and user.get('is_suspended'):
            flash('This account has been suspended.', 'error')
            return redirect(url_for('login'))

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['full_name']
            session['user_role'] = user.get('role', 'registered')
            # Redirect straight to Profile Page after login
            return redirect(url_for('profile'))

        flash('Invalid email or password.', 'error')
        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return redirect(url_for('login') + '#register')

    full_name = request.form.get('fullName')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirmPassword')

    if password != confirm_password:
        flash('Passwords do not match.', 'register_error')
        return redirect(url_for('login') + '#register')

    hashed_pw = generate_password_hash(password)

    conn = get_db_connection()
    if not conn:
        flash('Database connection failed. Please check MySQL settings.', 'register_error')
        return redirect(url_for('login') + '#register')

    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (full_name, email, password_hash) VALUES (%s, %s, %s)",
            (full_name, email, hashed_pw)
        )
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        if err.errno == 1062:
            flash('Email is already registered.', 'register_error')
        else:
            flash('An error occurred during registration.', 'register_error')
        return redirect(url_for('login') + '#register')
    finally:
        cursor.close()
        conn.close()

    session.clear()
    flash('Account created successfully! Please sign in with your new email and password.', 'success')
    return redirect(url_for('login'))


@app.route('/add-recipe', methods=['GET', 'POST'])
def add_recipe():
    if 'user_id' not in session:
        flash('Please sign in to add a recipe.', 'error')
        return redirect(url_for('login'))

    if request.method == 'GET':
        return render_template('add-recipe.html')

    title = request.form.get('recipeTitle', '').strip()
    category = request.form.get('recipeCategory', '').strip()
    cuisine = request.form.get('recipeCuisine', '').strip()
    diet = request.form.get('recipeDiet', '').strip()
    allergy_names = request.form.getlist('allergies')
    difficulty = request.form.get('recipeDifficulty', '').strip().title()
    description = request.form.get('recipeDescription', '').strip()
    ingredients = request.form.get('ingredients', '').strip()
    instructions = request.form.get('instructions', '').strip()
    image = request.files.get('recipeImage')

    try:
        prep_time = int(request.form.get('prepTime', '0'))
        cooking_time = int(request.form.get('cookTime', '0'))
        servings = int(request.form.get('servings', '0'))
    except ValueError:
        flash('Times and servings must be valid numbers.', 'error')
        return redirect(url_for('add_recipe'))

    if not all([title, category, cuisine, diet, difficulty, description, ingredients, instructions]):
        flash('Please complete all required recipe fields.', 'error')
        return redirect(url_for('add_recipe'))

    if prep_time < 0 or cooking_time < 0 or servings < 1:
        flash('Recipe times cannot be negative and servings must be at least 1.', 'error')
        return redirect(url_for('add_recipe'))

    image_filename = None
    if image and image.filename:
        original_filename = secure_filename(image.filename)
        extension = original_filename.rsplit('.', 1)[-1].lower() if '.' in original_filename else ''
        if extension not in ALLOWED_IMAGE_EXTENSIONS:
            flash('Please upload a JPG, PNG, GIF, or WEBP image.', 'error')
            return redirect(url_for('add_recipe'))
        image_filename = f'{uuid.uuid4().hex}.{extension}'
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        image.save(os.path.join(UPLOAD_DIR, image_filename))

    conn = get_db_connection()
    if not conn:
        flash('Database connection failed.', 'error')
        return redirect(url_for('add_recipe'))

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute('SELECT id FROM categories WHERE name = %s', (category,))
        category_row = cursor.fetchone()
        cursor.execute('SELECT id FROM cuisines WHERE name = %s', (cuisine,))
        cuisine_row = cursor.fetchone()
        cursor.execute('SELECT id FROM diet_types WHERE name = %s', (diet,))
        diet_row = cursor.fetchone()

        if not category_row or not cuisine_row or not diet_row:
            flash('One of the selected recipe classifications is invalid.', 'error')
            return redirect(url_for('add_recipe'))

        cursor.execute(
            """
            INSERT INTO recipes (
                user_id, catergory_id, cuisine_id, diet_type_id, title,
                description, difficulty, prep_time_minutes,
                cooking_time_minutes, serving_size, ingredients, instructions,
                image_filename
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                session['user_id'], category_row['id'], cuisine_row['id'],
                diet_row['id'], title, description, difficulty, prep_time,
                cooking_time, servings, ingredients, instructions, image_filename,
            ),
        )
        sync_structured_recipe_data(cursor, cursor.lastrowid, ingredients, instructions)
        sync_recipe_allergies(cursor, cursor.lastrowid, allergy_names)
        conn.commit()
    except mysql.connector.Error as error:
        conn.rollback()
        if error.errno == 1062:
            flash('You already have a recipe with that title.', 'error')
        else:
            flash('An error occurred while saving the recipe.', 'error')
        return redirect(url_for('add_recipe'))
    finally:
        cursor.close()
        conn.close()

    flash('Recipe published successfully!', 'success')
    return redirect(url_for('profile'))


def get_recipe_for_user(recipe_id):
    conn = get_db_connection()
    if not conn:
        return None, None
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM recipes WHERE id = %s AND user_id = %s",
        (recipe_id, session['user_id']),
    )
    recipe = cursor.fetchone()
    cursor.close()
    return recipe, conn


@app.route('/recipes/<int:recipe_id>/edit', methods=['GET', 'POST'])
def edit_recipe(recipe_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    recipe, conn = get_recipe_for_user(recipe_id)
    if not recipe or not conn:
        flash('Recipe not found.', 'error')
        return redirect(url_for('profile'))

    if request.method == 'GET':
        allergy_cursor = conn.cursor(dictionary=True)
        allergy_cursor.execute(
            """
            SELECT allergies.name
            FROM recipe_allergies
            JOIN allergies ON allergies.id = recipe_allergies.allergy_id
            WHERE recipe_allergies.recipe_id = %s
            """,
            (recipe_id,),
        )
        recipe_allergies = [row['name'] for row in allergy_cursor.fetchall()]
        allergy_cursor.close()
        conn.close()
        return render_template('edit-recipe.html', recipe=recipe, recipe_allergies=recipe_allergies)

    title = request.form.get('recipeTitle', '').strip()
    description = request.form.get('recipeDescription', '').strip()
    ingredients = request.form.get('ingredients', '').strip()
    instructions = request.form.get('instructions', '').strip()
    allergy_names = request.form.getlist('allergies')
    difficulty = request.form.get('recipeDifficulty', '').strip().title()
    try:
        prep_time = int(request.form.get('prepTime', '0'))
        cooking_time = int(request.form.get('cookTime', '0'))
        servings = int(request.form.get('servings', '0'))
    except ValueError:
        conn.close()
        flash('Times and servings must be valid numbers.', 'error')
        return redirect(url_for('edit_recipe', recipe_id=recipe_id))

    if not all([title, description, ingredients, instructions, difficulty]):
        conn.close()
        flash('Please complete all required fields.', 'error')
        return redirect(url_for('edit_recipe', recipe_id=recipe_id))

    new_image_filename = None
    image = request.files.get('recipeImage')
    if image and image.filename:
        original_filename = secure_filename(image.filename)
        extension = original_filename.rsplit('.', 1)[-1].lower() if '.' in original_filename else ''
        if extension not in ALLOWED_IMAGE_EXTENSIONS:
            conn.close()
            flash('Please upload a JPG, PNG, GIF, or WEBP image.', 'error')
            return redirect(url_for('edit_recipe', recipe_id=recipe_id))
        new_image_filename = f'{uuid.uuid4().hex}.{extension}'
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        image.save(os.path.join(UPLOAD_DIR, new_image_filename))

    cursor = conn.cursor()
    try:
        if new_image_filename:
            cursor.execute(
                """
                UPDATE recipes
                SET title=%s, description=%s, difficulty=%s,
                    prep_time_minutes=%s, cooking_time_minutes=%s,
                    serving_size=%s, ingredients=%s, instructions=%s,
                    image_filename=%s
                WHERE id=%s AND user_id=%s
                """,
                (title, description, difficulty, prep_time, cooking_time,
                 servings, ingredients, instructions, new_image_filename,
                 recipe_id, session['user_id']),
            )
        else:
            cursor.execute(
                """
                UPDATE recipes
                SET title=%s, description=%s, difficulty=%s,
                    prep_time_minutes=%s, cooking_time_minutes=%s,
                    serving_size=%s, ingredients=%s, instructions=%s
                WHERE id=%s AND user_id=%s
                """,
                (title, description, difficulty, prep_time, cooking_time,
                 servings, ingredients, instructions, recipe_id,
                 session['user_id']),
            )
        sync_structured_recipe_data(cursor, recipe_id, ingredients, instructions)
        sync_recipe_allergies(cursor, recipe_id, allergy_names)
        conn.commit()
    except mysql.connector.Error:
        conn.rollback()
        flash('Unable to update this recipe. The title may already be in use.', 'error')
        return redirect(url_for('edit_recipe', recipe_id=recipe_id))
    finally:
        cursor.close()
        conn.close()

    if new_image_filename and recipe.get('image_filename'):
        old_image = os.path.join(UPLOAD_DIR, recipe['image_filename'])
        if os.path.exists(old_image):
            os.remove(old_image)

    flash('Recipe updated successfully!', 'success')
    return redirect(url_for('profile'))


@app.post('/recipes/<int:recipe_id>/delete')
def delete_recipe(recipe_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    recipe, conn = get_recipe_for_user(recipe_id)
    if not recipe and session.get('user_role') == 'moderator':
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT * FROM recipes WHERE id = %s', (recipe_id,))
            recipe = cursor.fetchone()
            cursor.close()
    if not recipe or not conn:
        flash('Recipe not found.', 'error')
        return redirect(url_for('profile'))

    cursor = conn.cursor()
    if session.get('user_role') == 'moderator':
        cursor.execute("DELETE FROM recipes WHERE id = %s", (recipe_id,))
    else:
        cursor.execute(
            "DELETE FROM recipes WHERE id = %s AND user_id = %s",
            (recipe_id, session['user_id']),
        )
    conn.commit()
    cursor.close()
    conn.close()

    if recipe.get('image_filename'):
        image_path = os.path.join(UPLOAD_DIR, recipe['image_filename'])
        if os.path.exists(image_path):
            os.remove(image_path)

    flash('Recipe deleted.', 'success')
    return redirect(url_for('profile'))


@app.post('/recipes/<int:recipe_id>/save')
def save_recipe(recipe_id):
    if 'user_id' not in session:
        flash('Please sign in to save recipes.', 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()
    if not conn:
        flash('Database connection failed.', 'error')
        return redirect(url_for('browse'))

    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT IGNORE INTO saved_recipes (user_id, recipe_id) VALUES (%s, %s)',
            (session['user_id'], recipe_id),
        )
        cursor.execute(
            "INSERT IGNORE INTO collections (user_id, name) VALUES (%s, 'Favorites')",
            (session['user_id'],),
        )
        cursor.execute(
            'SELECT id FROM collections WHERE user_id = %s AND name = %s',
            (session['user_id'], 'Favorites'),
        )
        favorite_collection = cursor.fetchone()
        if favorite_collection:
            cursor.execute(
                'INSERT IGNORE INTO collection_recipes (collection_id, recipe_id) VALUES (%s, %s)',
                (favorite_collection[0], recipe_id),
            )
        conn.commit()
    finally:
        cursor.close()
        conn.close()

    destination = request.referrer or url_for('browse')
    return redirect(destination.split('#', 1)[0] + f'#recipe-card-{recipe_id}')


@app.post('/recipes/<int:recipe_id>/unsave')
def unsave_recipe(recipe_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute(
            'DELETE FROM saved_recipes WHERE user_id = %s AND recipe_id = %s',
            (session['user_id'], recipe_id),
        )
        cursor.execute(
            """
            DELETE cr FROM collection_recipes cr
            JOIN collections c ON c.id = cr.collection_id
            WHERE c.user_id = %s AND c.name = 'Favorites' AND cr.recipe_id = %s
            """,
            (session['user_id'], recipe_id),
        )
        conn.commit()
        cursor.close()
        conn.close()

    destination = request.referrer or url_for('browse')
    return redirect(destination.split('#', 1)[0] + f'#recipe-card-{recipe_id}')


@app.post('/recipes/<int:recipe_id>/like')
def like_recipe(recipe_id):
    if 'user_id' not in session:
        flash('Please sign in to like recipes.', 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()
    if not conn:
        flash('Database connection failed.', 'error')
        return redirect(request.referrer or url_for('browse'))

    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT IGNORE INTO recipe_likes (user_id, recipe_id) VALUES (%s, %s)',
            (session['user_id'], recipe_id),
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()

    destination = request.referrer or url_for('browse')
    return redirect(destination.split('#', 1)[0] + f'#recipe-card-{recipe_id}')


@app.post('/recipes/<int:recipe_id>/unlike')
def unlike_recipe(recipe_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute(
            'DELETE FROM recipe_likes WHERE user_id = %s AND recipe_id = %s',
            (session['user_id'], recipe_id),
        )
        conn.commit()
        cursor.close()
        conn.close()

    destination = request.referrer or url_for('browse')
    return redirect(destination.split('#', 1)[0] + f'#recipe-card-{recipe_id}')


@app.route('/browse')
def browse():
    conn = get_db_connection()
    recipes = []
    if request.query_string:
        session['browse_query'] = request.query_string.decode('utf-8')
    else:
        session.pop('browse_query', None)
    search_term = request.args.get('q', '').strip()
    category_filter = request.args.get('category', '').strip()
    difficulty_filter = request.args.get('difficulty', '').strip()
    cuisine_filter = request.args.get('cuisine', '').strip()
    diet_filter = request.args.get('diet', '').strip()
    allergy_filters = [value.strip() for value in request.args.getlist('allergy') if value.strip()]
    allergy_names = []

    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT name FROM allergies ORDER BY name")
        allergy_names = [row["name"] for row in cursor.fetchall()]
        current_user_id = session.get('user_id', 0)
        search_clause = ''
        filter_clause = ''
        query_params = [current_user_id]

        if search_term:
            search_clause = """
                AND (
                    r.title LIKE %s OR r.description LIKE %s OR
                    r.ingredients LIKE %s OR c.name LIKE %s OR
                    cu.name LIKE %s OR d.name LIKE %s OR
                    EXISTS (
                        SELECT 1 FROM recipe_ingredients found_ri
                        JOIN ingredients found_ing ON found_ing.id = found_ri.ingredient_id
                        WHERE found_ri.recipe_id = r.id AND found_ing.name LIKE %s
                    )
                )
            """
            search_value = f'%{search_term}%'
            query_params.extend([search_value] * 7)

        if category_filter:
            filter_clause += ' AND c.name = %s'
            query_params.append(category_filter)
        if difficulty_filter in {'Easy', 'Medium', 'Hard'}:
            filter_clause += ' AND r.difficulty = %s'
            query_params.append(difficulty_filter)
        if cuisine_filter:
            filter_clause += ' AND cu.name = %s'
            query_params.append(cuisine_filter)
        if diet_filter:
            filter_clause += ' AND d.name = %s'
            query_params.append(diet_filter)
        if allergy_filters:
            allergy_placeholders = ', '.join(['%s'] * len(allergy_filters))
            filter_clause += f"""
                AND NOT EXISTS (
                    SELECT 1
                    FROM recipe_ingredients ri
                    JOIN ingredient_allergies ia ON ia.ingredient_id = ri.ingredient_id
                    JOIN allergies a ON a.id = ia.allergy_id
                    WHERE ri.recipe_id = r.id AND a.name IN ({allergy_placeholders})
                )
                AND NOT EXISTS (
                    SELECT 1
                    FROM recipe_allergies ra
                    JOIN allergies recipe_a ON recipe_a.id = ra.allergy_id
                    WHERE ra.recipe_id = r.id AND recipe_a.name IN ({allergy_placeholders})
                )
            """
            query_params.extend(allergy_filters + allergy_filters)

        cursor.execute(
            f"""
            SELECT r.*, c.name AS category_name, cu.name AS cuisine_name,
                   d.name AS diet_name, s.recipe_id IS NOT NULL AS is_saved,
                   l.recipe_id IS NOT NULL AS is_liked,
                   (SELECT COUNT(*) FROM recipe_likes all_likes
                    WHERE all_likes.recipe_id = r.id) AS like_count,
                   (SELECT COUNT(*) FROM comments all_comments
                    WHERE all_comments.recipe_id = r.id
                      AND all_comments.is_hidden = FALSE) AS comment_count
            FROM recipes r
            LEFT JOIN categories c ON r.catergory_id = c.id
            LEFT JOIN cuisines cu ON r.cuisine_id = cu.id
            LEFT JOIN diet_types d ON r.diet_type_id = d.id
            LEFT JOIN saved_recipes s
              ON s.recipe_id = r.id AND s.user_id = %s
            LEFT JOIN recipe_likes l
              ON l.recipe_id = r.id AND l.user_id = %s
            WHERE 1=1
            {search_clause}
            {filter_clause}
            ORDER BY r.created_at DESC
            """,
            [current_user_id, current_user_id] + query_params[1:],
        )
        recipes = cursor.fetchall()
        cursor.close()
        conn.close()

    return render_template(
        'browse.html',
        recipes=recipes,
        search_term=request.args.get('q', '').strip(),
        filters={
            'category': category_filter,
            'difficulty': difficulty_filter,
            'cuisine': cuisine_filter,
            'diet': diet_filter,
            'allergies': allergy_filters,
        },
        allergy_names=allergy_names,
    )


@app.route('/recipes/<int:recipe_id>')
def recipe_detail(recipe_id):
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed.', 'error')
        return redirect(url_for('browse'))

    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT r.*, u.full_name AS author_name, c.name AS category_name,
               cu.name AS cuisine_name, d.name AS diet_name,
               (SELECT COUNT(*) FROM recipe_likes WHERE recipe_id = r.id) AS like_count,
               EXISTS(
                   SELECT 1 FROM recipe_likes
                   WHERE recipe_likes.recipe_id = r.id
                     AND recipe_likes.user_id = %s
               ) AS is_liked
        FROM recipes r
        JOIN users u ON r.user_id = u.id
        LEFT JOIN categories c ON r.catergory_id = c.id
        LEFT JOIN cuisines cu ON r.cuisine_id = cu.id
        LEFT JOIN diet_types d ON r.diet_type_id = d.id
        WHERE r.id = %s
        """,
        (session.get('user_id', 0), recipe_id),
    )
    recipe = cursor.fetchone()
    comments = []
    if recipe:
        try:
            cursor.execute(
                """
                SELECT comments.id, comments.body, comments.created_at,
                       comments.user_id, users.full_name AS author_name,
                       users.profile_image_filename
                FROM comments
                JOIN users ON users.id = comments.user_id
                WHERE comments.recipe_id = %s
                  AND comments.is_hidden = FALSE
                ORDER BY comments.created_at DESC
                """,
                (recipe_id,),
            )
            comments = cursor.fetchall()
        except mysql.connector.Error:
            # Keep recipe pages available before the comments migration runs.
            comments = []
    cursor.close()
    conn.close()

    if not recipe:
        flash('Recipe not found.', 'error')
        return redirect(url_for('browse'))

    return render_template('recipe-detail.html', recipe=recipe, comments=comments)


@app.route('/users/<int:user_id>')
def public_profile(user_id):
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed.', 'error')
        return redirect(url_for('browse'))

    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        'SELECT id, full_name, profile_image_filename, created_at FROM users WHERE id = %s AND is_suspended = FALSE',
        (user_id,),
    )
    user = cursor.fetchone()
    recipes = []
    if user:
        cursor.execute(
            """
            SELECT r.*, c.name AS category_name
            FROM recipes r
            LEFT JOIN categories c ON r.catergory_id = c.id
            WHERE r.user_id = %s
            ORDER BY r.created_at DESC
            """,
            (user_id,),
        )
        recipes = cursor.fetchall()
    cursor.close()
    conn.close()

    if not user:
        flash('Profile not found.', 'error')
        return redirect(url_for('browse'))

    return render_template('public-profile.html', user=user, recipes=recipes)


@app.post('/recipes/<int:recipe_id>/comments')
def add_comment(recipe_id):
    if 'user_id' not in session:
        flash('Please sign in to comment on recipes.', 'error')
        return redirect(url_for('login'))

    body = request.form.get('body', '').strip()
    if not body:
        flash('Please write a comment before submitting.', 'error')
        return redirect(url_for('recipe_detail', recipe_id=recipe_id))
    if len(body) > 1000:
        flash('Comments must be 1000 characters or fewer.', 'error')
        return redirect(url_for('recipe_detail', recipe_id=recipe_id))

    conn = get_db_connection()
    if not conn:
        flash('Database connection failed.', 'error')
        return redirect(url_for('recipe_detail', recipe_id=recipe_id))

    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO comments (user_id, recipe_id, body) VALUES (%s, %s, %s)',
            (session['user_id'], recipe_id, body),
        )
        conn.commit()
        comment_id = cursor.lastrowid
        flash('Comment added.', 'success')
    except mysql.connector.Error:
        conn.rollback()
        flash('Unable to add your comment.', 'error')
    finally:
        cursor.close()
        conn.close()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'id': comment_id,
            'body': body,
            'author_name': session.get('user_name', 'You'),
            'user_id': session['user_id'],
        })

    return redirect(url_for('recipe_detail', recipe_id=recipe_id) + '#comments')


@app.post('/comments/<int:comment_id>/delete')
def delete_comment(comment_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    if not conn:
        flash('Database connection failed.', 'error')
        return redirect(request.referrer or url_for('browse'))

    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        'SELECT recipe_id, user_id FROM comments WHERE id = %s',
        (comment_id,),
    )
    comment = cursor.fetchone()
    can_moderate = session.get('user_role') == 'moderator'
    if not comment or (comment['user_id'] != session['user_id'] and not can_moderate):
        cursor.close()
        conn.close()
        flash('You do not have permission to remove this comment.', 'error')
        return redirect(request.referrer or url_for('browse'))

    cursor.execute('DELETE FROM comments WHERE id = %s', (comment_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Comment removed.', 'success')
    return redirect(url_for('recipe_detail', recipe_id=comment['recipe_id']) + '#comments')


@app.post('/comments/<int:comment_id>/hide')
def hide_comment(comment_id):
    if 'user_id' not in session or session.get('user_role') != 'moderator':
        flash('Only moderators can hide comments.', 'error')
        return redirect(request.referrer or url_for('browse'))

    conn = get_db_connection()
    if not conn:
        flash('Database connection failed.', 'error')
        return redirect(request.referrer or url_for('browse'))

    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT recipe_id FROM comments WHERE id = %s', (comment_id,))
    comment = cursor.fetchone()
    if comment:
        cursor.execute('UPDATE comments SET is_hidden = TRUE WHERE id = %s', (comment_id,))
        conn.commit()
        flash('Comment hidden from public view.', 'success')
    else:
        flash('Comment not found.', 'error')
    cursor.close()
    conn.close()
    return redirect(url_for('recipe_detail', recipe_id=comment['recipe_id']) + '#comments' if comment else (request.referrer or url_for('browse')))


@app.route('/moderation/comments')
def moderation_comments():
    if 'user_id' not in session or session.get('user_role') != 'moderator':
        flash('Only moderators can access moderation tools.', 'error')
        return redirect(url_for('home'))

    conn = get_db_connection()
    hidden_comments = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT comments.id, comments.body, comments.created_at,
                   users.full_name AS author_name, recipes.id AS recipe_id,
                   recipes.title AS recipe_title
            FROM comments
            JOIN users ON users.id = comments.user_id
            JOIN recipes ON recipes.id = comments.recipe_id
            WHERE comments.is_hidden = TRUE
            ORDER BY comments.created_at DESC
            """
        )
        hidden_comments = cursor.fetchall()
        cursor.close()
        conn.close()
    return render_template('moderation-comments.html', comments=hidden_comments)


@app.post('/comments/<int:comment_id>/unhide')
def unhide_comment(comment_id):
    if 'user_id' not in session or session.get('user_role') != 'moderator':
        flash('Only moderators can unhide comments.', 'error')
        return redirect(url_for('home'))

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE comments SET is_hidden = FALSE WHERE id = %s', (comment_id,))
        conn.commit()
        cursor.close()
        conn.close()
    flash('Comment restored to public view.', 'success')
    return redirect(url_for('moderation_comments'))


@app.route('/collections')
def collections():
    if 'user_id' not in session:
        flash('Please sign in to view your collections.', 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()
    saved_recipes = []
    created_recipes = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT r.*, c.name AS category_name
            FROM saved_recipes s
            JOIN recipes r ON r.id = s.recipe_id
            LEFT JOIN categories c ON r.catergory_id = c.id
            WHERE s.user_id = %s
            ORDER BY s.saved_at DESC
            """,
            (session['user_id'],),
        )
        saved_recipes = cursor.fetchall()
        cursor.execute(
            """
            SELECT r.*, c.name AS category_name
            FROM recipes r
            LEFT JOIN categories c ON r.catergory_id = c.id
            WHERE r.user_id = %s
            ORDER BY r.created_at DESC
            """,
            (session['user_id'],),
        )
        created_recipes = cursor.fetchall()
        cursor.close()
        conn.close()

    return render_template(
        'collections.html',
        saved_recipes=saved_recipes,
        created_recipes=created_recipes,
    )


@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Please sign in to access your profile.', 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()
    if not conn:
        flash('Database connection failed.', 'error')
        return redirect(url_for('home'))

    cursor = conn.cursor(dictionary=True)
    
    # Fetch account details
    cursor.execute("SELECT id, full_name, email, profile_image_filename, created_at FROM users WHERE id = %s", (session['user_id'],))
    user = cursor.fetchone()

    # Fetch user's recipes (safely handles case where recipes table isn't created yet)
    recipes = []
    try:
        cursor.execute("SELECT * FROM recipes WHERE user_id = %s ORDER BY created_at DESC", (session['user_id'],))
        recipes = cursor.fetchall()
    except mysql.connector.Error:
        pass
    finally:
        cursor.close()
        conn.close()

    return render_template('profile.html', user=user, recipes=recipes)


@app.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        flash('Please sign in to edit your profile.', 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()
    if not conn:
        flash('Database connection failed.', 'error')
        return redirect(url_for('profile'))

    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        'SELECT id, full_name, email, profile_image_filename FROM users WHERE id = %s',
        (session['user_id'],),
    )
    user = cursor.fetchone()

    if request.method == 'GET':
        cursor.close()
        conn.close()
        return render_template('profile-edit.html', user=user)

    full_name = request.form.get('fullName', '').strip()
    email = request.form.get('email', '').strip().lower()
    profile_image = request.files.get('profileImage')

    if not full_name or not email:
        cursor.close()
        conn.close()
        flash('Name and email are required.', 'error')
        return redirect(url_for('edit_profile'))

    new_profile_image = None
    if profile_image and profile_image.filename:
        original_filename = secure_filename(profile_image.filename)
        extension = original_filename.rsplit('.', 1)[-1].lower() if '.' in original_filename else ''
        if extension not in ALLOWED_IMAGE_EXTENSIONS:
            cursor.close()
            conn.close()
            flash('Please upload a JPG, PNG, GIF, or WEBP image.', 'error')
            return redirect(url_for('edit_profile'))
        new_profile_image = f'profile-{uuid.uuid4().hex}.{extension}'
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        profile_image.save(os.path.join(UPLOAD_DIR, new_profile_image))

    try:
        if new_profile_image:
            cursor.execute(
                'UPDATE users SET full_name = %s, email = %s, profile_image_filename = %s WHERE id = %s',
                (full_name, email, new_profile_image, session['user_id']),
            )
        else:
            cursor.execute(
                'UPDATE users SET full_name = %s, email = %s WHERE id = %s',
                (full_name, email, session['user_id']),
            )
        conn.commit()
    except mysql.connector.Error as error:
        conn.rollback()
        cursor.close()
        conn.close()
        if error.errno == 1062:
            flash('That email is already in use.', 'error')
        else:
            flash('Unable to update your profile.', 'error')
        return redirect(url_for('edit_profile'))

    old_profile_image = user.get('profile_image_filename')
    cursor.close()
    conn.close()
    if new_profile_image and old_profile_image:
        old_image_path = os.path.join(UPLOAD_DIR, old_profile_image)
        if os.path.exists(old_image_path):
            os.remove(old_image_path)
    session['user_name'] = full_name
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('profile'))


@app.route('/profile/password', methods=['GET', 'POST'])
def change_password():
    if 'user_id' not in session:
        flash('Please sign in to change your password.', 'error')
        return redirect(url_for('login'))

    if request.method == 'GET':
        return render_template('change-password.html')

    current_password = request.form.get('currentPassword', '')
    new_password = request.form.get('newPassword', '')
    confirm_password = request.form.get('confirmPassword', '')

    if len(new_password) < 8:
        flash('Your new password must be at least 8 characters.', 'error')
        return redirect(url_for('change_password'))

    if new_password != confirm_password:
        flash('The new passwords do not match.', 'error')
        return redirect(url_for('change_password'))

    conn = get_db_connection()
    if not conn:
        flash('Database connection failed.', 'error')
        return redirect(url_for('profile'))

    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT password_hash FROM users WHERE id = %s', (session['user_id'],))
    user = cursor.fetchone()

    if not user or not check_password_hash(user['password_hash'], current_password):
        cursor.close()
        conn.close()
        flash('Your current password is incorrect.', 'error')
        return redirect(url_for('change_password'))

    cursor.execute(
        'UPDATE users SET password_hash = %s WHERE id = %s',
        (generate_password_hash(new_password), session['user_id']),
    )
    conn.commit()
    cursor.close()
    conn.close()

    flash('Password changed successfully.', 'success')
    return redirect(url_for('profile'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True, port=int(os.getenv('PORT', '5050')))
