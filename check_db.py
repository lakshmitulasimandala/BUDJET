import sqlite3

conn = sqlite3.connect("F:/TULASI BSMS/All_Projects/BUDJET/database.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM transactions")
rows = cursor.fetchall()
print(rows)

conn.close()
