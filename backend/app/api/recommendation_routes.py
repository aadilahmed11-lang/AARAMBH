from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Scheme, SchemeRule, Recommendation
from ..schemas import RecommendationIn, EligibilityIn
from ..auth import current_user
from ..services.recommendation_service import rank_schemes
from ..services.eligibility_service import check_rules
from ..services.ai_service import extract_profile_with_ai

router=APIRouter(prefix="/api/recommendations",tags=["Recommendations"])

@router.post("/rank")
def recommend(data:RecommendationIn,user=Depends(current_user),db:Session=Depends(get_db)):
    scheme_type = data.scheme_type if data.scheme_type in ("business", "education") else "business"
    schemes=db.query(Scheme).filter_by(active=True, scheme_type=scheme_type).all()
    rules={}
    for s in schemes: rules[s.id]=db.query(SchemeRule).filter_by(scheme_id=s.id).all()
    ranked=rank_schemes(data.profile,schemes,rules)
    db.query(Recommendation).filter_by(user_id=user.id).delete()
    for x in ranked:
        db.add(Recommendation(user_id=user.id,scheme_id=x["scheme"].id,match_score=x["score"],
                              rank=x["rank"],eligible=x["eligible"],reason=x["reason"]))
    db.commit()
    return [{"scheme":x["scheme"],"score":x["score"],"rank":x["rank"],
             "eligible":x["eligible"],"reason":x["reason"],
             "matching_factors":x.get("matching_factors",[]),"gaps":x.get("gaps",[])} for x in ranked]

@router.post("/eligibility")
def eligibility(data:EligibilityIn,user=Depends(current_user),db:Session=Depends(get_db)):
    s=db.get(Scheme,data.scheme_id)
    rules=db.query(SchemeRule).filter_by(scheme_id=s.id).all()
    profile=data.profile
    if profile is None:
        from ..models import EntrepreneurProfile
        profile=db.query(EntrepreneurProfile).filter_by(user_id=user.id).first()
    return check_rules(s,rules,profile)

@router.post("/extract-profile")
async def extract_profile(payload:dict,user=Depends(current_user)):
    return await extract_profile_with_ai(payload.get("text",""))
