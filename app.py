from flask import Flask, render_template, session, redirect, url_for, request, flash
from Backend.db import get_db_connection
from Backend.auth import auth_routes
from Backend.stats import get_tasks_stats, calculate_progress

import Backend.db_actions as db_actions
from datetime import datetime

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
    active_tasks, completed_tasks = get_tasks_stats(user_tasks)
    progress = calculate_progress(active_tasks, completed_tasks)



    return render_template('dashboard.html', fullname=fullname, email=email, 
                           joined_at=joined_at, tasks=displayed_tasks,
                            active_tasks = active_tasks, completed_tasks = completed_tasks,
                             progress = progress )

@app.route('/create-task', methods=['GET','POST'])
def create_task():
    user_id = session['user_id']
    if 'user_id' not in session:
        return redirect(url_for('auth_routes.login_form'))
    fullname = db_actions.get_fullname_by_id(user_id)
    if request.method == 'POST':
        title= request.form.get('title')
        description = request.form.get('description')
        due_date = request.form.get('dueDate')
        priority = int(request.form.get('priority'))
        user_id = session['user_id']

        if due_date:
            due_date = datetime.strptime(due_date, "%Y-%m-%d")
        else:
            due_date = None
        
        task = db_actions.create_task(user_id, title, description, due_date, priority)
        if task:
            print("TASK CREATED:", task)
            return redirect(url_for('dashboard'))
        else:
            print("TASK CREATION FAILED")
    return render_template('create-task.html', fullname= fullname)

def display_tasks():
    user = session.get('user_id')
    if not user:
        return []
    tasks = db_actions.get_tasks_by_user(user)
    keys_to_remove = [ 'user_id']
    for task in tasks:
        created_at = task['created_at']
        due_date = task['due_date']
        task['created_at_str'] = created_at.strftime("%d %b %Y")
        task['due_date_str'] = due_date.strftime("%d %b %Y") if due_date else None
        for key in keys_to_remove:
            task.pop(key, None)
    overdue_tasks(tasks)
    return tasks

def mark_overdue_task(task):
    today = datetime.today().date()
    if task['due_date']:
        due = task['due_date'].date() if isinstance(task['due_date'], datetime) else task['due_date']
        task['overdue'] = due < today and not task.get('completed', False)
    else:
        task['overdue'] = False
    return task

def overdue_tasks(tasks):
    for task in tasks:
        mark_overdue_task(task)
    return tasks

@app.route('/all-tasks')
def all_tasks():
    if 'user_id' not in session:
        return redirect(url_for('auth_routes.login_form'))
    tasks = display_tasks()
    user_id = session['user_id']
    fullname = db_actions.get_fullname_by_id(user_id)
    return render_template('all-tasks.html', tasks=tasks, fullname=fullname)

@app.route('/delete-task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    user_id = session['user_id']
    if 'user_id' not in session:
        return redirect(url_for('auth.routes.login_form'))
    success = db_actions.delete_task(task_id,user_id)
    if success:
        print("Task Deleted")
    else:
        print("Task Failed to delete")
    return redirect(url_for('all_tasks'))

@app.route('/edit-task/<int:task_id>', methods=['GET','POST'])
def edit_task(task_id):
    if 'user_id' not in session:
        return redirect(url_for('auth_routes.login_form'))

    user_id = session['user_id']

    if request.method == 'POST':
        title = request.form.get('title')
        if not title:
            print("Title cannot be empty")
            return redirect(url_for('edit_task', task_id = task_id))
        description = request.form.get('description')
        due_date = request.form.get('due_date')
        priority = request.form.get('priority')

        success = db_actions.edit_task(task_id, user_id, title, description, due_date, priority)
        if success:
            print("Successfully edited")
        else:
            print("edit failed")
        return redirect(url_for('all_tasks'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM user_tasks WHERE id = %s AND user_id = %s", (task_id, user_id))
    task = cur.fetchone()
    cur.close()
    conn.close()

    if not task:
        flash("Task not found.", "danger")
        return redirect(url_for('all_tasks'))

    return render_template('edit-task.html', task=task)


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)