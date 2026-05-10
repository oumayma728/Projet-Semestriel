"""
Application de gestion de bibliothèque avec interface graphique CustomTkinter
Communique avec une API REST backend sur localhost:5000
Intégration d'un chatbot IA
"""

import requests
import customtkinter as ctk
from typing import List, Dict, Optional, Any
import threading
import re
from datetime import datetime

# ==================== CONFIGURATION ====================
API_URL = "http://localhost:5000"

# Configuration du thème
ctk.set_appearance_mode("dark")  # "dark" ou "light"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"

# ==================== FONCTIONS API ====================
def get_livres() -> List[Dict]:
    """Récupère tous les livres"""
    try:
        response = requests.get(f"{API_URL}/livres")
        return response.json() if response.status_code == 200 else []
    except Exception as e:
        print(f"Erreur : {e}")
        return []

def creer_livre(donnees: Dict) -> Dict:
    """Crée un nouveau livre"""
    response = requests.post(f"{API_URL}/livres", json=donnees)
    return response.json()

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
    url = f"{API_URL}/livres/recherche?{query}"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else []

def supprimer_livre(id_livre: int) -> Dict:
    """Supprime un livre par son ID"""
    response = requests.delete(f"{API_URL}/livres/{id_livre}")
    return response.json()

def modifier_livre(id_livre: int, donnees: Dict) -> Dict:
    """Modifie un livre existant"""
    response = requests.put(f"{API_URL}/livres/{id_livre}", json=donnees)
    return response.json()

def envoyer_message_chatbot(message: str) -> str:
    """Envoie un message au chatbot et retourne la réponse"""
    try:
        response = requests.post(
            f"{API_URL}/chatbot",
            json={"question": message},
            timeout=10
        )
        if response.status_code == 200:
            return response.json().get('response', "Désolé, je n'ai pas compris.")
        return f"Erreur {response.status_code}"
    except Exception as e:
        return f"❌ Erreur de connexion au serveur: {str(e)}"

# ==================== CLASSE CHATBOT ====================
class ChatbotFrame(ctk.CTkFrame):
    """Frame pour le chatbot"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self._create_widgets()
        
    def _create_widgets(self):
        """Crée l'interface du chatbot"""
        
        # En-tête
        header_frame = ctk.CTkFrame(self)
        header_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            header_frame,
            text="🤖 Assistant Bibliothèque Intelligente",
            font=("Arial", 18, "bold")
        ).pack()
        
        ctk.CTkLabel(
            header_frame,
            text="Posez-moi des questions sur les livres disponibles",
            font=("Arial", 12),
            text_color="gray"
        ).pack()
        
        # Zone de chat (scrollable)
        self.chat_frame = ctk.CTkScrollableFrame(self)
        self.chat_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Message de bienvenue
        self._add_message("bot", "👋 Bonjour ! Je suis votre bibliothécaire virtuel. Comment puis-je vous aider ?\n\n"
                           "📚 **Exemples de questions :**\n"
                           "• 'Livres de Victor Hugo'\n"
                           "• 'Cherche Le Petit Prince'\n"
                           "• 'Liste tous les livres'\n"
                           "• 'Aide'")
        
        # Zone de saisie
        input_frame = ctk.CTkFrame(self)
        input_frame.pack(fill="x", padx=10, pady=10)
        
        self.input_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Posez votre question ici...",
            font=("Arial", 12),
            height=40
        )
        self.input_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.input_entry.bind("<Return>", self._send_message)
        
        self.send_button = ctk.CTkButton(
            input_frame,
            text="Envoyer ✨",
            command=self._send_message,
            height=40,
            width=100
        )
        self.send_button.pack(side="right")
        
        # Suggestions rapides
        suggestions_frame = ctk.CTkFrame(self)
        suggestions_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        suggestions = [
            "📚 Livres de Victor Hugo",
            "🔍 Cherche Le Petit Prince",
            "📖 Liste tous les livres",
            "❓ Aide"
        ]
        
        for suggestion in suggestions:
            btn = ctk.CTkButton(
                suggestions_frame,
                text=suggestion,
                command=lambda s=suggestion: self._use_suggestion(s),
                fg_color="transparent",
                border_width=1,
                height=30,
                width=120
            )
            btn.pack(side="left", padx=5)
    
    def _add_message(self, sender: str, message: str):
        """Ajoute un message dans la zone de chat"""
        message_frame = ctk.CTkFrame(self.chat_frame)
        message_frame.pack(fill="x", padx=10, pady=5)
        
        # Style différent selon l'expéditeur
        if sender == "user":
            bg_color = "#1f538d"
            text_color = "white"
            align = "right"
            emoji = "👤"
        else:
            bg_color = "#2d2d2d"
            text_color = "#e0e0e0"
            align = "left"
            emoji = "🤖"
        
        ctk.CTkLabel(
            message_frame,
            text=f"{emoji} {message}",
            font=("Arial", 11),
            wraplength=500,
            justify="left"
        ).pack(fill="x", pady=5)
    
    def _use_suggestion(self, text: str):
        """Utilise une suggestion"""
        # Nettoyer l'emoji
        clean_text = re.sub(r'[📚🔍📖❓]', '', text).strip()
        self.input_entry.delete(0, "end")
        self.input_entry.insert(0, clean_text)
        self._send_message()
    
    def _send_message(self, event=None):
        """Envoie un message au chatbot"""
        user_message = self.input_entry.get().strip()
        if not user_message:
            return
        
        # Afficher le message de l'utilisateur
        self._add_message("user", user_message)
        self.input_entry.delete(0, "end")
        
        # Désactiver le bouton pendant le traitement
        self.send_button.configure(state="disabled", text="🤔 Réflexion...")
        
        # Envoyer dans un thread séparé
        thread = threading.Thread(target=self._get_bot_response, args=(user_message,))
        thread.daemon = True
        thread.start()
    
    def _get_bot_response(self, message: str):
        """Récupère la réponse du bot dans un thread"""
        response = envoyer_message_chatbot(message)
        
        # Mettre à jour l'UI dans le thread principal
        self.after(0, self._add_message, "bot", response)
        self.after(0, lambda: self.send_button.configure(state="normal", text="Envoyer ✨"))

