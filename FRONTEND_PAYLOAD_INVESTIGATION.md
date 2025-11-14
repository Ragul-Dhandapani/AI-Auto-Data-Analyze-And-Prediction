# Frontend Payload Investigation - Variable Selection Issue

## Critical Finding from Debug Logs

### What Backend is Receiving (WRONG!)
```json
{
  "target_variables": [],
  "user_target": null,
  "user_targets": {
    "target": null,
    "features": []
  }
}
```

### What Frontend Should Be Sending (CORRECT!)
```json
{
  "target_variable": "memory_usage_mb",  // singular, not plural
  "selected_features": ["cpu_usage", "latency_ms"],
  "mode": "manual"
}
```

## The Problem

**The backend is receiving COMPLETELY WRONG keys!**

- ❌ Receiving: `user_targets` (object), `user_target`, `target_variables`
- ✅ Expected: `target_variable` (string), `selected_features` (array)

These keys (`user_targets`, `user_target`) are **internal backend variable names**, NOT the HTTP request structure!

## Possible Causes

### Cause 1: Frontend is Sending Wrong Structure ⭐ MOST LIKELY
The frontend might be accidentally sending backend variable names instead of the correct payload structure.

**Check in PredictiveAnalysis.jsx around line 334:**
```javascript
payload.user_selection = {
  target_variable: variableSelection.target,      // Should be this
  selected_features: variableSelection.features,  // Should be this
  mode: variableSelection.mode
};
```

**Make sure it's NOT doing this:**
```javascript
// WRONG - Don't do this!
payload.user_selection = {
  user_target: variableSelection.target,  // ❌
  user_targets: {...},  // ❌
  target_variables: []  // ❌
};
```

### Cause 2: variableSelection State is Corrupted
The `variableSelection` state object might have wrong keys:
```javascript
// Check what's in variableSelection
console.log('variableSelection object:', JSON.stringify(variableSelection, null, 2));
```

### Cause 3: Modal is Returning Wrong Structure
The VariableSelectionModal might be calling `onConfirm` with wrong structure.

**Check in VariableSelectionModal.jsx around line 116:**
```javascript
const selection = {
  target: validTargets[0].target,      // Correct
  features: validTargets[0].features,  // Correct
  mode: mode
};
onConfirm(selection);
```

**Make sure it's NOT this:**
```javascript
// WRONG!
const selection = {
  user_target: null,  // ❌
  user_targets: {...},  // ❌
  target_variables: []  // ❌
};
```

## Debugging Steps

### Step 1: Add Console Logs in Frontend

**In VariableSelectionModal.jsx (before onConfirm):**
```javascript
const handleConfirm = () => {
  // ... existing code ...
  
  const selection = {
    target: validTargets[0].target,
    features: validTargets[0].features,
    mode: mode,
    problem_type: problemType
  };
  
  console.log('🟢 MODAL - Calling onConfirm with:', JSON.stringify(selection, null, 2));
  onConfirm(selection);
};
```

**In PredictiveAnalysis.jsx (in setVariableSelection callback):**
```javascript
const handleVariableSelectionComplete = (selection) => {
  console.log('🟡 PREDICTIVE - Received from modal:', JSON.stringify(selection, null, 2));
  setVariableSelection(selection);
  console.log('🟡 PREDICTIVE - State updated with:', JSON.stringify(selection, null, 2));
};
```

**In PredictiveAnalysis.jsx (before API call):**
```javascript
console.log('🔵 PREDICTIVE - variableSelection state:', JSON.stringify(variableSelection, null, 2));
console.log('🔵 PREDICTIVE - Building payload.user_selection:', JSON.stringify({
  target_variable: variableSelection.target,
  selected_features: variableSelection.features,
  mode: variableSelection.mode
}, null, 2));
```

**In PredictiveAnalysis.jsx (full payload before send):**
```javascript
console.log('🔴 SENDING TO API:', JSON.stringify(payload, null, 2));
```

### Step 2: Check Network Request

1. Open **Browser DevTools → Network tab**
2. Upload dataset and select variables
3. Click "Run Analysis"
4. Find the POST request to `/api/analysis/holistic`
5. Click on it → **Payload tab**
6. Look for `user_selection` object

**Expected structure:**
```json
{
  "dataset_id": "...",
  "workspace_name": "...",
  "user_selection": {
    "target_variable": "memory_usage_mb",
    "selected_features": ["cpu_usage", "latency_ms"],
    "mode": "manual"
  }
}
```

**If you see this instead, it's WRONG:**
```json
{
  "user_selection": {
    "user_target": null,
    "user_targets": {...},
    "target_variables": []
  }
}
```

### Step 3: Check Backend Logs

