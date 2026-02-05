"""
Intelligent Auto-Assignment Service for Teacher Substitution
Automatically finds and assigns the best substitute teacher based on multiple criteria.
"""

from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime

from app.infrastructure import models


class SubstituteScorer:
    """Calculate scores for potential substitute teachers"""
    
    # Configurable weights for scoring algorithm
    WEIGHTS = {
        "availability": 100,
        "subject_expertise": 80,
        "workload_balance": 50,
        "same_department": 30,
    }
    
    def __init__(self, db: Session, version_id: int):
        self.db = db
        self.version_id = version_id
    
    def score_substitute(
        self,
        candidate_id: int,
        required_time_slots: List[int],
        required_subjects: List[str],
        max_hours_threshold: int = 18
    ) -> Dict:
        """
        Calculate a score for a potential substitute teacher.
        
        Returns:
            Dict with score, breakdown, and availability info
        """
        candidate = self.db.query(models.Teacher).filter(
            models.Teacher.id == candidate_id
        ).first()
        
        if not candidate:
            return {"score": 0, "available": False, "reason": "Teacher not found"}
        
        # Check availability for all required time slots
        is_available, conflicting_slots = self._check_availability(
            candidate_id, required_time_slots
        )
        
        if not is_available:
            return {
                "teacher_id": candidate_id,
                "teacher_name": candidate.name,
                "score": 0,
                "available": False,
                "reason": f"Busy in {len(conflicting_slots)} slots",
                "conflicting_slots": conflicting_slots
            }
        
        # Calculate individual scores
        availability_score = self.WEIGHTS["availability"]  # Full points if available
        
        subject_score = self._calculate_subject_expertise_score(
            candidate_id, required_subjects
        )
        
        workload_score = self._calculate_workload_score(
            candidate_id, max_hours_threshold
        )
        
        # Total score
        total_score = availability_score + subject_score + workload_score
        
        # Get current workload info
        current_workload = self._get_teacher_workload(candidate_id)
        
        return {
            "teacher_id": candidate_id,
            "teacher_name": candidate.name,
            "score": total_score,
            "available": True,
            "breakdown": {
                "availability": availability_score,
                "subject_expertise": subject_score,
                "workload_balance": workload_score,
            },
            "current_workload": current_workload,
            "max_hours": candidate.max_hours_per_week,
            "teaches_same_subject": subject_score > 0
        }
    
    def _check_availability(
        self, 
        teacher_id: int, 
        time_slot_ids: List[int]
    ) -> Tuple[bool, List[int]]:
        """Check if teacher is free during all required time slots"""
        conflicting = self.db.query(models.TimetableEntry.time_slot_id).filter(
            models.TimetableEntry.version_id == self.version_id,
            models.TimetableEntry.teacher_id == teacher_id,
            models.TimetableEntry.time_slot_id.in_(time_slot_ids)
        ).all()
        
        conflicting_slots = [slot[0] for slot in conflicting]
        is_available = len(conflicting_slots) == 0
        
        return is_available, conflicting_slots
    
    def _calculate_subject_expertise_score(
        self, 
        teacher_id: int, 
        required_subjects: List[str]
    ) -> float:
        """Calculate score based on subject expertise match"""
        teacher_subjects = self.db.query(models.Subject).filter(
            models.Subject.teacher_id == teacher_id
        ).all()
        
        teacher_subject_names = {s.name.lower() for s in teacher_subjects}
        required_subject_names = {s.lower() for s in required_subjects}
        
        # Check for exact or partial matches
        exact_matches = teacher_subject_names & required_subject_names
        
        if exact_matches:
            # Full expertise score if they teach the exact subject
            return self.WEIGHTS["subject_expertise"]
        
        # Partial credit for related subjects (e.g., "ML Lab" and "Machine Learning")
        for ts in teacher_subject_names:
            for rs in required_subject_names:
                if ts in rs or rs in ts:
                    return self.WEIGHTS["subject_expertise"] * 0.7
        
        return 0
    
    def _calculate_workload_score(
        self, 
        teacher_id: int, 
        max_hours_threshold: int
    ) -> float:
        """Calculate score based on current workload (prefer less busy teachers)"""
        teacher = self.db.query(models.Teacher).filter(
            models.Teacher.id == teacher_id
        ).first()
        
        current_classes = self.db.query(models.TimetableEntry).filter(
            models.TimetableEntry.version_id == self.version_id,
            models.TimetableEntry.teacher_id == teacher_id
        ).count()
        
        # Calculate utilization percentage
        max_hours = teacher.max_hours_per_week if teacher else max_hours_threshold
        utilization = (current_classes / max_hours) * 100
        
        # Score inversely proportional to workload
        # Teacher at 0% utilization gets full score
        # Teacher at 100% utilization gets 0 score
        workload_score = self.WEIGHTS["workload_balance"] * (1 - (utilization / 100))
        
        return max(0, workload_score)
    
    def _get_teacher_workload(self, teacher_id: int) -> int:
        """Get current number of classes for teacher"""
        return self.db.query(models.TimetableEntry).filter(
            models.TimetableEntry.version_id == self.version_id,
            models.TimetableEntry.teacher_id == teacher_id
        ).count()


