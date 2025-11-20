import sqlite3
import config

def db_init():
    conn = sqlite3.connect(config.DB_URL)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY,
        customer_name TEXT NOT NULL,
        customer_location TEXT NOT NULL,
        no_of_chickens INTEGER NOT NULL,
        amount_paid INTEGER NOT NULL,
        outstanding_amount INTEGER NOT NULL
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY,
        expense_name TEXT NOT NULL,
        expense_amount INTEGER NOT NULL,
        expense_date TEXT NOT NULL,
        comments TEXT
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS batch (
        id INTEGER PRIMARY KEY,
        month TEXT NOT NULL,
        start_date TEXT NOT NULL,
        chickens_bought INTEGER NOT NULL,
        dead_chicken INTEGER NOT NULL,
        live_chicken INTEGER NOT NULL,
        current_week INTEGER NOT NULL
    )''')

    conn.commit()
    conn.close()

