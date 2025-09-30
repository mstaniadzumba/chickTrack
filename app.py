from flask import Flask, url_for, render_template, redirect
import sqlite3
from models import orders


app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/orders')
def show_orders():
    return render_template('orders.html')

@app.route('/expenses')
def expenses():
    return render_template('expenses.html')



if __name__ == '__main__':
    orders.db_init()
    app.run(debug=True)
   
    