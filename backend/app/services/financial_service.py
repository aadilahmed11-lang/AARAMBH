def calculate_emi(principal: float, annual_rate: float, months: int):
    r = annual_rate / 12 / 100
    if r == 0:
        emi = principal / months
    else:
        emi = principal * r * (1+r)**months / ((1+r)**months - 1)
    total = emi * months
    return {
        "principal": round(principal,2),
        "annual_rate": annual_rate,
        "tenure_months": months,
        "emi": round(emi,2),
        "total_interest": round(total-principal,2),
        "total_repayment": round(total,2)
    }
