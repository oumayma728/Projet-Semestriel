import flask
from flask import request, jsonify
from database.database import get_db
from models.livre import Livre
import re

# création de l'application Flask
app = flask.Flask(__name__)
# activation du mode debug pour le développement
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

# ============ CHATBOT ENDPOINT ============
@app.route('/chatbot', methods=['POST'])
def chatbot():
    """Endpoint pour le chatbot"""
    try:
        data = request.get_json()
        user_question = data.get('question', '').lower()
        response = process_question(user_question)
        return jsonify({'response': response}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def process_question(question):
    """Analyse la question de l'utilisateur et genere une reponse appropriee"""
    
    # 1. Détection des salutations
    if re.search(r'\b(hello|hi|hey|bonjour|salut|coucou)\b', question):
        return "Bonjour ! Je suis votre bibliothécaire virtuel. Comment puis-je vous aider ?\n\n📚 Recherche par :\n• Auteur (ex: 'Livres de Victor Hugo')\n• Titre (ex: 'Cherche Le Petit Prince')\n• Tous les livres (ex: 'Liste tous les livres')"
    
    # 2. Recherche par auteur
    if re.search(r'(auteur|écrit par|livres? de|œuvres? de|de qui)', question):
        patterns = [
            r'(?:livres? de|auteur|écrit par|de qui|par)\s+([a-zàâçéèêëîïôûùüÿñ\s-]+)$',
            r'([a-zàâçéèêëîïôûùüÿñ\s-]+)(?:\s+est l\'auteur|\s+a écrit)'
        ]
        author = None
        for pattern in patterns:
            match = re.search(pattern, question)
            if match:
                author = match.group(1).strip()
                break
        
        if author:
            # ✅ Appel direct à votre méthode Livre.search_livres()
            return search_by_author(author)
        return "Désolé, je n'ai pas pu identifier l'auteur. Essayez 'Livres de Victor Hugo'."
    
    # 3. Recherche par titre
    if re.search(r'(titre|appelé|intitulé|cherche.*livre|nom du livre)', question):
        patterns = [
            r'(?:titre|appelé|intitulé|cherche|livre|nom du livre)\s+(.+)$',
            r'le livre\s+(.+?)(?:\s+de|\s+par|\s*$)'
        ]
        title = None
        for pattern in patterns:
            match = re.search(pattern, question)
            if match:
                title = match.group(1).strip()
                break
        
        if title:
            # ✅ Appel direct à votre méthode Livre.search_livres()
            return search_by_title(title)
        return "Désolé, je n'ai pas pu identifier le titre. Essayez 'Cherche Le Petit Prince'."
    
    # 4. Afficher tous les livres
    if re.search(r'\b(tous les livres|affiche tous les livres|montre tous les livres|liste des livres|catalogue|liste livres)\b', question):
        # ✅ Appel direct à votre méthode Livre.get_all_livres()
        return get_all_books()
    
    # 5. Aide
    if re.search(r'\b(aide|help|que peux-tu faire|quelles sont tes fonctionnalités|commande)\b', question):
        return """🤖 **Fonctionnalités du bibliothécaire virtuel :**

**Astuce** : Utilisez l'onglet 'Gestion des livres' pour ajouter/modifier/supprimer des livres."""
    
    # 6. Fallback
    return "❓ Je n'ai pas compris. Essayez :\n• 'Livres de Victor Hugo' (par auteur)\n• 'Cherche Le Petit Prince' (par titre)\n• 'Liste tous les livres' (catalogue)\n• 'Aide' (liste des commandes)"

# ============ FONCTIONS CHATBOT QUI UTILISENT VOS MÉTHODES EXISTANTES ============

def search_by_author(author):
    """
    Utilise votre méthode Livre.search_livres() pour chercher par auteur
    """
    try:
        # ✅ RÉUTILISATION DE VOTRE MÉTHODE EXISTANTE
        # None, None, author signifie: pas d'id, pas de titre, recherche par auteur
        livres = Livre.search_livres(None, None, author)
        
        if livres and len(livres) > 0:
            result = f"📚 **{len(livres)} livre(s) trouvé(s) de '{author}' :**\n\n"
            for livre in livres:
                result += f"• **{livre['titre']}**\n"
                result += f"  ✍️ Auteur : {livre['auteur']}\n"
                result += f"  📂 Catégorie : {livre['categorie']}\n"
                result += f"  📅 Année : {livre['annee_publication']}\n"
                result += f"  📊 Disponible : {livre['quantite_disponible']} exemplaire(s)\n"
                result += f"  📌 Statut : {livre['statut']}\n\n"
            return result
        return f"Désolé, je n'ai trouvé aucun livre de '{author}'."
    
    except Exception as e:
        return f"❌ Erreur lors de la recherche : {str(e)}"

def search_by_title(title):
    """
    Utilise votre méthode Livre.search_livres() pour chercher par titre
    """
    try:
        # ✅ RÉUTILISATION DE VOTRE MÉTHODE EXISTANTE
        # None, title, None signifie: pas d'id, recherche par titre, pas d'auteur
        livres = Livre.search_livres(None, title, None)
        
        if livres and len(livres) > 0:
            result = f"📖 **{len(livres)} résultat(s) pour '{title}' :**\n\n"
            for livre in livres:
                result += f"• **{livre['titre']}**\n"
                result += f"  ✍️ {livre['auteur']}\n"
                result += f"  📂 Catégorie : {livre['categorie']}\n"
                result += f"  📅 {livre['annee_publication']}\n"
                result += f"  📊 {livre['quantite_disponible']} disponible(s)\n\n"
            return result
        return f"Désolé, je n'ai pas trouvé de livre avec le titre '{title}'."
    
    except Exception as e:
        return f"❌ Erreur lors de la recherche : {str(e)}"

def get_all_books():
    """
    Utilise votre méthode Livre.get_all_livres() pour obtenir tous les livres
    """
    try:
        # ✅ RÉUTILISATION DE VOTRE MÉTHODE EXISTANTE
        livres = Livre.get_all_livres()
        
        if livres and len(livres) > 0:
            result = f"📚 **Notre bibliothèque contient {len(livres)} livres :**\n\n"
            for livre in livres:
                result += f"• **{livre['titre']}** - {livre['auteur']} ({livre['annee_publication']})\n"
                result += f"  📂 {livre['categorie']} - 📊 {livre['quantite_disponible']} disponible(s)"
                result += f"\n  📌 Statut : {livre['statut']}\n\n"
            return result
        return "📚 La bibliothèque est vide pour le moment."
    
    except Exception as e:
        return f"❌ Erreur lors de la récupération des livres : {str(e)}"

if __name__ == '__main__':
    app.run()