import pickle
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)

app.secret_key = "12312323423wddasdsadasd"

users = {"tal": "admin", "gal": "admin", "alex": "admin"}


def load():
    try:
        with open("tasks.pickle", 'rb') as file:
            return pickle.load(file)
    except FileNotFoundError:
        return []


def save(tasks):
    with open("tasks.pickle", 'wb') as file:
        pickle.dump(tasks, file)


@app.route('/')
def hello():
    username = session.get("username")
    if username in users:
        return render_template('home.html')
    else:
        return redirect('/login')


@app.route('/add', methods=['GET', 'POST'])
def add():
    if session.get("username"):
        tasks = load()
        username = session["username"]
        if request.method == 'POST':
            name = request.form.get("name")
            date = request.form.get("date")
            category = request.form.get("category")
            notes = request.form.get("notes")
            new_task = (name, date, category, username, notes)
            tasks.append(new_task)
            save(tasks)
            return redirect('/view')
        return render_template("add.html")
    else:
        return redirect('/login')


@app.route('/view')
def view():
    if session.get("username"):
        username = session["username"]
        tasks = load()
        user_tasks = []
        for task in tasks:
            if task[3] == username:
                user_tasks.append(task)
        return render_template("view.html", tasks=user_tasks)
    else:
        return redirect('/login')


@app.route('/delete', methods=['POST'])
def delete_task():
    tasks = load()
    task_index = int(request.form.get("task_index"))

    if 0 <= task_index < len(tasks):
        del tasks[task_index]
        save(tasks)

    return redirect('/view')


@app.route('/search')
def search():
    tasks = load()
    search = request.args.get("search")
    filtered_tasks = []
    for task in tasks:
        if search in task:
            filtered_tasks.append(task)
    if not filtered_tasks:
        return render_template("error.html", message="Task not Found")
    return render_template("view.html", tasks=filtered_tasks)


@app.route('/update')
def update():
    return render_template("update.html")


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    else:
        if {request.form["username"] in users} and (request.form["password"] == "admin"):
            session["username"] = request.form["username"]
            return redirect('/')
        return render_template("login.html", message="incorrect user or password")


@app.route('/logout')
def logout():
    session.pop("username", None)
    return redirect('/login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        if username in users:
            return render_template("register.html", message="Username already exists")
        users[username] = password
        return redirect('/login')
    return render_template("register.html")
