from flask import Blueprint, request, jsonify, session
from models.expenses import add_expense, get_expenses_by_batch, get_expense_by_id, delete_expense
from models.batch import get_batch_by_id
from models.audit import log_audit, diff_changes
from routes.auth import login_required, admin_required
import sqlite3
import config
from datetime import datetime

expense_routes = Blueprint('expenses_routes', __name__)

@expense_routes.route("/api/add-expense", methods=['POST'])
@login_required
def create_expense():
    data = request.get_json()

    # An expense must belong to an existing batch.
    batch_id = data.get('batch_id')
    if not batch_id or not get_batch_by_id(batch_id):
        return jsonify({"message": "Please add a batch first, then choose it before adding expenses"}), 400

    conn = sqlite3.connect(config.DB_URL)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    created_by = session['user']['name']

    cursor.execute(""" INSERT INTO expenses (expense_name, expense_amount, expense_date, comments, batch_id, created_by, created_at)
                   VALUES (?,?,?,?,?,?,?)
                   """, (data['expense_name'], data['expense_amount'], data['expense_date'],
                         data.get('comments'), batch_id, created_by, created_at))

    expense_id = cursor.lastrowid

    cursor.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
    new_expense = dict(cursor.fetchone())

    conn.commit()
    conn.close()

    log_audit(batch_id, 'expense', new_expense['id'], 'added',
              f"Added expense: {new_expense['expense_name']} — R{new_expense['expense_amount']}",
              created_by)

    return jsonify({"message": "Expense successfully added", 'data': new_expense})

@expense_routes.route("/api/expenses", methods=["GET"])
@login_required
def get_expenses():
    batch_id = request.args.get('batch_id')
    if batch_id:
        expenses = get_expenses_by_batch(int(batch_id))
    else:
        expenses = get_expenses_by_batch()  # Gets all expenses
    return jsonify(expenses)

@expense_routes.route("/api/update-expense/<int:expense_id>", methods=["PUT"])
@login_required
def update_expense(expense_id):
    try:
        data = request.get_json()

        conn = sqlite3.connect(config.DB_URL)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
        existing = cursor.fetchone()
        if not existing:
            conn.close()
            return jsonify({"message": "Expense not found"}), 404
        existing = dict(existing)

        updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        updated_by = session['user']['name']

        cursor.execute("""
            UPDATE expenses SET
            expense_name=?, expense_amount=?, expense_date=?, comments=?, updated_by=?, updated_at=?
            WHERE id=?
        """, (data['expense_name'], data['expense_amount'], data['expense_date'],
              data.get('comments', ''), updated_by, updated_at, expense_id))

        cursor.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
        updated_expense = dict(cursor.fetchone())

        conn.commit()
        conn.close()

        changes = diff_changes([
            ("Description", existing['expense_name'], data['expense_name']),
            ("Amount", existing['expense_amount'], data['expense_amount']),
            ("Date", existing['expense_date'], data['expense_date']),
            ("Comments", existing['comments'] or '', data.get('comments', '') or ''),
        ])
        log_audit(existing['batch_id'], 'expense', expense_id, 'edited', changes, updated_by)

        return jsonify({"message": "Expense updated successfully", "data": updated_expense})
    except Exception as e:
        return jsonify({"message": f"Error updating expense: {str(e)}"}), 500

@expense_routes.route("/api/delete-expense/<int:expense_id>", methods=["DELETE"])
@admin_required
def remove_expense(expense_id):
    data = request.get_json() or {}
    reason = (data.get('reason') or '').strip()
    if not reason:
        return jsonify({"message": "Please give a reason for deleting"}), 400

    expense = get_expense_by_id(expense_id)
    deleted = delete_expense(expense_id, reason, session['user']['name'])
    if not deleted:
        return jsonify({"message": "Expense not found"}), 404

    log_audit(expense['batch_id'], 'expense', expense_id, 'deleted',
              f"Deleted expense: {expense['expense_name']}. Reason: {reason}",
              session['user']['name'])

    return jsonify({"message": "Expense deleted"})
