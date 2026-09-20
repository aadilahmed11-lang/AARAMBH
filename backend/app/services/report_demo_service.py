"""
Features 14 & 20: Applicant Report for Partners & Judge Demo Mode
"""
from typing import Dict, List, Any
from datetime import datetime
from sqlalchemy.orm import Session
from ..models import User, Application, Document, Scheme

class ApplicantReportService:
    """Service for generating comprehensive applicant reports for partners/banks"""
    
    @staticmethod
    def generate_partner_report(
        application_id: int,
        db: Session
    ) -> Dict[str, Any]:
        """Generate complete applicant report for bank/partner review"""
        
        app = db.query(Application).filter(Application.id == application_id).first()
        if not app:
            return {"error": "Application not found"}
        
        user = db.query(User).filter(User.id == app.user_id).first()
        
        # Applicant Profile Section
        applicant_profile = {
            "full_name": user.name,
            "email": user.email,
            "phone": user.phone,
            "gender": user.gender if hasattr(user, 'gender') else "N/A",
            "age": user.age if hasattr(user, 'age') else "N/A",
            "address": f"{user.address}, {user.city}, {user.state}",
            "document_verification": ApplicantReportService._get_document_verification_status(app, db)
        }
        
        # Business Profile Section
        business_profile = {
            "business_name": user.business_name if hasattr(user, 'business_name') else "N/A",
            "business_type": user.business_type if hasattr(user, 'business_type') else "N/A",
            "business_age": user.business_age if hasattr(user, 'business_age') else "N/A",
            "registration_number": user.registration_number if hasattr(user, 'registration_number') else "N/A",
            "gst_number": user.gst_number if hasattr(user, 'gst_number') else "N/A",
            "employees_count": user.employees_count if hasattr(user, 'employees_count') else "N/A"
        }
        
        # Financial Profile Section
        financial_profile = {
            "annual_turnover": user.annual_turnover if hasattr(user, 'annual_turnover') else "N/A",
            "monthly_revenue": user.monthly_revenue if hasattr(user, 'monthly_revenue') else "N/A",
            "existing_liabilities": user.existing_liabilities if hasattr(user, 'existing_liabilities') else "N/A",
            "credit_score": user.credit_score if hasattr(user, 'credit_score') else "N/A",
            "bank_account_holder": user.bank_account_holder if hasattr(user, 'bank_account_holder') else "N/A"
        }
        
        # Loan Request Section
        loan_request = {
            "loan_amount": app.loan_amount if hasattr(app, 'loan_amount') else "N/A",
            "loan_purpose": app.loan_purpose if hasattr(app, 'loan_purpose') else "N/A",
            "preferred_tenure": app.preferred_tenure if hasattr(app, 'preferred_tenure') else "N/A",
            "collateral_available": app.collateral_available if hasattr(app, 'collateral_available') else False,
            "guarantor_available": app.guarantor_available if hasattr(app, 'guarantor_available') else False
        }
        
        # Eligibility Section
        eligibility = {
            "scheme_name": app.scheme.name if app.scheme else "N/A",
            "is_eligible": app.is_eligible,
            "eligibility_status": "Eligible" if app.is_eligible else "Not Eligible",
            "eligibility_check_date": app.updated_at.isoformat() if app.updated_at else None
        }
        
        # Documents Section
        documents = db.query(Document).filter(Document.application_id == application_id).all()
        documents_info = [
            {
                "type": doc.document_type,
                "status": doc.verification_status,
                "uploaded_date": doc.uploaded_at.isoformat() if hasattr(doc, 'uploaded_at') and doc.uploaded_at else None,
                "ocr_confidence": doc.ocr_confidence if hasattr(doc, 'ocr_confidence') else None
            }
            for doc in documents
        ]
        
        # Application History
        application_history = {
            "submission_date": app.created_at.isoformat() if app.created_at else None,
            "last_updated": app.updated_at.isoformat() if app.updated_at else None,
            "current_status": app.status,
            "status_history": ApplicantReportService._get_status_history(app)
        }
        
        return {
            "report_id": f"RPT-{application_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "generated_at": datetime.utcnow().isoformat(),
            "application_id": application_id,
            "applicant_profile": applicant_profile,
            "business_profile": business_profile,
            "financial_profile": financial_profile,
            "loan_request": loan_request,
            "eligibility": eligibility,
            "documents": documents_info,
            "application_history": application_history,
            "recommendation": ApplicantReportService._generate_recommendation(app, documents)
        }
    
    @staticmethod
    def _get_document_verification_status(app: Any, db: Session) -> Dict[str, Any]:
        """Get document verification status"""
        documents = db.query(Document).filter(Document.application_id == app.id).all()
        
        verified = len([d for d in documents if d.verification_status == 'verified'])
        total = len(documents)
        
        return {
            "verified": verified,
            "total": total,
            "percentage": round((verified / total * 100) if total > 0 else 0, 1),
            "status": "Complete" if verified == total else "Pending"
        }
    
    @staticmethod
    def _get_status_history(app: Any) -> List[Dict[str, Any]]:
        """Get application status history"""
        return [
            {
                "status": "Submitted",
                "date": app.created_at.isoformat() if app.created_at else None
            },
            {
                "status": "In Review",
                "date": app.updated_at.isoformat() if app.updated_at else None
            }
        ]
    
    @staticmethod
    def _generate_recommendation(app: Any, documents: List) -> Dict[str, Any]:
        """Generate partner recommendation based on application"""
        
        recommendation_score = 0
        recommendation_factors = []
        
        # Check eligibility
        if app.is_eligible:
            recommendation_score += 40
            recommendation_factors.append("✓ Eligible for the scheme")
        
        # Check documents
        verified_docs = len([d for d in documents if d.verification_status == 'verified'])
        doc_ratio = verified_docs / len(documents) if documents else 0
        
        if doc_ratio >= 0.8:
            recommendation_score += 30
            recommendation_factors.append(f"✓ {verified_docs}/{len(documents)} documents verified")
        
        # Check financial profile
        if hasattr(app, 'annual_turnover') and app.annual_turnover:
            recommendation_score += 20
            recommendation_factors.append("✓ Complete financial profile")
        
        recommendation_text = "Approve" if recommendation_score >= 70 else "Review Further" if recommendation_score >= 50 else "Request More Information"
        
        return {
            "recommendation": recommendation_text,
            "recommendation_score": recommendation_score,
            "recommendation_factors": recommendation_factors
        }


