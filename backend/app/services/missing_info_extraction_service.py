"""
Features 12 & 13: Smart Extracted Information & Missing Information Engine
"""
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from ..models import User, Application, Scheme

class SmartExtractionService:
    """Service for converting voice/OCR information into structured fields"""
    
    @staticmethod
    def extract_and_structure_info(
        raw_data: Dict[str, Any],
        data_source: str = "voice"  # or "ocr"
    ) -> Dict[str, Any]:
        """Convert voice/OCR information into structured fields"""
        
        structured_info = {
            "applicant_details": SmartExtractionService._extract_applicant_info(raw_data),
            "business_details": SmartExtractionService._extract_business_info(raw_data),
            "financial_details": SmartExtractionService._extract_financial_info(raw_data),
            "loan_details": SmartExtractionService._extract_loan_info(raw_data),
            "extraction_confidence": SmartExtractionService._calculate_extraction_confidence(raw_data),
            "source": data_source
        }
        
        return structured_info
    
    @staticmethod
    def _extract_applicant_info(data: Dict) -> Dict[str, Any]:
        """Extract applicant information"""
        return {
            "name": data.get("name") or data.get("applicant_name"),
            "email": data.get("email"),
            "phone": data.get("phone") or data.get("mobile"),
            "gender": data.get("gender"),
            "dob": data.get("dob") or data.get("date_of_birth"),
            "address": data.get("address"),
            "city": data.get("city"),
            "state": data.get("state"),
            "pincode": data.get("pincode")
        }
    
    @staticmethod
    def _extract_business_info(data: Dict) -> Dict[str, Any]:
        """Extract business information"""
        return {
            "business_name": data.get("business_name"),
            "business_type": data.get("business_type") or data.get("sector"),
            "business_age_years": data.get("business_age") or data.get("years_in_business"),
            "business_registration": data.get("registration_number"),
            "gst_number": data.get("gst_number") or data.get("gst"),
            "employees_count": data.get("employees") or data.get("staff_count"),
            "business_address": data.get("business_address"),
            "ownership_type": data.get("ownership_type") or data.get("sole_proprietor")
        }
    
    @staticmethod
    def _extract_financial_info(data: Dict) -> Dict[str, Any]:
        """Extract financial information"""
        return {
            "annual_turnover": data.get("annual_turnover") or data.get("turnover"),
            "monthly_revenue": data.get("monthly_revenue") or data.get("monthly_income"),
            "existing_liabilities": data.get("existing_liabilities") or data.get("other_loans"),
            "profit_margin": data.get("profit_margin"),
            "bank_account_holder": data.get("bank_account_holder"),
            "current_bank": data.get("current_bank")
        }
    
    @staticmethod
    def _extract_loan_info(data: Dict) -> Dict[str, Any]:
        """Extract loan information"""
        return {
            "loan_amount_required": data.get("loan_amount") or data.get("loan_needed"),
            "loan_purpose": data.get("loan_purpose") or data.get("purpose"),
            "preferred_tenure": data.get("tenure") or data.get("repayment_period"),
            "collateral_available": data.get("collateral"),
            "guarantor_available": data.get("guarantor"),
            "preferred_interest_rate": data.get("interest_rate_preference")
        }
    
    @staticmethod
    def _calculate_extraction_confidence(data: Dict) -> Dict[str, float]:
        """Calculate confidence scores for extracted information"""
        return {
            "applicant_confidence": 0.85 if data.get("name") and data.get("phone") else 0.6,
            "business_confidence": 0.80 if data.get("business_type") and data.get("business_age") else 0.5,
            "financial_confidence": 0.75 if data.get("annual_turnover") else 0.4,
            "loan_confidence": 0.90 if data.get("loan_amount") and data.get("loan_purpose") else 0.6,
            "overall_confidence": 0.8
        }


