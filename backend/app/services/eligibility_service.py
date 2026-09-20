from typing import Any

OPS = {
    ">=": lambda a,b: a >= b,
    "<=": lambda a,b: a <= b,
    ">": lambda a,b: a > b,
    "<": lambda a,b: a < b,
    "==": lambda a,b: str(a).lower() == str(b).lower(),
    "in": lambda a,b: str(a).lower() in [x.strip().lower() for x in str(b).split(",")],
}

def get_field(profile: Any, name: str):
    if isinstance(profile, dict):
        return profile.get(name)
    return getattr(profile, name, None)

def check_rules(scheme, rules, profile):
    reasons = []
    missing = []
    eligible = True

    if scheme.min_loan and (get_field(profile, "loan_amount") or 0) < scheme.min_loan:
        eligible = False
        reasons.append(f"Loan amount must be at least ₹{scheme.min_loan:,.0f}.")
    if scheme.max_loan and (get_field(profile, "loan_amount") or 0) > scheme.max_loan:
        eligible = False
        reasons.append(f"Loan amount must not exceed ₹{scheme.max_loan:,.0f}.")

    for rule in rules:
        actual = get_field(profile, rule.field_name)
        if actual is None or actual == "":
            if rule.required:
                eligible = False
                missing.append(rule.field_name)
            continue
        try:
            expected = float(rule.value) if isinstance(actual, (int,float)) else rule.value
            ok = OPS.get(rule.operator, lambda a,b: True)(actual, expected)
        except Exception:
            ok = False
        if not ok:
            eligible = False
            reasons.append(f"{rule.field_name} does not satisfy {rule.operator} {rule.value}.")

    if missing:
        reasons.append("Missing: " + ", ".join(missing))
    if not reasons:
        reasons.append("Profile satisfies the configured scheme rules.")
    return {"eligible": eligible, "reasons": reasons}
