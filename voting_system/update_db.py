import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("delete from users where voter_id='jay0310'")

conn.commit()
conn.close()

print("Column added successfully")
# import sqlite3

# conn = sqlite3.connect("database.db")
# cursor = conn.cursor()

# # 1. Create new table with voter_id as PRIMARY KEY
# cursor.execute("""
# CREATE TABLE users_new (
#     voter_id TEXT PRIMARY KEY,
#     name TEXT,
#     email TEXT,
#     password TEXT
# )
# """)

# # 2. Copy data from old table
# cursor.execute("""
# INSERT INTO users_new (voter_id, name, email, password)
# SELECT voter_id, name, email, password FROM users
# """)

# # 3. Drop old table
# cursor.execute("DROP TABLE users")

# 4. Rename new table
# cursor.execute("ALTER TABLE users_new RENAME TO users")
cursor.execute("ALTER TABLE votes ADD COLUMN voter_id TEXT")

conn.commit()
conn.close()

print("voter_id is now PRIMARY KEY")
# import sqlite3

# conn = sqlite3.connect("database.db")
# cursor = conn.cursor()

# cursor.execute("DELETE FROM votes")

# conn.commit()
# conn.close()

# print("All votes deleted successfully!")