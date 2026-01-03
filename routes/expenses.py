from flask import Blueprint, request, jsonify
from models.expenses import add_expense, get_expenses_by_batch
import sqlite3
import config
from datetime import datetime

expense_routes = Blueprint('expenses_routes', __name__)

@expense_routes.route("/api/add-expense", methods=['POST'])
def create_expense():
    data = request.get_json()
    
    conn = sqlite3.connect(config.DB_URL)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    from datetime import datetime
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute(""" INSERT INTO expenses (expense_name, expense_amount, expense_date, comments, batch_id, created_by, created_at)
                   VALUES (?,?,?,?,?,?,?)
                   """, (data['expense_name'], data['expense_amount'], data['expense_date'], 
                         data.get('comments'), data.get('batch_id'), data.get('created_by'), created_at))
    
    expense_id = cursor.lastrowid
    
    # Get the created expense with ID
    cursor.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
    new_expense = dict(cursor.fetchone())
    
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Expense successfully added", 'data': new_expense})

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
    try:
        data = request.get_json()
        print(f"Updating expense {expense_id} with data: {data}")
        
        # Update expense in database
        conn = sqlite3.connect(config.DB_URL)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check if expense exists
        cursor.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
        existing = cursor.fetchone()
        if not existing:
            return jsonify({"message": "Expense not found"}), 404
        
        print(f"Found existing expense: {dict(existing)}")
        
        # Simple update without tracking columns first
        updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        updated_by = data.get('created_by')  # This is actually the current user updating
        
        cursor.execute("""
            UPDATE expenses SET 
            expense_name=?, expense_amount=?, expense_date=?, comments=?, updated_by=?, updated_at=?
            WHERE id=?
        """, (data['expense_name'], data['expense_amount'], data['expense_date'], 
              data.get('comments', ''), updated_by, updated_at, expense_id))
        
        print(f"Updated {cursor.rowcount} rows")
        
        # Get updated record
        cursor.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
        updated_expense = cursor.fetchone()
        
        if updated_expense:
            updated_expense = dict(updated_expense)
            print(f"Updated expense: {updated_expense}")
        
        conn.commit()
        conn.close()
        
        return jsonify({"message": "Expense updated successfully", "data": updated_expense})
    except Exception as e:
        print(f"Error updating expense: {str(e)}")
        return jsonify({"message": f"Error updating expense: {str(e)}"}), 500