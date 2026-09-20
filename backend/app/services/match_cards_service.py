from typing import List, Dict, Any
from sqlalchemy.orm import Session
from ..models import EntrepreneurProfile, Scheme

class MatchCardsService:
    @staticmethod
    def generate_match_cards(user_id:int, scheme_ids:List[int], db:Session)->List[Dict[str,Any]]:
        p=db.query(EntrepreneurProfile).filter_by(user_id=user_id).first(); out=[]
        for sid in scheme_ids:
            s=db.get(Scheme,sid)
            if not s: continue
            factors=[]; score=50
            if p:
                if p.category and p.category.upper()=='SC': factors.append({"factor":"Community","user_detail":"SC","scheme_requirement":"SC eligibility","match_percentage":100}); score+=15
                if p.annual_income is not None and p.annual_income<=500000: factors.append({"factor":"Family income","user_detail":f"₹{p.annual_income:,.0f}","scheme_requirement":"Up to ₹5 lakh","match_percentage":100}); score+=15
                if s.scheme_type=='education' and p.course_fee: factors.append({"factor":"Course fee","user_detail":f"₹{p.course_fee:,.0f}","scheme_requirement":f"Up to ₹{s.max_loan:,.0f} loan / coverage rules","match_percentage":100}); score+=10
                if s.scheme_type=='business' and p.loan_amount and s.min_loan<=p.loan_amount<=s.max_loan: factors.append({"factor":"Loan amount","user_detail":f"₹{p.loan_amount:,.0f}","scheme_requirement":f"₹{s.min_loan:,.0f}–₹{s.max_loan:,.0f}","match_percentage":100}); score+=10
            out.append({"scheme_id":s.id,"scheme_name":s.name,"scheme_description":s.description,"interest_rate":s.interest_rate,"tenure_months":s.tenure_months,"match_percentage":min(score,100),"matching_factors":factors,"call_to_action":"Apply Now" if score>=80 else "View Details"})
        return out
