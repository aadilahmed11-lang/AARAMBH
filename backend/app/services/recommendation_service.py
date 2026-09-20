from typing import Any
import re
from .eligibility_service import check_rules, get_field


def _csv(value):
    return {x.strip().lower() for x in str(value or "").split(",") if x.strip()}


def _profile_text(p):
    fields = ["occupation","business_type","business_stage","state","district","city","course_type","education_level","employment_status","disability_type"]
    return " ".join(str(get_field(p, f) or "") for f in fields).lower()


def _score_scheme(profile: Any, scheme, rules):
    score = 20.0
    factors, gaps = [], []
    category = str(get_field(profile, "category") or "").strip().lower()
    category_aliases={"general / other":"general","general":"general","other backward class (obc)":"obc","obc":"obc","backward class (bc)":"bc","bc":"bc","backward class muslim (bcm)":"bcm","bcm":"bcm","scheduled caste (sc)":"sc","sc":"sc","scheduled tribe (st)":"st","st":"st","economically weaker section (ews)":"ews","ews":"ews"}
    category=category_aliases.get(category,category)
    targets_raw=_csv(scheme.target_categories)
    targets={category_aliases.get(x,x) for x in targets_raw}
    if targets and "all" not in targets:
        if category in targets:
            score += 25; factors.append(f"Category {get_field(profile, 'category')} matches the scheme target.")
        else:
            score -= 25; gaps.append(f"Category {get_field(profile, 'category') or 'not provided'} is not listed in the scheme target categories.")
    income = get_field(profile, "annual_income")
    if income is not None and scheme.target_income_max:
        if float(income) <= float(scheme.target_income_max):
            score += 15; factors.append(f"Family income ₹{float(income):,.0f} is within the configured income limit.")
        else:
            score -= 20; gaps.append("Family income is above the configured income limit.")
    state = str(get_field(profile, "state") or "").lower()
    states = _csv(scheme.target_states)
    if states:
        if state in states:
            score += 10; factors.append(f"State {get_field(profile, 'state')} is supported by this scheme record.")
        else:
            gaps.append(f"State {get_field(profile, 'state') or 'not provided'} is not listed in this scheme record.")
    disability = str(get_field(profile, "disability_status") or "").lower()
    target_disability = str(scheme.target_disability or "").lower()
    if disability and target_disability:
        if target_disability in ("all", disability) or (target_disability == "yes" and disability == "yes"):
            score += 12; factors.append("Disability profile matches the scheme targeting information.")
        elif target_disability == "no" and disability == "no":
            score += 5
        else:
            gaps.append("Disability status does not match the scheme targeting information.")
    age = get_field(profile, "age")
    if age is not None and str(age) != "":
        try:
            agef=float(age)
            if scheme.target_age_min is not None and agef < scheme.target_age_min:
                score -= 8; gaps.append("Age is below the configured scheme range.")
            elif scheme.target_age_max is not None and agef > scheme.target_age_max:
                score -= 8; gaps.append("Age is above the configured scheme range.")
            elif scheme.target_age_min is not None or scheme.target_age_max is not None:
                score += 5; factors.append("Age fits the configured scheme range.")
        except Exception:
            pass
    amount = get_field(profile, "loan_amount") or get_field(profile, "course_fee")
    if amount and (scheme.min_loan or scheme.max_loan):
        amount=float(amount)
        if (not scheme.min_loan or amount >= scheme.min_loan) and (not scheme.max_loan or amount <= scheme.max_loan):
            score += 15; factors.append(f"Requested amount ₹{amount:,.0f} fits the scheme range.")
        else:
            score -= 15; gaps.append(f"Requested amount ₹{amount:,.0f} is outside the configured scheme range.")
    profile_text=_profile_text(profile)
    keywords=_csv(scheme.target_keywords)
    if keywords:
        hits=sorted(k for k in keywords if k in profile_text)
        if hits:
            score += min(10, 3*len(hits)); factors.append("Purpose/profile keywords match: " + ", ".join(hits[:4]) + ".")
    education=str(get_field(profile,"education_level") or "").lower()
    if scheme.scheme_type=="education" and education and any(k in education for k in ("undergraduate","postgraduate","doctoral","professional","technical")):
        score += 5; factors.append("Education level fits the education journey.")
    result=check_rules(scheme,rules,profile)
    if result["eligible"]:
        score += 10; factors.append("Configured eligibility rules currently pass.")
    else:
        score -= 18; gaps.extend(result["reasons"][:3])
    score=max(0.0,min(100.0,score))
    reason=" ".join(factors[:4]) if factors else "Profile information has limited matching signals for this scheme."
    if gaps: reason += " Review: " + " ".join(gaps[:2])
    return round(score,2),result["eligible"],reason,factors,gaps


def rank_schemes(profile, schemes, rules_by_scheme):
    results=[]
    for scheme in schemes:
        score,eligible,reason,factors,gaps=_score_scheme(profile,scheme,rules_by_scheme.get(scheme.id,[]))
        results.append({"scheme":scheme,"score":score,"eligible":eligible,"reason":reason,"matching_factors":factors,"gaps":gaps})
    results.sort(key=lambda x:(x["score"],x["eligible"]),reverse=True)
    for rank,item in enumerate(results[:5],1): item["rank"]=rank
    return results[:5]
