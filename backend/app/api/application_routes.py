from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Application, ApplicationStatusHistory, QRCodeRecord, Partner, User, EntrepreneurProfile, PartnerAvailability, Scheme, Document
from ..schemas import ApplicationIn, StatusIn
from ..auth import current_user, require_role
from ..services.qr_service import create_qr_token, encode_qr_png
from ..services.partner_service import rank_partners

router=APIRouter(prefix="/api/applications",tags=["Applications"])

def ref():
    return "AAR-" + datetime.utcnow().strftime("%Y%m%d") + "-" + datetime.utcnow().strftime("%H%M%S%f")[-6:]


@router.post("/draft")
def create_draft(data:ApplicationIn,user=Depends(current_user),db:Session=Depends(get_db)):
    """Create a saved application shell before document upload. It stays Draft until final submission."""
    scheme=db.get(Scheme,data.scheme_id)
    if not scheme or not scheme.active: raise HTTPException(404,"Scheme not found or inactive")
    if scheme.max_loan and data.loan_amount > scheme.max_loan: raise HTTPException(400,f"Loan amount exceeds the scheme maximum of ₹{scheme.max_loan:,.0f}")
    if scheme.min_loan and data.loan_amount < scheme.min_loan: raise HTTPException(400,f"Loan amount is below the scheme minimum of ₹{scheme.min_loan:,.0f}")
    existing=db.query(Application).filter_by(user_id=user.id,scheme_id=scheme.id,status="Draft").order_by(Application.created_at.desc()).first()
    if existing:
        existing.loan_amount=data.loan_amount
        if data.partner_id: existing.partner_id=data.partner_id
        db.commit(); db.refresh(existing); return existing
    app=Application(reference_no=ref(),user_id=user.id,scheme_id=scheme.id,partner_id=data.partner_id,loan_amount=data.loan_amount,status="Draft",is_eligible=None)
    db.add(app); db.flush()
    db.add(ApplicationStatusHistory(application_id=app.id,status="Draft",remarks="Application saved; awaiting documents and partner selection.",updated_by=user.id))
    db.commit(); db.refresh(app); return app

@router.post("/{application_id}/submit")
def submit_saved_application(application_id:int,data:dict,user=Depends(current_user),db:Session=Depends(get_db)):
    app=db.get(Application,application_id)
    if not app or app.user_id!=user.id: raise HTTPException(404,"Saved application not found")
    if app.status not in ("Draft","More Information Required"): raise HTTPException(400,"This application is already submitted or closed")
    scheme=db.get(Scheme,app.scheme_id)
    partner_id=data.get("partner_id")
    if partner_id is None: raise HTTPException(400,"Select a partner before submission")
    partner=db.get(Partner,int(partner_id))
    if not partner or not partner.active: raise HTTPException(400,"Selected partner is unavailable")
    profile=db.query(EntrepreneurProfile).filter_by(user_id=user.id).first()
    if not profile or profile.latitude is None or profile.longitude is None: raise HTTPException(400,"Location is required before final submission")
    partners=db.query(Partner).filter_by(active=True).all(); av={a.partner_id:a for a in db.query(PartnerAvailability).all()}
    ranked=rank_partners(profile,partners,av,scheme.scheme_type,max_distance_km=50.0)
    if not any(x["partner"].id==partner.id for x in ranked): raise HTTPException(400,"Selected partner is not an eligible available partner within 50 km")
    app.partner_id=partner.id
    app.status="Submitted"
    app.is_eligible=True if data.get("is_eligible") is True else None
    db.add(ApplicationStatusHistory(application_id=app.id,status="Submitted",remarks="Application submitted to selected channel partner.",updated_by=user.id))
    db.commit(); db.refresh(app); return app

