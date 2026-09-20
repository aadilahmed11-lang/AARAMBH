from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth import current_user, require_role
from ..models import Application, BankVisitRequest, Notification, BusinessProfile, User

router=APIRouter(prefix="/api/workflow", tags=["Workflow"])

@router.put('/business')
def save_business(payload:dict,user=Depends(current_user),db:Session=Depends(get_db)):
    b=db.query(BusinessProfile).filter_by(user_id=user.id).first()
    if not b: b=BusinessProfile(user_id=user.id); db.add(b)
    for k in ['stage','business_type','industry','location','expected_investment','loan_purpose','business_idea']:
        if k in payload: setattr(b,k,payload[k])
    db.commit(); db.refresh(b); return b

@router.get('/notifications')
def notifications(user=Depends(current_user),db:Session=Depends(get_db)):
    return db.query(Notification).filter_by(user_id=user.id).order_by(Notification.created_at.desc()).limit(50).all()

@router.post('/applications/{application_id}/bank-visit')
def bank_visit(application_id:int,payload:dict,user=Depends(require_role('partner','admin')),db:Session=Depends(get_db)):
    app=db.get(Application,application_id)
    if not app: raise HTTPException(404,'Application not found')
    if not app.partner_id: raise HTTPException(400,'Application has no assigned partner')
    if user.role=='partner':
        from .partner_routes import get_assigned_partner
        partner=get_assigned_partner(user,db)
        if not partner or app.partner_id!=partner.id: raise HTTPException(403,'Application is not assigned to this partner')
    req=BankVisitRequest(application_id=app.id,partner_id=app.partner_id,requested_date=payload.get('date'),requested_time=payload.get('time'),location=payload.get('location'),status='Requested')
    app.status='Bank Visit Requested'
    db.add(req)
    db.add(Notification(user_id=app.user_id,title='Bank visit requested',message=f'Partner requested a bank visit for application {app.reference_no}.'))
    db.commit(); db.refresh(req); return req

@router.get('/applications/{application_id}/history')
def history(application_id:int,user=Depends(current_user),db:Session=Depends(get_db)):
    app=db.get(Application,application_id)
    if not app or (user.role=='user' and app.user_id!=user.id): raise HTTPException(403,'Access denied')
    from ..models import ApplicationStatusHistory
    return db.query(ApplicationStatusHistory).filter_by(application_id=application_id).order_by(ApplicationStatusHistory.created_at.asc()).all()
