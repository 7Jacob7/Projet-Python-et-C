"""
Gestionnaire des Présences
Module pour marquer et gérer les présences des étudiants
"""

import json
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple
from enum import Enum

class AttendanceStatus(Enum):
    """Énumération des statuts de présence"""
    PRESENT = "Présent"
    ABSENT = "Absent"
    LATE = "En retard"

class AttendanceRecord:
    """Classe représentant un enregistrement de présence"""
    
    def __init__(self, student_id: str, date_str: str, status: AttendanceStatus,
                 td_name: str = "", notes: str = "", time_marked: str = None):
        self.student_id = student_id
        self.date = date_str
        self.status = status
        self.td_name = td_name
        self.notes = notes
        self.time_marked = time_marked or datetime.now().strftime("%H:%M:%S")
        self.created_timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Convertir l'enregistrement en dictionnaire"""
        return {
            'student_id': self.student_id,
            'date': self.date,
            'status': self.status.value,
            'td_name': self.td_name,
            'notes': self.notes,
            'time_marked': self.time_marked,
            'created_timestamp': self.created_timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Créer un enregistrement à partir d'un dictionnaire"""
        status = AttendanceStatus.PRESENT
        for s in AttendanceStatus:
            if s.value == data.get('status', 'Présent'):
                status = s
                break
        
        record = cls(
            data['student_id'],
            data['date'],
            status,
            data.get('td_name', ''),
            data.get('notes', ''),
            data.get('time_marked')
        )
        record.created_timestamp = data.get('created_timestamp', datetime.now().isoformat())
        return record

class AttendanceSession:
    """Classe représentant une session de présence (une date + TD)"""
    
    def __init__(self, date_str: str, td_name: str = "", description: str = ""):
        self.date = date_str
        self.td_name = td_name
        self.description = description
        self.created_timestamp = datetime.now().isoformat()
        self.records: Dict[str, AttendanceRecord] = {}
    
    def add_record(self, record: AttendanceRecord):
        """Ajouter un enregistrement à la session"""
        self.records[record.student_id] = record
    
    def get_record(self, student_id: str) -> Optional[AttendanceRecord]:
        """Récupérer l'enregistrement d'un étudiant"""
        return self.records.get(student_id)
    
    def get_all_records(self) -> List[AttendanceRecord]:
        """Récupérer tous les enregistrements de la session"""
        return list(self.records.values())
    
    def to_dict(self) -> Dict:
        """Convertir la session en dictionnaire"""
        return {
            'date': self.date,
            'td_name': self.td_name,
            'description': self.description,
            'created_timestamp': self.created_timestamp,
            'records': {student_id: record.to_dict() 
                       for student_id, record in self.records.items()}
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Créer une session à partir d'un dictionnaire"""
        session = cls(
            data['date'],
            data.get('td_name', ''),
            data.get('description', '')
        )
        session.created_timestamp = data.get('created_timestamp', datetime.now().isoformat())
        
        for student_id, record_data in data.get('records', {}).items():
            record = AttendanceRecord.from_dict(record_data)
            session.records[student_id] = record
        
        return session

class AttendanceManager:
    """Gestionnaire pour les opérations de présence"""
    
    def __init__(self):
        self.sessions: Dict[str, AttendanceSession] = {}  # key: date_str
        self._observers = []
    
    def add_observer(self, observer):
        """Ajouter un observateur pour les changements"""
        self._observers.append(observer)
    
    def notify_observers(self, event_type: str, date_str: str = None):
        """Notifier les observateurs des changements"""
        for observer in self._observers:
            if hasattr(observer, 'on_attendance_change'):
                observer.on_attendance_change(event_type, date_str)
    
    def create_session(self, date_str: str, td_name: str = "", description: str = "") -> AttendanceSession:
        """Créer une nouvelle session de présence"""
        if date_str in self.sessions:
            return self.sessions[date_str]
        
        session = AttendanceSession(date_str, td_name, description)
        self.sessions[date_str] = session
        self.notify_observers('session_created', date_str)
        return session
    
    def get_session(self, date_str: str) -> Optional[AttendanceSession]:
        """Récupérer une session par date"""
        return self.sessions.get(date_str)
    
    def get_all_sessions(self) -> List[AttendanceSession]:
        """Récupérer toutes les sessions"""
        return list(self.sessions.values())
    
    def mark_attendance(self, student_id: str, date_str: str, status: AttendanceStatus,
                       td_name: str = "", notes: str = "", time_marked: str = None) -> bool:
        """Marquer la présence d'un étudiant"""
        # Créer la session si elle n'existe pas
        if date_str not in self.sessions:
            self.create_session(date_str, td_name)
        
        session = self.sessions[date_str]
        
        # Créer l'enregistrement
        record = AttendanceRecord(student_id, date_str, status, td_name, notes, time_marked)
        session.add_record(record)
        
        # Mettre à jour le nom du TD de la session si fourni
        if td_name and not session.td_name:
            session.td_name = td_name
        
        self.notify_observers('attendance_marked', date_str)
        return True
    
    def get_student_attendance(self, student_id: str) -> List[AttendanceRecord]:
        """Récupérer tous les enregistrements de présence d'un étudiant"""
        records = []
        for session in self.sessions.values():
            record = session.get_record(student_id)
            if record:
                records.append(record)
        
        # Trier par date
        records.sort(key=lambda x: x.date)
        return records
    
    def get_attendance_by_date(self, date_str: str) -> List[AttendanceRecord]:
        """Récupérer tous les enregistrements pour une date donnée"""
        session = self.get_session(date_str)
        return session.get_all_records() if session else []
    
    def get_attendance_summary(self, student_id: str) -> Dict[str, int]:
        """Récupérer un résumé des présences d'un étudiant"""
        records = self.get_student_attendance(student_id)
        
        summary = {
            'total_sessions': len(records),
            'present': 0,
            'absent': 0,
            'late': 0
        }
        
        for record in records:
            if record.status == AttendanceStatus.PRESENT:
                summary['present'] += 1
            elif record.status == AttendanceStatus.ABSENT:
                summary['absent'] += 1
            elif record.status == AttendanceStatus.LATE:
                summary['late'] += 1
        
        return summary
    
    def get_date_range(self) -> Tuple[Optional[str], Optional[str]]:
        """Récupérer la plage de dates des sessions"""
        if not self.sessions:
            return None, None
        
        dates = list(self.sessions.keys())
        return min(dates), max(dates)
    
    def get_td_names(self) -> List[str]:
        """Récupérer la liste de tous les noms de TD"""
        td_names = set()
        for session in self.sessions.values():
            if session.td_name.strip():
                td_names.add(session.td_name.strip())
        return sorted(list(td_names))
    
    def delete_session(self, date_str: str) -> bool:
        """Supprimer une session complète"""
        if date_str in self.sessions:
            del self.sessions[date_str]
            self.notify_observers('session_deleted', date_str)
            return True
        return False
    
    def delete_student_attendance(self, student_id: str, date_str: str) -> bool:
        """Supprimer la présence d'un étudiant pour une date donnée"""
        session = self.get_session(date_str)
        if session and student_id in session.records:
            del session.records[student_id]
            self.notify_observers('attendance_deleted', date_str)
            return True
        return False
    
    def get_attendance_statistics(self) -> Dict:
        """Récupérer les statistiques générales de présence"""
        total_sessions = len(self.sessions)
        total_records = sum(len(session.records) for session in self.sessions.values())
        
        status_counts = {'present': 0, 'absent': 0, 'late': 0}
        
        for session in self.sessions.values():
            for record in session.records.values():
                if record.status == AttendanceStatus.PRESENT:
                    status_counts['present'] += 1
                elif record.status == AttendanceStatus.ABSENT:
                    status_counts['absent'] += 1
                elif record.status == AttendanceStatus.LATE:
                    status_counts['late'] += 1
        
        return {
            'total_sessions': total_sessions,
            'total_records': total_records,
            'status_counts': status_counts
        }
    
    def get_sessions_by_date_range(self, start_date: str, end_date: str) -> List[AttendanceSession]:
        """Récupérer les sessions dans une plage de dates"""
        sessions = []
        for date_str, session in self.sessions.items():
            if start_date <= date_str <= end_date:
                sessions.append(session)
        
        return sorted(sessions, key=lambda x: x.date)
    
    def load_from_dict(self, data: Dict):
        """Charger les sessions depuis un dictionnaire"""
        self.sessions.clear()
        for date_str, session_data in data.items():
            try:
                session = AttendanceSession.from_dict(session_data)
                self.sessions[date_str] = session
            except Exception as e:
                print(f"Erreur lors du chargement de la session {date_str}: {e}")
        
        self.notify_observers('load')
    
    def to_dict(self) -> Dict:
        """Convertir toutes les sessions en dictionnaire"""
        return {date_str: session.to_dict() 
                for date_str, session in self.sessions.items()}
