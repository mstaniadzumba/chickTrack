from flask import Blueprint, request, jsonify
from models.orders import add_order, get_orders_by_batch

order_routes = Blueprint('order_routes', __name__)

@order_routes.route("/api/add-order", methods=["POST"])
def create_order():
    data = request.get_json()
    full_order = add_order(customer_name=data['customer_name'],
              customer_location=data['customer_location'],
              customer_cell = data['customer_cell'],
              no_of_chickens=data['chickens_ordered'],
              amount_paid=data['amount_paid'],
              batch_id=data.get('batch_id')
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