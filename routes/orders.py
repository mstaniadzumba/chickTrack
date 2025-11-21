from flask import Blueprint, request, jsonify
from models.orders import add_order

order_routes = Blueprint('order_routes', __name__)

@order_routes.route("/api/add-order", methods=["POST"])
def create_order():
    data = request.get_json()
    full_order = add_order(customer_name=data['customer_name'],
              customer_location=data['customer_location'],
              customer_cell = data['customer_cell'],
              no_of_chickens=data['chickens_ordered'],
              amount_paid=data['amount_paid']
    )
    
    #if order successfull addded

    return jsonify({"message": "order successfully added",
                    'data':full_order})

    #else return order could notbe added, try again