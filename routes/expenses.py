from flask import Blueprint, request, jsonify
from models.expenses import add_expense

expense_routes = Blueprint('expenses_routes', __name__)

@expense_routes.route("/api/add-expense", methods=['POST'])
def create_expense():
    data = request.get_json()
    print(data)
    add_expense(expense_name=data['expense_name'],
                expense_amount=data['expense_amount'])
    
    return jsonify({"message": "Expense successfully added"})