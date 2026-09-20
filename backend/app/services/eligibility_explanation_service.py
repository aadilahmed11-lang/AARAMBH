from typing import Dict, Any
from sqlalchemy.orm import Session
from ..models import EntrepreneurProfile, Scheme, SchemeRule
from .eligibility_service import check_rules

class EligibilityExplanationService:
    @staticmethod
    def get_eligibility_explanation(user_id:int, scheme_id:int, db:Session)->Dict[str,Any]:
        profile=db.query(EntrepreneurProfile).filter_by(user_id=user_id).first(); scheme=db.get(Scheme,scheme_id)
        if not profile or not scheme: return {"error":"Profile or scheme not found"}
        rules=db.query(SchemeRule).filter_by(scheme_id=scheme.id).all(); result=check_rules(scheme,rules,profile)
        eligible=[x for x in result['reasons'] if not x.startswith(('Loan amount','Missing'))] if result['eligible'] else []
        return {"scheme_name":scheme.name,"is_eligible":result['eligible'],"eligible_reasons":eligible,"ineligible_reasons":[] if result['eligible'] else result['reasons'],
                "simple_explanation":("Your profile satisfies the configured prototype rules." if result['eligible'] else "Some requirements are missing or do not match this scheme."),
                "next_steps":["Review scheme details","Prepare required documents","Use the matched channel partner"]}
