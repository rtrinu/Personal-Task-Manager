from flask import Flask, render_template, session, redirect, url_for, request, flash
from Backend.db import get_db_connection
from Backend.auth import auth_routes
import Backend.db_actions as db_actions


def create_app():
    app = Flask(__name__)
    app.secret_key = "your_secret_key"

    db_actions.init_user_table()
    db_actions.init_task_table()

    app.register_blueprint(auth_routes)
    return app

app = create_app()


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth_routes.login_form'))
    
    user_id = session['user_id']
    fullname = db_actions.get_fullname_by_id(user_id)
    email = db_actions.get_email_by_id(user_id)
    joined_at = db_actions.get_joined_at_date_by_id(user_id)
    user_tasks = display_tasks()
    displayed_tasks = user_tasks[:3]
    return render_template('dashboard.html', fullname=fullname, email=email, joined_at=joined_at, tasks=displayed_tasks )

@app.route('/create-task', methods=['GET','POST'])
def create_task():
    if 'user_id' not in session:
        return redirect(url_for('auth_routes.login_form'))
    if request.method == 'POST':
        title= request.form.get('title')
        description = request.form.get('description')
        due_date = request.form.get('due_date')
        priority = int(request.form.get('priority'))
        user_id = session['user_id']

        if due_date:
            from datetime import datetime
            due_date = datetime.strptime(due_date, "%Y-%m-%d")
        else:
            due_date = None
        
        task = db_actions.create_task(user_id, title, description, due_date, priority)
        if task:
            print("TASK CREATED:", task)
            return redirect(url_for('dashboard'))
        else:
            print("TASK CREATION FAILED")
    return render_template('create-task.html')

def display_tasks():
    user = session.get('user_id')
    if not user:
        return []
    tasks = db_actions.get_tasks_by_user(user)
    keys_to_remove = ['id', 'user_id']
    for task in tasks:
        for key in keys_to_remove:
            task.pop(key, None)
    return tasks


@app.route('/all-tasks')
def all_tasks():
    if 'user_id' not in session:
        return redirect(url_for('auth_routes.login_form'))
    tasks = display_tasks()
    return render_template('all-tasks.html', tasks=tasks)


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)