# backend/app.py
import os
import uuid
import mysql.connector
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, flash
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


@app.route('/')
def home():
    return render_template('home.html')


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

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['full_name']
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
        conn.close()
        return render_template('edit-recipe.html', recipe=recipe)

    title = request.form.get('recipeTitle', '').strip()
    description = request.form.get('recipeDescription', '').strip()
    ingredients = request.form.get('ingredients', '').strip()
    instructions = request.form.get('instructions', '').strip()
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
    if not recipe or not conn:
        flash('Recipe not found.', 'error')
        return redirect(url_for('profile'))

    cursor = conn.cursor()
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
        conn.commit()
    finally:
        cursor.close()
        conn.close()

    return redirect(request.referrer or url_for('browse'))


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
        conn.commit()
        cursor.close()
        conn.close()

    return redirect(request.referrer or url_for('browse'))


@app.route('/browse')
def browse():
    conn = get_db_connection()
    recipes = []

    if conn:
        cursor = conn.cursor(dictionary=True)
        current_user_id = session.get('user_id', 0)
        cursor.execute(
            """
            SELECT r.*, c.name AS category_name, cu.name AS cuisine_name,
                   d.name AS diet_name, s.recipe_id IS NOT NULL AS is_saved
            FROM recipes r
            LEFT JOIN categories c ON r.catergory_id = c.id
            LEFT JOIN cuisines cu ON r.cuisine_id = cu.id
            LEFT JOIN diet_types d ON r.diet_type_id = d.id
            LEFT JOIN saved_recipes s
              ON s.recipe_id = r.id AND s.user_id = %s
            ORDER BY r.created_at DESC
            """,
            (current_user_id,),
        )
        recipes = cursor.fetchall()
        cursor.close()
        conn.close()

    return render_template('browse.html', recipes=recipes)


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
               cu.name AS cuisine_name, d.name AS diet_name
        FROM recipes r
        JOIN users u ON r.user_id = u.id
        LEFT JOIN categories c ON r.catergory_id = c.id
        LEFT JOIN cuisines cu ON r.cuisine_id = cu.id
        LEFT JOIN diet_types d ON r.diet_type_id = d.id
        WHERE r.id = %s
        """,
        (recipe_id,),
    )
    recipe = cursor.fetchone()
    cursor.close()
    conn.close()

    if not recipe:
        flash('Recipe not found.', 'error')
        return redirect(url_for('browse'))

    return render_template('recipe-detail.html', recipe=recipe)


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
    cursor.execute("SELECT id, full_name, email, created_at FROM users WHERE id = %s", (session['user_id'],))
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


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True, port=5000)
