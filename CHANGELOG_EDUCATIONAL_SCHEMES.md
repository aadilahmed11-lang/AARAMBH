# AARAMBH - Educational Schemes Update

## Overview
This update adds support for **Educational Schemes** in addition to the existing **Business Schemes**. Users now have two separate dashboards to explore schemes matching their needs.

## Changes Made

### Backend Changes

#### 1. **Database Models** (`backend/app/models.py`)
- Added `scheme_type` field to the `Scheme` model
  - Values: `"business"` (default) or `"education"`
  - Allows distinguishing between business and educational schemes

#### 2. **Seed Data** (`backend/seed.py`)
- Added 5 new educational schemes:
  - National Scholarship for Higher Education
  - Skill Development Program Grants
  - Girl Child Education Fund
  - Technical Education Assistance
  - Educational Loan Facility
- Updated existing 5 business schemes with explicit `scheme_type="business"`
- Added educational scheme documents (e.g., Educational Certificate)

### Frontend Changes

#### 1. **Updated SchemesPage Component** (`frontend/src/App.jsx`)
- Added `schemeType` prop (default: `"business"`)
- Filters schemes by `scheme_type` on load
- Filters AI recommendations by scheme type
- Dynamic titles and descriptions based on scheme type
  - Business: "Business Schemes" with business-focused copy
  - Education: "Educational Schemes" with education-focused copy

#### 2. **Updated Dashboard Component** (`frontend/src/App.jsx`)
- Added two new quick action buttons:
  - **Business Schemes**: Opens the business schemes dashboard
  - **Educational Schemes**: Opens the educational schemes dashboard
- Uses appropriate icons (Building2 for business, Globe2 for education)
- Maintains all existing functionality

#### 3. **Updated App Routing** (`frontend/src/App.jsx`)
- New page routes:
  - `business-schemes`: Shows business schemes with AI matching
  - `education-schemes`: Shows educational schemes with AI matching
- Updated dashboard primary action button to navigate to business schemes
- Backward compatible with existing `schemes` route

## User Experience

### For Applicants:
1. **Main Dashboard** now shows two separate scheme categories in Quick Actions
2. **Business Schemes Dashboard**
   - AI-powered scheme matching for business loans
   - Personalized rankings based on profile
   - Loan amounts, interest rates, and tenures
   
3. **Educational Schemes Dashboard**
   - Browse available educational opportunities
   - Scholarships and educational loan assistance
   - No loan requirements (appropriate for education context)

## API Considerations

**Note**: The current backend API endpoints (`/schemes/`, `/recommendations/rank`) return all schemes. The filtering by `scheme_type` happens on the frontend.

For production deployment, consider:
- Adding `?type=business` or `?type=education` query parameter to `/schemes/` endpoint
- Filtering recommendations in the `/recommendations/rank` endpoint
- Adding database indexes on `scheme_type` for performance

## Database Migration

When deploying this update:

1. **First-time deployment** (fresh database):
   - Run `python seed.py` to populate both business and educational schemes

2. **Existing deployment** (with data):
   ```sql
   -- Add the new column
   ALTER TABLE schemes ADD COLUMN scheme_type VARCHAR(50) DEFAULT 'business' NOT NULL;
   
   -- Update existing schemes if needed
   UPDATE schemes SET scheme_type = 'business' WHERE id IN (1,2,3,4,5);
   ```

## Testing Checklist

- [ ] Demo user can see both Business and Educational Schemes buttons in dashboard
- [ ] Business Schemes dashboard filters and displays only business schemes
- [ ] Educational Schemes dashboard filters and displays only educational schemes
- [ ] AI matching works correctly for each scheme type
- [ ] Eligibility rules apply correctly for each scheme type
- [ ] Document requirements differ appropriately (Business Proof vs Educational Certificate)
- [ ] Navigation between dashboards is smooth
- [ ] All existing features remain functional

## Files Modified

1. `backend/app/models.py` - Added scheme_type to Scheme model
2. `backend/seed.py` - Updated seed data with educational schemes
3. `frontend/src/App.jsx` - Updated SchemesPage, Dashboard, and App routing

## Rollback (if needed)

1. Restore from `frontend/src/App.jsx.backup`
2. Revert `models.py` changes (remove `scheme_type` field)
3. Run seed.py with the original scheme data only

## Future Enhancements

- [ ] Backend API filtering by scheme_type
- [ ] Separate recommendation engines for business vs education
- [ ] Educational profile questionnaire (different from business profile)
- [ ] Educational document OCR rules
- [ ] Partner types specific to educational institutions


## 2026-09-17 — 50 km Channel Partner Selection
- Added a hard 50 km maximum radius to applicant partner routing.
- Added distance-sorted partner cards with address, type, phone, email, capacity and rating.
- Added selected-scheme interest rate to each partner card.
- Added Google Maps directions links.
- Added browser geolocation capture during the application partner step.
- Added selected partner persistence and application submission using the selected partner.
