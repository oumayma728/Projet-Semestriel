import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "bibliotheque.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS livre (
        id_livre INTEGER PRIMARY KEY AUTOINCREMENT,
        titre TEXT NOT NULL,
        auteur TEXT NOT NULL,
        categorie TEXT NOT NULL,
        annee_publication INTEGER NOT NULL,
        quantite_disponible INTEGER NOT NULL,
        statut TEXT NOT NULL
    )
''')

conn.commit()
conn.close()

print("Table 'livre' créée avec succès !")