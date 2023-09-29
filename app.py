import sqlite3
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)

app.secret_key = "12312323423wddasdsadasd"


def initialize_database():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            date TEXT,
            category TEXT,
            username TEXT NOT NULL,
            notes TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()


def load_tasks(username):
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE username=?", (username,))
    tasks = cursor.fetchall()
    conn.close()
    return tasks


def save_task(task):
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (name, date, category, username, notes) VALUES (?, ?, ?, ?, ?)", task)
    conn.commit()
    conn.close()


def authenticate_user(username, password):
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and user[2] == password:
        return True
    else:
        return False


def load_user_details(username):
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user_details = cursor.fetchone()
    conn.close()
    return user_details


@app.route('/profile')
def profile():
    if session.get("username"):
        username = session["username"]
        user_details = load_user_details(username)
        return render_template("profile.html", user=user_details)
    else:
        return redirect('/login')


@app.route('/')
def hello():
    if session.get("username"):
        username = session["username"]
        user_details = load_user_details(username)
        return render_template("add.html", user=user_details)
    else:
        return redirect('/login')


@app.route('/add', methods=['GET', 'POST'])
def add():
    if session.get("username"):
        username = session["username"]
        if request.method == 'POST':
            name = request.form.get("name")
            date = request.form.get("date")
            category = request.form.get("category")
            notes = request.form.get("notes")
            new_task = (name, date, category, username, notes)
            save_task(new_task)
            return redirect('/view')
        return render_template("add.html")
    else:
        return redirect('/login')


@app.route('/view')
def view():
    if session.get("username"):
        username = session["username"]
        user_tasks = load_tasks(username)
        return render_template("view.html", tasks=user_tasks)
    else:
        return redirect('/login')


@app.route('/delete', methods=['POST'])
def delete_task():
    task_id = int(request.form.get("task_id"))
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()
    return redirect('/view')


@app.route('/search')
def search():
    if session.get("username"):
        username = session["username"]
        search = request.args.get("search")
        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE (name LIKE ? OR notes LIKE ?) AND username = ?",
                       ('%' + search + '%', '%' + search + '%', username))
        filtered_tasks = cursor.fetchall()
        conn.close()
        if not filtered_tasks:
            return render_template("error.html", message="Task not Found")
        return render_template("view.html", tasks=filtered_tasks)
    else:
        return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    else:
        username = request.form["username"]
        password = request.form["password"]
        if authenticate_user(username, password):
            session["username"] = username
            return redirect('/')
        return render_template("login.html", message="Error username or password")


@app.route('/logout')
def logout():
    session.pop("username", None)
    return redirect('/login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        existing_user = cursor.fetchone()
        conn.close()

        if existing_user:
            return render_template("register.html", message="Username already exists")

        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template("register.html")


@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit(task_id):
    if session.get("username"):
        username = session["username"]

        if request.method == 'POST':
            name = request.form.get("name")
            date = request.form.get("date")
            category = request.form.get("category")
            notes = request.form.get("notes")
            conn = sqlite3.connect('tasks.db')
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE tasks SET name=?, date=?, category=?, notes=? WHERE id=? AND username=?",
                (name, date, category, notes, task_id, username)
            )
            conn.commit()
            conn.close()

            return redirect('/view')

        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM tasks WHERE id=? AND username=?", (task_id, username))
        task = cursor.fetchone()
        conn.close()

        if task:
            return render_template("edit.html", task=task)
        else:
            return render_template("error.html", message="Task not found")

    else:
        return redirect('/login')
