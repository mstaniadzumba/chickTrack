import sqlite3
import config

def db_init():
    conn = sqlite3.connect(config.DB_URL)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
                   id Integer PRIMARY KEY,
                   customer_name TEXT NOT NULL,
                   customer_location TEXT NOT NULL,
                   no_of_chickens Integer NOT NULL,
                   amount_paid Integer NOT NULL,
                   outstanding_amount Integer NOT NULL)
                   ''')
    

    cursor.execute('''CREATE TABLE IF NOT EXISTS expenses (
                   id Integer PRIMARY KEY,
                   expense_name TEXT NOT NULL,
                   expense_amount Integer NOT NULL)
                   ''')
    
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS batch (
                   id Integer PRIMARY KEY,
                   month TEXT NOT NULL,
                   start_date TEXT NOT NULL,
                   chickens_bought Integer NOT NULL,
                   dead_chicken Integer NOT NULL,
                   live_chicken Integer NOT NULL,
                   current_week Integer NOT NULL)
                   ''')



    conn.commit()
    conn.close()