from .db import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2.extras

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
            fullname VARCHAR(255) NOT NULL
        );
    """)
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
