import config
import sqlite3
from datetime import datetime


def add_expense(expense_name, expense_amount, expense_date, comments=None, batch_id=None, created_by=None):
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conn = sqlite3.connect(config.DB_URL)
    cursor = conn.cursor()

    cursor.execute(""" INSERT INTO expenses (expense_name, expense_amount, expense_date, comments, batch_id, created_by, created_at)
                   VALUES (?,?,?,?,?,?,?)
                   """, (expense_name, expense_amount, expense_date, comments, batch_id, created_by, created_at))
    conn.commit()
    conn.close()

def get_expenses_by_batch(batch_id=None):
    conn = sqlite3.connect(config.DB_URL)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if batch_id:
        cursor.execute("SELECT * FROM expenses WHERE batch_id = ? ORDER BY id DESC", (batch_id,))
    else:
        cursor.execute("SELECT * FROM expenses ORDER BY id DESC")

    expenses = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return expenses

def get_expense_by_id(expense_id):
    conn = sqlite3.connect(config.DB_URL)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
    row = cursor.fetchone()

    conn.close()
    return dict(row) if row else None

def delete_expense(expense_id, reason, deleted_by):
    """Soft-delete an expense: flag it and keep it (crossed out) with who/why/when.

    The row stays in the table so nothing is lost, but it no longer counts towards
    total expenses.
    """
    expense = get_expense_by_id(expense_id)
    if not expense:
        return False

    deleted_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conn = sqlite3.connect(config.DB_URL)
    cursor = conn.cursor()

    cursor.execute("""UPDATE expenses SET is_deleted = 1, deleted_reason = ?, deleted_by = ?, deleted_at = ?
                   WHERE id = ?""", (reason, deleted_by, deleted_at, expense_id))

    conn.commit()
    conn.close()
    return True
