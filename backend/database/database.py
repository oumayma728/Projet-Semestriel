import sqlite3
import os

# Get absolute path of this project folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "bibliotheque.db")

def get_db():
    return sqlite3.connect(DB_PATH)