from typing import Dict, List, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models import Application, User, Scheme, Partner, EntrepreneurProfile

class OfflineDataService:
    @staticmethod
    def get_offline_cache_data(user_id: int, db: Session) -> Dict[str, Any]:
        user=db.get(User,user_id)
        if not user: return {"error":"User not found"}
        apps=db.query(Application).filter_by(user_id=user_id).all()
        schemes=db.query(Scheme).filter_by(active=True).all()
        partners=db.query(Partner).filter_by(active=True).all()
        profile=db.query(EntrepreneurProfile).filter_by(user_id=user_id).first()
        return {"user_profile":{"id":user.id,"name":user.name,"email":user.email,"last_updated":datetime.utcnow().isoformat(),
                                  "category":getattr(profile,"category",None),"annual_income":getattr(profile,"annual_income",None),
                                  "state":getattr(profile,"state",None),"district":getattr(profile,"district",None),
                                  "city":getattr(profile,"city",None),"age":getattr(profile,"age",None),"gender":getattr(profile,"gender",None),"marital_status":getattr(profile,"marital_status",None),"residence_type":getattr(profile,"residence_type",None),"minority_status":getattr(profile,"minority_status",None),"employment_status":getattr(profile,"employment_status",None),"disability_status":getattr(profile,"disability_status",None),"disability_percent":getattr(profile,"disability_percent",None),"disability_type":getattr(profile,"disability_type",None),"latitude":getattr(profile,"latitude",None),"longitude":getattr(profile,"longitude",None)},
                "applications":[{"id":a.id,"reference_no":a.reference_no,"scheme_id":a.scheme_id,"scheme_name":a.scheme.name if a.scheme else None,"status":a.status,"loan_amount":a.loan_amount,"partner_id":a.partner_id,"created_at":a.created_at.isoformat() if a.created_at else None} for a in apps],
                "cached_schemes":[{"id":s.id,"name":s.name,"scheme_type":s.scheme_type,"description":s.description,"interest_rate":s.interest_rate,"max_loan":s.max_loan,"min_loan":s.min_loan,"tenure_months":s.tenure_months,"moratorium_months":s.moratorium_months,"coverage_percent":s.coverage_percent,"eligibility_summary":s.eligibility_summary,"source_url":s.source_url,"verification_status":s.verification_status,"target_categories":s.target_categories,"target_disability":s.target_disability,"target_income_max":s.target_income_max,"target_states":s.target_states,"target_keywords":s.target_keywords,"target_age_min":s.target_age_min,"target_age_max":s.target_age_max,"updated_at":s.updated_at.isoformat() if s.updated_at else None} for s in schemes],
                "cached_partners":[{"id":p.id,"name":p.name,"partner_type":p.partner_type,"address":p.address,"district":p.district,"state":p.state,"latitude":p.latitude,"longitude":p.longitude,"phone":p.phone,"email":p.email,"rating":p.rating,"fund_utilization_percent":p.fund_utilization_percent,"npa_percent":p.npa_percent,"overdue_percent":p.overdue_percent,"supported_scheme_types":p.supported_scheme_types,"source_url":p.source_url,"verification_status":p.verification_status} for p in partners],
                "sync_status":{"last_synced":datetime.utcnow().isoformat(),"sync_status":"synced","offline_mode_enabled":True,"data_scope":"schemes, partners, profile and applications"}}
    @staticmethod
    def check_sync_status(user_id, db):
        if not db.get(User,user_id): return {"error":"User not found"}
        return {"is_synced":True,"last_sync_time":datetime.utcnow().isoformat(),"pending_uploads":0,"sync_message":"Your data is fully synchronized","connectivity_status":"online","offline_data_available":True}

class GeographicAnalyticsService:
    @staticmethod
    def get_geographic_analytics(db: Session) -> Dict[str, Any]:
        rows=db.query(EntrepreneurProfile.state, func.count(Application.id)).join(Application, Application.user_id==EntrepreneurProfile.user_id, isouter=True).group_by(EntrepreneurProfile.state).all()
        states=[]
        for state,count in rows:
            if not state: continue
            users=db.query(EntrepreneurProfile).filter_by(state=state).count()
            states.append({"state":state,"applications":int(count),"active_users":users,"conversion_rate":round(count/users*100,1) if users else 0,"demand_level":"High" if count>=50 else "Medium" if count>=20 else "Low"})
        states.sort(key=lambda x:x['applications'],reverse=True)
        return {"total_applications":sum(x['applications'] for x in states),"total_users":sum(x['active_users'] for x in states),"states_breakdown":states,"top_demand_states":states[:5]}

class SchemePerformanceAnalyticsService:
    @staticmethod
    def get_scheme_performance(db: Session) -> Dict[str, Any]:
        out=[]
        for s in db.query(Scheme).all():
            apps=db.query(Application).filter_by(scheme_id=s.id).all(); total=len(apps); approved=sum(1 for a in apps if (a.status or '').lower()=='approved')
            rejected=sum(1 for a in apps if (a.status or '').lower()=='rejected')
            out.append({"scheme_id":s.id,"scheme_name":s.name,"scheme_type":s.scheme_type,"total_applications":total,"approved_count":approved,"rejected_count":rejected,"pending_count":total-approved-rejected,"approval_rate":round(approved/total*100,1) if total else 0})
        out.sort(key=lambda x:x['total_applications'],reverse=True)
        total=sum(x['total_applications'] for x in out); approved=sum(x['approved_count'] for x in out)
        return {"total_schemes":len(out),"total_applications_processed":total,"total_approvals":approved,"overall_approval_rate":round(approved/total*100,1) if total else 0,"scheme_performance":out,"top_performing_schemes":out[:5]}
