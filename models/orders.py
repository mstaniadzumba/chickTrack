import config
import sqlite3
from datetime import datetime

def add_order(customer_name, customer_location, customer_cell, no_of_chickens, amount_paid=0, batch_id=None, created_by=None):
    total_price = config.CHICKEN_PRICE * no_of_chickens
    outstanding_amount = total_price - amount_paid
    order_date = datetime.now().strftime('%Y-%m-%d')
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conn = sqlite3.connect(config.DB_URL)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(""" INSERT INTO orders (customer_name, customer_cell, customer_location, no_of_chickens,total_amount, amount_paid, outstanding_amount, batch_id, order_date, created_by, created_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?)
                   """, (customer_name,customer_cell,customer_location, no_of_chickens, total_price,amount_paid, outstanding_amount, batch_id, order_date, created_by, created_at))

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
        cursor.execute("SELECT * FROM orders WHERE batch_id = ? ORDER BY id DESC", (batch_id,))
    else:
        cursor.execute("SELECT * FROM orders ORDER BY id DESC")

    orders = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return orders

def get_total_sold(batch_id):
    """Total chickens sold (ordered) for a batch, ignoring deleted orders."""
    conn = sqlite3.connect(config.DB_URL)
    cursor = conn.cursor()

    cursor.execute("SELECT COALESCE(SUM(no_of_chickens), 0) FROM orders WHERE batch_id = ? AND is_deleted = 0", (batch_id,))
    total = cursor.fetchone()[0]

    conn.close()
    return total

def get_order_by_id(order_id):
    conn = sqlite3.connect(config.DB_URL)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
    row = cursor.fetchone()

    conn.close()
    return dict(row) if row else None

def delete_order(order_id, reason, deleted_by):
    """Soft-delete an order: flag it and keep it (crossed out) with who/why/when.

    The row stays in the table so nothing is lost, but it no longer counts towards
    sold chickens or revenue.
    """
    order = get_order_by_id(order_id)
    if not order:
        return False

    deleted_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conn = sqlite3.connect(config.DB_URL)
    cursor = conn.cursor()

    cursor.execute("""UPDATE orders SET is_deleted = 1, deleted_reason = ?, deleted_by = ?, deleted_at = ?
                   WHERE id = ?""", (reason, deleted_by, deleted_at, order_id))

    conn.commit()
    conn.close()
    return True
