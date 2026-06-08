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
        is_deleted INTEGER NOT NULL DEFAULT 0,
        deleted_reason TEXT,
        deleted_by TEXT,
        deleted_at TEXT,
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
        is_deleted INTEGER NOT NULL DEFAULT 0,
        deleted_reason TEXT,
        deleted_by TEXT,
        deleted_at TEXT,
        FOREIGN KEY (batch_id) REFERENCES batch(id)
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS batch (
        id INTEGER PRIMARY KEY,
        month TEXT NOT NULL,
        start_date TEXT NOT NULL,
        chickens_bought INTEGER NOT NULL,
        dead_chicken INTEGER NOT NULL,
        live_chicken INTEGER NOT NULL,
        created_by TEXT,
        created_at TEXT,
        updated_by TEXT,
        updated_at TEXT
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        phone TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        is_admin INTEGER NOT NULL DEFAULT 0
    )''')

    # History / audit log: one permanent (never overwritten) entry for every
    # add, edit and delete, so we can always see what happened in each batch.
    cursor.execute('''CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY,
        batch_id INTEGER,
        record_type TEXT NOT NULL,
        record_id INTEGER,
        action TEXT NOT NULL,
        changes TEXT,
        user_name TEXT,
        created_at TEXT
    )''')

    conn.commit()
    conn.close()

    migrate()


def migrate():
    """Bring an existing database up to date without losing data.

    SQLite has no 'ADD COLUMN IF NOT EXISTS', so we look at the current columns
    first and only add what's missing.
    """
    conn = sqlite3.connect(config.DB_URL)
    cursor = conn.cursor()

    def columns(table):
        cursor.execute(f"PRAGMA table_info({table})")
        return [row[1] for row in cursor.fetchall()]

    def add_column_if_missing(table, column, definition):
        if column not in columns(table):
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

    # Roles
    add_column_if_missing("users", "is_admin", "INTEGER NOT NULL DEFAULT 0")

    # Safe (soft) delete: rows are flagged rather than removed, so we keep a record
    # of what was deleted, by whom and why.
    for table in ("orders", "expenses"):
        add_column_if_missing(table, "is_deleted", "INTEGER NOT NULL DEFAULT 0")
        add_column_if_missing(table, "deleted_reason", "TEXT")
        add_column_if_missing(table, "deleted_by", "TEXT")
        add_column_if_missing(table, "deleted_at", "TEXT")

    conn.commit()
    conn.close()
