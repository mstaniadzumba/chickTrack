import config
import sqlite3
from datetime import datetime

def add_order(customer_name, customer_location, customer_cell, no_of_chickens, amount_paid=0, batch_id=None):
    total_price = 120 * no_of_chickens
    outstanding_amount = total_price - amount_paid
    order_date = datetime.now().strftime('%Y-%m-%d')

    conn = sqlite3.connect(config.DB_URL)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(""" INSERT INTO orders (customer_name, customer_cell, customer_location, no_of_chickens,total_amount, amount_paid, outstanding_amount, batch_id, order_date)
                   VALUES (?,?,?,?,?,?,?,?,?)
                   """, (customer_name,customer_cell,customer_location, no_of_chickens, total_price,amount_paid, outstanding_amount, batch_id, order_date))
    
    new_id = cursor.lastrowid

    cursor.execute("SELECT * FROM orders WHERE id = ?", (new_id,))
    row = cursor.fetchone()
    
    conn.commit()
    conn.close()

    return dict(row)

def get_orders_by_batch(batch_id=None):
    conn = sqlite3.connect(config.DB_URL)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if batch_id:
        cursor.execute("SELECT * FROM orders WHERE batch_id = ?", (batch_id,))
    else:
        cursor.execute("SELECT * FROM orders")
    
    orders = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return orders
