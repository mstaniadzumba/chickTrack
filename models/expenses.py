import config
import sqlite3



def add_expense(expense_name, expense_amount, expense_date):
    conn = sqlite3.connect(config.DB_URL)
    cursor = conn.cursor()

    cursor.execute(""" INSERT INTO expenses (expense_name, expense_amount, expense_date)
                   VALUES (?,?,?)
                   """, (expense_name, expense_amount, expense_date))
    conn.commit()
    conn.close()