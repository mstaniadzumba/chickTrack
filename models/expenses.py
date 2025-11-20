import config
import sqlite3



def add_expense(expense_name, expense_amount, expense_date, comments=None):
    conn = sqlite3.connect(config.DB_URL)
    cursor = conn.cursor()

    cursor.execute(""" INSERT INTO expenses (expense_name, expense_amount, expense_date, comments)
                   VALUES (?,?,?,?)
                   """, (expense_name, expense_amount, expense_date, comments))
    conn.commit()
    conn.close()