import sqlite3
import os

db_path = "backend/wvs_storage.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(users);")
columns = cursor.fetchall()
for col in columns:
    print(col)
conn.close()
