"""
API Routes for all 20 new features
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from ..database import get_db
from ..services.eligibility_explanation_service import EligibilityExplanationService
from ..services.match_cards_service import MatchCardsService
from ..services.readiness_service import ReadinessService
from ..services.partner_matching_service import PartnerMatchingService, TimelineService
from ..services.comparison_notification_service import SchemeComparisonService, NotificationService
from ..services.missing_info_extraction_service import SmartExtractionService, MissingInformationService
from ..services.emi_repayment_service import EMICalculatorService, RepaymentBreakdownService
from ..services.offline_analytics_service import OfflineDataService, GeographicAnalyticsService, SchemePerformanceAnalyticsService
from ..services.report_demo_service import ApplicantReportService, DemoModeService
from ..auth import require_role

router = APIRouter(prefix="/api/v1/features", tags=["Features"])

# Feature 1: AI Eligibility Explanation
@router.get("/eligibility-explanation/{user_id}/{scheme_id}")
def get_eligibility_explanation(
    user_id: int,
    scheme_id: int,
    db: Session = Depends(get_db)
):
    """Get AI-powered eligibility explanation"""
    return EligibilityExplanationService.get_eligibility_explanation(user_id, scheme_id, db)

# Feature 2: Personalized Match Cards
@router.post("/match-cards/{user_id}")
def generate_match_cards(
    user_id: int,
    scheme_ids: List[int],
    db: Session = Depends(get_db)
):
    """Generate personalized match cards for schemes"""
    return MatchCardsService.generate_match_cards(user_id, scheme_ids, db)

# Features 3 & 4: Readiness Scores
@router.get("/application-readiness/{user_id}/{application_id}")
def get_application_readiness(
    user_id: int,
    application_id: int,
    db: Session = Depends(get_db)
):
    """Get application readiness score"""
    return ReadinessService.get_application_readiness(user_id, application_id, db)

@router.get("/document-readiness/{user_id}/{application_id}")
def get_document_readiness(
    user_id: int,
    application_id: int,
    db: Session = Depends(get_db)
):
    """Get document readiness score"""
    return ReadinessService.get_document_readiness(user_id, application_id, db)

# Feature 6: Smart Partner Matching
@router.get("/partner-matching/{user_id}/{scheme_id}")
def get_ranked_partners(
    user_id: int,
    scheme_id: int,
    location: str = Query(...),
    db: Session = Depends(get_db)
):
    """Get ranked partners for loan"""
    return PartnerMatchingService.get_ranked_partners(user_id, scheme_id, location, db)

# Feature 7: Application Timeline
@router.get("/application-timeline/{application_id}")
def get_application_timeline(
    application_id: int,
    db: Session = Depends(get_db)
):
    """Get application progress timeline"""
    return TimelineService.get_application_timeline(application_id, db)

# Feature 9: Scheme Comparison
@router.post("/scheme-comparison")
def compare_schemes(
    scheme_ids: List[int],
    db: Session = Depends(get_db)
):
    """Compare multiple schemes side-by-side"""
    return SchemeComparisonService.compare_schemes(scheme_ids, db)

# Feature 10: Notifications
@router.get("/notifications/{user_id}")
def get_notifications(
    user_id: int,
    unread_only: bool = False,
    db: Session = Depends(get_db)
):
    """Get user notifications"""
    return NotificationService.get_user_notifications(user_id, db, unread_only)

@router.post("/notifications/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db)
):
    """Mark notification as read"""
    return NotificationService.mark_as_read(notification_id, db)

# Feature 12: Smart Extraction
@router.post("/extract-information")
def extract_information(
    raw_data: dict,
    data_source: str = "voice"
):
    """Extract and structure information from voice/OCR"""
    return SmartExtractionService.extract_and_structure_info(raw_data, data_source)

# Feature 13: Missing Information
@router.get("/missing-information/{user_id}/{application_id}")
def get_missing_information(
    user_id: int,
    application_id: int,
    db: Session = Depends(get_db)
):
    """Get missing information and documents"""
    return MissingInformationService.get_missing_information(user_id, application_id, db)

# Feature 15: EMI Calculator
@router.post("/emi-calculator")
def calculate_emi(
    loan_amount: float,
    scheme_id: int,
    tenure_months: int = None,
    db: Session = Depends(get_db)
):
    """Calculate EMI using scheme parameters"""
    return EMICalculatorService.calculate_emi(loan_amount, scheme_id, tenure_months, db)

@router.post("/emi-comparison")
def compare_emi(
    loan_amount: float,
    scheme_ids: List[int],
    db: Session = Depends(get_db)
):
    """Compare EMI across schemes"""
    return EMICalculatorService.compare_emi_across_schemes(loan_amount, scheme_ids, db)

# Feature 16: Repayment Breakdown
@router.post("/repayment-breakdown")
def get_repayment_breakdown(
    loan_amount: float,
    scheme_id: int,
    tenure_months: int = None,
    db: Session = Depends(get_db)
):
    """Get repayment breakdown visualization"""
    return RepaymentBreakdownService.get_repayment_breakdown(
        loan_amount, scheme_id, tenure_months, db
    )

# Feature 17: Offline Data
@router.get("/offline-data/{user_id}")
def get_offline_cache(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get data for offline access"""
    return OfflineDataService.get_offline_cache_data(user_id, db)

@router.get("/sync-status/{user_id}")
def check_sync(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Check data synchronization status"""
    return OfflineDataService.check_sync_status(user_id, db)

# Feature 18: Geographic Analytics (Admin)
@router.get("/admin/geographic-analytics", dependencies=[Depends(require_role("admin"))])
def get_geographic_analytics(
    db: Session = Depends(get_db)
):
    """Get geographic demand analytics"""
    return GeographicAnalyticsService.get_geographic_analytics(db)

# Feature 19: Scheme Performance Analytics (Admin)
@router.get("/admin/scheme-performance", dependencies=[Depends(require_role("admin"))])
def get_scheme_performance(
    db: Session = Depends(get_db)
):
    """Get scheme performance analytics"""
    return SchemePerformanceAnalyticsService.get_scheme_performance(db)

# Feature 14: Partner Report
@router.get("/partner-report/{application_id}")
def get_partner_report(
    application_id: int,
    db: Session = Depends(get_db)
):
    """Generate applicant report for partners"""
    return ApplicantReportService.generate_partner_report(application_id, db)

# Feature 20: Demo Mode
@router.get("/demo/scenarios")
def get_demo_scenarios():
    """Get available demo scenarios"""
    return DemoModeService.get_demo_scenarios()

@router.post("/demo/create/{scenario_id}")
def create_demo_application(
    scenario_id: int,
    role: str = "applicant"
):
    """Create a demo application"""
    return DemoModeService.create_demo_application(scenario_id, role)

# Feature 8: Government Analytics Dashboard
@router.get("/admin/dashboard", dependencies=[Depends(require_role("admin"))])
def get_admin_dashboard(db: Session = Depends(get_db)):
    """Get government analytics dashboard"""
    geo_data = GeographicAnalyticsService.get_geographic_analytics(db)
    scheme_data = SchemePerformanceAnalyticsService.get_scheme_performance(db)
    
    return {
        "dashboard": "Government Analytics",
        "timestamp": datetime.utcnow().isoformat(),
        "sections": {
            "geographic_analytics": geo_data,
            "scheme_performance": scheme_data,
            "summary": {
                "total_applications": geo_data.get("total_applications", 0),
                "total_users": geo_data.get("total_users", 0),
                "approval_rate": scheme_data.get("overall_approval_rate", 0)
            }
        }
    }

