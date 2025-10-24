import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()

try:
    c.execute("ALTER TABLE transactions ADD COLUMN main_category TEXT")
    print("Added column main_category (if it didn't exist).")
except Exception as e:
    print("ALTER failed may be column exists : ",e)

#for null values in main categories 

c.execute("UPDATE transactions SET main_category = 'Others' WHERE main_category IS NULL")
conn.commit()
conn.close()
print('Migration done.')