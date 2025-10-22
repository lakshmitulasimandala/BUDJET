import sqlite3

conn = sqlite3.connect("database.db")
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    category TEXT NOT NULL,
    amount REAL NOT NULL,
    note TEXT
)
''')

conn.commit()
conn.close()

print("! Database and table created successfully !")
