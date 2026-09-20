from typing import Optional, List
from pydantic import BaseModel, Field

class RegisterIn(BaseModel):
    name: str
    email: str
    password: str
    role: str = "user"

class LoginIn(BaseModel):
    email: str
    password: str

class ProfileIn(BaseModel):
    category: Optional[str] = None
    annual_income: Optional[float] = None
    occupation: Optional[str] = None
    business_type: Optional[str] = None
    business_stage: Optional[str] = None
    loan_amount: Optional[float] = None
    state: Optional[str] = None
    district: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    education_level: Optional[str] = None
    course_type: Optional[str] = None
    institution: Optional[str] = None
    course_fee: Optional[float] = None
    study_location: Optional[str] = None
    course_duration_months: Optional[int] = None
    marital_status: Optional[str] = None
    residence_type: Optional[str] = None
    minority_status: Optional[str] = None
    employment_status: Optional[str] = None
    disability_status: Optional[str] = None
    disability_percent: Optional[float] = None
    disability_type: Optional[str] = None
    aadhaar_available: Optional[str] = None
    caste_certificate_available: Optional[str] = None
    income_certificate_available: Optional[str] = None
    existing_loan: Optional[str] = None

class CalculatorIn(BaseModel):
    principal: float = Field(gt=0)
    annual_rate: float = Field(ge=0)
    tenure_months: int = Field(gt=0, le=360)

class EligibilityIn(BaseModel):
    scheme_id: int
    profile: Optional[ProfileIn] = None

class RecommendationIn(BaseModel):
    profile: ProfileIn
    scheme_type: str = "business"

class ApplicationIn(BaseModel):
    scheme_id: int
    partner_id: Optional[int] = None
    loan_amount: float = Field(gt=0)

class StatusIn(BaseModel):
    status: str
    remarks: Optional[str] = None

class SchemeIn(BaseModel):
    name: str
    scheme_type: str = "business"
    description: str
    min_loan: float = 0
    max_loan: float = 0
    interest_rate: float = 0
    tenure_months: int = 60
    moratorium_months: int = 0
    coverage_percent: float = 90
    max_project_cost: float = 0
    benefit_type: str = "Loan"
    eligibility_summary: Optional[str] = None
    active: bool = True
    source_url: Optional[str] = None
    data_source: Optional[str] = None
    verification_status: str = "Unverified"
    next_review_date: Optional[str] = None
    target_categories: Optional[str] = None
    target_disability: Optional[str] = None
    target_income_max: Optional[float] = None
    target_states: Optional[str] = None
    target_keywords: Optional[str] = None
    target_age_min: Optional[int] = None
    target_age_max: Optional[int] = None
    rules: List[dict] = []
    documents: List[dict] = []