New debug logs added (backend restarted):
```
🔍 RAW REQUEST RECEIVED: {...entire request...}
🔍 USER_SELECTION EXTRACTED: {...user_selection only...}
```

Compare what frontend sends vs what backend receives.

## Likely Root Cause: Modal Returns Wrong Keys

Based on the structure, I suspect the modal is returning an object with wrong keys. Let me show you the fix:

### Fix in VariableSelectionModal.jsx

**Current (line 116-125):**
```javascript
const selection = {
  target: validTargets[0].target,      // ✅ Correct
  features: validTargets[0].features,  // ✅ Correct
  mode: mode,
  problem_type: problemType,
  time_column: problemType === "time_series" ? timeColumn : undefined,
  aiSuggestions: aiSuggestions
};
```

**Make absolutely sure the keys are:**
- `target` (not `user_target`)
- `features` (not `user_targets` or `target_variables`)
- `mode`
- `problem_type`

### Fix in PredictiveAnalysis.jsx

**Current (line 334-339):**
```javascript
payload.user_selection = {
  target_variable: variableSelection.target,      // Maps modal's "target" to "target_variable"
  selected_features: variableSelection.features,  // Maps modal's "features" to "selected_features"
  mode: variableSelection.mode,
  ai_suggestions: variableSelection.aiSuggestions
};
```

**Verify this mapping is correct!** The modal returns:
- `selection.target` → becomes → `target_variable`
- `selection.features` → becomes → `selected_features`

## Test Case

### Input
1. Upload `application_latency.csv`
2. Open Variable Selection Modal
3. Select target: `memory_usage_mb`
4. Select features: `cpu_usage`, `latency_ms`, `network_traffic_mb`
5. Mode: Manual
6. Click "Confirm Selection"
7. Click "Run Analysis"

### Expected Console Output

```
🟢 MODAL - Calling onConfirm with: {
  "target": "memory_usage_mb",
  "features": ["cpu_usage", "latency_ms", "network_traffic_mb"],
  "mode": "manual",
  "problem_type": "regression"
}

🟡 PREDICTIVE - Received from modal: {
  "target": "memory_usage_mb",
  "features": ["cpu_usage", "latency_ms", "network_traffic_mb"],
  "mode": "manual",
  "problem_type": "regression"
}

🔵 PREDICTIVE - Building payload.user_selection: {
  "target_variable": "memory_usage_mb",
  "selected_features": ["cpu_usage", "latency_ms", "network_traffic_mb"],
  "mode": "manual"
}

🔴 SENDING TO API: {
  "dataset_id": "ea216840-5e44-4ab7-ac87-ab653b093e84",
  "workspace_name": "latency_141125_3",
  "user_selection": {
    "target_variable": "memory_usage_mb",
    "selected_features": ["cpu_usage", "latency_ms", "network_traffic_mb"],
    "mode": "manual"
  },
  "problem_type": "regression"
}
```

### Expected Backend Log

```
🔍 RAW REQUEST RECEIVED: {
  "dataset_id": "ea216840-5e44-4ab7-ac87-ab653b093e84",
  "workspace_name": "latency_141125_3",
  "user_selection": {
    "target_variable": "memory_usage_mb",
    "selected_features": ["cpu_usage", "latency_ms", "network_traffic_mb"],
    "mode": "manual"
  },
  "problem_type": "regression"
}

🔍 USER_SELECTION EXTRACTED: {
  "target_variable": "memory_usage_mb",
  "selected_features": ["cpu_usage", "latency_ms", "network_traffic_mb"],
  "mode": "manual"
}

🔍 DEBUG - user_target: memory_usage_mb, user_targets: []
🔍 DEBUG - Converting single target. Features extracted: ["cpu_usage", "latency_ms", "network_traffic_mb"]
Validating user selection: targets=['memory_usage_mb'], features=['cpu_usage', 'latency_ms', 'network_traffic_mb']
```

## Quick Diagnostic

**Run this in browser console when you have a selection:**
```javascript
// After selecting variables and before clicking "Run Analysis"
console.log('variableSelection:', JSON.stringify(variableSelection, null, 2));
```

If you see keys like `user_target`, `user_targets`, `target_variables` in the output, **the modal is setting wrong keys!**

## Summary

The issue is that somewhere in the frontend:
1. ❌ Wrong keys are being set (`user_target`, `user_targets`, `target_variables`)
2. ✅ Should be: `target`, `features` (in modal) → `target_variable`, `selected_features` (in payload)

**Next Action:** Add all the console.log statements above and share:
1. Browser console output
2. Network tab → Request Payload
3. Backend logs with 🔍 markers

This will pinpoint exactly where the wrong keys are being introduced!
