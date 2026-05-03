import sqlite3
import os

db_path = "database.db"

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. Recreate 'users' table
cursor.execute("CREATE TABLE users_clean (voter_id TEXT PRIMARY KEY, name TEXT, email TEXT)")
try:
    cursor.execute("INSERT INTO users_clean (voter_id, name, email) SELECT voter_id, name, email FROM users")
except sqlite3.OperationalError:
    pass

# 2. Recreate 'votes' table
cursor.execute("CREATE TABLE votes_clean (id INTEGER PRIMARY KEY AUTOINCREMENT, candidate TEXT, voter_id TEXT)")
try:
    cursor.execute("INSERT INTO votes_clean (id, candidate, voter_id) SELECT id, candidate, voter_id FROM votes")
except sqlite3.OperationalError:
    pass

# 3. Settings table 
cursor.execute("CREATE TABLE IF NOT EXISTS settings_clean (key TEXT PRIMARY KEY, value TEXT)")
try:
    cursor.execute("INSERT INTO settings_clean (key, value) SELECT key, value FROM settings")
except sqlite3.OperationalError:
    pass

# Drop all
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for table in tables:
    table_name = table[0]
    if table_name not in ('sqlite_sequence', 'users_clean', 'votes_clean', 'settings_clean'):
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

# Rename clean tables
cursor.execute("ALTER TABLE users_clean RENAME TO users")
cursor.execute("ALTER TABLE votes_clean RENAME TO votes")
cursor.execute("ALTER TABLE settings_clean RENAME TO settings")

conn.commit()
conn.close()

print("Database cleaned up successfully.")
