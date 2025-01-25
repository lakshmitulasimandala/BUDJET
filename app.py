import sqlite3
import atexit
from flask import Flask, render_template, request

# Create Flask instance
app = Flask(__name__)

# Database cleanup function to move transactions to history and reset the transactions table
def move_to_history():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Insert the transactions from 'transactions' to 'history'
    cursor.execute("INSERT INTO history (amount, category) SELECT amount, category FROM transactions")
    
    # Delete all transactions after moving them to history
    cursor.execute("DELETE FROM transactions")
    
    # Reset the auto-increment 'id' to 0, so it starts from 1 again
    cursor.execute("UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME='transactions'")
    
    conn.commit()
    conn.close()

# Register the move_to_history function to be called when the app stops
atexit.register(move_to_history)

# Home route to display the form and transaction table
@app.route('/')
def home():
    # Connect to the database and fetch transactions
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, amount, category FROM transactions")
    transactions = cursor.fetchall()
    conn.close()

    # Render the home page with the transactions
    return render_template('index.html', transactions=transactions)

# Route to handle form submission
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    # Get form data
    amount = request.form['amount']
    category = request.form['category']

    # Insert transaction into the database
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO transactions (amount, category) VALUES (?, ?)", (amount, category))
    conn.commit()
    conn.close()

    # Redirect back to the home page after adding the transaction
    return """
    <h1>Transaction Added: {amount} in category {category}</h1>
    <button onclick="window.location.href='/'">Back to Add Transactions</button>
    """.format(amount=amount, category=category)

# Route to view history
@app.route('/history')
def history():
    # Connect to the database and fetch history transactions
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, amount, category FROM history")
    history_transactions = cursor.fetchall()
    conn.close()

    # Render the history page
    return render_template('transactions.html', transactions=history_transactions)

if __name__ == "__main__":
    #app.run(debug=True)
    app.run(host='0.0.0.0', port=8000, debug=True)
