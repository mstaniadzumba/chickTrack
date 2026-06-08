from flask import Blueprint, request, jsonify, session
from models.orders import add_order, get_orders_by_batch, get_order_by_id, delete_order
from models.batch import get_batch_by_id
from models.audit import log_audit, diff_changes
from routes.auth import login_required, admin_required
import sqlite3
import config
from datetime import datetime

order_routes = Blueprint('order_routes', __name__)

@order_routes.route("/api/add-order", methods=["POST"])
@login_required
def create_order():
    data = request.get_json()

    # An order must belong to an existing batch.
    batch_id = data.get('batch_id')
    if not batch_id or not get_batch_by_id(batch_id):
        return jsonify({"message": "Please add a batch first, then choose it before adding orders"}), 400

    full_order = add_order(customer_name=data['customer_name'],
              customer_location=data['customer_location'],
              customer_cell=data['customer_cell'],
              no_of_chickens=data['chickens_ordered'],
              amount_paid=data['amount_paid'],
              batch_id=batch_id,
              created_by=session['user']['name']
    )

    log_audit(batch_id, 'order', full_order['id'], 'added',
              f"Added order for {full_order['customer_name']} — {full_order['no_of_chickens']} chickens, paid R{full_order['amount_paid']}",
              session['user']['name'])

    return jsonify({"message": "Order successfully added",
                    'data': full_order})

@order_routes.route("/api/orders", methods=["GET"])
@login_required
def get_orders():
    batch_id = request.args.get('batch_id')
    if batch_id:
        orders = get_orders_by_batch(int(batch_id))
    else:
        orders = get_orders_by_batch()  # Gets all orders
    return jsonify(orders)

@order_routes.route("/api/update-order/<int:order_id>", methods=["PUT"])
@login_required
def update_order(order_id):
    data = request.get_json()

    # Grab the current values first so we can record what actually changed.
    old = get_order_by_id(order_id)
    if not old:
        return jsonify({"message": "Order not found"}), 404

    conn = sqlite3.connect(config.DB_URL)
    cursor = conn.cursor()

    total_amount = config.CHICKEN_PRICE * data['chickens_ordered']
    outstanding_amount = total_amount - data['amount_paid']
    updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    updated_by = session['user']['name']

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

    changes = diff_changes([
        ("Name", old['customer_name'], data['customer_name']),
        ("Location", old['customer_location'], data['customer_location']),
        ("Cell", old['customer_cell'], data['customer_cell']),
        ("Chickens", old['no_of_chickens'], data['chickens_ordered']),
        ("Amount paid", old['amount_paid'], data['amount_paid']),
    ])
    log_audit(old['batch_id'], 'order', order_id, 'edited', changes, updated_by)

    return jsonify({"message": "Order updated successfully", "data": data})

@order_routes.route("/api/delete-order/<int:order_id>", methods=["DELETE"])
@admin_required
def remove_order(order_id):
    data = request.get_json() or {}
    reason = (data.get('reason') or '').strip()
    if not reason:
        return jsonify({"message": "Please give a reason for deleting"}), 400

    order = get_order_by_id(order_id)
    deleted = delete_order(order_id, reason, session['user']['name'])
    if not deleted:
        return jsonify({"message": "Order not found"}), 404

    log_audit(order['batch_id'], 'order', order_id, 'deleted',
              f"Deleted order for {order['customer_name']}. Reason: {reason}",
              session['user']['name'])

    return jsonify({"message": "Order deleted"})
