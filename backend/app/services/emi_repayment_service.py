"""
Features 15 & 16: Scheme-Connected EMI Calculator & Repayment Breakdown
"""
from typing import Dict, List, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models import Scheme

class EMICalculatorService:
    """Service for calculating EMI and repayments using scheme parameters"""
    
    @staticmethod
    def calculate_emi(
        loan_amount: float,
        scheme_id: int,
        custom_tenure_months: int = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """Calculate EMI using scheme parameters"""
        
        scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first() if db else None
        
        if not scheme:
            return {"error": "Scheme not found"}
        
        # Get parameters from scheme or use defaults
        annual_rate = scheme.interest_rate or 8.5
        tenure_months = custom_tenure_months or scheme.tenure_months or 60
        
        # EMI Calculation Formula: EMI = P * r * (1 + r)^n / ((1 + r)^n - 1)
        # where r = monthly rate
        monthly_rate = annual_rate / 12 / 100
        
        if monthly_rate == 0:
            emi = loan_amount / tenure_months
        else:
            numerator = loan_amount * monthly_rate * ((1 + monthly_rate) ** tenure_months)
            denominator = ((1 + monthly_rate) ** tenure_months) - 1
            emi = numerator / denominator
        
        total_repayment = emi * tenure_months
        total_interest = total_repayment - loan_amount
        
        return {
            "loan_amount": round(loan_amount, 2),
            "annual_interest_rate": annual_rate,
            "tenure_months": tenure_months,
            "tenure_years": round(tenure_months / 12, 1),
            "monthly_emi": round(emi, 2),
            "total_repayment": round(total_repayment, 2),
            "total_interest": round(total_interest, 2),
            "repayment_schedule": EMICalculatorService._generate_repayment_schedule(
                loan_amount, emi, monthly_rate, tenure_months
            ),
            "scheme_name": scheme.name if scheme else "Custom Scheme",
            "scheme_benefits": {
                "moratorium_period": scheme.moratorium_period if hasattr(scheme, 'moratorium_period') else 0,
                "prepayment_allowed": scheme.prepayment_allowed if hasattr(scheme, 'prepayment_allowed') else True,
                "processing_fee": scheme.processing_fee if hasattr(scheme, 'processing_fee') else 0
            }
        }
    
    @staticmethod
    def _generate_repayment_schedule(
        principal: float,
        emi: float,
        monthly_rate: float,
        tenure_months: int
    ) -> List[Dict[str, Any]]:
        """Generate detailed repayment schedule"""
        schedule = []
        remaining_balance = principal
        
        for month in range(1, min(tenure_months + 1, 13)):  # Show first 12 months
            interest_paid = remaining_balance * monthly_rate
            principal_paid = emi - interest_paid
            remaining_balance -= principal_paid
            
            schedule.append({
                "month": month,
                "emi": round(emi, 2),
                "principal": round(principal_paid, 2),
                "interest": round(interest_paid, 2),
                "balance": round(max(0, remaining_balance), 2)
            })
        
        if tenure_months > 12:
            schedule.append({
                "month": "...",
                "emi": "...",
                "principal": "...",
                "interest": "...",
                "balance": "..."
            })
        
        return schedule
    
    @staticmethod
    def compare_emi_across_schemes(
        loan_amount: float,
        scheme_ids: List[int],
        db: Session
    ) -> List[Dict[str, Any]]:
        """Compare EMI across different schemes"""
        comparisons = []
        
        for scheme_id in scheme_ids:
            emi_data = EMICalculatorService.calculate_emi(
                loan_amount, scheme_id, db=db
            )
            if "error" not in emi_data:
                comparisons.append({
                    "scheme_id": scheme_id,
                    "scheme_name": emi_data["scheme_name"],
                    "monthly_emi": emi_data["monthly_emi"],
                    "total_interest": emi_data["total_interest"],
                    "total_repayment": emi_data["total_repayment"],
                    "benefit": EMICalculatorService._get_emi_benefit(emi_data)
                })
        
        # Sort by monthly EMI
        comparisons.sort(key=lambda x: x["monthly_emi"])
        
        return comparisons
    
    @staticmethod
    def _get_emi_benefit(emi_data: Dict) -> str:
        """Get benefit text for EMI option"""
        if emi_data["annual_interest_rate"] <= 5:
            return "Lowest Interest"
        elif emi_data["tenure_months"] >= 60:
            return "Longest Tenure"
        else:
            return "Balanced Option"


class RepaymentBreakdownService:
    """Service for visualizing repayment components"""
    
    @staticmethod
    def get_repayment_breakdown(
        loan_amount: float,
        scheme_id: int,
        custom_tenure_months: int = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """Get visual breakdown of principal and interest components"""
        
        emi_data = EMICalculatorService.calculate_emi(
            loan_amount, scheme_id, custom_tenure_months, db
        )
        
        if "error" in emi_data:
            return emi_data
        
        # Calculate breakdown by year
        yearly_breakdown = RepaymentBreakdownService._calculate_yearly_breakdown(
            loan_amount,
            emi_data["annual_interest_rate"],
            emi_data["tenure_months"]
        )
        
        return {
            "loan_summary": {
                "loan_amount": emi_data["loan_amount"],
                "total_interest": emi_data["total_interest"],
                "total_repayment": emi_data["total_repayment"],
                "interest_percentage": round(
                    (emi_data["total_interest"] / emi_data["total_repayment"]) * 100, 1
                )
            },
            "monthly_breakdown": {
                "emi": emi_data["monthly_emi"],
                "avg_principal": round(emi_data["loan_amount"] / emi_data["tenure_months"], 2),
                "avg_interest": round(emi_data["total_interest"] / emi_data["tenure_months"], 2)
            },
            "yearly_breakdown": yearly_breakdown,
            "visualization_data": RepaymentBreakdownService._prepare_visualization_data(yearly_breakdown)
        }
    
    @staticmethod
    def _calculate_yearly_breakdown(
        principal: float,
        annual_rate: float,
        tenure_months: int
    ) -> List[Dict[str, Any]]:
        """Calculate breakdown year by year"""
        monthly_rate = annual_rate / 12 / 100
        emi = principal * monthly_rate * ((1 + monthly_rate) ** tenure_months) / \
              (((1 + monthly_rate) ** tenure_months) - 1)
        
        breakdown = []
        remaining_balance = principal
        months_per_year = 12
        years = (tenure_months + 11) // 12
        
        for year in range(1, years + 1):
            year_principal = 0
            year_interest = 0
            
            for month in range(months_per_year):
                if remaining_balance <= 0:
                    break
                
                interest = remaining_balance * monthly_rate
                principal_payment = emi - interest
                year_interest += interest
                year_principal += principal_payment
                remaining_balance -= principal_payment
            
            breakdown.append({
                "year": year,
                "principal_paid": round(year_principal, 2),
                "interest_paid": round(year_interest, 2),
                "total_paid": round(year_principal + year_interest, 2),
                "remaining_balance": round(max(0, remaining_balance), 2)
            })
        
        return breakdown
    
    @staticmethod
    def _prepare_visualization_data(yearly_breakdown: List) -> Dict[str, List]:
        """Prepare data for pie and bar charts"""
        return {
            "pie_chart": {
                "principal": sum(y["principal_paid"] for y in yearly_breakdown),
                "interest": sum(y["interest_paid"] for y in yearly_breakdown)
            },
            "bar_chart": {
                "years": [y["year"] for y in yearly_breakdown],
                "principal_amounts": [y["principal_paid"] for y in yearly_breakdown],
                "interest_amounts": [y["interest_paid"] for y in yearly_breakdown]
            }
        }
