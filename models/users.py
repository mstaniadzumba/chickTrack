import config
import sqlite3
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(name, phone, password, is_admin=0):
    conn = sqlite3.connect(config.DB_URL)
    cursor = conn.cursor()

    try:
        hashed_password = hash_password(password)
        cursor.execute("INSERT INTO users (name, phone, password, is_admin) VALUES (?,?,?,?)",
                      (name, phone, hashed_password, 1 if is_admin else 0))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False  # Phone already exists

def login_user(phone, password):
    conn = sqlite3.connect(config.DB_URL)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    hashed_password = hash_password(password)
    cursor.execute("SELECT * FROM users WHERE phone = ? AND password = ?",
                  (phone, hashed_password))
    user = cursor.fetchone()

    conn.close()
    return dict(user) if user else None

def get_all_users():
    conn = sqlite3.connect(config.DB_URL)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, phone, is_admin FROM users ORDER BY name")
    users = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return users

def delete_user(user_id):
    conn = sqlite3.connect(config.DB_URL)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    deleted = cursor.rowcount

    conn.commit()
    conn.close()
    return deleted > 0

def count_admins():
    conn = sqlite3.connect(config.DB_URL)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = 1")
    count = cursor.fetchone()[0]

    conn.close()
    return count
