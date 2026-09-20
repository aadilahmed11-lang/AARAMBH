"""Smart channel-partner matching and application timeline services."""
from typing import Dict, List, Any
from datetime import datetime
from sqlalchemy.orm import Session
from ..models import Partner, PartnerAvailability, Application, Scheme, EntrepreneurProfile
from .partner_service import rank_partners


class PartnerMatchingService:
    @staticmethod
    def get_ranked_partners(user_id: int, scheme_id: int, user_location: str, db: Session) -> List[Dict[str, Any]]:
        scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()
        profile = db.query(EntrepreneurProfile).filter(EntrepreneurProfile.user_id == user_id).first()
        if not scheme or not profile:
            return []
        partners = db.query(Partner).filter_by(active=True).all()
        availability = {a.partner_id: a for a in db.query(PartnerAvailability).all()}
        ranked = rank_partners(profile, partners, availability, scheme.scheme_type, max_distance_km=50.0)
        return [{
            "partner_id": x["partner"].id,
            "partner_name": x["partner"].name,
            "partner_type": x["partner"].partner_type,
            "location": x["partner"].address,
            "contact_phone": x["partner"].phone,
            "contact_email": x["partner"].email,
            "rating": x["rating"],
            "match_score": x["score"],
            "distance_km": x["distance_km"],
            "availability": "Available",
            "capacity": x["capacity"],
            "fund_utilization_percent": x["fund_utilization_percent"],
            "npa_percent": x["npa_percent"],
            "processing_days": "7-10",
        } for x in ranked[:5]]


class TimelineService:
    @staticmethod
    def get_application_timeline(application_id: int, db: Session) -> Dict[str, Any]:
        app = db.query(Application).filter(Application.id == application_id).first()
        if not app:
            return {"error": "Application not found"}
        stages = [
            {"stage": "Submitted", "icon": "✓", "timestamp": app.created_at, "status": "completed", "description": "Application submitted successfully"},
            {"stage": "Document Verification", "icon": "📄", "timestamp": app.document_verified_at, "status": TimelineService._get_stage_status(app, "document_verification"), "description": "Verifying submitted documents"},
            {"stage": "Partner Review", "icon": "🔍", "timestamp": app.partner_review_at, "status": TimelineService._get_stage_status(app, "partner_review"), "description": "Channel partner reviewing the application"},
            {"stage": "Final Decision", "icon": "✓", "timestamp": app.decision_date, "status": TimelineService._get_stage_status(app, "final_decision"), "description": "Final decision on the application"},
        ]
        return {"application_id": application_id, "current_stage": TimelineService._get_current_stage(app),
                "overall_progress_percentage": TimelineService._calculate_progress(app), "timeline_stages": stages,
                "estimated_completion_days": TimelineService._estimate_completion_days(app)}

    @staticmethod
    def _get_stage_status(app, stage):
        s = (app.status or "").lower().replace(" ", "_")
        if s in ("submitted",): return "in_progress" if stage == "document_verification" else "pending"
        if s in ("document_verification", "under_verification"): return "completed" if stage == "document_verification" else "in_progress" if stage == "partner_review" else "pending"
        if s in ("under_review", "bank_visit_requested"): return "completed" if stage == "document_verification" else "in_progress" if stage == "partner_review" else "pending"
        if s == "approved": return "completed"
        if s == "rejected": return "failed"
        return "pending"

    @staticmethod
    def _get_current_stage(app):
        s = (app.status or "").lower().replace(" ", "_")
        return {"submitted": "Document Verification", "document_verification": "Document Verification", "under_verification": "Document Verification",
                "under_review": "Partner Review", "bank_visit_requested": "Partner Review", "approved": "Final Decision", "rejected": "Application Closed"}.get(s, "Submitted")

    @staticmethod
    def _calculate_progress(app):
        s = (app.status or "").lower().replace(" ", "_")
        return {"submitted": 25, "document_verification": 50, "under_verification": 50, "under_review": 75, "bank_visit_requested": 75, "approved": 100, "rejected": 100}.get(s, 0)

    @staticmethod
    def _estimate_completion_days(app):
        s = (app.status or "").lower().replace(" ", "_")
        return {"submitted": 7, "document_verification": 5, "under_verification": 5, "under_review": 3, "bank_visit_requested": 3, "approved": 0, "rejected": 0}.get(s, 14)
