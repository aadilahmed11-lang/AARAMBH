from fastapi import APIRouter
from ..schemas import CalculatorIn
from ..services.financial_service import calculate_emi
router=APIRouter(prefix="/api/calculator",tags=["Calculator"])

@router.post("/emi")
def emi(data:CalculatorIn):
    return calculate_emi(data.principal,data.annual_rate,data.tenure_months)
