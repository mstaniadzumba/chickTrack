from flask import Blueprint, request, jsonify, session
from models.batch import add_batch, get_all_batches, get_batch_by_id
from models.orders import get_orders_by_batch, get_total_sold
from models.expenses import get_expenses_by_batch
from models.audit import log_audit, diff_changes, get_audit_by_batch
from routes.auth import login_required, admin_required
import sqlite3
import config
from datetime import datetime

dashboard_routes = Blueprint('dashboard_routes', __name__)

@dashboard_routes.route("/api/add-batch", methods=['POST'])
@admin_required
def create_batch():
    data = request.get_json()
    batch_id = add_batch(
        start_date=data['start_date'],
        chickens_bought=data['chickens_bought'],
        dead_chicken=data.get('dead_chicken', 0),
        created_by=session['user']['name']
    )
    log_audit(batch_id, 'batch', batch_id, 'added',
              f"Added batch — bought {data['chickens_bought']}, dead {data.get('dead_chicken', 0)}",
              session['user']['name'])
    return jsonify({"message": "Batch added successfully", "batch_id": batch_id})

@dashboard_routes.route("/api/update-batch/<int:batch_id>", methods=['PUT'])
@admin_required
def update_batch(batch_id):
    data = request.get_json()

    # Capture current values so we can record what changed.
    old = get_batch_by_id(batch_id)
    if not old:
        return jsonify({"message": "Batch not found"}), 404

    conn = sqlite3.connect(config.DB_URL)
    cursor = conn.cursor()

    # Extract month-year from start_date for batch naming
    date_obj = datetime.strptime(data['start_date'], '%Y-%m-%d')
    month = date_obj.strftime('%B %Y')

    live_chicken = data['chickens_bought'] - data.get('dead_chicken', 0)
    updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    updated_by = session['user']['name']

    cursor.execute("""
        UPDATE batch SET
        month=?, start_date=?, chickens_bought=?, dead_chicken=?, live_chicken=?, updated_by=?, updated_at=?
        WHERE id=?
    """, (month, data['start_date'], data['chickens_bought'], data.get('dead_chicken', 0),
          live_chicken, updated_by, updated_at, batch_id))

    conn.commit()
    conn.close()

    changes = diff_changes([
        ("Start date", old['start_date'], data['start_date']),
        ("Chickens bought", old['chickens_bought'], data['chickens_bought']),
        ("Dead chickens", old['dead_chicken'], data.get('dead_chicken', 0)),
    ])
    log_audit(batch_id, 'batch', batch_id, 'edited', changes, updated_by)

    return jsonify({"message": "Batch updated successfully", "batch_id": batch_id})

@dashboard_routes.route("/api/batches", methods=['GET'])
@login_required
def get_batches():
    batches = get_all_batches()
    return jsonify(batches)

@dashboard_routes.route("/api/dashboard/<int:batch_id>", methods=['GET'])
@login_required
def get_dashboard_data(batch_id):
    batch = get_batch_by_id(batch_id)
    if not batch:
        return jsonify({"message": "Batch not found"}), 404

    orders = get_orders_by_batch(batch_id)
    expenses = get_expenses_by_batch(batch_id)

    # Live chickens = bought - dead - sold. Computed here so it always matches the
    # orders, rather than relying on a stored value that can drift.
    sold = get_total_sold(batch_id)
    bought = batch['chickens_bought']
    dead = batch['dead_chicken']
    live = bought - dead - sold

    # Deleted (crossed-out) records don't count towards the money totals.
    live_orders = [o for o in orders if not o.get('is_deleted')]
    live_expenses = [e for e in expenses if not e.get('is_deleted')]
    total_revenue = sum(order['total_amount'] for order in live_orders)
    total_expenses = sum(expense['expense_amount'] for expense in live_expenses)

    return jsonify({
        "batch": batch,
        "bought": bought,
        "dead": dead,
        "sold": sold,
        "live": live,
        "total_orders": len(live_orders),
        "total_revenue": total_revenue,
        "total_expenses": total_expenses,
        "profit": total_revenue - total_expenses
    })

@dashboard_routes.route("/api/history", methods=['GET'])
@dashboard_routes.route("/api/history/<int:batch_id>", methods=['GET'])
@admin_required
def get_history(batch_id=None):
    return jsonify(get_audit_by_batch(batch_id))
