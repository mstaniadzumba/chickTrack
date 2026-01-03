from flask import Blueprint, request, jsonify
from models.expenses import add_expense, get_expenses_by_batch
import sqlite3
import config
from datetime import datetime

expense_routes = Blueprint('expenses_routes', __name__)

@expense_routes.route("/api/add-expense", methods=['POST'])
def create_expense():
    data = request.get_json()
    add_expense(expense_name=data['expense_name'],
                expense_amount=data['expense_amount'],
                expense_date=data['expense_date'],
                comments=data['comments'],
                batch_id=data.get('batch_id'),
                created_by=data.get('created_by'))
    
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

@expense_routes.route("/api/update-expense/<int:expense_id>", methods=["PUT"])
def update_expense(expense_id):
    data = request.get_json()
    
    # Update expense in database
    conn = sqlite3.connect(config.DB_URL)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    updated_by = data.get('created_by')
    
    cursor.execute("""
        UPDATE expenses SET 
        expense_name=?, expense_amount=?, expense_date=?, comments=?,
        updated_by=?, updated_at=?
        WHERE id=?
    """, (data['expense_name'], data['expense_amount'], data['expense_date'], 
          data['comments'], updated_by, updated_at, expense_id))
    
    # Get updated record
    cursor.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
    updated_expense = dict(cursor.fetchone())
    
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Expense updated successfully", "data": updated_expense})