# ==================== CLASSE PRINCIPALE ====================
class BibliothequeApp(ctk.CTk):
    """Application principale de gestion de bibliothèque"""
    
    # Constantes pour le tableau
    HEADERS = ["ID", "Titre", "Auteur", "Catégorie", "Année", "Quantité", "Statut", "Actions"]
    COLUMN_WIDTHS = [50, 200, 150, 100, 70, 80, 100, 100]
    
    def __init__(self):
        super().__init__()
        
        # Configuration de la fenêtre principale
        self.title("📚 Bibliothèque Intelligente")
        self.geometry("1200x800")
        
        # Attributs
        self.lignes = []
        
        # Construction de l'interface
        self._create_widgets()
        
        # Chargement initial des données
        self.charger_livres()
        
        # Vérification de la connexion au serveur
        self._check_server_connection()
    
    def _check_server_connection(self):
        """Vérifie si le serveur backend est accessible"""
        try:
            response = requests.get(f"{API_URL}/livres", timeout=2)
            if response.status_code == 200:
                print("✅ Connecté au serveur backend")
                self.title("📚 Bibliothèque Intelligente - Connecté")
            else:
                print("⚠️ Problème de connexion au serveur")
                self.title("📚 Bibliothèque Intelligente - ⚠️ Serveur indisponible")
        except:
            print("❌ Impossible de contacter le serveur")
            self.title("📚 Bibliothèque Intelligente - ❌ Serveur déconnecté")
    
    def _create_widgets(self):
        """Crée tous les widgets de l'interface avec onglets"""
        
        # Création du notebook (système d'onglets)
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Onglet 1 : Gestion des livres
        self.tab_livres = self.tabview.add("📚 Livres")
        self._create_livres_tab()
        
        # Onglet 2 : Chatbot
        self.tab_chatbot = self.tabview.add("🤖 Chatbot IA")
        self.chatbot = ChatbotFrame(self.tab_chatbot)
        self.chatbot.pack(fill="both", expand=True)
        
        # Onglet 3 : Statistiques (bonus)
        self.tab_stats = self.tabview.add("📊 Statistiques")
        self._create_stats_tab()
    
    def _create_livres_tab(self):
        """Crée l'onglet de gestion des livres"""
        
        # Frame formulaire
        self._create_form_frame(self.tab_livres)
        
        # Frame recherche
        self._create_search_frame(self.tab_livres)
        
        # Frame tableau
        self._create_table_frame(self.tab_livres)
    
    def _create_form_frame(self, parent):
        """Crée le frame du formulaire d'ajout"""
        form_frame = ctk.CTkFrame(parent)
        form_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(form_frame, text="➕ Ajouter un livre", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=7, pady=5)
        
        # Champs de saisie
        self.entry_titre = ctk.CTkEntry(form_frame, placeholder_text="Titre", width=180)
        self.entry_titre.grid(row=1, column=0, padx=5, pady=5)
        
        self.entry_auteur = ctk.CTkEntry(form_frame, placeholder_text="Auteur", width=150)
        self.entry_auteur.grid(row=1, column=1, padx=5, pady=5)
        
        self.entry_categorie = ctk.CTkEntry(form_frame, placeholder_text="Catégorie", width=120)
        self.entry_categorie.grid(row=1, column=2, padx=5, pady=5)
        
        self.entry_annee = ctk.CTkEntry(form_frame, placeholder_text="Année", width=80)
        self.entry_annee.grid(row=1, column=3, padx=5, pady=5)
        
        self.entry_quantite = ctk.CTkEntry(form_frame, placeholder_text="Quantité", width=80)
        self.entry_quantite.grid(row=1, column=4, padx=5, pady=5)
        
        self.combo_statut = ctk.CTkComboBox(
            form_frame, 
            values=["Disponible", "Emprunté"],
            width=100
        )
        self.combo_statut.grid(row=1, column=5, padx=5, pady=5)
        self.combo_statut.set("Disponible")
        
        self.button_ajouter = ctk.CTkButton(
            form_frame, 
            text="Ajouter", 
            command=self.ajouter_livre,
            width=100
        )
        self.button_ajouter.grid(row=1, column=6, padx=5, pady=5)
    
    def _create_search_frame(self, parent):
        """Crée le frame de recherche"""
        search_frame = ctk.CTkFrame(parent)
        search_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(search_frame, text="🔍 Rechercher", font=("Arial", 14, "bold")).pack(side="left", padx=10)
        
        self.entry_recherche = ctk.CTkEntry(
            search_frame, 
            placeholder_text="ID, titre ou auteur...", 
            width=250
        )
        self.entry_recherche.pack(side="left", padx=10)
        
        self.button_rechercher = ctk.CTkButton(
            search_frame, 
            text="Rechercher", 
            command=self.rechercher_livre,
            width=100
        )
        self.button_rechercher.pack(side="left", padx=5)
        
        self.button_reset = ctk.CTkButton(
            search_frame, 
            text="Réinitialiser", 
            command=self.charger_livres, 
            fg_color="gray",
            width=100
        )
        self.button_reset.pack(side="left", padx=5)
        
        # Label de statut
        self.status_label = ctk.CTkLabel(search_frame, text="", font=("Arial", 10))
        self.status_label.pack(side="right", padx=10)
    
    def _create_table_frame(self, parent):
        """Crée le frame du tableau"""
        table_frame = ctk.CTkFrame(parent)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Frame scrollable pour le tableau
        self.tableau_frame = ctk.CTkScrollableFrame(table_frame)
        self.tableau_frame.pack(fill="both", expand=True)
        
        # Création des en-têtes
        for col, (titre, largeur) in enumerate(zip(self.HEADERS, self.COLUMN_WIDTHS)):
            label = ctk.CTkLabel(
                self.tableau_frame, 
                text=titre,
                font=("Arial", 13, "bold"),
                width=largeur
            )
            label.grid(row=0, column=col, padx=2, pady=5)
        
        # Stockage des lignes
        self.lignes = []
    
    def _create_stats_tab(self):
        """Crée l'onglet des statistiques"""
        stats_frame = ctk.CTkScrollableFrame(self.tab_stats)
        stats_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Titre
        ctk.CTkLabel(
            stats_frame,
            text="📊 Statistiques de la Bibliothèque",
            font=("Arial", 20, "bold")
        ).pack(pady=20)
        
        # Frame pour les métriques
        metrics_frame = ctk.CTkFrame(stats_frame)
        metrics_frame.pack(fill="x", padx=20, pady=10)
        
        self.stats_labels = {}
        
        # Création des cartes de statistiques
        stats = [
            ("📚 Total livres", "0"),
            ("✍️ Auteurs uniques", "0"),
            ("📂 Catégories", "0"),
            ("✅ Livres disponibles", "0"),
            ("📖 Livres empruntés", "0")
        ]
        
        for i, (titre, valeur) in enumerate(stats):
            card = ctk.CTkFrame(metrics_frame)
            card.grid(row=i//3, column=i%3, padx=10, pady=10, sticky="nsew")
            
            ctk.CTkLabel(card, text=titre, font=("Arial", 14)).pack(pady=10)
            self.stats_labels[titre] = ctk.CTkLabel(card, text=valeur, font=("Arial", 24, "bold"))
            self.stats_labels[titre].pack(pady=10)
        
        # Bouton rafraîchir
        ctk.CTkButton(
            stats_frame,
            text="Rafraîchir les statistiques",
            command=self._update_stats,
            height=40
        ).pack(pady=20)
        
        # Mettre à jour les stats
        self._update_stats()
    
    def _update_stats(self):
        """Met à jour les statistiques"""
        try:
            livres = get_livres()
            
            if livres:
                total = len(livres)
                auteurs = len(set(l.get('auteur', '') for l in livres))
                categories = len(set(l.get('categorie', '') for l in livres))
                disponibles = sum(1 for l in livres if l.get('statut') == 'Disponible')
                empruntes = sum(1 for l in livres if l.get('statut') == 'Emprunté')
                
                self.stats_labels["📚 Total livres"].configure(text=str(total))
                self.stats_labels["✍️ Auteurs uniques"].configure(text=str(auteurs))
                self.stats_labels["📂 Catégories"].configure(text=str(categories))
                self.stats_labels["✅ Livres disponibles"].configure(text=str(disponibles))
                self.stats_labels["📖 Livres empruntés"].configure(text=str(empruntes))
        except Exception as e:
            print(f"Erreur stats: {e}")
    
    # ==================== GESTION DES LIVRES ====================
    def charger_livres(self):
        """Charge tous les livres depuis l'API"""
        try:
            livres = get_livres()
            self._remplir_tableau(livres)
            self.status_label.configure(text=f"📚 {len(livres)} livres chargés", text_color="green")
            self._update_stats()
        except Exception as e:
            self.status_label.configure(text=f"❌ Erreur: {e}", text_color="red")
    
    def ajouter_livre(self):
        """Ajoute un nouveau livre"""
        # Récupération des données
        titre = self.entry_titre.get()
        auteur = self.entry_auteur.get()
        categorie = self.entry_categorie.get()
        annee_publication = self.entry_annee.get()
        quantite_disponible = self.entry_quantite.get()
        statut = self.combo_statut.get()
        
        # Validation
        if not all([titre, auteur, categorie, annee_publication, quantite_disponible, statut]):
            self.status_label.configure(text="⚠️ Tous les champs sont requis", text_color="orange")
            return
        
        try:
            annee_int = int(annee_publication)
            quantite_int = int(quantite_disponible)
            
            if annee_int < 0 or annee_int > datetime.now().year:
                self.status_label.configure(text="❌ Année invalide", text_color="red")
                return
            if quantite_int < 0:
                self.status_label.configure(text="❌ Quantité invalide", text_color="red")
                return
                
        except ValueError:
            self.status_label.configure(text="❌ Année et Quantité doivent être des nombres", text_color="red")
            return
        
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
            if 'error' not in resultat:
                self.status_label.configure(text="✅ Livre ajouté avec succès", text_color="green")
                self._clear_form_fields()
                self.charger_livres()
            else:
                self.status_label.configure(text=f"❌ {resultat['error']}", text_color="red")
        except Exception as e:
            self.status_label.configure(text=f"❌ Erreur: {e}", text_color="red")
    
    def supprimer_livre(self, id_livre: int):
        """Supprime un livre par son ID"""
        try:
            resultat = supprimer_livre(id_livre)
            if 'error' not in resultat:
                self.status_label.configure(text=f"✅ Livre {id_livre} supprimé", text_color="green")
                self.charger_livres()
            else:
                self.status_label.configure(text=f"❌ {resultat['error']}", text_color="red")
        except Exception as e:
            self.status_label.configure(text=f"❌ Erreur: {e}", text_color="red")
    
    def rechercher_livre(self):
        """Recherche des livres par ID, titre ou auteur"""
        texte_recherche = self.entry_recherche.get().strip()
        
        if not texte_recherche:
            self.charger_livres()
            return
        
        try:
            # Recherche par ID
            id_livre = int(texte_recherche)
            results = chercher_livre(id_livre=id_livre)
            self._remplir_tableau(results)
            self.status_label.configure(text=f"🔍 {len(results)} résultat(s) trouvé(s)", text_color="blue")
        except ValueError:
            # Recherche par titre et auteur
            results_titre = chercher_livre(titre=texte_recherche)
            results_auteur = chercher_livre(auteur=texte_recherche)
            
            # Fusion et dédoublonnement
            results = {livre['id_livre']: livre for livre in results_titre + results_auteur}.values()
            results = list(results)
            
            self._remplir_tableau(results)
            self.status_label.configure(text=f"🔍 {len(results)} résultat(s) trouvé(s)", text_color="blue")
        except Exception as e:
            self.status_label.configure(text=f"❌ Erreur recherche: {e}", text_color="red")
    
    # ==================== MÉTHODES UTILITAIRES ====================
    def _remplir_tableau(self, livres: List[Dict]):
        """Remplit le tableau avec la liste des livres"""
        # Suppression des anciennes lignes
        for ligne in self.lignes:
            for widget in ligne:
                widget.destroy()
        self.lignes.clear()
        
        if not livres:
            # Message "Aucun résultat"
            label = ctk.CTkLabel(
                self.tableau_frame, 
                text="📭 Aucun livre trouvé",
                font=("Arial", 14),
                text_color="gray"
            )
            label.grid(row=1, column=0, columnspan=len(self.HEADERS), pady=20)
            return
        
        # Ajout de chaque livre
        for i, livre in enumerate(livres):
            ligne_widgets = []
            
            # ID
            label_id = ctk.CTkLabel(
                self.tableau_frame, 
                text=str(livre['id_livre']), 
                width=self.COLUMN_WIDTHS[0]
            )
            label_id.grid(row=i+1, column=0, padx=2, pady=2)
            ligne_widgets.append(label_id)
            
            # Titre
            label_titre = ctk.CTkLabel(
                self.tableau_frame, 
                text=livre['titre'][:30],  # Tronquer si trop long
                width=self.COLUMN_WIDTHS[1],
                wraplength=180
            )
            label_titre.grid(row=i+1, column=1, padx=2, pady=2)
            ligne_widgets.append(label_titre)
            
            # Auteur
            label_auteur = ctk.CTkLabel(
                self.tableau_frame, 
                text=livre['auteur'], 
                width=self.COLUMN_WIDTHS[2]
            )
            label_auteur.grid(row=i+1, column=2, padx=2, pady=2)
            ligne_widgets.append(label_auteur)
            
            # Catégorie
            label_categorie = ctk.CTkLabel(
                self.tableau_frame, 
                text=livre['categorie'], 
                width=self.COLUMN_WIDTHS[3]
            )
            label_categorie.grid(row=i+1, column=3, padx=2, pady=2)
            ligne_widgets.append(label_categorie)
            
            # Année
            label_annee = ctk.CTkLabel(
                self.tableau_frame, 
                text=str(livre['annee_publication']), 
                width=self.COLUMN_WIDTHS[4]
            )
            label_annee.grid(row=i+1, column=4, padx=2, pady=2)
            ligne_widgets.append(label_annee)
            
            # Quantité
            label_quantite = ctk.CTkLabel(
                self.tableau_frame, 
                text=str(livre['quantite_disponible']), 
                width=self.COLUMN_WIDTHS[5]
            )
            label_quantite.grid(row=i+1, column=5, padx=2, pady=2)
            ligne_widgets.append(label_quantite)
            
            # Statut avec couleur
            statut = livre['statut']
            statut_color = "#2ecc71" if statut == "Disponible" else "#e74c3c"
            label_statut = ctk.CTkLabel(
                self.tableau_frame, 
                text=statut, 
                width=self.COLUMN_WIDTHS[6],
                text_color=statut_color
            )
            label_statut.grid(row=i+1, column=6, padx=2, pady=2)
            ligne_widgets.append(label_statut)
            
            # Bouton Supprimer
            button_supprimer = ctk.CTkButton(
                self.tableau_frame, 
                text="🗑️", 
                command=lambda id_livre=livre['id_livre']: self.supprimer_livre(id_livre), 
                width=40,
                height=30,
                fg_color="#e74c3c",
                hover_color="#c0392b"
            )
            button_supprimer.grid(row=i+1, column=7, padx=2, pady=2)
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