from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import EntrepreneurProfile
from ..schemas import ProfileIn
from ..auth import current_user

router=APIRouter(prefix="/api/profile",tags=["Profile"])

@router.get("/")
def get_profile(user=Depends(current_user),db:Session=Depends(get_db)):
    p=db.query(EntrepreneurProfile).filter_by(user_id=user.id).first()
    return p or {}

@router.put("/")
def save_profile(data:ProfileIn,user=Depends(current_user),db:Session=Depends(get_db)):
    p=db.query(EntrepreneurProfile).filter_by(user_id=user.id).first()
    if not p:
        p=EntrepreneurProfile(user_id=user.id); db.add(p)
    for k,v in data.model_dump().items():
        setattr(p,k,v)
    db.commit(); db.refresh(p)
    return p
