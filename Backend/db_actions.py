from .db import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2.extras
import datetime

def init_user_table():
    conn = get_db_connection()
    if not conn:
        return
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            fullname VARCHAR(255) NOT NULL,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP    
        );
    """)
    print("User table ensured.")

    conn.commit()
    cur.close()
    conn.close()

def init_task_table():
    conn = get_db_connection()
    if not conn:
        return
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_tasks (
            id SERIAL PRIMARY KEY,
            user_id INT NOT NULL,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            due_date TIMESTAMP,
            PRIORITY INT DEFAULT 0,
            completed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """)
    print("Tasks table ensured.")
    conn.commit()
    cur.close()
    conn.close()

def register_user(email, password, fullname):
    password_hash = generate_password_hash(password)
    conn = get_db_connection()
    if not conn:
        return None
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cur.execute(
            "INSERT INTO users (email, password_hash, fullname) "
            "VALUES (%s, %s, %s) RETURNING id, email, fullname;",
            (email, password_hash, fullname)
        )
        user = cur.fetchone()
        conn.commit()
        if user:
            return dict(user)
    except Exception as e:
        conn.rollback()
    finally:
        cur.close()
        conn.close()
    return None

def verify_user(email, password):
    conn = get_db_connection()
    if not conn:
        return None
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cur.execute(
            "SELECT id, email, fullname, password_hash FROM users WHERE email = %s;",
            (email,)
        )
        user = cur.fetchone()
        if user and check_password_hash(user['password_hash'], password):
            return {'id': user['id'], 'email': user['email'], 'fullname': user['fullname']}
    finally:
        cur.close()
        conn.close()
    return None

def get_fullname_by_id(user_id):
    conn = get_db_connection()
    if not conn:
        return None
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cur.execute("SELECT fullname FROM users WHERE id = %s;", (user_id,))
        user = cur.fetchone()
        if user:
            return user['fullname']
    finally:
        cur.close()
        conn.close()
    return None

def get_email_by_id(user_id):
    conn = get_db_connection()
    if not conn:
        return None
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cur.execute("SELECT email FROM users WHERE id = %s;",(user_id,))
        user = cur.fetchone()
        if user:
            return user['email']
    finally:
        cur.close()
        conn.close()
    return None

def get_joined_at_date_by_id(user_id):
    conn = get_db_connection()
    if not conn: 
        return None
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cur.execute("SELECT joined_at FROM users WHERE id = %s;",(user_id,))
        user = cur.fetchone()
        if user:
            date = user['joined_at']
            formatted = date.strftime("%d %b %Y")
            return formatted
    finally:
        cur.close()
        conn.close()
    return None

def create_task(user_id, title, description=None, due_date=None, priority=0):
    conn = get_db_connection()
    if not conn:
        return None
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cur.execute(
            "INSERT INTO user_tasks (user_id, title, description, due_date, priority) "
            "VALUES (%s, %s, %s, %s, %s) RETURNING id, title, description, due_date, created_at, priority;",
            (user_id, title, description, due_date, priority)
        )

        task = cur.fetchone()
        conn.commit()
        if task:
            return dict(task)
    except Exception as e:
        print(e)
        conn.rollback()
    finally:
        cur.close()
        conn.close()
    return None

def get_tasks_by_user(user_id):
    conn = get_db_connection()
    if not conn:
        return []
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cur.execute(
            "SELECT id, title, description, due_date, created_at, priority FROM user_tasks WHERE user_id = %s ORDER BY created_at DESC;",
            (user_id,)
        )
        tasks = cur.fetchall()
        return [dict(task) for task in tasks]
    finally:
        cur.close()
        conn.close()

def delete_task(task_id, user_id):
    conn = get_db_connection()
    if not conn:
        return False
    cur = conn.cursor()
    try:
        cur.execute(
            "DELETE FROM user_tasks WHERE id = %s AND user_id = %s;",
            (task_id, user_id)
        )
        conn.commit()
        return cur.rowcount > 0
    except Exception as e:
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def edit_task(task_id, user_id, title, description=None, due_date = None, priority=0):
    conn = get_db_connection()
    if not conn:
        return False
    cur = conn.cursor()
    try:
        if due_date:
            due_date = due_date if isinstance(due_date, datetime) else datetime.strptime(due_date, "%Y-%m-%d")
        cur.execute("""
            UPDATE user_tasks
                    SET title = %s, description = %s, due_date = %s, priority = %s
                    WHERE id = %s AND user_id = %s
                    """, (title, description, due_date, priority, task_id, user_id))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(e)
        return False
    finally:
        cur.close()
        conn.close()
