import os, json, uuid
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Document, Application
from ..auth import current_user
from ..config import UPLOAD_DIR
from ..services.ocr_service import extract_text, basic_fields

router=APIRouter(prefix="/api/documents",tags=["Documents"])

@router.post("/upload")
def upload(application_id:int=Form(...),document_type:str=Form(...),file:UploadFile=File(...),
           user=Depends(current_user),db:Session=Depends(get_db)):
    app=db.get(Application,application_id)
    if not app or (user.role=="user" and app.user_id!=user.id):
        raise HTTPException(403,"Access denied")
    os.makedirs(UPLOAD_DIR,exist_ok=True)
    ext=os.path.splitext(file.filename or "")[1].lower()
    path=os.path.join(UPLOAD_DIR,f"{uuid.uuid4().hex}{ext}")
    with open(path,"wb") as f: f.write(file.file.read())
    doc=Document(application_id=application_id,document_type=document_type,file_path=path)
    try:
        text=extract_text(path)
        doc.ocr_status="Completed"
        doc.extracted_data=json.dumps(basic_fields(text))
    except Exception as e:
        doc.ocr_status="Unavailable"
        doc.extracted_data=json.dumps({"message":"OCR unavailable; manual verification required."})
    db.add(doc); db.commit(); db.refresh(doc)
    return doc

@router.get("/{application_id}")
def docs(application_id:int,user=Depends(current_user),db:Session=Depends(get_db)):
    app=db.get(Application,application_id)
    if not app or (user.role=="user" and app.user_id!=user.id): raise HTTPException(403,"Access denied")
    return db.query(Document).filter_by(application_id=application_id).all()

@router.post('/{document_id}/verify')
def verify_document(document_id:int,user=Depends(current_user),db:Session=Depends(get_db)):
    doc=db.get(Document,document_id)
    if not doc: raise HTTPException(404,'Document not found')
    app=db.get(Application,doc.application_id)
    if not app: raise HTTPException(404,'Application not found')
    if user.role=='user' and app.user_id!=user.id: raise HTTPException(403,'Access denied')
    if user.role=='partner':
        from .partner_routes import get_assigned_partner
        partner=get_assigned_partner(user,db)
        if not partner or app.partner_id!=partner.id: raise HTTPException(403,'Document is not assigned to this partner')
    if user.role not in ('user','partner','admin'): raise HTTPException(403,'Access denied')
    doc.verification_status='Verified'
    db.commit(); db.refresh(doc); return doc

@router.get('/{document_id}/file')
def document_file(document_id:int,user=Depends(current_user),db:Session=Depends(get_db)):
    doc=db.get(Document,document_id)
    if not doc: raise HTTPException(404,'Document not found')
    app=db.get(Application,doc.application_id)
    if not app: raise HTTPException(404,'Application not found')
    allowed=app.user_id==user.id
    if user.role=='partner':
        from .partner_routes import get_assigned_partner
        partner=get_assigned_partner(user,db)
        allowed=bool(partner and app.partner_id==partner.id)
    elif user.role=='admin':
        allowed=True
    if not allowed: raise HTTPException(403,'Access denied')
    if not doc.file_path or not os.path.exists(doc.file_path): raise HTTPException(404,'Document file unavailable')
    return FileResponse(doc.file_path,filename=os.path.basename(doc.file_path))
