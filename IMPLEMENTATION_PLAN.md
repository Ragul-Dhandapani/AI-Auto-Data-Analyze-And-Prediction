# Implementation Plan for Remaining Tasks

## ✅ Completed
- **Task #9**: JSON Serialization Fix - Added `sanitize_json_response()` function to handle NaN/inf values
- **Oracle Adapter**: Fully fixed and tested (11/11 tests passing)

## 🚧 In Progress

### **Task #1: UI Section Reordering in PredictiveAnalysis.jsx** (P0)

**Current Section Order (approximate line numbers):**
1. Volume Insights (~line 1134)
2. Business Recommendations (~line 1367)
3. Key Correlations (~line 1441)
4. ML Model Comparison (~line 1609)
5. Actual vs Predicted (~line 2128)
6. Forecasting & Insights (~line 2722)
7. Outliers (embedded in various sections)

**Target Section Order:**
1. Key Correlations
2. ML Model Comparison
3. Forecast & Insights
4. Actual vs Prediction
5. Outliers
6. Business Recommendations
7. Volume Insights

**Implementation Approach:**
- The file is 3200+ lines - too large for single edits
- Need to locate each section's JSX block
- Cut and paste in correct order within the main return statement
- Test after reordering to ensure no broken references

---

### **Task #2: Complete UI for New Features** (P1)

#### 2.1 WorkspaceManager.jsx
**Location**: `/app/frontend/src/components/WorkspaceManager.jsx`
**Current Status**: Stub component
**Features to Implement:**
- List all workspaces in a grid/table
- Create new workspace modal (name, description, tags)
- Delete workspace with confirmation
- Navigate to workspace details
- Show workspace stats (dataset count, training count)
- Search/filter workspaces

#### 2.2 ModelMonitoring.jsx
**Location**: `/app/frontend/src/components/ModelMonitoring.jsx`
**Current Status**: Stub component
**Features to Implement:**
- Display model performance over time (line chart)
- Show recent training runs (table)
- Model accuracy trends
- Training duration comparison
- Filter by date range, model type, workspace
- Real-time status indicators

#### 2.3 HyperparameterSuggestions.jsx
**Location**: `/app/frontend/src/components/HyperparameterSuggestions.jsx`
**Current Status**: Stub component
**Features to Implement:**
- Display AI-powered tuning suggestions
- Show recommended parameter ranges
- Explain why each parameter matters
- Allow user to apply suggestions
- Show before/after comparison
- Integration point in PredictiveAnalysis.jsx

---

### **Task #3: Implement Holistic Workspace Score** (P1)

#### 3.1 Backend API
**New Endpoint**: `GET /api/workspace/{workspace_id}/holistic-score`
**File**: `/app/backend/app/routes/workspace.py`

**Algorithm:**
```python
def calculate_holistic_score(workspace_id):
    # Get all training metadata for workspace
    trainings = get_training_history(workspace_id)
    
    if not trainings:
        return {"score": 0, "message": "No training data"}
    
    # Calculate metrics
    avg_accuracy = mean([t.metrics.r2_score for t in trainings if t.metrics.r2_score])
    best_model = max(trainings, key=lambda t: t.metrics.r2_score)
    improvement_trend = calculate_trend(trainings)
    
    # Weighted score (0-100)
    score = (
        avg_accuracy * 0.4 +
        best_model.r2_score * 0.3 +
        improvement_trend * 0.2 +
        (training_count / 10) * 0.1  # Bonus for more training
    ) * 100
    
    return {
        "score": round(score, 2),
        "avg_accuracy": avg_accuracy,
        "best_model": best_model.model_name,
        "training_count": len(trainings),
        "trend": "improving" if improvement_trend > 0 else "declining"
    }
```

#### 3.2 Frontend Display
**File**: `/app/frontend/src/components/WorkspaceManager.jsx`
- Fetch holistic score for each workspace
- Display as circular progress indicator
- Show trend indicator (↗ ↘ →)
- Color code: Green (>80), Yellow (50-80), Red (<50)

---

### **Task #4: Connect AutoML Toggle to Backend** (P2)

