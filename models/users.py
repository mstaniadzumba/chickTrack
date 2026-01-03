import config
import sqlite3
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(name, phone, password):
    conn = sqlite3.connect(config.DB_URL)
    cursor = conn.cursor()
    
    try:
        hashed_password = hash_password(password)
        cursor.execute("INSERT INTO users (name, phone, password) VALUES (?,?,?)", 
                      (name, phone, hashed_password))
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