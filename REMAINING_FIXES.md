# Remaining Issues - Comprehensive Fix Plan

## Issues to Fix

### Issue #1: Dataset Deletion
**Status**: Oracle adapter delete_dataset works, but might fail due to:
- Foreign key constraints (file_id references)
- Need to delete associated files first

**Fix**: Update delete endpoint to delete files first, then dataset

### Issue #2: ML Model Comparison Missing
**Root Cause**: Multi-target prediction not showing comparison table
**Fix Needed**: Check PredictiveAnalysis.jsx for multi-target rendering

### Issue #3: DateTime Detection
**Status**: Endpoint exists and looks correct
**Possible Issue**: Data type conversion when loading from Oracle
**Fix**: Ensure dtypes are properly applied during load (already done)

### Issue #4: Tab Switching State Loss
**Root Cause**: Frontend not preserving cached results properly
**Fix**: Already has caching in DashboardPage, might be useEffect dependency issue

### Issue #6: Prophet Not Showing Results
**Root Cause**: time_series_service might be returning incomplete data
**Fix**: Check Prophet forecast response structure

### Issue #7: Feedback Tab Not Recognizing Analysis
**Root Cause**: Feedback panel checking for model_name that doesn't exist
**Fix**: Pass proper model name from analysis results

### Issue #11: Technical Error Messages
**Root Cause**: sklearn/xgboost errors shown directly to users
**Fix**: Add error translation layer in hyperparameter tuning endpoint