class AutoAssignmentService:
    """Main service for auto-assigning substitute teachers"""
    
    def __init__(self, db: Session):
        self.db = db
        self.latest_version = self._get_latest_version()
        if self.latest_version:
            self.scorer = SubstituteScorer(db, self.latest_version.id)
        else:
            self.scorer = None
    
    def _get_latest_version(self) -> Optional[models.TimetableVersion]:
        """Get the latest active timetable version"""
        return self.db.query(models.TimetableVersion).order_by(
            models.TimetableVersion.created_at.desc()
        ).first()
    
    def auto_assign_substitutes(
        self,
        teacher_id: int,
        date: str,
        auto_notify: bool = False
    ) -> Dict:
        """
        Automatically assign substitutes for all classes of an absent teacher.
        
        Args:
            teacher_id: ID of the absent teacher
            date: Date of absence (YYYY-MM-DD)
            auto_notify: Whether to send notifications (placeholder for now)
        
        Returns:
            Dict with assignment results and details
        """
        if not self.latest_version:
            return {
                "success": False,
                "error": "No timetable found. Please generate a timetable first."
            }
        
        # Get absent teacher info
        absent_teacher = self.db.query(models.Teacher).filter(
            models.Teacher.id == teacher_id
        ).first()
        
        if not absent_teacher:
            return {
                "success": False,
                "error": f"Teacher with ID {teacher_id} not found"
            }
        
        # Find all classes taught by this teacher
        entries = self.db.query(models.TimetableEntry).filter(
            models.TimetableEntry.version_id == self.latest_version.id,
            models.TimetableEntry.teacher_id == teacher_id
        ).all()
        
        if not entries:
            return {
                "success": True,
                "teacher_name": absent_teacher.name,
                "date": date,
                "affected_classes": 0,
                "assignments": [],
                "message": "No classes found for this teacher"
            }
        
        # Collect required time slots and subjects
        time_slot_ids = [entry.time_slot_id for entry in entries]
        subject_ids = list(set([entry.subject_id for entry in entries]))
        
        subjects = self.db.query(models.Subject).filter(
            models.Subject.id.in_(subject_ids)
        ).all()
        required_subjects = [s.name for s in subjects]
        
        # Get all potential substitutes (all teachers except the absent one)
        all_teachers = self.db.query(models.Teacher).filter(
            models.Teacher.id != teacher_id
        ).all()
        
        # Score all candidates
        scored_candidates = []
        for candidate in all_teachers:
            score_result = self.scorer.score_substitute(
                candidate.id,
                time_slot_ids,
                required_subjects,
                max_hours_threshold=18
            )
            if score_result.get("available", False):
                scored_candidates.append(score_result)
        
        # Sort by score (highest first)
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        
        # Assign the best substitute to all classes
        assignments = []
        
        if scored_candidates:
            best_substitute = scored_candidates[0]
            
            for entry in entries:
                # Create substitution record
                substitution = models.Substitution(
                    date=date,
                    timetable_entry_id=entry.id,
                    original_teacher_id=teacher_id,
                    substitute_teacher_id=best_substitute["teacher_id"],
                    status="confirmed"  # Auto-confirmed for now
                )
                self.db.add(substitution)
                
                # Get class details
                subject = self.db.query(models.Subject).filter(
                    models.Subject.id == entry.subject_id
                ).first()
                time_slot = self.db.query(models.TimeSlot).filter(
                    models.TimeSlot.id == entry.time_slot_id
                ).first()
                class_group = self.db.query(models.ClassGroup).filter(
                    models.ClassGroup.id == entry.class_group_id
                ).first()
                room = self.db.query(models.Room).filter(
                    models.Room.id == entry.room_id
                ).first()
                
                assignments.append({
                    "subject": subject.name if subject else "Unknown",
                    "time_slot": f"{time_slot.day} {time_slot.start_time}-{time_slot.end_time}" if time_slot else "Unknown",
                    "class_group": class_group.name if class_group else "Unknown",
                    "room": room.name if room else "Unknown",
                    "substitute_teacher": best_substitute["teacher_name"],
                    "confidence_score": best_substitute["score"]
                })
            
            self.db.commit()
            
            return {
                "success": True,
                "teacher_name": absent_teacher.name,
                "date": date,
                "affected_classes": len(entries),
                "substitute_assigned": best_substitute["teacher_name"],
                "substitute_id": best_substitute["teacher_id"],
                "confidence_score": best_substitute["score"],
                "score_breakdown": best_substitute["breakdown"],
                "assignments": assignments,
                "alternative_substitutes": scored_candidates[1:4],  # Top 3 alternatives
                "notification_sent": auto_notify  # Placeholder
            }
        else:
            # No available substitute found - mark classes as cancelled
            for entry in entries:
                substitution = models.Substitution(
                    date=date,
                    timetable_entry_id=entry.id,
                    original_teacher_id=teacher_id,
                    substitute_teacher_id=None,
                    status="cancelled"
                )
                self.db.add(substitution)
            
            self.db.commit()
            
            return {
                "success": False,
                "teacher_name": absent_teacher.name,
                "date": date,
                "affected_classes": len(entries),
                "error": "No available substitute teachers found",
                "message": "All classes have been marked as cancelled",
                "reason": "All potential substitutes are busy during these time slots"
            }
    
    def get_ranked_suggestions(
        self,
        entry_id: int,
        top_n: int = 5
    ) -> List[Dict]:
        """
        Get ranked substitute suggestions for a specific class entry.
        
        Args:
            entry_id: Timetable entry ID
            top_n: Number of top suggestions to return
        
        Returns:
            List of ranked substitute suggestions
        """
        if not self.latest_version:
            return []
        
        # Get the entry
        entry = self.db.query(models.TimetableEntry).filter(
            models.TimetableEntry.id == entry_id
        ).first()
        
        if not entry:
            return []
        
        # Get subject info
        subject = self.db.query(models.Subject).filter(
            models.Subject.id == entry.subject_id
        ).first()
        
        required_subjects = [subject.name] if subject else []
        time_slot_ids = [entry.time_slot_id]
        
        # Get all teachers except the current one
        all_teachers = self.db.query(models.Teacher).filter(
            models.Teacher.id != entry.teacher_id
        ).all()
        
        # Score all candidates
        scored_candidates = []
        for candidate in all_teachers:
            score_result = self.scorer.score_substitute(
                candidate.id,
                time_slot_ids,
                required_subjects
            )
            scored_candidates.append(score_result)
        
        # Sort by score and return top N
        scored_candidates.sort(key=lambda x: x.get("score", 0), reverse=True)
        return scored_candidates[:top_n]
