from flask import Blueprint, request, jsonify
from models.orders import add_order, get_orders_by_batch
import sqlite3
import config
from datetime import datetime

order_routes = Blueprint('order_routes', __name__)

@order_routes.route("/api/add-order", methods=["POST"])
def create_order():
    data = request.get_json()
    full_order = add_order(customer_name=data['customer_name'],
              customer_location=data['customer_location'],
              customer_cell = data['customer_cell'],
              no_of_chickens=data['chickens_ordered'],
              amount_paid=data['amount_paid'],
              batch_id=data.get('batch_id'),
              created_by=data.get('created_by')
    )
    
    return jsonify({"message": "order successfully added",
                    'data':full_order})

@order_routes.route("/api/orders", methods=["GET"])
def get_orders():
    batch_id = request.args.get('batch_id')
    if batch_id:
        orders = get_orders_by_batch(int(batch_id))
    else:
        orders = get_orders_by_batch()  # Gets all orders
    return jsonify(orders)

@order_routes.route("/api/update-order/<int:order_id>", methods=["PUT"])
def update_order(order_id):
    data = request.get_json()
    
    # Update order in database
    conn = sqlite3.connect(config.DB_URL)
    cursor = conn.cursor()
    
    total_amount = 120 * data['chickens_ordered']
    outstanding_amount = total_amount - data['amount_paid']
    updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    updated_by = data.get('created_by')
    
    cursor.execute("""
        UPDATE orders SET 
        customer_name=?, customer_location=?, customer_cell=?, 
        no_of_chickens=?, total_amount=?, amount_paid=?, outstanding_amount=?,
        updated_by=?, updated_at=?
        WHERE id=?
    """, (data['customer_name'], data['customer_location'], data['customer_cell'],
          data['chickens_ordered'], total_amount, data['amount_paid'], outstanding_amount,
          updated_by, updated_at, order_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Order updated successfully", "data": data})