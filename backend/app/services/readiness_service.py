from typing import Dict, List, Any
from sqlalchemy.orm import Session
from ..models import User, EntrepreneurProfile, Application, Document, SchemeDocument

class ReadinessService:
    @staticmethod
    def get_application_readiness(user_id: int, application_id: int, db: Session) -> Dict[str, Any]:
        user = db.get(User, user_id); app = db.get(Application, application_id)
        if not user or not app: return {"error": "User or application not found"}
        profile = db.query(EntrepreneurProfile).filter_by(user_id=user_id).first()
        profile_score = ReadinessService._profile_completion(profile)
        doc = ReadinessService.get_document_readiness(user_id, application_id, db)
        eligibility = 100 if app.is_eligible is True else 50 if app.is_eligible is None else 0
        financial = ReadinessService._financial_completion(profile, app.scheme.scheme_type if app.scheme else "business")
        score = profile_score*.25 + eligibility*.25 + doc["overall_score"]*.30 + financial*.20
        components = [
            {"name":"Profile Information","percentage":profile_score,"weight":25,"status":"Complete" if profile_score==100 else "Incomplete"},
            {"name":"Eligibility","percentage":eligibility,"weight":25,"status":"Eligible" if eligibility==100 else "Check eligibility"},
            {"name":"Documents","percentage":doc["overall_score"],"weight":30,"status":f'{doc["uploaded"]}/{doc["total_required"]} uploaded'},
            {"name":"Financial / Course Details","percentage":financial,"weight":20,"status":"Complete" if financial==100 else "Incomplete"},
        ]
        return {"overall_readiness_score": round(score), "readiness_level": ReadinessService._level(score), "components": components,
                "recommended_actions":[f'Complete {c["name"]} ({c["percentage"]}% done)' for c in components if c["percentage"]<100][:3]}

    @staticmethod
    def get_document_readiness(user_id: int, application_id: int, db: Session) -> Dict[str, Any]:
        app = db.get(Application, application_id)
        if not app: return {"error":"Application not found"}
        required = db.query(SchemeDocument).filter_by(scheme_id=app.scheme_id, required=True).all()
        docs = db.query(Document).filter_by(application_id=application_id).all()
        uploaded_types = {d.document_type.lower() for d in docs if d.file_path}
        uploaded = len([d for d in docs if d.file_path])
        verified = len([d for d in docs if (d.verification_status or '').lower() == 'verified'])
        missing = max(0, len(required)-uploaded)
        score = (verified/len(required)*100) if required else (100 if uploaded else 0)
        return {"overall_score":round(score),"total_required":len(required),"uploaded":uploaded,"verified":verified,"missing":missing,
                "needs_correction":len([d for d in docs if (d.verification_status or '').lower()=='needs_correction']),
                "status_breakdown":{"uploaded":uploaded,"verified":verified,"missing":missing},
                "required_documents":[{"name":d.document_name,"type":d.document_type,"uploaded":d.document_type.lower() in uploaded_types} for d in required]}

    @staticmethod
    def _profile_completion(p):
        if not p: return 0
        fields=['category','annual_income','state','district','city']
        done=sum(1 for f in fields if getattr(p,f,None) not in (None,''))
        return round(done/len(fields)*100)

    @staticmethod
    def _financial_completion(p, scheme_type):
        if not p: return 0
        fields=['annual_income'] + (['business_type','loan_amount'] if scheme_type=='business' else ['education_level','course_type','institution','course_fee'])
        done=sum(1 for f in fields if getattr(p,f,None) not in (None,''))
        return round(done/len(fields)*100)

    @staticmethod
    def _level(score):
        return 'Ready to Submit' if score>=90 else 'Almost Ready' if score>=75 else 'More Information Needed' if score>=50 else 'Getting Started'