class DemoModeService:
    """Service for Judge Demo Mode with pre-filled scenarios"""
    
    @staticmethod
    def get_demo_scenarios() -> Dict[str, Any]:
        """Get available demo scenarios"""
        
        return {
            "available_scenarios": [
                {
                    "id": 1,
                    "name": "Small Business Owner",
                    "description": "Dairy farmer looking for equipment loan",
                    "applicant_type": "Individual",
                    "business_type": "Dairy Farming",
                    "loan_amount": 500000,
                    "expected_status": "Eligible for PM KUSUM"
                },
                {
                    "id": 2,
                    "name": "Retail Shop Owner",
                    "description": "Clothing retail entrepreneur seeking expansion loan",
                    "applicant_type": "Individual",
                    "business_type": "Retail Trade",
                    "loan_amount": 1000000,
                    "expected_status": "Eligible for MUDRA"
                },
                {
                    "id": 3,
                    "name": "Manufacturing Unit",
                    "description": "Small manufacturing business requiring working capital",
                    "applicant_type": "Company",
                    "business_type": "Manufacturing",
                    "loan_amount": 5000000,
                    "expected_status": "Eligible for CGTMSE"
                },
                {
                    "id": 4,
                    "name": "Agricultural Enterprise",
                    "description": "Farm-based business needing technology upgrade",
                    "applicant_type": "Individual",
                    "business_type": "Agriculture",
                    "loan_amount": 300000,
                    "expected_status": "Eligible for PM-ACHY"
                },
                {
                    "id": 5,
                    "name": "Women Entrepreneur",
                    "description": "Women-led startup seeking growth capital",
                    "applicant_type": "Individual",
                    "business_type": "Services",
                    "loan_amount": 750000,
                    "expected_status": "Eligible for STDS & STEP"
                }
            ]
        }
    
    @staticmethod
    def create_demo_application(
        scenario_id: int,
        role: str = "applicant"
    ) -> Dict[str, Any]:
        """Create a demo application with pre-filled realistic data"""
        
        demo_data = {
            1: DemoModeService._create_dairy_farmer_demo(),
            2: DemoModeService._create_retail_demo(),
            3: DemoModeService._create_manufacturing_demo(),
            4: DemoModeService._create_agricultural_demo(),
            5: DemoModeService._create_women_entrepreneur_demo()
        }
        
        demo_app = demo_data.get(scenario_id)
        
        if not demo_app:
            return {"error": "Scenario not found"}
        
        return {
            "demo_application": demo_app,
            "demo_mode": True,
            "scenario_id": scenario_id,
            "role": role,
            "instruction": f"This is a demo application for testing. You are viewing as a {role}.",
            "can_submit": True,
            "demo_documents_available": True
        }
    
    @staticmethod
    def _create_dairy_farmer_demo() -> Dict[str, Any]:
        return {
            "applicant_name": "Rajesh Kumar",
            "email": "rajesh.dairy@example.com",
            "phone": "9876543210",
            "business_name": "Kumar Dairy Farm",
            "business_type": "Dairy Farming",
            "business_age": "5 years",
            "annual_turnover": 1500000,
            "loan_amount": 500000,
            "loan_purpose": "Buy dairy equipment",
            "state": "Gujarat",
            "city": "Anand",
            "credit_score": 720,
            "documents": ["Aadhar", "PAN", "Bank Statements", "Business Registration"]
        }
    
    @staticmethod
    def _create_retail_demo() -> Dict[str, Any]:
        return {
            "applicant_name": "Priya Sharma",
            "email": "priya.retail@example.com",
            "phone": "9876543211",
            "business_name": "Sharma Boutique",
            "business_type": "Retail Trade",
            "business_age": "3 years",
            "annual_turnover": 2500000,
            "loan_amount": 1000000,
            "loan_purpose": "Expand store and inventory",
            "state": "Maharashtra",
            "city": "Pune",
            "credit_score": 750,
            "documents": ["Aadhar", "PAN", "GST Certificate", "Bank Statements"]
        }
    
    @staticmethod
    def _create_manufacturing_demo() -> Dict[str, Any]:
        return {
            "applicant_name": "Amit Patel",
            "email": "amit.manufacturing@example.com",
            "phone": "9876543212",
            "business_name": "Patel Manufacturing Ltd.",
            "business_type": "Manufacturing",
            "business_age": "8 years",
            "annual_turnover": 8000000,
            "loan_amount": 5000000,
            "loan_purpose": "Working capital and machinery",
            "state": "Tamil Nadu",
            "city": "Chennai",
            "credit_score": 800,
            "documents": ["Aadhar", "PAN", "GST Certificate", "Bank Statements", "ITR"]
        }
    
    @staticmethod
    def _create_agricultural_demo() -> Dict[str, Any]:
        return {
            "applicant_name": "Suresh Reddy",
            "email": "suresh.agri@example.com",
            "phone": "9876543213",
            "business_name": "Reddy Farms",
            "business_type": "Agriculture",
            "business_age": "10 years",
            "annual_turnover": 1200000,
            "loan_amount": 300000,
            "loan_purpose": "Farm equipment and technology",
            "state": "Andhra Pradesh",
            "city": "Visakhapatnam",
            "credit_score": 680,
            "documents": ["Aadhar", "Land Papers", "Bank Statements"]
        }
    
    @staticmethod
    def _create_women_entrepreneur_demo() -> Dict[str, Any]:
        return {
            "applicant_name": "Neha Gupta",
            "email": "neha.startup@example.com",
            "phone": "9876543214",
            "business_name": "Neha's Digital Services",
            "business_type": "Services",
            "business_age": "2 years",
            "annual_turnover": 1800000,
            "loan_amount": 750000,
            "loan_purpose": "Technology and hiring",
            "state": "Delhi",
            "city": "New Delhi",
            "credit_score": 730,
            "documents": ["Aadhar", "PAN", "GST Certificate", "Bank Statements"]
        }
