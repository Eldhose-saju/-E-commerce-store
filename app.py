from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key in production
app.config['DATABASE'] = os.path.join('instance', 'db.sqlite')

# ---------- DB INITIALIZATION ----------
def init_db():
    if not os.path.exists('instance'):
        os.makedirs('instance')
    
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()

    # Create products table
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL,
            image_url TEXT
        )
    ''')

    # Create users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Add admin user if not exists
    c.execute("SELECT * FROM users WHERE username = ?", ("adminreal",))
    if not c.fetchone():
        admin_hashed = generate_password_hash("three.03")
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("adminreal", admin_hashed))

    conn.commit()
    conn.close()

init_db()

# ---------- ROUTES ----------
@app.route('/')
def home():
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    c.execute("SELECT * FROM products")
    products = c.fetchall()
    conn.close()
    return render_template('home.html', products=products)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        raw_password = request.form['password']
        hashed_password = generate_password_hash(raw_password)

        conn = sqlite3.connect(app.config['DATABASE'])
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            flash("Signup successful! Please login.")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Username already exists!")
        finally:
            conn.close()
    return render_template('sign_up.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        raw_password = request.form['password']

        conn = sqlite3.connect(app.config['DATABASE'])
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[0], raw_password):
            session['username'] = username
            if username == "adminreal":
                return redirect(url_for('admin_panel'))
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password!")
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' in session and session['username'] != 'adminreal':
        return render_template('dashboard.html', username=session['username'])
    elif 'username' in session:
        return redirect(url_for('admin_panel'))
    else:
        flash("Please log in first.")
        return redirect(url_for('login'))

@app.route('/admin')
def admin_panel():
    if 'username' in session and session['username'] == 'adminreal':
        return render_template('admin_panel.html', username='adminreal')
    else:
        flash("Unauthorized access!")
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("Logged out successfully.")
    return redirect(url_for('login'))

# ---------- MAIN ----------
if __name__ == '__main__':
    app.run(debug=True)
