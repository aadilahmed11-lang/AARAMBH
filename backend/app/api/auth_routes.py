from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..schemas import RegisterIn, LoginIn
from ..auth import hash_password, verify_password, create_token

router=APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/register")
def register(data:RegisterIn, db:Session=Depends(get_db)):
    if db.query(User).filter(User.email==data.email).first():
        raise HTTPException(400,"Email already registered")
    # Public registration creates applicant accounts only; partner/admin access is provisioned by the organization.
    role="user"
    user=User(name=data.name,email=data.email,password_hash=hash_password(data.password),role=role)
    db.add(user); db.commit(); db.refresh(user)
    return {"message":"registered","token":create_token(user),"user":{"id":user.id,"name":user.name,"email":user.email,"role":user.role}}

@router.post("/login")
def login(data:LoginIn, db:Session=Depends(get_db)):
    user=db.query(User).filter(User.email==data.email).first()
    if not user or not verify_password(data.password,user.password_hash):
        raise HTTPException(401,"Invalid credentials")
    return {"token":create_token(user),"user":{"id":user.id,"name":user.name,"email":user.email,"role":user.role}}


@router.post('/aadhaar-demo')
def aadhaar_demo(payload:dict, db:Session=Depends(get_db)):
    """Prototype-only Aadhaar-shaped login. Never represents real UIDAI authentication."""
    identity=str(payload.get('aadhaar','')).replace(' ','').replace('-','')
    otp=str(payload.get('otp',''))
    role=str(payload.get('role','user'))
    if len(identity) != 12 or not identity.isdigit():
        raise HTTPException(400,'Enter a valid 12-digit demo Aadhaar number')
    if otp != '123456':
        raise HTTPException(401,'Invalid demo OTP. Use 123456.')
    if role not in ('user','partner','admin'):
        role='user'
    # Demo identity mapping only. This does NOT validate an Aadhaar number with UIDAI.
    demo_emails={'user':'aadhaar.user@aarambh.local','partner':'aadhaar.partner@aarambh.local','admin':'aadhaar.admin@aarambh.local'}
    demo_names={'user':'Demo Aadhaar Applicant','partner':'Demo Aadhaar Partner','admin':'Demo Aadhaar Admin'}
    demo_passwords={'user':'aadhaar123','partner':'aadhaar123','admin':'aadhaar123'}
    email=demo_emails[role]
    user=db.query(User).filter(User.email==email).first()
    if not user:
        user=User(name=demo_names[role],email=email,password_hash=hash_password(demo_passwords[role]),role=role)
        db.add(user); db.commit(); db.refresh(user)
    elif user.role != role:
        user.role=role; db.commit(); db.refresh(user)
    return {'token':create_token(user),'user':{'id':user.id,'name':user.name,'email':user.email,'role':user.role},'verification':'demo_verified'}
