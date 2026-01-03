import config
import sqlite3



def add_expense(expense_name, expense_amount, expense_date, comments=None, batch_id=None, created_by=None):
    from datetime import datetime
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
        cursor.execute("SELECT * FROM expenses WHERE batch_id = ?", (batch_id,))
    else:
        cursor.execute("SELECT * FROM expenses")
    
    expenses = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return expenses