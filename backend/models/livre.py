from database.database import get_db

class Livre:

    @staticmethod
    def get_all_livres():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM livres")
        return cursor.fetchall()

    @staticmethod
    def creer_livre(titre, auteur, categorie, annee_publication, quantite_disponible, statut):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO livres (titre, auteur, categorie, annee_publication, quantite_disponible, statut)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (titre, auteur, categorie, annee_publication, quantite_disponible, statut))
        conn.commit()

    @staticmethod
    def delete_livre(id_livre):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM livres WHERE id = ?", (id_livre,))
        conn.commit()

    @staticmethod
    def search_livres(id_livre=None, titre=None, auteur=None):
        conn = get_db()
        cursor = conn.cursor()

        query = "SELECT * FROM livres WHERE 1=1"
        params = []

        if id_livre:
            query += " AND id = ?"
            params.append(id_livre)

        if titre:
            query += " AND titre LIKE ?"
            params.append(f"%{titre}%")

        if auteur:
            query += " AND auteur LIKE ?"
            params.append(f"%{auteur}%")

        cursor.execute(query, params)
        return cursor.fetchall()

    @staticmethod
    def update_livre(id_livre, data):
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE livres
            SET titre=?, auteur=?, categorie=?, annee_publication=?, quantite_disponible=?, statut=?
            WHERE id=?
        """, (
            data["titre"],
            data["auteur"],
            data["categorie"],
            data["annee_publication"],
            data["quantite_disponible"],
            data["statut"],
            id_livre
        ))

        conn.commit()