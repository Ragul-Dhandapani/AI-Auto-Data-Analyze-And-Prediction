"""
Model Export Service
Helper functions for generating model export artifacts
"""
from typing import Dict, List, Any
import re
from datetime import datetime


def sanitize_filename(filename: str) -> str:
    """Remove invalid characters from filename"""
    sanitized = re.sub(r'[^\w\-.]', '_', filename)
    return sanitized


def generate_requirements_txt(models_metadata: List[Dict]) -> str:
    """Generate requirements.txt with all necessary dependencies"""
    requirements = [
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "scikit-learn>=1.3.0",
        "joblib>=1.3.0"
    ]
    
    model_types = set()
    for metadata in models_metadata:
        model_type = metadata.get("model_type", "").lower()
        model_types.add(model_type)
    
    if any("xgb" in mt or "xgboost" in mt for mt in model_types):
        requirements.append("xgboost>=2.0.0")
    
    if any("lgb" in mt or "lightgbm" in mt for mt in model_types):
        requirements.append("lightgbm>=4.0.0")
    
    if any("catboost" in mt for mt in model_types):
        requirements.append("catboost>=1.2.0")
    
    requirements.append("matplotlib>=3.7.0")
    
    return "\n".join(requirements) + "\n"


def get_model_rationale(model_type: str, problem_type: str, metrics: Dict) -> str:
    """Generate model rationale based on type and performance"""
    rationales = {
        "RandomForest": "Random Forest combines multiple decision trees to improve accuracy and reduce overfitting. Robust to outliers.",
        "LinearRegression": "Linear Regression models relationships using a linear equation. Interpretable and fast.",
        "LogisticRegression": "Logistic Regression models probabilities for classification. Fast and interpretable.",
        "XGBClassifier": "XGBoost uses gradient boosting for high accuracy classification.",
        "XGBRegressor": "XGBoost Regressor builds ensemble trees for effective regression.",
        "GradientBoosting": "Gradient Boosting combines weak learners for powerful predictions.",
        "SVM": "Support Vector Machine finds optimal hyperplanes for classification.",
        "KNN": "K-Nearest Neighbors classifies based on similar examples.",
    }
    
    base_rationale = rationales.get(model_type, f"{model_type} is suitable for {problem_type} tasks.")
    
    if problem_type == "regression":
        r2 = metrics.get('r2_score', 0)
        if r2 > 0.8:
            performance_note = "Excellent performance on the dataset."
        elif r2 > 0.6:
            performance_note = "Good performance on the dataset."
        else:
            performance_note = "Moderate performance. Consider tuning."
    else:
        acc = metrics.get('accuracy', 0)
        if acc > 0.9:
            performance_note = "Excellent accuracy achieved."
        elif acc > 0.75:
            performance_note = "Good accuracy achieved."
        else:
            performance_note = "Moderate accuracy. Consider tuning."
    
    return f"{base_rationale} {performance_note}"


def generate_readme_md(dataset: Dict, models_metadata: List[Dict]) -> str:
    """Generate comprehensive README.md"""
    dataset_name = dataset.get("name", "Unknown Dataset")
    row_count = dataset.get("row_count", "N/A")
    column_count = dataset.get("column_count", "N/A")
    
    readme = f"""# Exported Models - {dataset_name}

## Dataset Information
- **Dataset Name**: {dataset_name}
- **Total Rows**: {row_count}
- **Total Columns**: {column_count}
- **Export Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Overview
This package contains {len(models_metadata)} trained ML model(s) from PROMISE AI.
Each model includes a runnable Python script for predictions.

---

## Exported Models

"""
    
    for idx, metadata in enumerate(models_metadata, 1):
        model_type = metadata.get("model_type", "Unknown")
        problem_type = metadata.get("problem_type", "unknown")
        target_variable = metadata.get("target_variable", "unknown")
        feature_variables = metadata.get("feature_variables", [])
        metrics = metadata.get("metrics", {})
        
        readme += f"""### Model {idx}: {model_type}

**Problem Type**: {problem_type.capitalize()}
**Target Variable**: `{target_variable}`
**Feature Variables**: {len(feature_variables)} features

**Performance Metrics**:
"""
        
        if problem_type == "regression":
            readme += f"""- R² Score: {metrics.get('r2_score', 'N/A')}
- RMSE: {metrics.get('rmse', 'N/A')}
- MAE: {metrics.get('mae', 'N/A')}
"""
        else:
            readme += f"""- Accuracy: {metrics.get('accuracy', 'N/A')}
- Precision: {metrics.get('precision', 'N/A')}
- Recall: {metrics.get('recall', 'N/A')}
"""
        
        readme += f"""
**Model Rationale**: {get_model_rationale(model_type, problem_type, metrics)}

**Script File**: `model_{idx}_{sanitize_filename(model_type)}.py`

---

"""
    
    readme += """## Usage

### Installation
```bash
pip install -r requirements.txt
```

### Training
```python
from model_1_RandomForest import train_model
import pandas as pd

df = pd.read_csv("your_data.csv")
model, metrics = train_model(df, target_column='your_target')
print(f"Metrics: {metrics}")
```

### Prediction
```python
from model_1_RandomForest import predict, load_model

model = load_model("trained_model.pkl")
predictions = predict(new_data, model)
```

---

**Generated by PROMISE AI** - """ + datetime.now().strftime("%Y-%m-%d") + "\n"
    
    return readme
