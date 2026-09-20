from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Scheme, SchemeRule, SchemeDocument
from ..schemas import SchemeIn
from ..auth import require_role

router=APIRouter(prefix="/api/schemes",tags=["Schemes"])

@router.get("/")
def schemes(db:Session=Depends(get_db)):
    return db.query(Scheme).filter_by(active=True).all()

@router.get("/{scheme_id}")
def scheme(scheme_id:int,db:Session=Depends(get_db)):
    s=db.get(Scheme,scheme_id)
    if not s: raise HTTPException(404,"Scheme not found")
    return {
        "scheme":s,
        "rules":db.query(SchemeRule).filter_by(scheme_id=s.id).all(),
        "documents":db.query(SchemeDocument).filter_by(scheme_id=s.id).all()
    }

@router.post("/", dependencies=[Depends(require_role("admin"))])
def add_scheme(data:SchemeIn,db:Session=Depends(get_db)):
    s=Scheme(**data.model_dump(exclude={"rules","documents"}))
    db.add(s); db.flush()
    for r in data.rules: db.add(SchemeRule(scheme_id=s.id,**r))
    for d in data.documents: db.add(SchemeDocument(scheme_id=s.id,**d))
    db.commit(); db.refresh(s)
    return s

@router.put("/{scheme_id}", dependencies=[Depends(require_role("admin"))])
def update_scheme(scheme_id:int,data:SchemeIn,db:Session=Depends(get_db)):
    s=db.get(Scheme,scheme_id)
    if not s: raise HTTPException(404,"Scheme not found")
    for k,v in data.model_dump(exclude={"rules","documents"}).items(): setattr(s,k,v)
    db.query(SchemeRule).filter_by(scheme_id=s.id).delete()
    db.query(SchemeDocument).filter_by(scheme_id=s.id).delete()
    for r in data.rules: db.add(SchemeRule(scheme_id=s.id,**r))
    for d in data.documents: db.add(SchemeDocument(scheme_id=s.id,**d))
    db.commit(); return s
