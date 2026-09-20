from app.database import Base, engine, SessionLocal
from app.models import User, Scheme, SchemeRule, SchemeDocument, Partner, PartnerAvailability
from app.auth import hash_password


def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()


    def user(email, name, password, role):
        u = db.query(User).filter_by(email=email).first()
        if not u:
            u = User(email=email, name=name, password_hash=hash_password(password), role=role)
            db.add(u)
        else:
            u.name, u.password_hash, u.role = name, hash_password(password), role
        db.flush()
        return u


    user("user@aarambh.local", "Demo Entrepreneur", "user123", "user")
    user("partner@aarambh.local", "Demo Partner", "partner123", "partner")
    user("admin@aarambh.local", "Demo Admin", "admin123", "admin")

    # Prototype catalogue. Official scheme links are included so the UI can show the source.
    # Values are seeded from the NSFDC information used for this prototype; verify live rules before production use.
    schemes = [
            dict(name="Micro Finance Scheme (MFS)", scheme_type="business", description="Micro-credit for small income-generating activities with project cost up to ₹1.40 lakh.", min_loan=10000, max_loan=125000, interest_rate=6.5, tenure_months=36, moratorium_months=3, coverage_percent=90, max_project_cost=140000, benefit_type="Loan", eligibility_summary="SC applicant; annual family income up to ₹5 lakh; project cost up to ₹1.40 lakh.", source_url="https://nsfdc.nic.in/faqs", data_source="NSFDC official FAQ (verify current rules before production)"),
            dict(name="Aajeevika Micro-Finance Yojana (AMY)", scheme_type="business", description="Need-based micro-finance for small projects up to ₹1.40 lakh through eligible channel partners.", min_loan=10000, max_loan=125000, interest_rate=15.0, tenure_months=36, moratorium_months=3, coverage_percent=90, max_project_cost=140000, benefit_type="Loan", eligibility_summary="SC applicant; annual family income up to ₹5 lakh; small project.", source_url="https://nsfdc.nic.in/faqs", data_source="NSFDC official FAQ (verify current rules before production)"),
            dict(name="Term Loan", scheme_type="business", description="Concessional finance for larger income-generating projects costing more than ₹1.40 lakh and up to ₹50 lakh.", min_loan=140001, max_loan=4500000, interest_rate=8.0, tenure_months=84, moratorium_months=6, coverage_percent=90, max_project_cost=5000000, benefit_type="Loan", eligibility_summary="SC applicant; annual family income up to ₹5 lakh; project cost above ₹1.40 lakh and up to ₹50 lakh.", source_url="https://nsfdc.nic.in/faqs", data_source="NSFDC official FAQ (verify current rules before production)"),
            dict(name="Udyam Nidhi Yojana (UNY)", scheme_type="business", description="Finance for small and micro activities with project cost up to ₹5 lakh through eligible channel partners.", min_loan=10000, max_loan=450000, interest_rate=13.0, tenure_months=60, moratorium_months=3, coverage_percent=90, max_project_cost=500000, benefit_type="Loan", eligibility_summary="SC applicant; annual family income up to ₹5 lakh; small/micro activity.", source_url="https://nsfdc.nic.in/faqs", data_source="NSFDC official FAQ (verify current rules before production)"),
            dict(name="Educational Loan Scheme (ELS)", scheme_type="education", description="Educational loan for eligible SC students pursuing regular full-time professional or technical recognized courses in India or abroad.", min_loan=10000, max_loan=4000000, interest_rate=6.5, tenure_months=144, moratorium_months=12, coverage_percent=90, max_project_cost=4444444, benefit_type="Education Loan", eligibility_summary="SC student; annual family income up to ₹5 lakh; recognized full-time professional/technical course; loan up to ₹40 lakh or 90% of course fee, whichever is lower.", source_url="https://nsfdc.nic.in/faqs", data_source="NSFDC official FAQ (verify current rules before production)"),
            dict(name="Skill Development Training Support", scheme_type="education", description="Skill-development support for eligible SC candidates through sponsored training programmes; this is not a conventional loan.", min_loan=0, max_loan=0, interest_rate=0, tenure_months=0, moratorium_months=0, coverage_percent=100, max_project_cost=0, benefit_type="Training Support", eligibility_summary="Eligible SC candidates can access sponsored skill-development training; programme-specific conditions apply.", source_url="https://nsfdc.nic.in/faqs", data_source="NSFDC official FAQ (verify current rules before production)"),
            dict(name="Professional & Technical Education Support", scheme_type="education", description="Education discovery card for professional and technical courses; users can review course-cost support and route an eligible loan application through a channel partner.", min_loan=10000, max_loan=4000000, interest_rate=6.5, tenure_months=144, moratorium_months=12, coverage_percent=90, max_project_cost=4444444, benefit_type="Education Loan", eligibility_summary="Prototype discovery view based on the Educational Loan Scheme; verify the exact course and institution rules before applying.", source_url="https://nsfdc.nic.in/faqs", data_source="NSFDC official FAQ (verify current rules before production)"),
        ]
    schemes += [
        dict(name="Pradhan Mantri Dakshta Aur Kushalta Sampann Hitgrahi (PM-DAKSH)", scheme_type="education", description="Free skill development and entrepreneurial training for eligible SC, OBC, EWS, DNT and Safai Mitra groups; not a conventional loan.", min_loan=0, max_loan=0, interest_rate=0, tenure_months=0, moratorium_months=0, coverage_percent=100, max_project_cost=0, benefit_type="Training / Grant", eligibility_summary="SC, OBC, EWS, DNT and Safai Mitra target groups; OBC/EWS income condition applies; scheme-specific conditions must be checked.", source_url="https://www.myscheme.gov.in/schemes/pm-daksh", data_source="myScheme official scheme page; verify current eligibility", target_categories="SC,OBC,EWS,DNT", target_income_max=300000, target_keywords="skill,training,employment,self employment,entrepreneurship"),
        dict(name="Prime Minister's Employment Generation Programme (PMEGP)", scheme_type="business", description="Government credit-linked support for eligible new micro-enterprises; terms, subsidy and beneficiary conditions are scheme-specific.", min_loan=0, max_loan=5000000, interest_rate=0, tenure_months=84, moratorium_months=0, coverage_percent=0, max_project_cost=5000000, benefit_type="Credit-linked subsidy", eligibility_summary="Eligibility depends on PMEGP rules, project type and applicant conditions. Verify the current scheme page before applying.", source_url="https://www.myscheme.gov.in/hi/schemes/pmegp", data_source="myScheme official scheme page; verify current eligibility", target_categories="SC,ST,OBC,EWS,GENERAL", target_keywords="new enterprise,micro enterprise,manufacturing,service,self employment"),
        dict(name="PM SVANidhi", scheme_type="business", description="Working-capital support for eligible street vendors; current loan tranches and conditions are scheme-specific.", min_loan=5000, max_loan=50000, interest_rate=0, tenure_months=12, moratorium_months=0, coverage_percent=0, max_project_cost=50000, benefit_type="Working capital", eligibility_summary="For eligible street vendors subject to current PM SVANidhi conditions and verification.", source_url="https://www.myscheme.gov.in/schemes/pm-svanidhi", data_source="myScheme official scheme page; verify current eligibility", target_categories="SC,ST,OBC,EWS,GENERAL", target_keywords="street vendor,vendor,working capital"),
        dict(name="Khelo India – Promotion of Inclusiveness through Sports", scheme_type="education", description="Sports development support that includes targeted interventions for persons with disabilities, women, rural and indigenous communities.", min_loan=0, max_loan=0, interest_rate=0, tenure_months=0, moratorium_months=0, coverage_percent=100, max_project_cost=0, benefit_type="Sports support", eligibility_summary="Programme-specific selection and eligibility conditions apply; includes support for persons with disabilities in the sports ecosystem.", source_url="https://www.myscheme.gov.in/schemes/kispits", data_source="myScheme official scheme page; verify current eligibility", target_categories="ALL", target_disability="yes", target_keywords="sports,para sports,disability,training,scholarship"),
        dict(name="State / UT Government Business Scheme Discovery", scheme_type="business", description="Discovery record for state-specific business, livelihood and entrepreneurship schemes available through myScheme's state catalogue.", min_loan=0, max_loan=0, interest_rate=0, tenure_months=0, moratorium_months=0, coverage_percent=0, max_project_cost=0, benefit_type="Discovery", eligibility_summary="Use the applicant's state and profile to verify state-specific schemes on myScheme.", source_url="https://www.myscheme.gov.in/", data_source="myScheme national platform; dynamic catalogue", target_categories="ALL", target_keywords="state business entrepreneurship livelihood"),
        dict(name="State / UT Government Education Scheme Discovery", scheme_type="education", description="Discovery record for state-specific scholarships, education assistance and student support available through myScheme's state catalogue.", min_loan=0, max_loan=0, interest_rate=0, tenure_months=0, moratorium_months=0, coverage_percent=100, max_project_cost=0, benefit_type="Discovery", eligibility_summary="Use the applicant's state, category, disability and education profile to verify state-specific schemes on myScheme.", source_url="https://www.myscheme.gov.in/", data_source="myScheme national platform; dynamic catalogue", target_categories="ALL", target_keywords="education scholarship student fee training disability"),
    ]

    for item in schemes:
        s = db.query(Scheme).filter_by(name=item["name"]).first()
        item.setdefault("target_categories", "SC" if "NSFDC" in item.get("data_source", "") else "ALL")
        item.setdefault("target_income_max", 500000 if "NSFDC" in item.get("data_source", "") else None)
        if not s:
            s = Scheme(**item)
            db.add(s)
            db.flush()
        else:
            for key, value in item.items():
                setattr(s, key, value)
        if "NSFDC" in item.get("data_source", ""):
            rules = db.query(SchemeRule).filter_by(scheme_id=s.id).all()
            if not rules:
                db.add(SchemeRule(scheme_id=s.id, field_name="category", operator="==", value="SC", required=True))
                db.add(SchemeRule(scheme_id=s.id, field_name="annual_income", operator="<=", value="500000", required=True))
                if item["scheme_type"] == "education":
                    db.add(SchemeRule(scheme_id=s.id, field_name="education_level", operator="in", value="Undergraduate,Postgraduate,Doctoral,Professional,Technical", required=False))
        else:
            # myScheme discovery records are governed by their explicit targeting metadata,
            # not by the NSFDC-only SC rule used for the original loan catalogue.
            db.query(SchemeRule).filter_by(scheme_id=s.id).delete()
        if db.query(SchemeDocument).filter_by(scheme_id=s.id).count() == 0:
            docs = [("Caste Certificate", "caste"), ("Income Certificate", "income"), ("Identity/KYC", "identity")]
            docs.append(("Admission / Course Proof", "education") if item["scheme_type"] == "education" else ("Business / Project Proof", "business"))
            for name, typ in docs:
                db.add(SchemeDocument(scheme_id=s.id, document_name=name, document_type=typ, required=True))

    if db.query(Partner).count() == 0:
        partners = [
            ("ABC Bank - Chennai", "PSB", "Chennai, Tamil Nadu", 13.0827, 80.2707, "business,education", 98, 3, 0, 4.4),
            ("XYZ RRB - Chennai", "RRB", "Chennai, Tamil Nadu", 13.0674, 80.2376, "business,education", 100, 10, 0, 4.2),
            ("Demo SCA - Kanchipuram", "SCA", "Kanchipuram, Tamil Nadu", 12.8342, 79.7036, "business,education", 96, 2, 0, 4.5),
            ("Demo NBFC-MFI - Chennai", "NBFC-MFI", "Chennai, Tamil Nadu", 13.0418, 80.2341, "business", 97, 4, 0, 4.1),
        ]
        for idx, (name, ptype, address, lat, lon, supported, utilization, npa, overdue, rating) in enumerate(partners):
            p = Partner(name=name, partner_type=ptype, address=address, state="Tamil Nadu", district="Demo", latitude=lat, longitude=lon,
                        email="partner@aarambh.local" if idx == 0 else None, phone="1800-000-0000", supported_scheme_types=supported, source_url="", data_source="Prototype seeded partner record; replace with verified authorized directory data",
                        fund_utilization_percent=utilization, npa_percent=npa, overdue_percent=overdue, rating=rating)
            db.add(p)
            db.flush()
            db.add(PartnerAvailability(partner_id=p.id, available=True, capacity=20 - idx * 2))
    else:
        p = db.query(Partner).filter_by(active=True).order_by(Partner.id.asc()).first()
        if p:
            p.email = "partner@aarambh.local"
            p.supported_scheme_types = p.supported_scheme_types or "business,education"
        for p in db.query(Partner).all():
            if not p.supported_scheme_types:
                p.supported_scheme_types = "business,education"
            if p.rating is None:
                p.rating = 4.0
            if p.fund_utilization_percent is None:
                p.fund_utilization_percent = 100
            if p.npa_percent is None:
                p.npa_percent = 0
            if p.overdue_percent is None:
                p.overdue_percent = 0
            if not db.query(PartnerAvailability).filter_by(partner_id=p.id).first():
                db.add(PartnerAvailability(partner_id=p.id, available=True, capacity=20))

    db.commit()
    db.close()
    print("Seed complete.")


if __name__ == "__main__":
    seed_database()
