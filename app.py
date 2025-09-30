from flask import Flask, url_for, render_template, redirect
import sqlite3


app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/orders')
def orders():
    return render_template('orders.html')

@app.route('/expenses')
def expenses():
    return render_template('expenses.html')



if __name__ == '__main__':
    app.run(debug=True)