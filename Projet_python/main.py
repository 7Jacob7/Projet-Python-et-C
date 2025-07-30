"""
Système de Gestion des Présences - Fichier Principal
Point d'entrée de l'application pour gérer les présences dans un club ou TD.
"""

import tkinter as tk
from tkinter import messagebox
import os
import sys
from ui_manager import AttendanceApp

def create_data_directory():
    """Créer le répertoire data s'il n'existe pas"""
    if not os.path.exists('data'):
        os.makedirs('data')
        print("Répertoire 'data' créé.")

def main():
    """Fonction principale pour lancer l'application"""
    try:
        # Créer le répertoire de données
        create_data_directory()
        
        # Créer la fenêtre principale
        root = tk.Tk()
        
        # Configurer l'apparence de la fenêtre
        root.title("Système de Gestion des Présences - Club/TD")
        root.geometry("1200x800")
        root.minsize(800, 600)
        root.resizable(True, True)
        
        # Icône de la fenêtre (optionnel)
        root.iconname("Présences")
        
        # Centrer la fenêtre
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (1200 // 2)
        y = (root.winfo_screenheight() // 2) - (800 // 2)
        root.geometry(f"1200x800+{x}+{y}")
        
        # Créer l'application
        app = AttendanceApp(root)
        
        # Gérer la fermeture de l'application
        def on_closing():
            """Gérer la fermeture propre de l'application"""
            if messagebox.askokcancel("Quitter", "Voulez-vous vraiment quitter l'application?"):
                try:
                    app.file_manager.save_all_data()
                    print("Données sauvegardées avec succès.")
                except Exception as e:
                    print(f"Erreur lors de la sauvegarde: {e}")
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Démarrer la boucle principale
        print("Démarrage de l'application de gestion des présences...")
        root.mainloop()
        
    except Exception as e:
        print(f"Erreur critique lors du démarrage: {e}")
        messagebox.showerror("Erreur", f"Impossible de démarrer l'application:\n{e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
