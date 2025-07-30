"""
Gestionnaire de l'Interface Utilisateur
Module principal pour l'interface graphique de l'application
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date
import calendar
from student_manager import StudentManager
from attendance_manager import AttendanceManager, AttendanceStatus
from statistics_manager import StatisticsManager
from file_manager import FileManager

class AttendanceApp:
    """Application principale de gestion des présences"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Système de Gestion des Présences - Club/TD")
        
        # Initialiser les gestionnaires
        self.student_manager = StudentManager()
        self.attendance_manager = AttendanceManager()
        self.statistics_manager = StatisticsManager(self.student_manager, self.attendance_manager)
        self.file_manager = FileManager(self.student_manager, self.attendance_manager)
        
        # Variables pour l'interface
        self.current_td_name = tk.StringVar(value="TD/Cours")
        self.selected_date = tk.StringVar(value=date.today().isoformat())
        
        # Charger les données
        self.file_manager.load_all_data()
        
        # Configurer l'interface
        self.setup_styles()
        self.create_main_interface()
        
        # Configurer la sauvegarde automatique
        self.file_manager.setup_auto_save(self.root)
        
        # Observer les changements
        self.student_manager.add_observer(self)
        self.attendance_manager.add_observer(self)
    
    def setup_styles(self):
        """Configurer les styles de l'interface"""
        style = ttk.Style()
        
        # Configurer le thème
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')
        elif 'alt' in available_themes:
            style.theme_use('alt')
        
        # Couleurs personnalisées
        colors = {
            'primary': '#2E86AB',      # Bleu principal
            'secondary': '#A23B72',    # Violet
            'success': '#38A169',      # Vert
            'warning': '#D69E2E',      # Orange
            'error': '#E53E3E',        # Rouge
            'light': '#F7FAFC',        # Gris très clair
            'dark': '#2D3748',         # Gris foncé
            'accent': '#805AD5'        # Violet clair
        }
        
        # Styles personnalisés avec couleurs
        style.configure('Title.TLabel', 
                       font=('Arial', 18, 'bold'), 
                       foreground=colors['primary'])
        style.configure('Subtitle.TLabel', 
                       font=('Arial', 12, 'bold'), 
                       foreground=colors['dark'])
        style.configure('Info.TLabel', 
                       font=('Arial', 10), 
                       foreground=colors['dark'])
        style.configure('Success.TLabel', 
                       foreground=colors['success'], 
                       font=('Arial', 10, 'bold'))
        style.configure('Warning.TLabel', 
                       foreground=colors['warning'], 
                       font=('Arial', 10, 'bold'))
        style.configure('Error.TLabel', 
                       foreground=colors['error'], 
                       font=('Arial', 10, 'bold'))
        
        # Styles pour les boutons
        style.configure('Primary.TButton',
                       font=('Arial', 10, 'bold'))
        style.configure('Success.TButton',
                       font=('Arial', 10))
        style.configure('Warning.TButton',
                       font=('Arial', 10))
        
        # Styles pour les frames
        style.configure('Card.TFrame', 
                       relief='solid', 
                       borderwidth=1)
        
        # Configuration des notebooks
        style.configure('TNotebook.Tab', 
                       padding=[20, 10],
                       font=('Arial', 10, 'bold'))
    
    def create_main_interface(self):
        """Créer l'interface principale"""
        # Configurer les couleurs de la fenêtre
        self.root.configure(bg='#f0f0f0')
        
        # Créer la barre de menu
        self.create_menu_bar()
        
        # Frame principal avec scrollbar
        self.main_canvas = tk.Canvas(self.root, bg='#f0f0f0')
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.main_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.main_canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        )
        
        self.main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.main_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Placement des éléments scrollables
        self.main_canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        self.scrollbar.pack(side="right", fill="y")
        
        # En-tête
        self.create_header(self.scrollable_frame)
        
        # Notebook pour les onglets avec couleurs
        self.notebook = ttk.Notebook(self.scrollable_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Créer les onglets
        self.create_students_tab()
        self.create_attendance_tab()
        self.create_statistics_tab()
        self.create_settings_tab()
        
        # Barre de statut
        self.create_status_bar(self.scrollable_frame)
        
        # Bind pour la molette de la souris
        self.bind_mousewheel()
        
        # Mettre à jour l'affichage initial
        self.update_status_bar()
    
    # Méthodes pour la barre de menu
    def new_file(self):
        """Créer un nouveau fichier"""
        if messagebox.askyesno("Nouveau", "Êtes-vous sûr de vouloir créer un nouveau fichier? Les données non sauvegardées seront perdues."):
            self.student_manager.students.clear()
            self.attendance_manager.sessions.clear()
            self.refresh_all_data()
            self.update_status("Nouveau fichier créé")
    
    def open_file(self):
        """Ouvrir un fichier"""
        file_path = filedialog.askopenfilename(
            title="Ouvrir un fichier de données",
            filetypes=[("Fichiers JSON", "*.json"), ("Tous les fichiers", "*.*")]
        )
        if file_path:
            if self.file_manager.import_data(file_path):
                self.refresh_all_data()
                self.update_status("Fichier ouvert avec succès")
            else:
                messagebox.showerror("Erreur", "Impossible d'ouvrir le fichier")
    
    def save_as(self):
        """Sauvegarder sous"""
        file_path = filedialog.asksaveasfilename(
            title="Sauvegarder sous",
            defaultextension=".json",
            filetypes=[("Fichiers JSON", "*.json"), ("Tous les fichiers", "*.*")]
        )
        if file_path:
            if self.file_manager.export_data(file_path):
                self.update_status("Fichier sauvegardé avec succès")
            else:
                messagebox.showerror("Erreur", "Impossible de sauvegarder le fichier")
    
    def quit_application(self):
        """Quitter l'application"""
        if messagebox.askyesno("Quitter", "Voulez-vous vraiment quitter l'application?"):
            try:
                self.file_manager.save_all_data()
                self.file_manager.stop_auto_save(self.root)
            except:
                pass
            self.root.quit()
            self.root.destroy()
    
    def create_new_session(self):
        """Créer une nouvelle session de présence"""
        self.notebook.select(1)  # Aller à l'onglet présences
        self.set_today_date()
        self.load_attendance_session()
    
    def generate_report(self):
        """Générer un rapport complet"""
        file_path = filedialog.asksaveasfilename(
            title="Sauvegarder le rapport",
            defaultextension=".json",
            filetypes=[("Fichiers JSON", "*.json"), ("Fichiers texte", "*.txt")]
        )
        if file_path:
            if file_path.endswith('.txt'):
                self.generate_text_report(file_path)
            else:
                if self.statistics_manager.export_statistics_report(file_path):
                    self.update_status("Rapport généré avec succès")
                    messagebox.showinfo("Succès", f"Rapport sauvegardé dans :\n{file_path}")
                else:
                    messagebox.showerror("Erreur", "Impossible de générer le rapport")
    
    def generate_text_report(self, file_path):
        """Générer un rapport au format texte"""
        try:
            overall_stats = self.statistics_manager.get_overall_statistics()
            all_students = self.statistics_manager.calculate_all_student_statistics()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("RAPPORT DE PRÉSENCES - SYSTÈME DE GESTION\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"Date de génération: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"Nom du TD/Cours: {self.current_td_name.get()}\n\n")
                
                # Statistiques générales
                f.write("STATISTIQUES GÉNÉRALES\n")
                f.write("-" * 30 + "\n")
                f.write(f"Nombre total d'étudiants: {overall_stats['total_students']}\n")
                f.write(f"Nombre total de sessions: {overall_stats['total_sessions']}\n")
                f.write(f"Taux de présence moyen: {overall_stats['average_attendance_rate']:.1f}%\n")
                f.write(f"Taux de ponctualité moyen: {overall_stats['average_punctuality_rate']:.1f}%\n\n")
                
                # Meilleur étudiant
                if overall_stats['best_student']:
                    best = overall_stats['best_student']
                    f.write(f"Meilleur étudiant: {best.student_name} ({best.attendance_rate:.1f}%)\n\n")
                
                # Détails par étudiant
                f.write("DÉTAILS PAR ÉTUDIANT\n")
                f.write("-" * 30 + "\n")
                for i, student in enumerate(sorted(all_students, key=lambda x: x.attendance_rate, reverse=True), 1):
                    f.write(f"{i:2d}. {student.student_name}\n")
                    f.write(f"    Sessions: {student.total_sessions}\n")
                    f.write(f"    Présent: {student.present_count} | Absent: {student.absent_count} | Retard: {student.late_count}\n")
                    f.write(f"    Taux présence: {student.attendance_rate:.1f}% | Taux ponctualité: {student.punctuality_rate:.1f}%\n\n")
                
                # Étudiants nécessitant attention
                if overall_stats['needs_attention']:
                    f.write("ÉTUDIANTS NÉCESSITANT ATTENTION (< 70%)\n")
                    f.write("-" * 40 + "\n")
                    for student in overall_stats['needs_attention']:
                        f.write(f"- {student.student_name}: {student.attendance_rate:.1f}%\n")
            
            self.update_status("Rapport texte généré avec succès")
            messagebox.showinfo("Succès", f"Rapport sauvegardé dans :\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de générer le rapport: {e}")
    
    def show_about(self):
        """Afficher les informations sur l'application"""
        about_text = """Système de Gestion des Présences
Version 1.0.0

Application développée pour la gestion des présences
dans un club ou TD universitaire.

Fonctionnalités:
• Gestion des étudiants
• Marquage des présences
• Statistiques et analyses
• Sauvegarde automatique
• Export/Import de données
• Génération de rapports

Développé avec Python et Tkinter"""
        
        messagebox.showinfo("À propos", about_text)
    
    def show_help(self):
        """Afficher l'aide"""
        help_text = """GUIDE D'UTILISATION

1. GESTION DES ÉTUDIANTS
   - Utilisez l'onglet "Gestion Étudiants"
   - Cliquez sur "Ajouter Étudiant" pour ajouter un nouvel étudiant
   - Double-cliquez sur un étudiant pour le modifier
   - Sélectionnez et cliquez "Supprimer" pour retirer un étudiant

2. MARQUAGE DES PRÉSENCES
   - Allez dans l'onglet "Présences"
   - Sélectionnez ou saisissez une date
   - Cliquez "Charger Session" pour voir les étudiants
   - Double-cliquez sur un étudiant pour changer son statut
   - Utilisez le clic droit pour plus d'options

3. CONSULTATION DES STATISTIQUES
   - Onglet "Statistiques" pour voir les analyses
   - Plusieurs sous-onglets disponibles
   - Génération de graphiques et rapports

4. SAUVEGARDE
   - Sauvegarde automatique toutes les 5 minutes
   - Menu "Fichier" > "Sauvegarder" pour sauvegarde manuelle
   - Utilisez "Outils" > "Sauvegarde" pour créer une sauvegarde complète"""
        
        # Créer une fenêtre d'aide
        help_window = tk.Toplevel(self.root)
        help_window.title("Guide d'utilisation")
        help_window.geometry("600x500")
        help_window.transient(self.root)
        
        text_widget = tk.Text(help_window, wrap=tk.WORD, padx=20, pady=20)
        scrollbar = ttk.Scrollbar(help_window, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)
        
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_menu_bar(self):
        """Créer la barre de menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Fichier
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Nouveau", command=self.new_file)
        file_menu.add_command(label="Ouvrir", command=self.open_file)
        file_menu.add_separator()
        file_menu.add_command(label="Sauvegarder", command=self.quick_save)
        file_menu.add_command(label="Sauvegarder sous...", command=self.save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exporter", command=self.export_data)
        file_menu.add_command(label="Importer", command=self.import_data)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.quit_application)
        
        # Menu Édition
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Édition", menu=edit_menu)
        edit_menu.add_command(label="Ajouter Étudiant", command=self.add_student_dialog)
        edit_menu.add_command(label="Supprimer Étudiant", command=self.delete_student)
        edit_menu.add_separator()
        edit_menu.add_command(label="Créer Session", command=self.create_new_session)
        
        # Menu Outils
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Outils", menu=tools_menu)
        tools_menu.add_command(label="Statistiques", command=lambda: self.notebook.select(2))
        tools_menu.add_command(label="Générer Rapport", command=self.generate_report)
        tools_menu.add_separator()
        tools_menu.add_command(label="Sauvegarde", command=self.create_backup)
        tools_menu.add_command(label="Restaurer", command=self.restore_backup)
        
        # Menu Aide
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aide", menu=help_menu)
        help_menu.add_command(label="À propos", command=self.show_about)
        help_menu.add_command(label="Guide d'utilisation", command=self.show_help)
    
    def bind_mousewheel(self):
        """Lier la molette de la souris pour le défilement"""
        def _on_mousewheel(event):
            self.main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            self.main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            self.main_canvas.unbind_all("<MouseWheel>")
        
        self.main_canvas.bind('<Enter>', _bind_to_mousewheel)
        self.main_canvas.bind('<Leave>', _unbind_from_mousewheel)
    
    def create_header(self, parent):
        """Créer l'en-tête de l'application"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Titre
        title_label = ttk.Label(header_frame, text="Système de Gestion des Présences", 
                               style='Title.TLabel')
        title_label.pack(side=tk.LEFT)
        
        # Informations du TD
        td_frame = ttk.Frame(header_frame)
        td_frame.pack(side=tk.RIGHT)
        
        ttk.Label(td_frame, text="Nom du TD/Cours:", style='Info.TLabel').pack(side=tk.LEFT)
        td_entry = ttk.Entry(td_frame, textvariable=self.current_td_name, width=20)
        td_entry.pack(side=tk.LEFT, padx=(5, 0))
        
        # Boutons d'actions rapides
        actions_frame = ttk.Frame(header_frame)
        actions_frame.pack(side=tk.RIGHT, padx=(20, 0))
        
        ttk.Button(actions_frame, text="Sauvegarder", 
                  command=self.quick_save).pack(side=tk.LEFT, padx=2)
        ttk.Button(actions_frame, text="Actualiser", 
                  command=self.refresh_all_data).pack(side=tk.LEFT, padx=2)
    
    def create_students_tab(self):
        """Créer l'onglet de gestion des étudiants"""
        students_frame = ttk.Frame(self.notebook)
        self.notebook.add(students_frame, text="Gestion Étudiants")
        
        # Frame pour les contrôles
        controls_frame = ttk.LabelFrame(students_frame, text="Actions", padding="10")
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Boutons d'actions avec couleurs
        buttons_frame = ttk.Frame(controls_frame)
        buttons_frame.pack(fill=tk.X)
        
        ttk.Button(buttons_frame, text="➕ Ajouter Étudiant", 
                  command=self.add_student_dialog, style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="✏️ Modifier", 
                  command=self.edit_student_dialog, style='Success.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="🗑️ Supprimer", 
                  command=self.delete_student, style='Warning.TButton').pack(side=tk.LEFT, padx=5)
        
        # Barre de recherche
        search_frame = ttk.Frame(controls_frame)
        search_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(search_frame, text="Rechercher:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_students)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=(5, 0))
        
        # Liste des étudiants
        list_frame = ttk.LabelFrame(students_frame, text="Liste des Étudiants", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview pour afficher les étudiants
        columns = ('ID', 'Nom', 'Prénom', 'Email', 'Groupe', 'Date création')
        self.students_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configuration des colonnes
        for col in columns:
            self.students_tree.heading(col, text=col, command=lambda c=col: self.sort_students(c))
            self.students_tree.column(col, width=120)
        
        # Scrollbars
        students_scrollbar_v = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.students_tree.yview)
        students_scrollbar_h = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.students_tree.xview)
        self.students_tree.configure(yscrollcommand=students_scrollbar_v.set, xscrollcommand=students_scrollbar_h.set)
        
        # Placement
        self.students_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        students_scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
        students_scrollbar_h.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind double-click pour édition
        self.students_tree.bind('<Double-1>', lambda e: self.edit_student_dialog())
        
        # Charger les données initiales
        self.refresh_students_list()
    
    def create_attendance_tab(self):
        """Créer l'onglet de marquage des présences"""
        attendance_frame = ttk.Frame(self.notebook)
        self.notebook.add(attendance_frame, text="Présences")
        
        # Frame supérieur pour les contrôles
        top_frame = ttk.Frame(attendance_frame)
        top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Sélection de date
        date_frame = ttk.LabelFrame(top_frame, text="Sélection de Date", padding="10")
        date_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        ttk.Label(date_frame, text="Date:").pack(anchor=tk.W)
        date_entry = ttk.Entry(date_frame, textvariable=self.selected_date, width=12)
        date_entry.pack(anchor=tk.W, pady=2)
        
        ttk.Button(date_frame, text="Aujourd'hui", 
                  command=self.set_today_date).pack(fill=tk.X, pady=2)
        ttk.Button(date_frame, text="Charger Session", 
                  command=self.load_attendance_session).pack(fill=tk.X, pady=2)
        
        # Actions rapides avec couleurs
        actions_frame = ttk.LabelFrame(top_frame, text="Actions Rapides", padding="10")
        actions_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        quick_actions = ttk.Frame(actions_frame)
        quick_actions.pack(fill=tk.X)
        
        ttk.Button(quick_actions, text="✅ Tous Présents", 
                  command=lambda: self.mark_all_students(AttendanceStatus.PRESENT), 
                  style='Success.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_actions, text="❌ Tous Absents", 
                  command=lambda: self.mark_all_students(AttendanceStatus.ABSENT),
                  style='Warning.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_actions, text="💾 Sauvegarder Session", 
                  command=self.save_attendance_session,
                  style='Primary.TButton').pack(side=tk.LEFT, padx=2)
        
        # Liste des présences
        list_frame = ttk.LabelFrame(attendance_frame, text="Marquage des Présences", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview pour les présences
        attendance_columns = ('ID', 'Nom', 'Prénom', 'Statut', 'Heure', 'Notes')
        self.attendance_tree = ttk.Treeview(list_frame, columns=attendance_columns, show='headings', height=20)
        
        for col in attendance_columns:
            self.attendance_tree.heading(col, text=col)
            if col == 'Notes':
                self.attendance_tree.column(col, width=200)
            else:
                self.attendance_tree.column(col, width=100)
        
        # Scrollbars
        attendance_scrollbar_v = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.attendance_tree.yview)
        self.attendance_tree.configure(yscrollcommand=attendance_scrollbar_v.set)
        
        self.attendance_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        attendance_scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind pour marquage rapide
        self.attendance_tree.bind('<Double-1>', self.quick_mark_attendance)
        
        # Menu contextuel
        self.create_attendance_context_menu()
        
        # Charger les données initiales
        self.refresh_attendance_list()
    
    def create_statistics_tab(self):
        """Créer l'onglet des statistiques"""
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="Statistiques")
        
        # Notebook pour les sous-onglets de statistiques
        stats_notebook = ttk.Notebook(stats_frame)
        stats_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Onglet Vue d'ensemble
        self.create_overview_tab(stats_notebook)
        
        # Onglet Étudiants
        self.create_student_stats_tab(stats_notebook)
        
        # Onglet Graphiques
        self.create_charts_tab(stats_notebook)
    
    def create_overview_tab(self, parent):
        """Créer l'onglet vue d'ensemble des statistiques"""
        overview_frame = ttk.Frame(parent)
        parent.add(overview_frame, text="Vue d'ensemble")
        
        # Frame pour les statistiques générales
        general_frame = ttk.LabelFrame(overview_frame, text="Statistiques Générales", padding="10")
        general_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.general_stats_frame = ttk.Frame(general_frame)
        self.general_stats_frame.pack(fill=tk.X)
        
        # Frame pour les étudiants nécessitant attention
        attention_frame = ttk.LabelFrame(overview_frame, text="Étudiants Nécessitant Attention", padding="10")
        attention_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview pour les étudiants en difficulté
        attention_columns = ('Nom', 'Taux Présence', 'Présent', 'Absent', 'Retard')
        self.attention_tree = ttk.Treeview(attention_frame, columns=attention_columns, show='headings', height=10)
        
        for col in attention_columns:
            self.attention_tree.heading(col, text=col)
            self.attention_tree.column(col, width=120)
        
        attention_scrollbar = ttk.Scrollbar(attention_frame, orient=tk.VERTICAL, command=self.attention_tree.yview)
        self.attention_tree.configure(yscrollcommand=attention_scrollbar.set)
        
        self.attention_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        attention_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bouton de rafraîchissement
        ttk.Button(overview_frame, text="Actualiser Statistiques", 
                  command=self.refresh_statistics).pack(pady=10)
        
        # Charger les statistiques initiales
        self.refresh_statistics()
    
    def create_student_stats_tab(self, parent):
        """Créer l'onglet des statistiques par étudiant"""
        student_stats_frame = ttk.Frame(parent)
        parent.add(student_stats_frame, text="Par Étudiant")
        
        # Contrôles
        controls_frame = ttk.Frame(student_stats_frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(controls_frame, text="Trier par:").pack(side=tk.LEFT)
        
        sort_var = tk.StringVar(value="attendance")
        sort_combo = ttk.Combobox(controls_frame, textvariable=sort_var, 
                                 values=["attendance", "punctuality", "name"], 
                                 state="readonly", width=15)
        sort_combo.pack(side=tk.LEFT, padx=5)
        sort_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh_student_statistics())
        
        ttk.Button(controls_frame, text="Exporter Rapport", 
                  command=self.export_statistics_report).pack(side=tk.RIGHT)
        
        # Liste des statistiques par étudiant
        list_frame = ttk.LabelFrame(student_stats_frame, text="Statistiques Détaillées", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        student_stats_columns = ('Rang', 'Nom', 'Sessions', 'Présent', 'Absent', 'Retard', 
                               'Taux Présence', 'Taux Ponctualité')
        self.student_stats_tree = ttk.Treeview(list_frame, columns=student_stats_columns, 
                                             show='headings', height=15)
        
        for col in student_stats_columns:
            self.student_stats_tree.heading(col, text=col)
            if col in ['Taux Présence', 'Taux Ponctualité']:
                self.student_stats_tree.column(col, width=100)
            else:
                self.student_stats_tree.column(col, width=80)
        
        student_stats_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, 
                                              command=self.student_stats_tree.yview)
        self.student_stats_tree.configure(yscrollcommand=student_stats_scrollbar.set)
        
        self.student_stats_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        student_stats_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.sort_var = sort_var
        self.refresh_student_statistics()
    
    def create_charts_tab(self, parent):
        """Créer l'onglet des graphiques"""
        charts_frame = ttk.Frame(parent)
        parent.add(charts_frame, text="Graphiques")
        
        # Contrôles pour les graphiques
        controls_frame = ttk.Frame(charts_frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(controls_frame, text="Graphique Présences", 
                  command=self.show_attendance_chart).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Comparaison Étudiants", 
                  command=self.show_comparison_chart).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Tendances", 
                  command=self.show_trends_chart).pack(side=tk.LEFT, padx=5)
        
        # Frame pour afficher les graphiques
        self.charts_display_frame = ttk.Frame(charts_frame)
        self.charts_display_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Message initial
        initial_label = ttk.Label(self.charts_display_frame, 
                                text="Sélectionnez un graphique à afficher", 
                                font=('Arial', 12))
        initial_label.pack(expand=True)
    
    def create_settings_tab(self):
        """Créer l'onglet des paramètres"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="Paramètres")
        
        # Gestion des fichiers
        files_frame = ttk.LabelFrame(settings_frame, text="Gestion des Fichiers", padding="10")
        files_frame.pack(fill=tk.X, padx=5, pady=5)
        
        files_buttons = ttk.Frame(files_frame)
        files_buttons.pack(fill=tk.X)
        
        ttk.Button(files_buttons, text="Créer Sauvegarde", 
                  command=self.create_backup).pack(side=tk.LEFT, padx=5)
        ttk.Button(files_buttons, text="Restaurer Sauvegarde", 
                  command=self.restore_backup).pack(side=tk.LEFT, padx=5)
        ttk.Button(files_buttons, text="Exporter Données", 
                  command=self.export_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(files_buttons, text="Importer Données", 
                  command=self.import_data).pack(side=tk.LEFT, padx=5)
        
        # Informations sur les fichiers
        info_frame = ttk.LabelFrame(settings_frame, text="Informations", padding="10")
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.file_info_frame = ttk.Frame(info_frame)
        self.file_info_frame.pack(fill=tk.X)
        
        # Configuration
        config_frame = ttk.LabelFrame(settings_frame, text="Configuration", padding="10")
        config_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Sauvegarde automatique
        auto_save_frame = ttk.Frame(config_frame)
        auto_save_frame.pack(fill=tk.X, pady=2)
        
        self.auto_save_var = tk.BooleanVar(value=self.file_manager.config.get('auto_save', True))
        ttk.Checkbutton(auto_save_frame, text="Sauvegarde automatique", 
                       variable=self.auto_save_var, 
                       command=self.update_auto_save_config).pack(side=tk.LEFT)
        
        # Charger les informations initiales
        self.refresh_file_info()
    
    def create_status_bar(self, parent):
        """Créer la barre de statut"""
        self.status_frame = ttk.Frame(parent)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Séparateur
        ttk.Separator(self.status_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(5, 0))
        
        status_content = ttk.Frame(self.status_frame)
        status_content.pack(fill=tk.X, pady=5)
        
        self.status_label = ttk.Label(status_content, text="Prêt", style='Info.TLabel')
        self.status_label.pack(side=tk.LEFT)
        
        self.info_label = ttk.Label(status_content, text="", style='Info.TLabel')
        self.info_label.pack(side=tk.RIGHT)
    
    def create_attendance_context_menu(self):
        """Créer le menu contextuel pour les présences"""
        self.attendance_context_menu = tk.Menu(self.root, tearoff=0)
        self.attendance_context_menu.add_command(label="Présent", 
                                                command=lambda: self.context_mark_attendance(AttendanceStatus.PRESENT))
        self.attendance_context_menu.add_command(label="Absent", 
                                                command=lambda: self.context_mark_attendance(AttendanceStatus.ABSENT))
        self.attendance_context_menu.add_command(label="En retard", 
                                                command=lambda: self.context_mark_attendance(AttendanceStatus.LATE))
        self.attendance_context_menu.add_separator()
        self.attendance_context_menu.add_command(label="Ajouter Note", 
                                                command=self.add_attendance_note)
        
        self.attendance_tree.bind('<Button-3>', self.show_attendance_context_menu)
    
    # Méthodes pour la gestion des étudiants
    def add_student_dialog(self):
        """Ouvrir la boîte de dialogue pour ajouter un étudiant"""
        dialog = StudentDialog(self.root, "Ajouter Étudiant")
        self.root.wait_window(dialog.dialog)
        if dialog.result:
            try:
                self.student_manager.add_student(**dialog.result)
                self.refresh_students_list()
                self.update_status("Étudiant ajouté avec succès")
            except ValueError as e:
                messagebox.showerror("Erreur", str(e))
    
    def edit_student_dialog(self):
        """Ouvrir la boîte de dialogue pour modifier un étudiant"""
        selection = self.students_tree.selection()
        if not selection:
            messagebox.showwarning("Sélection", "Veuillez sélectionner un étudiant à modifier")
            return
        
        item = self.students_tree.item(selection[0])
        student_id = item['values'][0]
        student = self.student_manager.get_student(student_id)
        
        if student:
            dialog = StudentDialog(self.root, "Modifier Étudiant", student)
            self.root.wait_window(dialog.dialog)
            if dialog.result:
                try:
                    self.student_manager.update_student(student_id, **dialog.result)
                    self.refresh_students_list()
                    self.update_status("Étudiant modifié avec succès")
                except ValueError as e:
                    messagebox.showerror("Erreur", str(e))
    
    def delete_student(self):
        """Supprimer un étudiant sélectionné"""
        selection = self.students_tree.selection()
        if not selection:
            messagebox.showwarning("Sélection", "Veuillez sélectionner un étudiant à supprimer")
            return
        
        item = self.students_tree.item(selection[0])
        student_id = item['values'][0]
        student_name = f"{item['values'][2]} {item['values'][1]}"
        
        if messagebox.askyesno("Confirmation", 
                              f"Êtes-vous sûr de vouloir supprimer l'étudiant {student_name}?"):
            try:
                self.student_manager.delete_student(student_id)
                self.refresh_students_list()
                self.update_status("Étudiant supprimé avec succès")
            except ValueError as e:
                messagebox.showerror("Erreur", str(e))
    
    def filter_students(self, *args):
        """Filtrer la liste des étudiants"""
        query = self.search_var.get()
        students = self.student_manager.search_students(query)
        self.populate_students_tree(students)
    
    def sort_students(self, column):
        """Trier les étudiants par colonne"""
        students = self.student_manager.get_all_students()
        
        if column == 'ID':
            students.sort(key=lambda x: x.student_id)
        elif column == 'Nom':
            students.sort(key=lambda x: x.last_name.lower())
        elif column == 'Prénom':
            students.sort(key=lambda x: x.first_name.lower())
        elif column == 'Email':
            students.sort(key=lambda x: x.email.lower())
        elif column == 'Groupe':
            students.sort(key=lambda x: x.group.lower())
        elif column == 'Date création':
            students.sort(key=lambda x: x.created_date)
        
        self.populate_students_tree(students)
    
    def refresh_students_list(self):
        """Actualiser la liste des étudiants"""
        students = self.student_manager.get_all_students()
        self.populate_students_tree(students)
    
    def populate_students_tree(self, students):
        """Remplir le TreeView avec la liste des étudiants"""
        # Vider la liste
        for item in self.students_tree.get_children():
            self.students_tree.delete(item)
        
        # Ajouter les étudiants
        for student in students:
            created_date = student.created_date[:10] if student.created_date else ""
            self.students_tree.insert('', tk.END, values=(
                student.student_id,
                student.last_name,
                student.first_name,
                student.email,
                student.group,
                created_date
            ))
    
    # Méthodes pour la gestion des présences
    def set_today_date(self):
        """Définir la date du jour"""
        self.selected_date.set(date.today().isoformat())
        self.refresh_attendance_list()
    
    def load_attendance_session(self):
        """Charger une session de présence"""
        self.refresh_attendance_list()
        selected_date = self.selected_date.get()
        session = self.attendance_manager.get_session(selected_date)
        
        if session:
            self.current_td_name.set(session.td_name or "TD/Cours")
            self.update_status(f"Session du {selected_date} chargée")
        else:
            self.update_status(f"Nouvelle session pour le {selected_date}")
    
    def refresh_attendance_list(self):
        """Actualiser la liste des présences"""
        # Vider la liste
        for item in self.attendance_tree.get_children():
            self.attendance_tree.delete(item)
        
        # Obtenir les étudiants et leurs présences
        students = self.student_manager.get_all_students()
        selected_date = self.selected_date.get()
        session = self.attendance_manager.get_session(selected_date)
        
        for student in students:
            record = session.get_record(student.student_id) if session else None
            
            if record:
                status = record.status.value
                time_marked = record.time_marked
                notes = record.notes
            else:
                status = "Non marqué"
                time_marked = ""
                notes = ""
            
            self.attendance_tree.insert('', tk.END, values=(
                student.student_id,
                student.last_name,
                student.first_name,
                status,
                time_marked,
                notes
            ))
    
    def quick_mark_attendance(self, event):
        """Marquage rapide de présence par double-clic"""
        selection = self.attendance_tree.selection()
        if selection:
            self.cycle_attendance_status(selection[0])
    
    def cycle_attendance_status(self, item_id):
        """Faire défiler les statuts de présence"""
        item = self.attendance_tree.item(item_id)
        student_id = item['values'][0]
        current_status = item['values'][3]
        
        # Cycle: Non marqué -> Présent -> Absent -> En retard -> Présent...
        if current_status == "Non marqué":
            new_status = AttendanceStatus.PRESENT
        elif current_status == "Présent":
            new_status = AttendanceStatus.ABSENT
        elif current_status == "Absent":
            new_status = AttendanceStatus.LATE
        else:  # En retard
            new_status = AttendanceStatus.PRESENT
        
        self.mark_student_attendance(student_id, new_status)
    
    def mark_student_attendance(self, student_id, status, notes=""):
        """Marquer la présence d'un étudiant"""
        selected_date = self.selected_date.get()
        td_name = self.current_td_name.get()
        
        try:
            self.attendance_manager.mark_attendance(
                student_id, selected_date, status, td_name, notes,
                datetime.now().strftime("%H:%M:%S")
            )
            self.refresh_attendance_list()
            self.update_status(f"Présence marquée pour {student_id}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du marquage: {e}")
    
    def show_attendance_context_menu(self, event):
        """Afficher le menu contextuel des présences"""
        item = self.attendance_tree.identify_row(event.y)
        if item:
            self.attendance_tree.selection_set(item)
            self.attendance_context_menu.post(event.x_root, event.y_root)
    
    def context_mark_attendance(self, status):
        """Marquer la présence via le menu contextuel"""
        selection = self.attendance_tree.selection()
        if selection:
            item = self.attendance_tree.item(selection[0])
            student_id = item['values'][0]
            self.mark_student_attendance(student_id, status)
    
    def add_attendance_note(self):
        """Ajouter une note à la présence"""
        selection = self.attendance_tree.selection()
        if not selection:
            return
        
        item = self.attendance_tree.item(selection[0])
        student_id = item['values'][0]
        current_notes = item['values'][5]
        
        dialog = NoteDialog(self.root, "Ajouter/Modifier Note", current_notes)
        if dialog.result is not None:
            # Mettre à jour la note dans la base de données
            selected_date = self.selected_date.get()
            session = self.attendance_manager.get_session(selected_date)
            if session and student_id in session.records:
                session.records[student_id].notes = dialog.result
                self.refresh_attendance_list()
                self.update_status("Note mise à jour")
    
    def mark_all_students(self, status):
        """Marquer tous les étudiants avec le même statut"""
        students = self.student_manager.get_all_students()
        td_name = self.current_td_name.get()
        selected_date = self.selected_date.get()
        
        count = 0
        for student in students:
            try:
                self.attendance_manager.mark_attendance(
                    student.student_id, selected_date, status, td_name,
                    time_marked=datetime.now().strftime("%H:%M:%S")
                )
                count += 1
            except Exception as e:
                print(f"Erreur pour {student.student_id}: {e}")
        
        self.refresh_attendance_list()
        self.update_status(f"{count} étudiants marqués comme {status.value.lower()}")
    
    def save_attendance_session(self):
        """Sauvegarder la session de présence"""
        try:
            self.file_manager.save_all_data()
            self.update_status("Session sauvegardée avec succès")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde: {e}")
    
    # Méthodes pour les statistiques
    def refresh_statistics(self):
        """Actualiser les statistiques générales"""
        overall_stats = self.statistics_manager.get_overall_statistics()
        
        # Vider le frame des statistiques générales
        for widget in self.general_stats_frame.winfo_children():
            widget.destroy()
        
        # Afficher les statistiques générales
        stats_text = f"Nombre d'étudiants: {overall_stats['total_students']}\n"
        stats_text += f"Nombre de sessions: {overall_stats['total_sessions']}\n"
        stats_text += f"Taux de présence moyen: {overall_stats['average_attendance_rate']:.1f}%\n"
        stats_text += f"Taux de ponctualité moyen: {overall_stats['average_punctuality_rate']:.1f}%"
        
        ttk.Label(self.general_stats_frame, text=stats_text, style='Info.TLabel').pack(anchor=tk.W)
        
        if overall_stats['best_student']:
            best_text = f"Meilleur étudiant: {overall_stats['best_student'].student_name} "
            best_text += f"({overall_stats['best_student'].attendance_rate:.1f}%)"
            ttk.Label(self.general_stats_frame, text=best_text, style='Success.TLabel').pack(anchor=tk.W)
        
        # Remplir la liste des étudiants nécessitant attention
        for item in self.attention_tree.get_children():
            self.attention_tree.delete(item)
        
        for student_stats in overall_stats['needs_attention']:
            self.attention_tree.insert('', tk.END, values=(
                student_stats.student_name,
                f"{student_stats.attendance_rate:.1f}%",
                student_stats.present_count,
                student_stats.absent_count,
                student_stats.late_count
            ))
    
    def refresh_student_statistics(self):
        """Actualiser les statistiques par étudiant"""
        sort_method = self.sort_var.get()
        
        if sort_method == "attendance":
            stats_list = self.statistics_manager.rank_students_by_attendance()
        elif sort_method == "punctuality":
            stats_list = self.statistics_manager.rank_students_by_punctuality()
        else:  # name
            stats_list = self.statistics_manager.calculate_all_student_statistics()
            stats_list.sort(key=lambda x: x.student_name.lower())
        
        # Vider la liste
        for item in self.student_stats_tree.get_children():
            self.student_stats_tree.delete(item)
        
        # Remplir la liste
        for rank, stats in enumerate(stats_list, 1):
            self.student_stats_tree.insert('', tk.END, values=(
                rank,
                stats.student_name,
                stats.total_sessions,
                stats.present_count,
                stats.absent_count,
                stats.late_count,
                f"{stats.attendance_rate:.1f}%",
                f"{stats.punctuality_rate:.1f}%"
            ))
    
    def show_attendance_chart(self):
        """Afficher le graphique des présences"""
        # Vider le frame d'affichage
        for widget in self.charts_display_frame.winfo_children():
            widget.destroy()
        
        chart_frame = self.statistics_manager.create_attendance_pie_chart(self.charts_display_frame)
        chart_frame.pack(fill=tk.BOTH, expand=True)
    
    def show_comparison_chart(self):
        """Afficher le graphique de comparaison des étudiants"""
        for widget in self.charts_display_frame.winfo_children():
            widget.destroy()
        
        chart_frame = self.statistics_manager.create_student_comparison_chart(self.charts_display_frame)
        chart_frame.pack(fill=tk.BOTH, expand=True)
    
    def show_trends_chart(self):
        """Afficher le graphique des tendances"""
        for widget in self.charts_display_frame.winfo_children():
            widget.destroy()
        
        chart_frame = self.statistics_manager.create_trends_chart(self.charts_display_frame)
        chart_frame.pack(fill=tk.BOTH, expand=True)
    
    def export_statistics_report(self):
        """Exporter un rapport de statistiques"""
        filename = filedialog.asksaveasfilename(
            title="Exporter Rapport Statistiques",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            if self.statistics_manager.export_statistics_report(filename):
                messagebox.showinfo("Succès", f"Rapport exporté vers {filename}")
            else:
                messagebox.showerror("Erreur", "Erreur lors de l'export du rapport")
    
    # Méthodes pour les paramètres et fichiers
    def create_backup(self):
        """Créer une sauvegarde"""
        if self.file_manager.create_backup():
            messagebox.showinfo("Succès", "Sauvegarde créée avec succès")
            self.refresh_file_info()
        else:
            messagebox.showerror("Erreur", "Erreur lors de la création de la sauvegarde")
    
    def restore_backup(self):
        """Restaurer une sauvegarde"""
        backups = self.file_manager.list_backups()
        if not backups:
            messagebox.showinfo("Information", "Aucune sauvegarde disponible")
            return
        
        dialog = BackupDialog(self.root, backups)
        if dialog.result:
            if self.file_manager.restore_backup(dialog.result):
                messagebox.showinfo("Succès", "Sauvegarde restaurée avec succès")
                self.refresh_all_data()
            else:
                messagebox.showerror("Erreur", "Erreur lors de la restauration")
    
    def export_data(self):
        """Exporter toutes les données"""
        filename = filedialog.asksaveasfilename(
            title="Exporter Données",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            if self.file_manager.export_data(filename):
                messagebox.showinfo("Succès", f"Données exportées vers {filename}")
            else:
                messagebox.showerror("Erreur", "Erreur lors de l'export")
    
    def import_data(self):
        """Importer des données"""
        filename = filedialog.askopenfilename(
            title="Importer Données",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            if messagebox.askyesno("Confirmation", 
                                  "L'import remplacera les données actuelles. Continuer?"):
                if self.file_manager.import_data(filename):
                    messagebox.showinfo("Succès", "Données importées avec succès")
                    self.refresh_all_data()
                else:
                    messagebox.showerror("Erreur", "Erreur lors de l'import")
    
    def refresh_file_info(self):
        """Actualiser les informations sur les fichiers"""
        for widget in self.file_info_frame.winfo_children():
            widget.destroy()
        
        file_info = self.file_manager.get_file_info()
        
        for file_type, info in file_info.items():
            frame = ttk.Frame(self.file_info_frame)
            frame.pack(fill=tk.X, pady=2)
            
            status = "✓" if info['exists'] else "✗"
            color = "green" if info['exists'] else "red"
            
            ttk.Label(frame, text=f"{status} {file_type.title()}:", 
                     foreground=color).pack(side=tk.LEFT)
            
            if info['exists']:
                size_kb = info['size'] / 1024
                modified = info['modified'][:19] if info['modified'] else "Inconnu"
                ttk.Label(frame, text=f"{size_kb:.1f} KB - Modifié: {modified}").pack(side=tk.LEFT, padx=(10, 0))
    
    def update_auto_save_config(self):
        """Mettre à jour la configuration de sauvegarde automatique"""
        self.file_manager.config['auto_save'] = self.auto_save_var.get()
        self.file_manager.save_config()
        
        if self.auto_save_var.get():
            self.file_manager.setup_auto_save(self.root)
        else:
            self.file_manager.stop_auto_save(self.root)
    
    # Méthodes utilitaires
    def quick_save(self):
        """Sauvegarde rapide"""
        try:
            self.file_manager.save_all_data()
            self.update_status("Données sauvegardées")
        except Exception as e:
            self.update_status(f"Erreur de sauvegarde: {e}")
    
    def refresh_all_data(self):
        """Actualiser toutes les données"""
        self.refresh_students_list()
        self.refresh_attendance_list()
        self.refresh_statistics()
        self.refresh_student_statistics()
        self.refresh_file_info()
        self.update_status("Données actualisées")
    
    def update_status(self, message):
        """Mettre à jour le message de statut"""
        self.status_label.config(text=message)
        self.root.after(5000, lambda: self.status_label.config(text="Prêt"))
    
    def update_status_bar(self):
        """Mettre à jour la barre de statut avec les informations"""
        student_count = self.student_manager.get_student_count()
        session_count = len(self.attendance_manager.get_all_sessions())
        info_text = f"Étudiants: {student_count} | Sessions: {session_count}"
        self.info_label.config(text=info_text)
    
    # Méthodes d'observation
    def on_student_change(self, event_type, student_id=None):
        """Réagir aux changements d'étudiants"""
        if event_type in ['add', 'update', 'delete', 'load']:
            self.refresh_students_list()
            self.refresh_attendance_list()
            self.update_status_bar()
    
    def on_attendance_change(self, event_type, date_str=None):
        """Réagir aux changements de présence"""
        if event_type in ['attendance_marked', 'session_created', 'load']:
            self.refresh_attendance_list()
            self.update_status_bar()


class StudentDialog:
    """Boîte de dialogue pour ajouter/modifier un étudiant"""
    
    def __init__(self, parent, title, student=None):
        self.result = None
        
        # Créer la fenêtre
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrer la fenêtre
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 200
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 150
        self.dialog.geometry(f"400x300+{x}+{y}")
        
        # Variables
        self.student_id_var = tk.StringVar(value=student.student_id if student else "")
        self.first_name_var = tk.StringVar(value=student.first_name if student else "")
        self.last_name_var = tk.StringVar(value=student.last_name if student else "")
        self.email_var = tk.StringVar(value=student.email if student else "")
        self.phone_var = tk.StringVar(value=student.phone if student else "")
        self.group_var = tk.StringVar(value=student.group if student else "")
        
        self.create_form()
        
        # Si modification, désactiver le champ ID
        if student and hasattr(self, 'id_entry'):
            self.id_entry.config(state='disabled')
    
    def create_form(self):
        """Créer le formulaire"""
        # Frame principal
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Champs du formulaire
        fields = [
            ("ID Étudiant:", self.student_id_var, 'id_entry'),
            ("Prénom:", self.first_name_var, None),
            ("Nom:", self.last_name_var, None),
            ("Email:", self.email_var, None),
            ("Téléphone:", self.phone_var, None),
            ("Groupe:", self.group_var, None)
        ]
        
        for i, (label, var, entry_name) in enumerate(fields):
            ttk.Label(main_frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=5)
            entry = ttk.Entry(main_frame, textvariable=var, width=30)
            entry.grid(row=i, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
            
            if entry_name:
                setattr(self, entry_name, entry)
            
            # Stocker le premier entry pour le focus
            if i == 0:
                self.first_entry = entry
        
        main_frame.columnconfigure(1, weight=1)
        
        # Boutons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Valider", command=self.validate).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Annuler", command=self.cancel).pack(side=tk.LEFT, padx=5)
        
        # Focus sur le premier champ
        if hasattr(self, 'first_entry'):
            self.first_entry.focus()
    
    def validate(self):
        """Valider et fermer la boîte de dialogue"""
        # Récupérer les valeurs
        data = {
            'student_id': self.student_id_var.get().strip(),
            'first_name': self.first_name_var.get().strip(),
            'last_name': self.last_name_var.get().strip(),
            'email': self.email_var.get().strip(),
            'phone': self.phone_var.get().strip(),
            'group': self.group_var.get().strip()
        }
        
        # Validation basique
        if not data['student_id']:
            messagebox.showerror("Erreur", "L'ID étudiant est obligatoire")
            return
        
        if not data['first_name']:
            messagebox.showerror("Erreur", "Le prénom est obligatoire")
            return
        
        if not data['last_name']:
            messagebox.showerror("Erreur", "Le nom est obligatoire")
            return
        
        if data['email'] and '@' not in data['email']:
            messagebox.showerror("Erreur", "L'adresse email n'est pas valide")
            return
        
        self.result = data
        self.dialog.destroy()
    
    def cancel(self):
        """Annuler et fermer la boîte de dialogue"""
        self.dialog.destroy()


class NoteDialog:
    """Boîte de dialogue pour ajouter/modifier une note"""
    
    def __init__(self, parent, title, initial_note=""):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrer
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 200
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 100
        self.dialog.geometry(f"400x200+{x}+{y}")
        
        # Contenu
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Note:").pack(anchor=tk.W)
        
        self.text_widget = tk.Text(main_frame, height=5, width=40)
        self.text_widget.pack(fill=tk.BOTH, expand=True, pady=5)
        self.text_widget.insert(tk.END, initial_note)
        
        # Boutons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Valider", command=self.validate).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Annuler", command=self.cancel).pack(side=tk.LEFT, padx=5)
        
        self.text_widget.focus()
    
    def validate(self):
        """Valider et fermer"""
        self.result = self.text_widget.get(1.0, tk.END).strip()
        self.dialog.destroy()
    
    def cancel(self):
        """Annuler"""
        self.dialog.destroy()


class BackupDialog:
    """Boîte de dialogue pour sélectionner une sauvegarde"""
    
    def __init__(self, parent, backups):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Restaurer Sauvegarde")
        self.dialog.geometry("500x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrer
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 250
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 150
        self.dialog.geometry(f"500x300+{x}+{y}")
        
        # Contenu
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Sélectionnez une sauvegarde à restaurer:").pack(anchor=tk.W)
        
        # Liste des sauvegardes
        columns = ('Nom', 'Date de création')
        self.tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200)
        
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Remplir la liste
        for backup in backups:
            creation_date = backup['creation_date'][:19].replace('T', ' ')
            self.tree.insert('', tk.END, values=(backup['name'], creation_date))
        
        # Boutons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Restaurer", command=self.validate).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Annuler", command=self.cancel).pack(side=tk.LEFT, padx=5)
    
    def validate(self):
        """Valider la sélection"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Sélection", "Veuillez sélectionner une sauvegarde")
            return
        
        item = self.tree.item(selection[0])
        self.result = item['values'][0]
        self.dialog.destroy()
    
    def cancel(self):
        """Annuler"""
        self.dialog.destroy()
