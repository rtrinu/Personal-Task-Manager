from .db import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash

def init_user_table():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to the database. ")
        return
    cur = conn.cursor()
    cur.execute("""
                CREATE TABLE IF NOT EXISTS users(
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL
                );
                """)
    conn.commit()
    cur.close()
    conn.close()
    print("User table initialized.")

def register_user(email, password):
    password_hash = generate_password_hash(password)
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to the database. ")
        return None
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (email, password_hash) Values (%s, %s) RETURNING id, email;",
                    (email, password_hash)
                    )
        user = cur.fetchone()
        conn.commit()
    except Exception as e:
        conn.rollback()
        user = None
        print(f"Error registering user: {e}")
    finally:
        cur.close()
        conn.close()
    return user

def verify_user(email,password):
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to the database. ")
        return None
    cur = conn.cursor()
    cur.execute("SELECT id, email, password_hash FROM users WHERE email = %s;")
    user = cur.fetchone()
    cur.close()
    conn.close()
    if user and check_password_hash(user['password_hash'], password):
        return {'id': user['id'], 'email': user['email']}
    return None