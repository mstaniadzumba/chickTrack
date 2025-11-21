import config
import sqlite3

def add_order(customer_name, customer_location, customer_cell, no_of_chickens, amount_paid=0):
    total_price = 120 * no_of_chickens
    outstanding_amount = total_price - amount_paid

    conn = sqlite3.connect(config.DB_URL)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(""" INSERT INTO orders (customer_name, customer_cell, customer_location, no_of_chickens,total_amount, amount_paid, outstanding_amount)
                   VALUES (?,?,?,?,?,?,?)
                   """, (customer_name,customer_cell,customer_location, no_of_chickens, total_price,amount_paid, outstanding_amount))
    
    new_id = cursor.lastrowid

    cursor.execute("SELECT * FROM orders WHERE id = ?", (new_id,))
    row = cursor.fetchone()
    
    conn.commit()
    conn.close()

    return dict(row)
