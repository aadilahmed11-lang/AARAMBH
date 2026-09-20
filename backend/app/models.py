from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="user", nullable=False)
    language = Column(String(20), default="English")
    created_at = Column(DateTime, default=datetime.utcnow)

class EntrepreneurProfile(Base):
    __tablename__ = "entrepreneur_profiles"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    name = Column(String(120))
    age = Column(Integer)
    gender = Column(String(30))
    contact = Column(String(30))
    existing_loan = Column(String(30))
    category = Column(String(100))
    annual_income = Column(Float)
    occupation = Column(String(150))
    business_type = Column(String(150))
    business_stage = Column(String(50))
    loan_amount = Column(Float)
    state = Column(String(100))
    district = Column(String(100))
    city = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)
    education_level = Column(String(120))
    course_type = Column(String(150))
    institution = Column(String(200))
    course_fee = Column(Float)
    study_location = Column(String(50))
    course_duration_months = Column(Integer)
    marital_status = Column(String(50))
    residence_type = Column(String(50))
    minority_status = Column(String(50))
    employment_status = Column(String(80))
    disability_status = Column(String(80))
    disability_percent = Column(Float)
    disability_type = Column(String(120))
    aadhaar_available = Column(String(20))
    caste_certificate_available = Column(String(20))
    income_certificate_available = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Scheme(Base):
    __tablename__ = "schemes"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    scheme_type = Column(String(50), default="business", nullable=False)  # business / education
    min_loan = Column(Float, default=0)
    max_loan = Column(Float, default=0)
    interest_rate = Column(Float, default=0)
    tenure_months = Column(Integer, default=60)
    moratorium_months = Column(Integer, default=0)
    coverage_percent = Column(Float, default=90)
    max_project_cost = Column(Float, default=0)
    benefit_type = Column(String(80), default="Loan")
    eligibility_summary = Column(Text)
    active = Column(Boolean, default=True)
    source_url = Column(String(500))
    data_source = Column(String(500))
    verification_status = Column(String(40), default="Unverified")
    verified_at = Column(DateTime)
    verified_by = Column(Integer, ForeignKey("users.id"))
    next_review_date = Column(String(30))
    target_categories = Column(String(300))
    target_disability = Column(String(80))
    target_income_max = Column(Float)
    target_states = Column(String(500))
    target_keywords = Column(String(800))
    target_age_min = Column(Integer)
    target_age_max = Column(Integer)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SchemeRule(Base):
    __tablename__ = "scheme_rules"
    id = Column(Integer, primary_key=True)
    scheme_id = Column(Integer, ForeignKey("schemes.id"), nullable=False)
    field_name = Column(String(100), nullable=False)
    operator = Column(String(20), nullable=False)
    value = Column(String(255), nullable=False)
    required = Column(Boolean, default=True)

class SchemeDocument(Base):
    __tablename__ = "scheme_documents"
    id = Column(Integer, primary_key=True)
    scheme_id = Column(Integer, ForeignKey("schemes.id"), nullable=False)
    document_name = Column(String(200), nullable=False)
    required = Column(Boolean, default=True)
    document_type = Column(String(100))

class Partner(Base):
    __tablename__ = "partners"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    partner_type = Column(String(100), default="Bank")
    address = Column(String(500))
    district = Column(String(100))
    state = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)
    phone = Column(String(30))
    email = Column(String(150))
    rating = Column(Float, default=4.0)
    fund_utilization_percent = Column(Float, default=100)
    npa_percent = Column(Float, default=0)
    overdue_percent = Column(Float, default=0)
    supported_scheme_types = Column(String(100), default="business,education")
    source_url = Column(String(500))
    data_source = Column(String(500))
    verification_status = Column(String(40), default="Unverified")
    verified_at = Column(DateTime)
    verified_by = Column(Integer, ForeignKey("users.id"))
    next_review_date = Column(String(30))
    active = Column(Boolean, default=True)

class PartnerAvailability(Base):
    __tablename__ = "partner_availability"
    id = Column(Integer, primary_key=True)
    partner_id = Column(Integer, ForeignKey("partners.id"), unique=True, nullable=False)
    available = Column(Boolean, default=True)
    capacity = Column(Integer, default=20)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Application(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True)
    reference_no = Column(String(50), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    scheme_id = Column(Integer, ForeignKey("schemes.id"), nullable=False)
    partner_id = Column(Integer, ForeignKey("partners.id"))
    status = Column(String(50), default="Submitted")
    loan_amount = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_eligible = Column(Boolean, default=None)
    document_verified_at = Column(DateTime)
    partner_review_at = Column(DateTime)
    decision_date = Column(DateTime)

    user = relationship("User")
    scheme = relationship("Scheme")
    partner = relationship("Partner")

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    document_type = Column(String(100), nullable=False)
    file_path = Column(String(500))
    ocr_status = Column(String(50), default="Pending")
    verification_status = Column(String(50), default="Pending")
    extracted_data = Column(Text)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

class ApplicationStatusHistory(Base):
    __tablename__ = "application_status_history"
    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    status = Column(String(50), nullable=False)
    remarks = Column(Text)
    updated_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

class Recommendation(Base):
    __tablename__ = "recommendations"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    scheme_id = Column(Integer, ForeignKey("schemes.id"), nullable=False)
    match_score = Column(Float, default=0)
    rank = Column(Integer)
    eligible = Column(Boolean, default=False)
    reason = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class QRCodeRecord(Base):
    __tablename__ = "qr_codes"
    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    qr_token = Column(String(100), unique=True, nullable=False)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    action = Column(String(100))
    entity = Column(String(100))
    entity_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)


class BusinessProfile(Base):
    __tablename__ = "business_profiles"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    stage = Column(String(50))
    business_type = Column(String(100))
    industry = Column(String(150))
    location = Column(String(200))
    expected_investment = Column(Float)
    loan_purpose = Column(String(150))
    business_idea = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BankVisitRequest(Base):
    __tablename__ = "bank_visit_requests"
    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    partner_id = Column(Integer, ForeignKey("partners.id"), nullable=False)
    requested_date = Column(String(30))
    requested_time = Column(String(30))
    location = Column(String(300))
    status = Column(String(50), default="Requested")
    created_at = Column(DateTime, default=datetime.utcnow)

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
