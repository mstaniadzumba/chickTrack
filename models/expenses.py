import config
import sqlite3



def add_expense(expense_name, expense_amount):
    conn = sqlite3.connect(config.DB_URL)
    cursor = conn.cursor()

    cursor.execute(""" INSERT INTO expenses (expense_name, expense_amount)
                   VALUES (?,?)
                   """, (expense_name, expense_amount))
    conn.commit()
    conn.close()