@router.post("/")
def create_application(data:ApplicationIn,user=Depends(current_user),db:Session=Depends(get_db)):
    scheme=db.get(Scheme,data.scheme_id)
    if not scheme or not scheme.active: raise HTTPException(404,"Scheme not found or inactive")
    if scheme.max_loan and data.loan_amount > scheme.max_loan: raise HTTPException(400,f"Loan amount exceeds the scheme maximum of ₹{scheme.max_loan:,.0f}")
    if scheme.min_loan and data.loan_amount < scheme.min_loan: raise HTTPException(400,f"Loan amount is below the scheme minimum of ₹{scheme.min_loan:,.0f}")
    profile=db.query(EntrepreneurProfile).filter_by(user_id=user.id).first()
    partner_id=data.partner_id
    if not partner_id and profile:
        partners=db.query(Partner).filter_by(active=True).all(); av={a.partner_id:a for a in db.query(PartnerAvailability).all()}
        ranked=rank_partners(profile,partners,av,scheme.scheme_type,max_distance_km=50.0)
        partner_id=ranked[0]["partner"].id if ranked else None
    app=Application(reference_no=ref(),user_id=user.id,scheme_id=scheme.id,partner_id=partner_id,loan_amount=data.loan_amount,status="Submitted",is_eligible=None)
    db.add(app); db.flush()
    db.add(ApplicationStatusHistory(application_id=app.id,status="Submitted",updated_by=user.id))
    db.commit(); db.refresh(app)
    return app

@router.get("/mine")
def mine(user=Depends(current_user),db:Session=Depends(get_db)):
    return db.query(Application).filter_by(user_id=user.id).order_by(Application.created_at.desc()).all()

@router.get("/{application_id}")
def get_application(application_id:int,user=Depends(current_user),db:Session=Depends(get_db)):
    app=db.get(Application,application_id)
    if not app: raise HTTPException(404,"Application not found")
    if user.role=="user" and app.user_id!=user.id: raise HTTPException(403,"Access denied")
    return app

@router.put("/{application_id}/status")
def status(application_id:int,data:StatusIn,user=Depends(require_role("partner","admin")),db:Session=Depends(get_db)):
    app=db.get(Application,application_id)
    if not app: raise HTTPException(404,"Application not found")
    app.status=data.status
    normalized=(data.status or "").lower()
    if normalized in ("under verification","document verification"): app.document_verified_at=datetime.utcnow()
    if normalized in ("under review","bank visit requested"): app.partner_review_at=datetime.utcnow()
    if normalized in ("approved","rejected","more information required"): app.decision_date=datetime.utcnow()
    db.add(ApplicationStatusHistory(application_id=app.id,status=data.status,remarks=data.remarks,updated_by=user.id))
    db.commit(); return app

@router.post("/{application_id}/qr")
def qr(application_id:int,user=Depends(current_user),db:Session=Depends(get_db)):
    app=db.get(Application,application_id)
    if not app: raise HTTPException(404,"Application not found")
    if user.role=="user" and app.user_id!=user.id: raise HTTPException(403,"Access denied")
    existing=db.query(QRCodeRecord).filter_by(application_id=app.id).order_by(QRCodeRecord.created_at.desc()).first()

    # Keep one persistent QR token per application. If a record already exists,
    # reuse it so refreshes/retries never create duplicate QR records.
    if existing:
        token=existing.qr_token
        if existing.expires_at and existing.expires_at <= datetime.utcnow():
            existing.expires_at=datetime.utcnow()+timedelta(days=30)
    else:
        token=create_qr_token()
        existing=QRCodeRecord(
            application_id=app.id,
            qr_token=token,
            expires_at=datetime.utcnow()+timedelta(days=30),
        )
        db.add(existing)

    db.commit()
    db.refresh(existing)

    import base64
    from ..config import FRONTEND_URL
    tracking_url=f"{FRONTEND_URL.rstrip('/')}/track?ref={app.reference_no}&token={token}"
    # Encode the exact tracking URL that contains the persisted token.
    png=encode_qr_png(tracking_url)
    return {"application_id":app.id,"reference_no":app.reference_no,"qr_token":token,"tracking_url":tracking_url,"qr_base64":base64.b64encode(png).decode()}

@router.get("/track")
def public_track(reference_no:str,token:str,db:Session=Depends(get_db)):
    record=db.query(QRCodeRecord).filter_by(qr_token=token).first()
    if not record or record.expires_at and record.expires_at<datetime.utcnow(): raise HTTPException(404,"Tracking code is invalid or expired")
    app=db.get(Application,record.application_id)
    if not app or app.reference_no!=reference_no: raise HTTPException(404,"Application not found")
    scheme=db.get(Scheme,app.scheme_id)
    docs=db.query(Document).filter_by(application_id=app.id).all()
    return {"application_id":app.id,"reference_no":app.reference_no,"status":app.status,"scheme_name":scheme.name if scheme else None,
            "created_at":app.created_at,"updated_at":app.updated_at,
            "documents":[{"document_type":d.document_type,"verification_status":d.verification_status or "Pending","ocr_status":d.ocr_status or "Pending"} for d in docs]}
