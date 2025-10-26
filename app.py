import sqlite3
import io
import csv 
from flask import make_response
from datetime import date 
from flask import Flask, render_template, redirect,request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")



@app.route('/add_transaction', methods = ["POST"])
def add_transaction():
    amount = float(request.form['amount'])
    main_category = request.form['main_category']
    category = request.form['category']
    note = request.form.get('note','')
    today = date.today().strftime("%Y-%m-%d")

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO transactions (date,main_category , category, amount, note) VALUES (?, ?, ?, ?, ?)''',
        (today, main_category, category, amount, note)
    )
    
    conn.commit()
    conn.close()

    return redirect("/history")



@app.route('/history')
def history():
    keyword = request.args.get('keyword', '')
    sort_order = request.args.get('sort_order','asc').upper()
    main_category = request.args.get('main_category','')
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    query = ("SELECT * FROM transactions")
    params = []

    if main_category:  # if user selected a category
        query += " WHERE main_category = ?"
        params.append(main_category)

    if keyword:
        if params:
            query += (" AND (category LIKE ? OR note LIKE ?)")
        else:
            query += (" WHERE (category LIKE ? OR note LIKE ?)")
        params.extend([f"%{keyword}%", f"%{keyword}%"])

    query += " ORDER BY DATE " + ("ASC" if sort_order == "ASC" else "DESC")

    cursor.execute(query,params)
    transactions = cursor.fetchall()

    total_amount = sum([t[3] for t in transactions])  # t[3] is the 'amount' column

    cursor.execute('''
        SELECT main_category, SUM(amount)
        FROM transactions
        GROUP BY main_category
    ''')
    summary_data = cursor.fetchall()

    categories = [row[0] for row in summary_data]

    conn.close()
    return render_template('history.html',
                           transactions = transactions, 
                           total_amount= total_amount,
                           keyword = keyword, 
                           selected_category = main_category,
                           summary_data = summary_data,
                           categories = categories)


@app.route('/delete_transaction/<int:trans_id>', methods = ["POST"])
def delete_transaction(trans_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("DELETE FROM transactions WHERE id = ?", (trans_id,))
    
    conn.commit()
    conn.close()

    return redirect("/history")


@app.route('/edit/<int:trans_id>')
def edit_transaction(trans_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("SELECT * FROM transactions WHERE id = ?", (trans_id,))
    transaction = c.fetchone()

    conn.close()

    return render_template('edit.html', transaction = transaction)


@app.route('/update_transaction/<int:trans_id>', methods = ["POST"])
def update_transaction(trans_id):
    main_category = request.form['main_category']
    category = request.form['category']
    amount = float(request.form['amount'])
    note = request.form.get('note',"")

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE transactions 
        SET main_category = ?, category = ?, amount = ?, note = ? 
        WHERE id = ?               
    ''', (main_category, category, amount, note, trans_id))

    conn.commit()
    conn.close()

    return redirect('/history')


@app.route('/download_csv')
def download_csv():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions")
    data = cursor.fetchall()
    conn.close()

    # Write CSV data into a memory buffer
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Date', 'Category', 'Amount', 'Note', 'Main Category'])
    writer.writerows(data)

    # Get CSV content as string
    csv_data = output.getvalue()
    output.close()

    # Create Flask response
    response = make_response(csv_data)
    response.headers["Content-Disposition"] = "attachment; filename=transactions.csv"
    response.headers["Content-Type"] = "text/csv"
    return response


if __name__ == "__main__":
    app.run(debug=True)
