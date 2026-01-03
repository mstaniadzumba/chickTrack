from flask import Blueprint, request, jsonify
from models.batch import add_batch, get_all_batches, get_batch_by_id
from models.orders import get_orders_by_batch
from models.expenses import get_expenses_by_batch

dashboard_routes = Blueprint('dashboard_routes', __name__)

@dashboard_routes.route("/api/add-batch", methods=['POST'])
def create_batch():
    data = request.get_json()
    batch_id = add_batch(
        start_date=data['start_date'],
        chickens_bought=data['chickens_bought'],
        dead_chicken=data.get('dead_chicken', 0),
        created_by=data.get('created_by')
    )
    return jsonify({"message": "Batch added successfully", "batch_id": batch_id})

@dashboard_routes.route("/api/batches", methods=['GET'])
def get_batches():
    batches = get_all_batches()
    return jsonify(batches)

@dashboard_routes.route("/api/dashboard/<int:batch_id>", methods=['GET'])
def get_dashboard_data(batch_id):
    batch = get_batch_by_id(batch_id)
    orders = get_orders_by_batch(batch_id)
    expenses = get_expenses_by_batch(batch_id)
    
    # Calculate totals
    total_revenue = sum(order['total_amount'] for order in orders)
    total_expenses = sum(expense['expense_amount'] for expense in expenses)
    
    return jsonify({
        "batch": batch,
        "total_orders": len(orders),
        "total_revenue": total_revenue,
        "total_expenses": total_expenses,
        "profit": total_revenue - total_expenses
    })
