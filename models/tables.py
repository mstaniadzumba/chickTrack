import sqlite3
import config

def db_init():
    conn = sqlite3.connect(config.DB_URL)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY,
        customer_name TEXT NOT NULL,
        customer_location TEXT NOT NULL,
        customer_cell TEXT NOT NULL,
        no_of_chickens INTEGER NOT NULL,
        total_amount INTEGER NOT NULL,
        amount_paid INTEGER NOT NULL,
        outstanding_amount INTEGER NOT NULL,
        batch_id INTEGER,
        order_date TEXT NOT NULL,
        created_by TEXT,
        created_at TEXT,
        updated_by TEXT,
        updated_at TEXT,
        FOREIGN KEY (batch_id) REFERENCES batch(id)
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY,
        expense_name TEXT NOT NULL,
        expense_amount INTEGER NOT NULL,
        expense_date TEXT NOT NULL,
        comments TEXT,
        batch_id INTEGER,
        created_by TEXT,
        created_at TEXT,
        updated_by TEXT,
        updated_at TEXT,
        FOREIGN KEY (batch_id) REFERENCES batch(id)
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS batch (
        id INTEGER PRIMARY KEY,
        month TEXT NOT NULL,
        start_date TEXT NOT NULL,
        chickens_bought INTEGER NOT NULL,
        dead_chicken INTEGER NOT NULL,
        live_chicken INTEGER NOT NULL,
        current_week INTEGER NOT NULL,
        created_by TEXT,
        created_at TEXT,
        updated_by TEXT,
        updated_at TEXT
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        phone TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )''')

    conn.commit()
    conn.close()