class MissingInformationService:
    """Service for detecting incomplete information and required documents"""
    
    @staticmethod
    def get_missing_information(
        user_id: int,
        application_id: int,
        db: Session
    ) -> Dict[str, Any]:
        """Detect incomplete information or missing documents"""
        
        user = db.query(User).filter(User.id == user_id).first()
        app = db.query(Application).filter(Application.id == application_id).first()
        
        if not user or not app:
            return {"error": "User or application not found"}
        
        missing_fields = MissingInformationService._find_missing_fields(user)
        missing_documents = MissingInformationService._find_missing_documents(app, db)
        
        overall_completeness = (
            (len(missing_fields) == 0) and (len(missing_documents) == 0)
        )
        
        return {
            "is_complete": overall_completeness,
            "missing_fields": missing_fields,
            "missing_documents": missing_documents,
            "total_missing": len(missing_fields) + len(missing_documents),
            "priority_actions": MissingInformationService._get_priority_actions(
                missing_fields, missing_documents
            ),
            "estimated_completion_time": MissingInformationService._estimate_completion_time(
                missing_fields, missing_documents
            ),
            "can_submit": len(missing_fields) == 0 and len(missing_documents) == 0
        }
    
    @staticmethod
    def _find_missing_fields(user: Any) -> List[Dict[str, Any]]:
        """Find missing required fields in user profile"""
        required_fields = [
            ("name", "Full Name"),
            ("email", "Email Address"),
            ("phone", "Phone Number"),
            ("dob", "Date of Birth"),
            ("gender", "Gender"),
            ("address", "Address"),
            ("state", "State"),
            ("city", "City"),
            ("business_type", "Business Type"),
            ("business_age", "Business Age"),
            ("annual_turnover", "Annual Turnover"),
            ("loan_amount", "Loan Amount Needed"),
            ("loan_purpose", "Loan Purpose")
        ]
        
        missing = []
        for field, label in required_fields:
            if not hasattr(user, field) or not getattr(user, field):
                missing.append({
                    "field": field,
                    "label": label,
                    "priority": "high" if field in ["name", "email", "phone", "loan_amount"] else "medium"
                })
        
        return missing
    
    @staticmethod
    def _find_missing_documents(app: Any, db: Session) -> List[Dict[str, Any]]:
        """Find missing required documents"""
        if not app.scheme:
            return []
        
        required_docs = app.scheme.required_documents if hasattr(app.scheme, 'required_documents') else []
        uploaded_docs = db.query(Document).filter(
            Document.application_id == app.id,
            Document.file_path.isnot(None)
        ).all()
        
        uploaded_types = set(doc.document_type for doc in uploaded_docs)
        
        missing = []
        for doc_type in required_docs:
            if doc_type not in uploaded_types:
                missing.append({
                    "document_type": doc_type,
                    "label": MissingInformationService._get_document_label(doc_type),
                    "priority": "high"
                })
        
        return missing
    
    @staticmethod
    def _get_document_label(doc_type: str) -> str:
        """Get readable label for document type"""
        label_map = {
            "aadhar": "Aadhar Card",
            "pan": "PAN Card",
            "bank_statement": "Bank Statement (6 months)",
            "itr": "Income Tax Returns",
            "business_registration": "Business Registration Certificate",
            "gst_certificate": "GST Certificate",
            "utility_bill": "Utility Bill",
            "property_document": "Property Document"
        }
        return label_map.get(doc_type, doc_type.replace("_", " ").title())
    
    @staticmethod
    def _get_priority_actions(missing_fields: List, missing_documents: List) -> List[str]:
        """Get priority actions to complete application"""
        actions = []
        
        if missing_fields:
            high_priority_fields = [f for f in missing_fields if f["priority"] == "high"]
            if high_priority_fields:
                actions.append(f"Complete {len(high_priority_fields)} required profile fields")
        
        if missing_documents:
            actions.append(f"Upload {len(missing_documents)} required documents")
        
        return actions[:3]
    
    @staticmethod
    def _estimate_completion_time(missing_fields: List, missing_documents: List) -> str:
        """Estimate time to complete missing items"""
        total_missing = len(missing_fields) + len(missing_documents)
        
        if total_missing == 0:
            return "Ready to submit!"
        elif total_missing <= 3:
            return "5-10 minutes"
        elif total_missing <= 6:
            return "15-20 minutes"
        else:
            return "30+ minutes"
