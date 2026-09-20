from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Partner, PartnerAvailability, EntrepreneurProfile, Application, User, BusinessProfile, Document, ApplicationStatusHistory, Scheme
from ..auth import current_user, require_role
from ..services.partner_service import rank_partners

router=APIRouter(prefix="/api/partners",tags=["Partners"])

def get_assigned_partner(user, db):
    # Partner accounts are linked to a channel partner by the partner email.
    partner=db.query(Partner).filter(Partner.email==user.email, Partner.active==True).first()
    if not partner:
        # Backward-compatible demo fallback for the seeded partner account.
        if user.email == "partner@aarambh.local":
            partner=db.query(Partner).filter_by(active=True).order_by(Partner.id.asc()).first()
    return partner

@router.get("/nearby")
def nearby(scheme_type: str = "business", scheme_id: int | None = None, max_distance_km: float = 50.0, user=Depends(current_user), db:Session=Depends(get_db)):
    profile=db.query(EntrepreneurProfile).filter_by(user_id=user.id).first()
    if not profile or profile.latitude is None or profile.longitude is None:
        return []
    partners=db.query(Partner).filter_by(active=True).all()
    av={a.partner_id:a for a in db.query(PartnerAvailability).all()}
    scheme=db.get(Scheme, scheme_id) if scheme_id else None
    effective_type=scheme.scheme_type if scheme else (scheme_type if scheme_type in ("business","education") else "business")
    radius=max(1.0,min(float(max_distance_km),50.0))
    ranked=rank_partners(profile,partners,av,effective_type,max_distance_km=radius)
    rate=float(scheme.interest_rate) if scheme else None
    return [{
        "partner": x["partner"], "distance_km": x["distance_km"], "score": x["score"],
        "capacity": x["capacity"], "fund_utilization_percent": x["fund_utilization_percent"],
        "npa_percent": x["npa_percent"], "overdue_percent": x["partner"].overdue_percent,
        "rating": x["rating"], "interest_rate": rate, "scheme_id": scheme.id if scheme else None,
        "directions_url": f"https://www.google.com/maps/dir/?api=1&destination={x['partner'].latitude},{x['partner'].longitude}"
    } for x in ranked]

@router.put("/{partner_id}/availability",dependencies=[Depends(require_role("admin"))])
def set_availability(partner_id:int,payload:dict,db:Session=Depends(get_db)):
    a=db.query(PartnerAvailability).filter_by(partner_id=partner_id).first()
    if not a: a=PartnerAvailability(partner_id=partner_id); db.add(a)
    a.available=bool(payload.get("available",True)); a.capacity=int(payload.get("capacity",20))
    db.commit(); db.refresh(a); return a

@router.get('/applications')
def partner_applications(user=Depends(require_role('partner')),db:Session=Depends(get_db)):
    partner=get_assigned_partner(user,db)
    if not partner: return []
    apps=db.query(Application).filter(Application.partner_id==partner.id).order_by(Application.created_at.desc()).all()
    return apps

@router.get('/applications/{application_id}')
def partner_application(application_id:int,user=Depends(require_role('partner')),db:Session=Depends(get_db)):
    partner=get_assigned_partner(user,db)
    app=db.get(Application,application_id)
    if not app or not partner or app.partner_id!=partner.id:
        raise HTTPException(404,'Assigned application not found')
    applicant=db.get(User,app.user_id)
    profile=db.query(EntrepreneurProfile).filter_by(user_id=app.user_id).first()
    business=db.query(BusinessProfile).filter_by(user_id=app.user_id).first()
    docs=db.query(Document).filter_by(application_id=app.id).all()
    history=db.query(ApplicationStatusHistory).filter_by(application_id=app.id).order_by(ApplicationStatusHistory.created_at.asc()).all()
    scheme=db.get(Scheme,app.scheme_id)
    return {"application":app,"applicant":applicant,"profile":profile,"business":business,"documents":docs,"history":history,"partner":partner,"scheme":scheme}

@router.post('/applications/{application_id}/status')
def partner_status(application_id:int,payload:dict,user=Depends(require_role('partner')),db:Session=Depends(get_db)):
    partner=get_assigned_partner(user,db)
    app=db.get(Application,application_id)
    if not app or not partner or app.partner_id!=partner.id:
        raise HTTPException(404,'Assigned application not found')
    status=str(payload.get('status','')).strip()
    allowed={'Under Review','Document Verification','Approved','Rejected','More Information Required'}
    if status not in allowed: raise HTTPException(400,'Invalid partner status')
    remarks=payload.get('remarks')
    if status=='Rejected' and not remarks: raise HTTPException(400,'Rejection reason is required')
    app.status=status
    db.add(ApplicationStatusHistory(application_id=app.id,status=status,remarks=remarks,updated_by=user.id))
    db.commit(); db.refresh(app); return app
