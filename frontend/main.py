"""
Application de gestion de bibliothèque avec interface graphique CustomTkinter
Communique avec une API REST backend sur localhost:5000
"""

import requests
import customtkinter as ctk
from typing import List, Dict, Optional, Any

# ==================== CONFIGURATION ====================
API_URL = "http://localhost:5000"

# ==================== FONCTIONS API ====================
def get_livres() -> List[Dict]:
    """Récupère tous les livres"""
    return requests.get(f"{API_URL}/livres").json()

def creer_livre(donnees: Dict) -> Dict:
    """Crée un nouveau livre"""
    return requests.post(f"{API_URL}/livres", json=donnees).json()

def chercher_livre(id_livre: Optional[int] = None, 
                titre: Optional[str] = None, 
                auteur: Optional[str] = None) -> List[Dict]:
    """Recherche des livres par ID, titre ou auteur"""
    params = []
    if id_livre:
        params.append(f"id_livre={id_livre}")
    if titre:
        params.append(f"titre={titre}")
    if auteur:
        params.append(f"auteur={auteur}")
    
    query = "&".join(params)
    url = f"{API_URL}/livres/rechercher?{query}"
    return requests.get(url).json()

def supprimer_livre(id_livre: int) -> Dict:
    """Supprime un livre par son ID"""
    return requests.delete(f"{API_URL}/livres/{id_livre}").json()

def modifier_livre(id_livre: int, donnees: Dict) -> Dict:
    """Modifie un livre existant"""
    return requests.put(f"{API_URL}/livres/{id_livre}", json=donnees).json()

