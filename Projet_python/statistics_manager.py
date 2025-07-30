"""
Gestionnaire des Statistiques
Module pour calculer et analyser les statistiques de présence
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from attendance_manager import AttendanceStatus

class StudentStats:
    """Classe pour les statistiques d'un étudiant"""
    
    def __init__(self, student_id: str, student_name: str):
        self.student_id = student_id
        self.student_name = student_name
        self.total_sessions = 0
        self.present_count = 0
        self.absent_count = 0
        self.late_count = 0
        self.attendance_rate = 0.0
        self.punctuality_rate = 0.0  # Taux de ponctualité (présent à l'heure)
    
    def calculate_rates(self):
        """Calculer les taux de présence et de ponctualité"""
        if self.total_sessions > 0:
            self.attendance_rate = ((self.present_count + self.late_count) / self.total_sessions) * 100
            self.punctuality_rate = (self.present_count / self.total_sessions) * 100
        else:
            self.attendance_rate = 0.0
            self.punctuality_rate = 0.0
    
    def to_dict(self) -> Dict:
        """Convertir les statistiques en dictionnaire"""
        return {
            'student_id': self.student_id,
            'student_name': self.student_name,
            'total_sessions': self.total_sessions,
            'present_count': self.present_count,
            'absent_count': self.absent_count,
            'late_count': self.late_count,
            'attendance_rate': round(self.attendance_rate, 2),
            'punctuality_rate': round(self.punctuality_rate, 2)
        }

