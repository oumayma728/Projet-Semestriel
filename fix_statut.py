import sqlite3
conn = sqlite3.connect(r'C:\Users\oumai\Projet-Semestriel\backend\database\bibliotheque.db')
cursor = conn.cursor()
cursor.execute("DELETE FROM livres WHERE statut = 'disponible'")
conn.commit()
print(f"Done! {cursor.rowcount} books deleted.")
conn.close()