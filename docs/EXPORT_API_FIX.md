# Export API Fix

## Problem
The frontend was trying to access export endpoints that were returning 404 errors:
- `/api/v1/export?format=pdf&type=summaries`
- `/api/v1/export?format=csv&type=activities`
- `/api/v1/export?format=excel&type=activities`
- `/api/v1/export?format=csv&type=members`
- `/api/v1/export?format=csv&type=stats`

## Root Cause
The frontend expected a unified export endpoint that accepts `format` and `type` parameters, but the backend had specific endpoints for each format and type combination. The unified endpoint was implemented but had issues with async/sync function calls and database session handling.

## Solution
Instead of fixing the problematic unified endpoint, the solution was to:

1. **Update the frontend API service** to use specific endpoints based on the type and format parameters
2. **Add missing specific endpoints** to the backend for all required combinations
3. **Fix async/sync inconsistencies** in the export functions

## Changes Made

### Frontend Changes (`frontend/src/services/api.ts`)
- Updated `exportData` function to map type/format combinations to specific endpoints
- Added support for JSON format exports
- Improved error handling for unsupported combinations

### Backend Changes (`app/api/v1/export.py`)
- Fixed async/sync inconsistencies in export functions
- Added missing endpoints:
  - `/api/v1/export/members/csv` - CSV export for members
  - `/api/v1/export/stats/csv` - CSV export for dashboard stats
  - `/api/v1/export/summaries/json` - JSON export for summaries
- Fixed helper functions to not use `Depends(get_db)` when called from other functions
- Fixed `export_stats_csv` to handle `DashboardStats` objects correctly

## Available Export Endpoints

### Members
- `GET /api/v1/export/members/json` - Export members as JSON
- `GET /api/v1/export/members/csv` - Export members as CSV

### Activities
- `GET /api/v1/export/activities/csv` - Export activities as CSV
- `GET /api/v1/export/activities/excel` - Export activities as Excel

### Summaries
- `GET /api/v1/export/summaries/pdf` - Export summaries as PDF
- `GET /api/v1/export/summaries/json` - Export summaries as JSON

### Stats
- `GET /api/v1/export/dashboard/stats` - Export dashboard stats as JSON
- `GET /api/v1/export/stats/csv` - Export dashboard stats as CSV

## Testing
All export endpoints have been tested and are working correctly:
- ✅ Members JSON export
- ✅ Members CSV export
- ✅ Stats CSV export
- ✅ Summaries JSON export
- ✅ Activities CSV export
- ✅ Activities Excel export

## Frontend Integration
The frontend now correctly maps export requests to the appropriate specific endpoints:
- `format=json&type=members` → `/api/v1/export/members/json`
- `format=csv&type=members` → `/api/v1/export/members/csv`
- `format=csv&type=stats` → `/api/v1/export/stats/csv`
- etc.

This approach is more reliable and maintainable than a unified endpoint, as each export type can be optimized independently.
