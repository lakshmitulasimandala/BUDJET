import sqlite3

# Connect to the database (or create it if it doesn't exist)
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Drop the existing tables if they exist
cursor.execute("DROP TABLE IF EXISTS transactions")
cursor.execute("DROP TABLE IF EXISTS history")

# Create the transactions table with auto-incrementing id
cursor.execute("""
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL,
    category TEXT
)
""")

# Create the history table to store past transactions
cursor.execute("""
CREATE TABLE history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL,
    category TEXT
)
""")

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database setup complete with auto-incrementing 'id' for both 'transactions' and 'history'.")
