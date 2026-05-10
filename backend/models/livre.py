import sqlite3
import os
from database.database import get_db

class Livre:
    def __init__(self, id_livre, titre, auteur, categorie, annee_publication, quantite_disponible, statut):
        self.id_livre = id_livre
        self.titre = titre
        self.auteur = auteur
        self.categorie = categorie
        self.annee_publication = annee_publication
        self.quantite_disponible = quantite_disponible
        self.statut = statut

    def to_dict(self):
        return {
            'id_livre': self.id_livre,
            'titre': self.titre,
            'auteur': self.auteur,
            'categorie': self.categorie,
            'annee_publication': self.annee_publication,
            'quantite_disponible': self.quantite_disponible,
            'statut': self.statut
        }
    
    @staticmethod
    def creer_livre(titre, auteur, categorie, annee_publication, quantite_disponible, statut):
        connection = None
        try:
            connection = get_db()
            cursor = connection.cursor()
            cursor.execute('''
                INSERT INTO livre (titre, auteur, categorie, annee_publication, quantite_disponible, statut)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (titre, auteur, categorie, annee_publication, quantite_disponible, statut))
            connection.commit()
            new_id = cursor.lastrowid
            return new_id
        except Exception as e:
            raise Exception(f"Error creating livre: {e}")
        finally:
            if connection:
                connection.close()
        
    @staticmethod
    def get_all_livres():
        connection = None

        try:
            connection =get_db()
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM livre')
            rows = cursor.fetchall()
            livres = []
            for row in rows:
                livre = Livre(*row)
                livres.append(livre.to_dict())
            return livres
        except Exception as e:
            raise Exception(f"Error fetching livres: {e}")
        finally:            
            if connection:
                connection.close()

    @staticmethod
    def search_livres(id_livre, titre, auteur):
        connection = None
        try:
            connection = get_db()
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM livre WHERE id_livre = ? OR titre LIKE ? OR auteur LIKE ?',  (id_livre, f'%{titre}%', f'%{auteur}%'))
            rows = cursor.fetchall()
            if rows:
                livres = []
                for row in rows:
                    livre = Livre(*row)
                    livres.append(livre.to_dict())
                return livres
            else:
                return None
        except Exception as e:
            raise Exception(f"Error fetching livres: {e}")
        finally:
            if connection:
                connection.close()


    @staticmethod
    def update_livre(id_livre, titre, auteur, categorie, annee_publication, quantite_disponible, statut):
        connection = None
        try: 
            connection = get_db()
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM livre WHERE id_livre = ?', (id_livre,))
            row = cursor.fetchone()
            if not row:
                raise Exception("Livre not found")
            else :
                cursor.execute('''
                UPDATE livre
                SET titre = ?, auteur = ?, categorie = ?, annee_publication = ?, quantite_disponible = ?, statut = ?
                WHERE id_livre = ?
            ''', (titre, auteur, categorie, annee_publication, quantite_disponible, statut, id_livre))
            connection.commit()
        except Exception as e:
            raise Exception(f"Error updating livre: {e}")
        finally:
            if connection:
                connection.close()

    @staticmethod
    def delete_livre(id_livre):
        connection = None
        try:
            connection = get_db()
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM livre WHERE id_livre = ?', (id_livre,))
            row = cursor.fetchone()
            if not row:
                raise Exception("Livre not found")
            else:
                cursor.execute('DELETE FROM livre WHERE id_livre = ?', (id_livre,))
                connection.commit()
        except Exception as e:
            raise Exception(f"Error deleting livre: {e}")
        finally:
            if connection:
                connection.close()
        
