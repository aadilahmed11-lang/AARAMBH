from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, Scheme, Partner, Application, Document
from ..auth import require_role

router=APIRouter(prefix="/api/admin",tags=["Admin"])

@router.get("/stats",dependencies=[Depends(require_role("admin"))])
def stats(db:Session=Depends(get_db)):
    return {
        "users":db.query(User).filter(User.role=="user").count(),
        "partners":db.query(Partner).count(),
        "schemes":db.query(Scheme).count(),
        "applications":db.query(Application).count(),
        "pending":db.query(Application).filter(Application.status.in_(["Submitted","Under Review","Document Verification"])).count(),
        "approved":db.query(Application).filter(Application.status=="Approved").count(),
        "rejected":db.query(Application).filter(Application.status=="Rejected").count(),
        "documents":db.query(Document).count(),
    }

@router.get("/applications",dependencies=[Depends(require_role("admin"))])
def applications(db:Session=Depends(get_db)):
    return db.query(Application).order_by(Application.created_at.desc()).all()

@router.get("/users",dependencies=[Depends(require_role("admin"))])
def users(db:Session=Depends(get_db)):
    return [{"id":u.id,"name":u.name,"email":u.email,"role":u.role,"created_at":u.created_at} for u in db.query(User).order_by(User.created_at.desc()).all()]

@router.get("/applications/{application_id}/detail",dependencies=[Depends(require_role("admin"))])
def application_detail(application_id:int,db:Session=Depends(get_db)):
    from ..models import EntrepreneurProfile, BusinessProfile, ApplicationStatusHistory, QRCodeRecord
    app=db.get(Application,application_id)
    if not app: raise HTTPException(404,"Application not found")
    user=db.get(User,app.user_id)
    profile=db.query(EntrepreneurProfile).filter_by(user_id=app.user_id).first()
    business=db.query(BusinessProfile).filter_by(user_id=app.user_id).first()
    docs=db.query(Document).filter_by(application_id=app.id).all()
    history=db.query(ApplicationStatusHistory).filter_by(application_id=app.id).order_by(ApplicationStatusHistory.created_at.asc()).all()
    qr=db.query(QRCodeRecord).filter_by(application_id=app.id).order_by(QRCodeRecord.created_at.desc()).first()
    return {"application":app,"applicant":user,"profile":profile,"business":business,"scheme":app.scheme,"partner":app.partner,"documents":docs,"history":history,"qr":qr}

@router.get('/partners',dependencies=[Depends(require_role('admin'))])
def partners(db:Session=Depends(get_db)):
    from ..models import PartnerAvailability
    av={a.partner_id:a for a in db.query(PartnerAvailability).all()}
    return [{'id':p.id,'name':p.name,'partner_type':p.partner_type,'address':p.address,'email':p.email,'active':p.active,
             'available':av.get(p.id).available if av.get(p.id) else False,
             'capacity':av.get(p.id).capacity if av.get(p.id) else 0,
             'verification_status':p.verification_status,'data_source':p.data_source,'source_url':p.source_url,'next_review_date':p.next_review_date} for p in db.query(Partner).order_by(Partner.id.asc()).all()]


@router.post("/schemes/{scheme_id}/verify", dependencies=[Depends(require_role("admin"))])
def verify_scheme(scheme_id:int, payload:dict, user=Depends(require_role("admin")), db:Session=Depends(get_db)):
    s=db.get(Scheme, scheme_id)
    if not s: raise HTTPException(404,"Scheme not found")
    s.verification_status="Verified"
    s.verified_at=__import__("datetime").datetime.utcnow()
    s.verified_by=user.id
    if payload.get("data_source") is not None: s.data_source=payload.get("data_source")
    if payload.get("next_review_date") is not None: s.next_review_date=payload.get("next_review_date")
    db.commit(); db.refresh(s); return s

@router.post("/partners/{partner_id}/verify", dependencies=[Depends(require_role("admin"))])
def verify_partner(partner_id:int, payload:dict, user=Depends(require_role("admin")), db:Session=Depends(get_db)):
    p=db.get(Partner, partner_id)
    if not p: raise HTTPException(404,"Partner not found")
    p.verification_status="Verified"
    p.verified_at=__import__("datetime").datetime.utcnow()
    p.verified_by=user.id
    if payload.get("data_source") is not None: p.data_source=payload.get("data_source")
    if payload.get("source_url") is not None: p.source_url=payload.get("source_url")
    if payload.get("next_review_date") is not None: p.next_review_date=payload.get("next_review_date")
    db.commit(); db.refresh(p); return p
