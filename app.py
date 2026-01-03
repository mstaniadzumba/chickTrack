from flask import Flask, render_template
from models.tables import db_init
from routes.expenses import expense_routes
from routes.orders import order_routes
from routes.dashboard import dashboard_routes

app = Flask(__name__)

#Register API routes

app.register_blueprint(expense_routes)
app.register_blueprint(order_routes)
app.register_blueprint(dashboard_routes)


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/orders")
def show_orders():
    return render_template("orders.html")

@app.route("/expenses")
def expenses():
    return render_template("expenses.html")


if __name__ == "__main__":
    db_init()
    app.run(debug=True)
