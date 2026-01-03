from flask import Blueprint, request, jsonify
from models.expenses import add_expense, get_expenses_by_batch

expense_routes = Blueprint('expenses_routes', __name__)

@expense_routes.route("/api/add-expense", methods=['POST'])
def create_expense():
    data = request.get_json()
    add_expense(expense_name=data['expense_name'],
                expense_amount=data['expense_amount'],
                expense_date=data['expense_date'],
                comments=data['comments'],
                batch_id=data.get('batch_id'))
    
    return jsonify({"message": "Expense successfully added",
                    'data':data})

@expense_routes.route("/api/expenses", methods=["GET"])
def get_expenses():
    batch_id = request.args.get('batch_id')
    if batch_id:
        expenses = get_expenses_by_batch(int(batch_id))
    else:
        expenses = get_expenses_by_batch()  # Gets all expenses
    return jsonify(expenses)