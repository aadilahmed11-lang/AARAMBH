"""
Features 9 & 10: Scheme Comparison & Notification Center
"""
from typing import Dict, List, Any
from datetime import datetime
from sqlalchemy.orm import Session
from ..models import Scheme, Notification, SchemeDocument

class SchemeComparisonService:
    """Neutral side-by-side scheme comparison using actual catalogue fields."""

    @staticmethod
    def compare_schemes(scheme_ids: List[int], db: Session) -> Dict[str, Any]:
        schemes = [db.get(Scheme, sid) for sid in scheme_ids]
        schemes = [s for s in schemes if s and s.active]
        if not schemes:
            return {"error": "No active schemes found"}
        documents = {s.id: db.query(SchemeDocument).filter_by(scheme_id=s.id, required=True).all() for s in schemes}
        data = []
        for s in schemes:
            data.append({
                "id": s.id, "name": s.name, "scheme_type": s.scheme_type,
                "description": s.description, "min_loan": s.min_loan, "max_loan": s.max_loan,
                "interest_rate": s.interest_rate, "tenure_months": s.tenure_months,
                "moratorium_months": s.moratorium_months, "coverage_percent": s.coverage_percent,
                "max_project_cost": s.max_project_cost, "benefit_type": s.benefit_type,
                "eligibility_summary": s.eligibility_summary,
                "documents": [d.document_name for d in documents[s.id]],
                "source_url": s.source_url, "verification_status": s.verification_status,
                "updated_at": s.updated_at.isoformat() if s.updated_at else None,
            })
        return {"schemes": data, "comparison_note": "Comparison is informational. Final eligibility and terms are subject to the verified scheme rules and the authorized channel partner."}


class NotificationService:
    """Service for managing notifications"""
    
    @staticmethod
    def create_notification(
        user_id: int,
        notification_type: str,
        title: str,
        message: str,
        application_id: int = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """Create a new notification"""
        try:
            notification = Notification(
                user_id=user_id,
                title=title,
                message=message,
                created_at=datetime.utcnow(),
                read=False
            )
            db.add(notification)
            db.commit()
            return {
                "id": notification.id,
                "status": "created",
                "message": "Notification created successfully"
            }
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def get_user_notifications(
        user_id: int,
        db: Session,
        unread_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Get user notifications"""
        query = db.query(Notification).filter(Notification.user_id == user_id)
        
        if unread_only:
            query = query.filter(Notification.read == False)
        
        notifications = query.order_by(Notification.created_at.desc()).all()
        
        return [
            {
                "id": n.id,
                "type": "application_update",
                "title": n.title,
                "message": n.message,
                "application_id": None,
                "created_at": n.created_at.isoformat() if n.created_at else None,
                "is_read": n.read,
                "icon": NotificationService._get_notification_icon("application_update")
            }
            for n in notifications
        ]
    
    @staticmethod
    def mark_as_read(notification_id: int, db: Session) -> Dict[str, Any]:
        """Mark notification as read"""
        notification = db.query(Notification).filter(Notification.id == notification_id).first()
        if notification:
            notification.read = True
            db.commit()
            return {"status": "updated"}
        return {"error": "Notification not found"}
    
    @staticmethod
    def _get_notification_icon(notification_type: str) -> str:
        """Get icon for notification type"""
        icon_map = {
            "application_update": "📋",
            "document_request": "📄",
            "verification": "✓",
            "partner_action": "🏦",
            "decision": "✓",
            "reminder": "🔔",
            "alert": "⚠️"
        }
        return icon_map.get(notification_type, "🔔")
