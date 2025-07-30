"""
Gestionnaire des Étudiants
Module pour la gestion des étudiants (ajout, modification, suppression)
"""

import json
from datetime import datetime
from typing import Dict, List, Optional

class Student:
    """Classe représentant un étudiant"""
    
    def __init__(self, student_id: str, first_name: str, last_name: str, 
                 email: str = "", phone: str = "", group: str = ""):
        self.student_id = student_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.group = group
        self.created_date = datetime.now().isoformat()
        self.modified_date = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Convertir l'étudiant en dictionnaire"""
        return {
            'student_id': self.student_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'group': self.group,
            'created_date': self.created_date,
            'modified_date': self.modified_date
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Créer un étudiant à partir d'un dictionnaire"""
        student = cls(
            data['student_id'],
            data['first_name'],
            data['last_name'],
            data.get('email', ''),
            data.get('phone', ''),
            data.get('group', '')
        )
        student.created_date = data.get('created_date', datetime.now().isoformat())
        student.modified_date = data.get('modified_date', datetime.now().isoformat())
        return student
    
    def get_full_name(self) -> str:
        """Retourner le nom complet de l'étudiant"""
        return f"{self.first_name} {self.last_name}"
    
    def update_info(self, **kwargs):
        """Mettre à jour les informations de l'étudiant"""
        for key, value in kwargs.items():
            if hasattr(self, key) and key != 'student_id':
                setattr(self, key, value)
        self.modified_date = datetime.now().isoformat()

class StudentManager:
    """Gestionnaire pour les opérations sur les étudiants"""
    
    def __init__(self):
        self.students: Dict[str, Student] = {}
        self._observers = []
    
    def add_observer(self, observer):
        """Ajouter un observateur pour les changements"""
        self._observers.append(observer)
    
    def notify_observers(self, event_type: str, student_id: str = None):
        """Notifier les observateurs des changements"""
        for observer in self._observers:
            if hasattr(observer, 'on_student_change'):
                observer.on_student_change(event_type, student_id)
    
    def add_student(self, student_id: str, first_name: str, last_name: str,
                   email: str = "", phone: str = "", group: str = "") -> bool:
        """Ajouter un nouvel étudiant"""
        if student_id in self.students:
            raise ValueError(f"Un étudiant avec l'ID '{student_id}' existe déjà")
        
        if not student_id.strip() or not first_name.strip() or not last_name.strip():
            raise ValueError("L'ID, le prénom et le nom sont obligatoires")
        
        student = Student(student_id.strip(), first_name.strip(), last_name.strip(),
                         email.strip(), phone.strip(), group.strip())
        
        self.students[student_id] = student
        self.notify_observers('add', student_id)
        return True
    
    def get_student(self, student_id: str) -> Optional[Student]:
        """Récupérer un étudiant par son ID"""
        return self.students.get(student_id)
    
    def get_all_students(self) -> List[Student]:
        """Récupérer tous les étudiants"""
        return list(self.students.values())
    
    def update_student(self, student_id: str, **kwargs) -> bool:
        """Mettre à jour les informations d'un étudiant"""
        if student_id not in self.students:
            raise ValueError(f"Aucun étudiant trouvé avec l'ID '{student_id}'")
        
        # Vérifier les champs obligatoires
        if 'first_name' in kwargs and not kwargs['first_name'].strip():
            raise ValueError("Le prénom ne peut pas être vide")
        if 'last_name' in kwargs and not kwargs['last_name'].strip():
            raise ValueError("Le nom ne peut pas être vide")
        
        self.students[student_id].update_info(**kwargs)
        self.notify_observers('update', student_id)
        return True
    
    def delete_student(self, student_id: str) -> bool:
        """Supprimer un étudiant"""
        if student_id not in self.students:
            raise ValueError(f"Aucun étudiant trouvé avec l'ID '{student_id}'")
        
        del self.students[student_id]
        self.notify_observers('delete', student_id)
        return True
    
    def search_students(self, query: str) -> List[Student]:
        """Rechercher des étudiants par nom, prénom ou ID"""
        query = query.lower().strip()
        if not query:
            return self.get_all_students()
        
        results = []
        for student in self.students.values():
            if (query in student.first_name.lower() or 
                query in student.last_name.lower() or 
                query in student.student_id.lower() or
                query in student.email.lower() or
                query in student.group.lower()):
                results.append(student)
        
        return results
    
    def get_students_by_group(self, group: str) -> List[Student]:
        """Récupérer les étudiants d'un groupe spécifique"""
        return [student for student in self.students.values() 
                if student.group.lower() == group.lower()]
    
    def get_groups(self) -> List[str]:
        """Récupérer la liste de tous les groupes"""
        groups = set()
        for student in self.students.values():
            if student.group.strip():
                groups.add(student.group.strip())
        return sorted(list(groups))
    
    def get_student_count(self) -> int:
        """Récupérer le nombre total d'étudiants"""
        return len(self.students)
    
    def validate_student_data(self, student_id: str, first_name: str, 
                            last_name: str, email: str = "") -> List[str]:
        """Valider les données d'un étudiant et retourner les erreurs"""
        errors = []
        
        if not student_id.strip():
            errors.append("L'ID étudiant est obligatoire")
        elif len(student_id.strip()) < 2:
            errors.append("L'ID étudiant doit contenir au moins 2 caractères")
        
        if not first_name.strip():
            errors.append("Le prénom est obligatoire")
        elif len(first_name.strip()) < 2:
            errors.append("Le prénom doit contenir au moins 2 caractères")
        
        if not last_name.strip():
            errors.append("Le nom est obligatoire")
        elif len(last_name.strip()) < 2:
            errors.append("Le nom doit contenir au moins 2 caractères")
        
        if email.strip() and '@' not in email:
            errors.append("L'adresse email n'est pas valide")
        
        return errors
    
    def load_from_dict(self, data: Dict):
        """Charger les étudiants depuis un dictionnaire"""
        self.students.clear()
        for student_id, student_data in data.items():
            try:
                student = Student.from_dict(student_data)
                self.students[student_id] = student
            except Exception as e:
                print(f"Erreur lors du chargement de l'étudiant {student_id}: {e}")
        
        self.notify_observers('load')
    
    def to_dict(self) -> Dict:
        """Convertir tous les étudiants en dictionnaire"""
        return {student_id: student.to_dict() 
                for student_id, student in self.students.items()}
