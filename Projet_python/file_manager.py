"""
Gestionnaire des Fichiers
Module pour la sauvegarde et le chargement des données en JSON
"""

import json
import os
import shutil
from datetime import datetime
from typing import Dict, Optional, List
import tkinter as tk
from tkinter import filedialog, messagebox

class FileManager:
    """Gestionnaire pour les opérations de fichiers"""
    
    def __init__(self, student_manager, attendance_manager):
        self.student_manager = student_manager
        self.attendance_manager = attendance_manager
        
        # Chemins des fichiers
        self.data_dir = "data"
        self.students_file = os.path.join(self.data_dir, "students.json")
        self.attendance_file = os.path.join(self.data_dir, "attendance.json")
        self.config_file = os.path.join(self.data_dir, "config.json")
        self.backup_dir = os.path.join(self.data_dir, "backups")
        
        # Configuration par défaut
        self.default_config = {
            'app_name': 'Système de Gestion des Présences',
            'version': '1.0.0',
            'auto_save': True,
            'auto_save_interval': 300,  # 5 minutes
            'backup_enabled': True,
            'backup_count': 5,
            'last_backup': None,
            'created_date': datetime.now().isoformat()
        }
        
        self.config = self.default_config.copy()
        self._ensure_directories()
        self._auto_save_job = None
    
    def _ensure_directories(self):
        """Créer les répertoires nécessaires s'ils n'existent pas"""
        directories = [self.data_dir, self.backup_dir]
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"Répertoire créé: {directory}")
    
    def load_config(self) -> Dict:
        """Charger la configuration depuis le fichier"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
                    print("Configuration chargée avec succès")
            else:
                print("Fichier de configuration non trouvé, utilisation des valeurs par défaut")
                self.save_config()
        except Exception as e:
            print(f"Erreur lors du chargement de la configuration: {e}")
            self.config = self.default_config.copy()
        
        return self.config
    
    def save_config(self) -> bool:
        """Sauvegarder la configuration"""
        try:
            self.config['last_modified'] = datetime.now().isoformat()
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la configuration: {e}")
            return False
    
    def load_students(self) -> bool:
        """Charger les données des étudiants"""
        try:
            if os.path.exists(self.students_file):
                with open(self.students_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.student_manager.load_from_dict(data)
                    print(f"Données de {len(data)} étudiants chargées")
                    return True
            else:
                print("Fichier des étudiants non trouvé")
                return False
        except Exception as e:
            print(f"Erreur lors du chargement des étudiants: {e}")
            return False
    
    def save_students(self) -> bool:
        """Sauvegarder les données des étudiants"""
        try:
            data = self.student_manager.to_dict()
            with open(self.students_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Données de {len(data)} étudiants sauvegardées")
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des étudiants: {e}")
            return False
    
    def load_attendance(self) -> bool:
        """Charger les données de présence"""
        try:
            if os.path.exists(self.attendance_file):
                with open(self.attendance_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.attendance_manager.load_from_dict(data)
                    print(f"Données de {len(data)} sessions de présence chargées")
                    return True
            else:
                print("Fichier des présences non trouvé")
                return False
        except Exception as e:
            print(f"Erreur lors du chargement des présences: {e}")
            return False
    
    def save_attendance(self) -> bool:
        """Sauvegarder les données de présence"""
        try:
            data = self.attendance_manager.to_dict()
            with open(self.attendance_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Données de {len(data)} sessions de présence sauvegardées")
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des présences: {e}")
            return False
    
    def load_all_data(self) -> bool:
        """Charger toutes les données"""
        try:
            self.load_config()
            students_loaded = self.load_students()
            attendance_loaded = self.load_attendance()
            
            if students_loaded or attendance_loaded:
                print("Chargement des données terminé")
                return True
            else:
                print("Aucune donnée existante trouvée, démarrage avec des données vides")
                return True
        except Exception as e:
            print(f"Erreur lors du chargement complet: {e}")
            return False
    
    def save_all_data(self) -> bool:
        """Sauvegarder toutes les données"""
        try:
            config_saved = self.save_config()
            students_saved = self.save_students()
            attendance_saved = self.save_attendance()
            
            if config_saved and students_saved and attendance_saved:
                print("Sauvegarde complète réussie")
                return True
            else:
                print("Erreur lors de la sauvegarde complète")
                return False
        except Exception as e:
            print(f"Erreur lors de la sauvegarde complète: {e}")
            return False
    
    def create_backup(self, backup_name: str = None) -> bool:
        """Créer une sauvegarde complète"""
        try:
            if not backup_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"backup_{timestamp}"
            
            backup_path = os.path.join(self.backup_dir, backup_name)
            
            # Créer le répertoire de sauvegarde
            if not os.path.exists(backup_path):
                os.makedirs(backup_path)
            
            # Sauvegarder d'abord les données actuelles
            self.save_all_data()
            
            # Copier les fichiers
            files_to_backup = [
                (self.students_file, "students.json"),
                (self.attendance_file, "attendance.json"),
                (self.config_file, "config.json")
            ]
            
            for source_file, backup_filename in files_to_backup:
                if os.path.exists(source_file):
                    backup_file_path = os.path.join(backup_path, backup_filename)
                    shutil.copy2(source_file, backup_file_path)
            
            # Mettre à jour la configuration
            self.config['last_backup'] = datetime.now().isoformat()
            self.save_config()
            
            # Nettoyer les anciennes sauvegardes
            self._cleanup_old_backups()
            
            print(f"Sauvegarde créée: {backup_path}")
            return True
            
        except Exception as e:
            print(f"Erreur lors de la création de la sauvegarde: {e}")
            return False
    
    def _cleanup_old_backups(self):
        """Nettoyer les anciennes sauvegardes"""
        try:
            if not self.config.get('backup_enabled', True):
                return
            
            backup_count = self.config.get('backup_count', 5)
            
            # Lister toutes les sauvegardes
            backups = []
            for item in os.listdir(self.backup_dir):
                backup_path = os.path.join(self.backup_dir, item)
                if os.path.isdir(backup_path) and item.startswith('backup_'):
                    backups.append((item, os.path.getctime(backup_path)))
            
            # Trier par date de création (plus récent en premier)
            backups.sort(key=lambda x: x[1], reverse=True)
            
            # Supprimer les sauvegardes excédentaires
            for backup_name, _ in backups[backup_count:]:
                backup_path = os.path.join(self.backup_dir, backup_name)
                shutil.rmtree(backup_path)
                print(f"Ancienne sauvegarde supprimée: {backup_name}")
                
        except Exception as e:
            print(f"Erreur lors du nettoyage des sauvegardes: {e}")
    
    def list_backups(self) -> List[Dict]:
        """Lister toutes les sauvegardes disponibles"""
        backups = []
        try:
            for item in os.listdir(self.backup_dir):
                backup_path = os.path.join(self.backup_dir, item)
                if os.path.isdir(backup_path) and item.startswith('backup_'):
                    creation_time = os.path.getctime(backup_path)
                    creation_date = datetime.fromtimestamp(creation_time)
                    
                    backups.append({
                        'name': item,
                        'path': backup_path,
                        'creation_date': creation_date.isoformat(),
                        'creation_timestamp': creation_time
                    })
            
            # Trier par date de création (plus récent en premier)
            backups.sort(key=lambda x: x['creation_timestamp'], reverse=True)
            
        except Exception as e:
            print(f"Erreur lors de la liste des sauvegardes: {e}")
        
        return backups
    
    def restore_backup(self, backup_name: str) -> bool:
        """Restaurer une sauvegarde"""
        try:
            backup_path = os.path.join(self.backup_dir, backup_name)
            
            if not os.path.exists(backup_path):
                print(f"Sauvegarde non trouvée: {backup_name}")
                return False
            
            # Créer une sauvegarde de sécurité avant la restauration
            self.create_backup("before_restore")
            
            # Restaurer les fichiers
            files_to_restore = [
                ("students.json", self.students_file),
                ("attendance.json", self.attendance_file),
                ("config.json", self.config_file)
            ]
            
            for backup_filename, target_file in files_to_restore:
                backup_file_path = os.path.join(backup_path, backup_filename)
                if os.path.exists(backup_file_path):
                    shutil.copy2(backup_file_path, target_file)
            
            # Recharger les données
            self.load_all_data()
            
            print(f"Sauvegarde restaurée: {backup_name}")
            return True
            
        except Exception as e:
            print(f"Erreur lors de la restauration: {e}")
            return False
    
    def export_data(self, export_path: str) -> bool:
        """Exporter toutes les données vers un fichier"""
        try:
            # Sauvegarder d'abord les données actuelles
            self.save_all_data()
            
            export_data = {
                'export_date': datetime.now().isoformat(),
                'app_info': {
                    'name': self.config.get('app_name', 'Système de Gestion des Présences'),
                    'version': self.config.get('version', '1.0.0')
                },
                'students': self.student_manager.to_dict(),
                'attendance': self.attendance_manager.to_dict(),
                'config': self.config
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            print(f"Données exportées vers: {export_path}")
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'export: {e}")
            return False
    
    def import_data(self, import_path: str) -> bool:
        """Importer des données depuis un fichier"""
        try:
            # Créer une sauvegarde avant l'import
            self.create_backup("before_import")
            
            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # Importer les données
            if 'students' in import_data:
                self.student_manager.load_from_dict(import_data['students'])
            
            if 'attendance' in import_data:
                self.attendance_manager.load_from_dict(import_data['attendance'])
            
            if 'config' in import_data:
                # Fusionner la configuration importée avec la configuration actuelle
                for key, value in import_data['config'].items():
                    if key not in ['created_date', 'last_backup']:  # Préserver certaines valeurs locales
                        self.config[key] = value
            
            # Sauvegarder les données importées
            self.save_all_data()
            
            print(f"Données importées depuis: {import_path}")
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'import: {e}")
            return False
    
    def get_file_info(self) -> Dict:
        """Obtenir des informations sur les fichiers de données"""
        info = {}
        
        files_to_check = [
            ('students', self.students_file),
            ('attendance', self.attendance_file),
            ('config', self.config_file)
        ]
        
        for file_type, file_path in files_to_check:
            if os.path.exists(file_path):
                stat = os.stat(file_path)
                info[file_type] = {
                    'exists': True,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'path': file_path
                }
            else:
                info[file_type] = {
                    'exists': False,
                    'size': 0,
                    'modified': None,
                    'path': file_path
                }
        
        return info
    
    def setup_auto_save(self, root_window):
        """Configurer la sauvegarde automatique"""
        if self.config.get('auto_save', True):
            interval = self.config.get('auto_save_interval', 300) * 1000  # Convertir en millisecondes
            
            def auto_save():
                try:
                    self.save_all_data()
                    print("Sauvegarde automatique effectuée")
                except Exception as e:
                    print(f"Erreur lors de la sauvegarde automatique: {e}")
                
                # Programmer la prochaine sauvegarde
                self._auto_save_job = root_window.after(interval, auto_save)
            
            # Démarrer la sauvegarde automatique
            self._auto_save_job = root_window.after(interval, auto_save)
    
    def stop_auto_save(self, root_window):
        """Arrêter la sauvegarde automatique"""
        if self._auto_save_job:
            root_window.after_cancel(self._auto_save_job)
            self._auto_save_job = None
