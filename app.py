import sqlite3
from datetime import date 
from flask import Flask, render_template, redirect,request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")



@app.route('/add_transaction', methods = ["POST"])
def add_transaction():
    amount = float(request.form['amount'])
    category = request.form['category']
    note = request.form.get('note','')
    today = date.today().strftime("%Y-%m-%d")

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO transactions (date, category, amount, note) VALUES (?, ?, ?, ?)''',
        (today, category, amount, note)
    )
    
    conn.commit()
    conn.close()

    return redirect("/history")



@app.route('/history')
def history():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM transactions ORDER by id")
    transactions = cursor.fetchall()

    total_amount = sum([t[3] for t in transactions])  # t[3] is the 'amount' column

    conn.close()
    return render_template('history.html',transactions = transactions, total_amount= total_amount)


@app.route('/delete_transaction/<int:trans_id>', methods = ["POST"])
def delete_transaction(trans_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("DELETE FROM transactions WHERE id = ?", (trans_id,))
    
    conn.commit()
    conn.close()

    return redirect("/history")



if __name__ == "__main__":
    app.run(debug=True)
