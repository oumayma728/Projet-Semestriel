import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "bibliotheque.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

schema_path = os.path.join(BASE_DIR, "database", "schema.sql")

with open(schema_path, 'r', encoding='utf-8') as f:
    schema = f.read()

cursor.executescript(schema)

conn.commit()
conn.close()

print("Database initialized successfully.")