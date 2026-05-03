import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    password TEXT
)
""")

cursor.execute("""
CREATE TABLE votes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate TEXT
)
""")

conn.commit()
conn.close()

print("Database created")
