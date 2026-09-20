from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth import current_user
from ..models import Application, Scheme, ApplicationStatusHistory

router = APIRouter(prefix="/api/offline", tags=["Offline Sync"])

@router.post("/sync")
def sync_offline_application(payload: dict, user=Depends(current_user), db: Session=Depends(get_db)):
    data = payload or {}
    scheme_id = data.get("scheme_id")
    loan_amount = float(data.get("loan_amount") or 0)
    if not scheme_id or loan_amount <= 0:
        raise HTTPException(400, "scheme_id and a positive loan_amount are required")
    scheme = db.get(Scheme, int(scheme_id))
    if not scheme or not scheme.active:
        raise HTTPException(404, "Scheme is no longer active")
    if scheme.max_loan and loan_amount > scheme.max_loan:
        raise HTTPException(400, f"Loan amount exceeds the scheme maximum of ₹{scheme.max_loan:,.0f}")
    from .application_routes import ref
    app = Application(reference_no=ref(), user_id=user.id, scheme_id=scheme.id,
                      partner_id=data.get("partner_id"), loan_amount=loan_amount,
                      status="Submitted", is_eligible=None)
    db.add(app); db.flush()
    db.add(ApplicationStatusHistory(application_id=app.id, status="Submitted", remarks="Submitted after offline sync", updated_by=user.id))
    db.commit(); db.refresh(app)
    return {"synced": True, "application": app}
