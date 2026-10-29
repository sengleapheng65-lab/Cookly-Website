# backend/app.py
import os
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db_connection

# Map Flask to the Presentation Tier directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, '../frontend/templates')
STATIC_DIR = os.path.join(BASE_DIR, '../frontend/static')

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.secret_key = 'cookly_jwt_secret_key'


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


@app.route('/register', methods=['POST'])
def register():
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

    flash('Account created successfully! Please sign in.', 'success')
    return redirect(url_for('login'))


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