# ==================== CLASSE PRINCIPALE ====================
class BibliothequeApp(ctk.CTk):
    """Application principale de gestion de bibliothèque"""
    
    # Constantes pour le tableau
    HEADERS = ["ID", "Titre", "Auteur", "Catégorie", "Année Publication", 
                "Quantité Disponible", "Statut", "Actions"]
    COLUMN_WIDTHS = [50, 200, 150, 100, 80, 80, 100, 100]
    
    def __init__(self):
        super().__init__()
        
        # Configuration de la fenêtre principale
        self.title("Gestion de Bibliothèque")
        self.geometry("900x1000")
        
        # Attributs
        self.lignes = []
        
        # Construction de l'interface
        self._create_widgets()
        
        # Chargement initial des données
        self.charger_livres()
    
    # ==================== CONSTRUCTION DE L'INTERFACE ====================
    def _create_widgets(self):
        """Crée tous les widgets de l'interface"""
        self._create_form_frame()
        self._create_search_frame()
        self._create_table()
    
    def _create_form_frame(self):
        """Crée le frame du formulaire d'ajout"""
        self.frame_formulaire = ctk.CTkFrame(self)
        self.frame_formulaire.pack(fill="x", padx=20, pady=10)
        
        # Champs de saisie
        self.entry_titre = ctk.CTkEntry(self.frame_formulaire, placeholder_text="Titre")
        self.entry_titre.grid(row=0, column=0, padx=5, pady=5)
        
        self.entry_auteur = ctk.CTkEntry(self.frame_formulaire, placeholder_text="Auteur")
        self.entry_auteur.grid(row=0, column=1, padx=5, pady=5)
        
        self.entry_categorie = ctk.CTkEntry(self.frame_formulaire, placeholder_text="Catégorie")
        self.entry_categorie.grid(row=0, column=2, padx=5, pady=5)
        
        self.entry_annee = ctk.CTkEntry(self.frame_formulaire, placeholder_text="Année Publication")
        self.entry_annee.grid(row=0, column=3, padx=5, pady=5)
        
        self.entry_quantite = ctk.CTkEntry(self.frame_formulaire, placeholder_text="Quantité Disponible")
        self.entry_quantite.grid(row=0, column=4, padx=5, pady=5)
        
        # ComboBox pour le statut
        self.combo_statut = ctk.CTkComboBox(
            self.frame_formulaire, 
            values=["Disponible", "Emprunté"]
        )
        self.combo_statut.grid(row=0, column=5, padx=5, pady=5)
        self.combo_statut.set("Disponible")
        
        # Bouton d'ajout
        self.button_ajouter = ctk.CTkButton(
            self.frame_formulaire, 
            text="Ajouter Livre", 
            command=self.ajouter_livre
        )
        self.button_ajouter.grid(row=0, column=6, padx=5, pady=5)
    
    def _create_search_frame(self):
        """Crée le frame de recherche"""
        self.frame_recherche = ctk.CTkFrame(self)
        self.frame_recherche.pack(fill="x", padx=20, pady=10)
        
        # Champ de recherche
        self.entry_recherche = ctk.CTkEntry(
            self.frame_recherche, 
            placeholder_text="ID, titre ou auteur...", 
            width=300
        )
        self.entry_recherche.grid(row=0, column=1, padx=5, pady=5)
        
        # Boutons de recherche
        self.button_rechercher = ctk.CTkButton(
            self.frame_recherche, 
            text="🔍 Rechercher", 
            command=self.rechercher_livre
        )
        self.button_rechercher.grid(row=0, column=2, padx=5, pady=5)
        
        self.button_reset = ctk.CTkButton(
            self.frame_recherche, 
            text="Réinitialiser", 
            command=self.charger_livres, 
            fg_color="gray"
        )
        self.button_reset.grid(row=0, column=3, padx=5, pady=5)
    
    def _create_table(self):
        """Crée le tableau d'affichage des livres"""
        self.frame_tableau = ctk.CTkScrollableFrame(self)
        self.frame_tableau.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Création des en-têtes
        for col, (titre, largeur) in enumerate(zip(self.HEADERS, self.COLUMN_WIDTHS)):
            label = ctk.CTkLabel(
                self.frame_tableau, 
                text=titre,
                font=("Arial", 14, "bold"),
                width=largeur
            )
            label.grid(row=0, column=col, padx=2, pady=5)
        
        # Stockage des lignes pour mise à jour
        self.lignes = []
    
    # ==================== GESTION DES LIVRES ====================
    def charger_livres(self):
        """Charge tous les livres depuis l'API"""
        try:
            livres = get_livres()
            self._remplir_tableau(livres)
        except Exception as e:
            print(f"❌ Erreur lors du chargement des livres: {e}")
    
    def ajouter_livre(self):
        """Ajoute un nouveau livre"""
        # Récupération des données
        titre = self.entry_titre.get()
        auteur = self.entry_auteur.get()
        categorie = self.entry_categorie.get()
        annee_publication = self.entry_annee.get()
        quantite_disponible = self.entry_quantite.get()
        statut = self.combo_statut.get()
        
        # Validation des champs
        if not all([titre, auteur, categorie, annee_publication, quantite_disponible, statut]):
            print("⚠️ Tous les champs sont requis")
            return
        
        # Validation des types numériques
        try:
            annee_int = int(annee_publication)
            quantite_int = int(quantite_disponible)
        except ValueError:
            print("❌ Année et Quantité doivent être des nombres")
            return
        
        # Création du livre
        donnees = {
            "titre": titre,
            "auteur": auteur,
            "categorie": categorie,
            "annee_publication": annee_int,
            "quantite_disponible": quantite_int,
            "statut": statut
        }
        
        try:
            resultat = creer_livre(donnees)
            print(f"✅ Livre ajouté: {resultat}")
            
            # Réinitialisation des champs
            self._clear_form_fields()
            
            # Rechargement de la liste
            self.charger_livres()
        except Exception as e:
            print(f"❌ Erreur lors de l'ajout du livre: {e}")
    
    def supprimer_livre(self, id_livre: int):
        """Supprime un livre par son ID"""
        try:
            resultat = supprimer_livre(id_livre)
            print(f"✅ Livre supprimé: {resultat}")
            self.charger_livres()
        except Exception as e:
            print(f"❌ Erreur lors de la suppression du livre: {e}")
    
    def rechercher_livre(self):
        """Recherche des livres par ID, titre ou auteur"""
        texte_recherche = self.entry_recherche.get().strip()
        
        if not texte_recherche:
            self.charger_livres()
            return
        
        try:
            # Tentative de recherche par ID (si c'est un nombre)
            id_livre = int(texte_recherche)
            results = chercher_livre(id_livre=id_livre)
            print(f"🔍 Recherche par ID: {id_livre}")
        except ValueError:
            # Recherche par titre et auteur
            results_titre = chercher_livre(titre=texte_recherche)
            results_auteur = chercher_livre(auteur=texte_recherche)
            
            # Fusion et dédoublonnement
            results = results_titre + results_auteur
            results = {livre['id_livre']: livre for livre in results}.values()
            results = list(results)
            
            print(f"🔍 Recherche par Titre/Auteur: {texte_recherche}")
        except Exception as e:
            print(f"❌ Erreur lors de la recherche: {e}")
            return
        
        self._remplir_tableau(results)
        print(f"📊 Résultats trouvés: {len(results)}")
    
    # ==================== MÉTHODES UTILITAIRES ====================
    def _remplir_tableau(self, livres: List[Dict]):
        """Remplit le tableau avec la liste des livres"""
        # Suppression des anciennes lignes
        for ligne in self.lignes:
            for widget in ligne:
                widget.destroy()
        self.lignes.clear()
        
        # Ajout de chaque livre dans le tableau
        for i, livre in enumerate(livres):
            ligne_widgets = []
            
            # ID
            label_id = ctk.CTkLabel(
                self.frame_tableau, 
                text=str(livre['id_livre']), 
                font=("Arial", 12),
                width=50
            )
            label_id.grid(row=i+1, column=0, padx=2, pady=5)
            ligne_widgets.append(label_id)
            
            # Titre
            label_titre = ctk.CTkLabel(
                self.frame_tableau, 
                text=livre['titre'], 
                font=("Arial", 12),
                width=200
            )
            label_titre.grid(row=i+1, column=1, padx=2, pady=5)
            ligne_widgets.append(label_titre)
            
            # Auteur
            label_auteur = ctk.CTkLabel(
                self.frame_tableau, 
                text=livre['auteur'], 
                font=("Arial", 12),
                width=150
            )
            label_auteur.grid(row=i+1, column=2, padx=2, pady=5)
            ligne_widgets.append(label_auteur)
            
            # Catégorie
            label_categorie = ctk.CTkLabel(
                self.frame_tableau, 
                text=livre['categorie'], 
                font=("Arial", 12),
                width=100
            )
            label_categorie.grid(row=i+1, column=3, padx=2, pady=5)
            ligne_widgets.append(label_categorie)
            
            # Année
            label_annee = ctk.CTkLabel(
                self.frame_tableau, 
                text=str(livre['annee_publication']), 
                font=("Arial", 12),
                width=80
            )
            label_annee.grid(row=i+1, column=4, padx=2, pady=5)
            ligne_widgets.append(label_annee)
            
            # Quantité
            label_quantite = ctk.CTkLabel(
                self.frame_tableau, 
                text=str(livre['quantite_disponible']), 
                font=("Arial", 12),
                width=80
            )
            label_quantite.grid(row=i+1, column=5, padx=2, pady=5)
            ligne_widgets.append(label_quantite)
            
            # Statut
            label_statut = ctk.CTkLabel(
                self.frame_tableau, 
                text=livre['statut'], 
                font=("Arial", 12),
                width=100
            )
            label_statut.grid(row=i+1, column=6, padx=2, pady=5)
            ligne_widgets.append(label_statut)
            
            # Bouton Supprimer
            button_supprimer = ctk.CTkButton(
                self.frame_tableau, 
                text="Supprimer", 
                command=lambda id_livre=livre['id_livre']: self.supprimer_livre(id_livre), 
                width=80
            )
            button_supprimer.grid(row=i+1, column=7, padx=2, pady=5)
            ligne_widgets.append(button_supprimer)
            
            self.lignes.append(ligne_widgets)
    
    def _clear_form_fields(self):
        """Réinitialise les champs du formulaire"""
        self.entry_titre.delete(0, 'end')
        self.entry_auteur.delete(0, 'end')
        self.entry_categorie.delete(0, 'end')
        self.entry_annee.delete(0, 'end')
        self.entry_quantite.delete(0, 'end')
        self.combo_statut.set("Disponible")

# ==================== POINT D'ENTRÉE ====================
if __name__ == "__main__":
    app = BibliothequeApp()
    app.mainloop()