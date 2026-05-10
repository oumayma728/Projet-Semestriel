import flask
from flask import request, jsonify
from database.database import get_db
from models.livre import Livre
#creation de l'application Flask
app = flask.Flask(__name__)
#activation du mode debug pour le developpement
app.config["DEBUG"] = True

@app.route('/livres', methods=['GET'])
def get_livres():
    try:
        livres = Livre.get_all_livres()
        return jsonify(livres), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/livres', methods=['POST'])
def cree_livre():
    try: 
        #verification des champs requis
        #recuperation des donnees du corps de la requete
        donnees = request.get_json()

        required_fields = ['titre', 'auteur', 'categorie', 'annee_publication', 'quantite_disponible', 'statut']
        for field in required_fields:
            if field not in donnees:
                return jsonify({'error': f'Missing field: {field}'}), 400
        Livre.creer_livre(
            donnees['titre'],
            donnees['auteur'],
            donnees['categorie'],
            donnees['annee_publication'],
            donnees['quantite_disponible'],
            donnees['statut']
        )
        return jsonify({'message': 'Livre created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/livres/<int:id_livre>', methods=['DELETE'])
def delete_livre(id_livre):
    try:
        Livre.delete_livre(id_livre)
        return jsonify({'message': 'Livre deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/livres/recherche', methods=['GET'])
def search_livres():
    try:
        #car les donnees de recherche sont envoyees en tant que parametres de requete
        id_livre = request.args.get('id_livre')
        titre = request.args.get('titre')
        auteur = request.args.get('auteur')
        livres = Livre.search_livres(id_livre, titre, auteur)
        return jsonify(livres), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/livres/<int:id_livre>', methods=['PUT'])
def update_livre(id_livre):
    try:
        donnees = request.get_json()
        Livre.update_livre(id_livre, donnees)
        return jsonify({'message': 'Livre updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
if __name__ == '__main__':
    app.run()