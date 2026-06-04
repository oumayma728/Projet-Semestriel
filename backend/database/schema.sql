CREATE TABLE IF NOT EXISTS livres(
    id_livre INTEGER PRIMARY KEY AUTOINCREMENT,
    titre TEXT  NOT NULL,
    auteur TEXT  NOT NULL,
    categorie TEXT  NOT NULL,
    annee_publication INTEGER NOT NULL,
    quantite_disponible INTEGER NOT NULL ,
    statut TEXT NOT NULL 
)