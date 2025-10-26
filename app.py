import sqlite3
import io
import csv 
import os
import matplotlib.pyplot as plt
from flask import make_response, send_file
from datetime import date 
from flask import Flask, render_template, redirect,request
from flask import make_response
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics


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
    sort_order = request.args.get('sort_order', 'asc')  # keep as 'asc'/'desc'
    main_category = request.args.get('main_category', '')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    query = "SELECT * FROM transactions"
    params = []

    filters = []
    if main_category:
        filters.append("main_category = ?")
        params.append(main_category)

    if keyword:
        filters.append("(category LIKE ? OR note LIKE ? OR main_category LIKE ?)")
        params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])

    if filters:
        query += " WHERE " + " AND ".join(filters)

    # Sort by date
    if sort_order.lower() == 'asc':
        query += " ORDER BY date ASC"
    else:
        query += " ORDER BY date DESC"

    cursor.execute(query, params)
    transactions = cursor.fetchall()

    total_amount = sum([t[3] for t in transactions])

    cursor.execute('SELECT main_category, SUM(amount) FROM transactions GROUP BY main_category')
    summary_data = cursor.fetchall()

    categories = [row[0] for row in summary_data]

    conn.close()

    return render_template(
        'history.html',
        transactions=transactions,
        total_amount=total_amount,
        keyword=keyword,
        selected_category=main_category,
        summary_data=summary_data,
        categories=categories,
        sort_order=sort_order  # pass current sort order to template
    )


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


pdfmetrics.registerFont(TTFont('PatrickHand', 'static/fonts/PatrickHand-Regular.ttf'))


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



@app.route('/download_pdf')
def download_pdf():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Fetch transactions
    cursor.execute("SELECT * FROM transactions")
    transactions_raw = cursor.fetchall()
    transactions = [
        {"id": t[0], "date": t[1], "category": t[2], "amount": t[3], "note": t[4], "main_category": t[5]}
        for t in transactions_raw
    ]

    # Fetch summary
    cursor.execute('SELECT main_category, SUM(amount) FROM transactions GROUP BY main_category')
    summary_data_raw = cursor.fetchall()
    summary = [[row[0], row[1]] for row in summary_data_raw]

    conn.close()

    # PDF setup
    pdf_path = "budjet_report.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title', parent=styles['Heading1'], fontName='PatrickHand', fontSize=24, textColor=colors.HexColor('#0A5C36')
    )
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontName='PatrickHand', fontSize=12)

    # Title
    elements.append(Paragraph("Budjet Report", title_style))
    elements.append(Spacer(1, 12))

    # Transactions Table
    if transactions:
        table_data = [["ID", "Date", "Category", "Amount", "Note", "Main Category"]]
        for i, t in enumerate(transactions, start=1):  # start numbering at 1
            table_data.append([i, t["date"], t["category"], f"₹{t['amount']:.2f}", t["note"], t["main_category"]])

        # Table styling
        t_style = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#FFFBF2')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#0A5C36')),
            ('FONTNAME', (0,0), (-1,-1), 'PatrickHand'),
            ('FONTSIZE', (0,0), (-1,-1), 12),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#14452F')),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ])
        trans_table = Table(table_data, hAlign='CENTER')
        trans_table.setStyle(t_style)

        elements.append(Paragraph("Transactions", styles['Heading2']))
        elements.append(trans_table)
        elements.append(Spacer(1, 20))

    # Summary Table
    if summary:
        summary_table_data = [["Main Category", "Total Spent (₹)"]] + summary
        s_style = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#FFFBF2')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#0A5C36')),
            ('FONTNAME', (0,0), (-1,-1), 'PatrickHand'),
            ('FONTSIZE', (0,0), (-1,-1), 12),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#14452F')),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ])
        sum_table = Table(summary_table_data, hAlign='CENTER')
        sum_table.setStyle(s_style)
        elements.append(Paragraph("Summary by Category", styles['Heading2']))
        elements.append(sum_table)


    # Generate pie chart
    if summary:
        labels = [row[0] for row in summary]
        sizes = [row[1] for row in summary]
        plt.figure(figsize=(4,4))
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', colors=['#0A5C36','#14452F','#18392B','#1D2E28'])
        plt.tight_layout()
        plt.savefig('static/chart.png', transparent=True)  # save in static so Flask can access if needed
        plt.close()

    # Insert chart image into PDF
    elements.append(Spacer(1, 12))  # optional spacing
    elements.append(RLImage('static/chart.png', width=300, height=300))



    # Build PDF
    doc.build(elements)

    return send_file(pdf_path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
