from flask import Flask, render_template, redirect, url_for, session
from datetime import timedelta
import config
from models.tables import db_init
from routes.expenses import expense_routes
from routes.orders import order_routes
from routes.dashboard import dashboard_routes
from routes.auth import auth_routes, create_admin_user, login_required, admin_required

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.permanent_session_lifetime = timedelta(days=14)

db_init()
create_admin_user()


# Register API routes

app.register_blueprint(expense_routes)
app.register_blueprint(order_routes)
app.register_blueprint(dashboard_routes)
app.register_blueprint(auth_routes)


@app.route("/")
def home():
    # Logo / root: go to the dashboard if logged in, otherwise to login.
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("index.html", user=session['user'])

@app.route("/login")
def login():
    # Already logged in? Skip straight to the dashboard.
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template("login.html")

@app.route("/orders")
@login_required
def show_orders():
    return render_template("orders.html", user=session['user'])

@app.route("/expenses")
@login_required
def expenses():
    return render_template("expenses.html", user=session['user'])

@app.route("/manage-users")
@admin_required
def manage_users():
    return render_template("manage_users.html", user=session['user'])

@app.route("/history")
@admin_required
def history():
    return render_template("history.html", user=session['user'])


if __name__ == "__main__":
    app.run(debug=True)
