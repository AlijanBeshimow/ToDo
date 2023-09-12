import pickle
from flask import Flask, render_template, request, redirect

app = Flask(__name__)


def load():
    try:
        with open("tasks.pickle", 'rb') as file:
            return pickle.load(file)
    except FileNotFoundError:
        return []


tasks = load()


def save(tasks):
    with open("tasks.pickle", 'wb') as file:
        pickle.dump(tasks, file)


@app.route('/')
def welcome_page():
    return render_template("home.html", title="Home")


@app.route('/add', methods=['GET', 'POST'])
def add():
    global tasks
    if request.method == 'POST':
        username = request.form.get("username")
        date = request.form.get("date")
        category = request.form.get("category")
        assigned = request.form.get("assigned")
        notes = request.form.get("notes")
        new_task = (username, date, category, assigned, notes)
        tasks.append(new_task)
        save(tasks)
        return redirect('/view')
    return render_template("add.html")


@app.route('/view')
def view():
    global tasks
    return render_template("view.html", tasks=tasks)


@app.route('/delete', methods=['POST'])
def delete_task():
    global tasks
    task_index = int(request.form.get("task_index"))

    if 0 <= task_index < len(tasks):
        del tasks[task_index]
        save(tasks)

    return redirect('/view')


@app.route('/search')
def search():
    global tasks
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