#### 4.1 Backend Changes
**File**: `/app/backend/app/routes/analysis.py`
- Add `enable_automl` parameter to holistic_analysis endpoint
- Pass to model training functions
- Trigger hyperparameter tuning when enabled

#### 4.2 Frontend Changes
**File**: `/app/frontend/src/components/DataSourceSelector.jsx`
- Ensure toggle state is captured
- Pass `enableAutoML: true/false` in analysis request
- Display "AutoML Enabled" badge when active

---

### **Task #5: Differentiator Features** (P3)

#### 5.1 Custom Model Support
- Upload .pkl/.joblib model files
- Validate model compatibility
- Register in model registry
- Use in predictions

#### 5.2 Model Monitoring Dashboard
- Real-time performance tracking
- Drift detection
- Alert system for degradation

#### 5.3 Instant API Deployment
- One-click Flask/FastAPI endpoint generation
- Docker containerization
- Deployment to cloud providers

---

### **Task #6: Domain-Specific Visualizations** (P3)

**File**: `/app/backend/app/services/domain_visualizations.py`
- Implement industry-specific chart logic
- Add retail-specific charts (sales funnels, cohort analysis)
- Add finance charts (portfolio allocation, risk curves)
- Add healthcare charts (patient outcomes, treatment efficacy)

---

### **Task #7: Optimize Large File Uploads** (P3)

**Files**:
- `/app/backend/app/routes/datasource.py`
- `/app/frontend/src/components/DataSourceSelector.jsx`

**Implementation:**
- Chunked upload (5MB chunks)
- Progress bar with percentage
- Pause/resume functionality
- Server-side chunk assembly

---

### **Task #8: Code Refactoring** (P3)

#### 8.1 Break Down PredictiveAnalysis.jsx
Extract into smaller components:
- `KeyCorrelationsSection.jsx`
- `MLModelComparisonSection.jsx`
- `ForecastInsightsSection.jsx`
- `ActualVsPredictedSection.jsx`
- `OutliersSection.jsx`
- `BusinessRecommendationsSection.jsx`
- `VolumeInsightsSection.jsx`

#### 8.2 Refactor DataSourceSelector.jsx
Extract:
- `FileUploadTab.jsx`
- `DatabaseConnectionTab.jsx`
- `CustomQueryTab.jsx`
- `WorkspaceSelector.jsx`

---

## 📊 Implementation Progress Tracker

| Task | Status | Estimated Time | Actual Time | Priority |
|------|--------|---------------|-------------|----------|
| #9 JSON Fix | ✅ Complete | 1h | 0.5h | P0 |
| #1 UI Reorder | 🔄 In Progress | 2h | - | P0 |
| #2.1 WorkspaceManager | ⏳ Pending | 2h | - | P1 |
| #2.2 ModelMonitoring | ⏳ Pending | 2h | - | P1 |
| #2.3 HyperparameterSuggestions | ⏳ Pending | 1h | - | P1 |
| #3 Holistic Score | ⏳ Pending | 2h | - | P1 |
| #4 AutoML Toggle | ⏳ Pending | 1h | - | P2 |
| #5 Differentiator Features | ⏳ Pending | 4h | - | P3 |
| #6 Domain Visualizations | ⏳ Pending | 2h | - | P3 |
| #7 Optimize Uploads | ⏳ Pending | 3h | - | P3 |
| #8 Refactoring | ⏳ Pending | 4h | - | P3 |

**Total Estimated**: ~24 hours
**Completed**: ~0.5 hours
**Remaining**: ~23.5 hours

---

## 🐛 Known Issues
1. **Oracle Client Library** - Disappears on code reload, requires re-running install script
2. **Backend Startup Failure** - Due to Oracle client issue (ephemeral environment)
3. **Large Component Files** - PredictiveAnalysis.jsx (3200+ lines) needs refactoring

---

## 🎯 Next Immediate Steps
1. Resolve Oracle client persistence issue
2. Complete UI section reordering (#1)
3. Implement workspace manager UI (#2.1)
4. Create holistic score API (#3)
5. Complete remaining high-priority tasks (#2.2, #2.3, #4)