class StatisticsManager:
    """Gestionnaire pour les statistiques de présence"""
    
    def __init__(self, student_manager, attendance_manager):
        self.student_manager = student_manager
        self.attendance_manager = attendance_manager
        
        # Configuration pour les graphiques
        plt.style.use('default')
        self.colors = {
            'present': '#4CAF50',
            'absent': '#F44336',
            'late': '#FF9800',
            'primary': '#2196F3',
            'secondary': '#9C27B0'
        }
    
    def calculate_student_statistics(self, student_id: str) -> Optional[StudentStats]:
        """Calculer les statistiques pour un étudiant spécifique"""
        student = self.student_manager.get_student(student_id)
        if not student:
            return None
        
        stats = StudentStats(student_id, student.get_full_name())
        records = self.attendance_manager.get_student_attendance(student_id)
        
        stats.total_sessions = len(records)
        
        for record in records:
            if record.status == AttendanceStatus.PRESENT:
                stats.present_count += 1
            elif record.status == AttendanceStatus.ABSENT:
                stats.absent_count += 1
            elif record.status == AttendanceStatus.LATE:
                stats.late_count += 1
        
        stats.calculate_rates()
        return stats
    
    def calculate_all_student_statistics(self) -> List[StudentStats]:
        """Calculer les statistiques pour tous les étudiants"""
        stats_list = []
        
        for student in self.student_manager.get_all_students():
            stats = self.calculate_student_statistics(student.student_id)
            if stats:
                stats_list.append(stats)
        
        return stats_list
    
    def get_overall_statistics(self) -> Dict:
        """Calculer les statistiques générales"""
        all_stats = self.calculate_all_student_statistics()
        
        if not all_stats:
            return {
                'total_students': 0,
                'total_sessions': 0,
                'average_attendance_rate': 0.0,
                'average_punctuality_rate': 0.0,
                'best_student': None,
                'needs_attention': []
            }
        
        total_students = len(all_stats)
        total_sessions = len(self.attendance_manager.get_all_sessions())
        
        # Calculer les moyennes
        avg_attendance = sum(stats.attendance_rate for stats in all_stats) / total_students
        avg_punctuality = sum(stats.punctuality_rate for stats in all_stats) / total_students
        
        # Trouver le meilleur étudiant
        best_student = max(all_stats, key=lambda x: x.attendance_rate)
        
        # Étudiants ayant besoin d'attention (taux de présence < 70%)
        needs_attention = [stats for stats in all_stats if stats.attendance_rate < 70]
        needs_attention.sort(key=lambda x: x.attendance_rate)
        
        return {
            'total_students': total_students,
            'total_sessions': total_sessions,
            'average_attendance_rate': round(avg_attendance, 2),
            'average_punctuality_rate': round(avg_punctuality, 2),
            'best_student': best_student,
            'needs_attention': needs_attention
        }
    
    def rank_students_by_attendance(self) -> List[StudentStats]:
        """Classer les étudiants par taux de présence"""
        all_stats = self.calculate_all_student_statistics()
        return sorted(all_stats, key=lambda x: x.attendance_rate, reverse=True)
    
    def rank_students_by_punctuality(self) -> List[StudentStats]:
        """Classer les étudiants par taux de ponctualité"""
        all_stats = self.calculate_all_student_statistics()
        return sorted(all_stats, key=lambda x: x.punctuality_rate, reverse=True)
    
    def get_attendance_trends(self, days: int = 30) -> Dict:
        """Analyser les tendances de présence sur les derniers jours"""
        sessions = self.attendance_manager.get_all_sessions()
        if not sessions:
            return {'dates': [], 'attendance_rates': [], 'student_counts': []}
        
        # Trier les sessions par date
        sessions.sort(key=lambda x: x.date)
        
        # Prendre les dernières sessions
        recent_sessions = sessions[-days:] if len(sessions) > days else sessions
        
        dates = []
        attendance_rates = []
        student_counts = []
        
        for session in recent_sessions:
            dates.append(session.date)
            
            records = session.get_all_records()
            if records:
                present_count = sum(1 for r in records 
                                  if r.status in [AttendanceStatus.PRESENT, AttendanceStatus.LATE])
                rate = (present_count / len(records)) * 100
                attendance_rates.append(rate)
                student_counts.append(len(records))
            else:
                attendance_rates.append(0)
                student_counts.append(0)
        
        return {
            'dates': dates,
            'attendance_rates': attendance_rates,
            'student_counts': student_counts
        }
    
    def create_attendance_pie_chart(self, parent_frame) -> tk.Frame:
        """Créer un graphique en secteurs pour les statistiques générales"""
        # Calculer les données
        overall_stats = self.get_overall_statistics()
        all_student_stats = self.calculate_all_student_statistics()
        
        if not all_student_stats:
            # Créer un frame vide avec un message
            empty_frame = tk.Frame(parent_frame)
            tk.Label(empty_frame, text="Aucune donnée disponible", 
                    font=('Arial', 12)).pack(expand=True)
            return empty_frame
        
        # Calculer les totaux
        total_present = sum(stats.present_count for stats in all_student_stats)
        total_absent = sum(stats.absent_count for stats in all_student_stats)
        total_late = sum(stats.late_count for stats in all_student_stats)
        
        # Créer le graphique
        fig, ax = plt.subplots(figsize=(8, 6))
        
        labels = ['Présent', 'Absent', 'En retard']
        sizes = [total_present, total_absent, total_late]
        colors = [self.colors['present'], self.colors['absent'], self.colors['late']]
        
        # Filtrer les valeurs nulles
        filtered_data = [(label, size, color) for label, size, color in zip(labels, sizes, colors) if size > 0]
        
        if filtered_data:
            labels, sizes, colors = zip(*filtered_data)
            wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, 
                                            autopct='%1.1f%%', startangle=90)
            
            # Améliorer l'apparence
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
        
        ax.set_title('Répartition Globale des Présences', fontsize=14, fontweight='bold')
        
        # Créer le frame et le canvas
        chart_frame = tk.Frame(parent_frame)
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        plt.close(fig)  # Fermer la figure pour libérer la mémoire
        return chart_frame
    
    def create_student_comparison_chart(self, parent_frame, top_n: int = 10) -> tk.Frame:
        """Créer un graphique comparatif des étudiants"""
        # Obtenir les données
        ranked_students = self.rank_students_by_attendance()[:top_n]
        
        if not ranked_students:
            empty_frame = tk.Frame(parent_frame)
            tk.Label(empty_frame, text="Aucune donnée disponible", 
                    font=('Arial', 12)).pack(expand=True)
            return empty_frame
        
        # Créer le graphique
        fig, ax = plt.subplots(figsize=(12, 8))
        
        names = [stats.student_name for stats in ranked_students]
        attendance_rates = [stats.attendance_rate for stats in ranked_students]
        
        bars = ax.bar(names, attendance_rates, color=self.colors['primary'], alpha=0.7)
        
        # Ajouter les valeurs sur les barres
        for bar, rate in zip(bars, attendance_rates):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                   f'{rate:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        ax.set_ylabel('Taux de Présence (%)', fontweight='bold')
        ax.set_title(f'Top {len(ranked_students)} - Taux de Présence par Étudiant', 
                    fontsize=14, fontweight='bold')
        ax.set_ylim(0, 105)
        
        # Rotation des noms pour une meilleure lisibilité
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Créer le frame et le canvas
        chart_frame = tk.Frame(parent_frame)
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        plt.close(fig)
        return chart_frame
    
    def create_trends_chart(self, parent_frame, days: int = 30) -> tk.Frame:
        """Créer un graphique des tendances de présence"""
        trends = self.get_attendance_trends(days)
        
        if not trends['dates']:
            empty_frame = tk.Frame(parent_frame)
            tk.Label(empty_frame, text="Aucune donnée de tendance disponible", 
                    font=('Arial', 12)).pack(expand=True)
            return empty_frame
        
        # Créer le graphique
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        dates = trends['dates']
        
        # Graphique 1: Taux de présence
        ax1.plot(dates, trends['attendance_rates'], marker='o', 
                color=self.colors['primary'], linewidth=2, markersize=6)
        ax1.set_ylabel('Taux de Présence (%)', fontweight='bold')
        ax1.set_title('Évolution du Taux de Présence', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(0, 105)
        
        # Graphique 2: Nombre d'étudiants
        ax2.bar(dates, trends['student_counts'], color=self.colors['secondary'], alpha=0.7)
        ax2.set_ylabel('Nombre d\'Étudiants', fontweight='bold')
        ax2.set_xlabel('Date', fontweight='bold')
        ax2.set_title('Nombre d\'Étudiants par Session', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        # Améliorer l'affichage des dates
        for ax in [ax1, ax2]:
            ax.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        # Créer le frame et le canvas
        chart_frame = tk.Frame(parent_frame)
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        plt.close(fig)
        return chart_frame
    
    def export_statistics_report(self, filepath: str) -> bool:
        """Exporter un rapport complet des statistiques"""
        try:
            # Collecter toutes les données
            overall_stats = self.get_overall_statistics()
            all_student_stats = self.calculate_all_student_statistics()
            ranked_students = self.rank_students_by_attendance()
            
            report = {
                'generated_date': datetime.now().isoformat(),
                'overall_statistics': overall_stats,
                'student_statistics': [stats.to_dict() for stats in all_student_stats],
                'ranking_by_attendance': [stats.to_dict() for stats in ranked_students],
                'trends': self.get_attendance_trends()
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'export du rapport: {e}")
            return False
    
    def get_attendance_calendar_data(self, student_id: str = None) -> Dict:
        """Obtenir les données pour un calendrier de présence"""
        if student_id:
            records = self.attendance_manager.get_student_attendance(student_id)
        else:
            # Données globales
            records = []
            for session in self.attendance_manager.get_all_sessions():
                records.extend(session.get_all_records())
        
        calendar_data = {}
        for record in records:
            date_str = record.date
            if date_str not in calendar_data:
                calendar_data[date_str] = {
                    'present': 0,
                    'absent': 0,
                    'late': 0,
                    'total': 0
                }
            
            calendar_data[date_str]['total'] += 1
            if record.status == AttendanceStatus.PRESENT:
                calendar_data[date_str]['present'] += 1
            elif record.status == AttendanceStatus.ABSENT:
                calendar_data[date_str]['absent'] += 1
            elif record.status == AttendanceStatus.LATE:
                calendar_data[date_str]['late'] += 1
        
        return calendar_data
