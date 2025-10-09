from flask import Flask, render_template, request, session, redirect
from datetime import timedelta
import mysql.connector
import hashlib
import os

app = Flask(__name__)

def read_secret(path):
    if path and os.path.exists(path):
        with open(path) as f:
            return f.read().strip()
    return None

secret_path = os.environ.get('FLASK_SECRET_KEY')
app.config["SECRET_KEY"] = read_secret(secret_path) # Would be needed in prod for cookie security
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

def get_db_connection():
    password = read_secret(os.environ.get("MYSQL_PASSWORD_FILE"))
    database = os.environ.get("MYSQL_DATABASE")

    return mysql.connector.connect(
        host=os.environ.get("MYSQL_HOST", "db"),
        user=os.environ.get("MYSQL_USER", "root"),
        password=password,
        database=database
    )

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route("/")
def index():
    return redirect("/login")

@app.route("/login", methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form.get('login_username')
        password = request.form.get('login_pwd')

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s",
                       (username, hash_password(password)))
        user = cursor.fetchone()
        db.close()

        if user:
            session['loggedin'] = True
            session['username'] = user['username']
            return redirect("/home")

    return render_template("login.html")

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('signup_username')
        password = request.form.get('signup_pwd')

        db = get_db_connection()
        cursor = db.cursor()

        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)",
                           (username, hash_password(password)))
            db.commit()
        except mysql.connector.Error:
            db.rollback()
            db.close()
            return "Username already exists"

        db.close()
        return redirect("/login")

    return render_template("signup.html")

@app.route("/home")
def home():
    if not session.get('loggedin'):
        return redirect("/login")
    return render_template("main_page.html", username=session['username'])

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)