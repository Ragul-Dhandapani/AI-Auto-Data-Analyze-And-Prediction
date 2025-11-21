"""
Model Script Generator
Generates runnable Python scripts for exported models
"""
from typing import Dict, List


def generate_model_script(metadata: Dict, dataset: Dict) -> str:
    """Generate a runnable Python script for the model"""
    model_type = metadata.get("model_type", "Unknown")
    problem_type = metadata.get("problem_type", "regression")
    target_variable = metadata.get("target_variable", "target")
    feature_variables = metadata.get("feature_variables", [])
    model_params = metadata.get("model_params", {})
    
    imports = get_imports(model_type, problem_type)
    feature_list_str = format_feature_list(feature_variables)
    model_init = get_model_initialization(model_type, problem_type)
    training_code = get_training_code(problem_type)
    
    script = f"""{imports}

# Model Configuration
TARGET_VARIABLE = "{target_variable}"
FEATURE_VARIABLES = {feature_list_str}
MODEL_TYPE = "{model_type}"
PROBLEM_TYPE = "{problem_type}"
MODEL_PARAMS = {model_params}

def train_model(df, target_column=TARGET_VARIABLE, test_size=0.2, random_state=42):
    \"\"\"Train the {model_type} model\"\"\"
    print(f"Training {{MODEL_TYPE}} model...")
    
    X = df[FEATURE_VARIABLES].copy()
    y = df[target_column].copy()
    X = X.fillna(X.mean())
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    
{model_init}
    
{training_code}

def predict(df, model=None):
    \"\"\"Make predictions using the trained model\"\"\"
    if model is None:
        raise ValueError("Model not provided. Train first.")
    
    for feature in FEATURE_VARIABLES:
        if feature not in df.columns:
            raise ValueError(f"Missing feature: {{feature}}")
    
    X = df[FEATURE_VARIABLES].copy()
    X = X.fillna(X.mean())
    predictions = model.predict(X)
    return predictions

def save_model(model, filepath="model.pkl"):
    \"\"\"Save trained model\"\"\"
    joblib.dump(model, filepath)
    print(f"Model saved to {{filepath}}")

def load_model(filepath="model.pkl"):
    \"\"\"Load trained model\"\"\"
    model = joblib.load(filepath)
    print(f"Model loaded from {{filepath}}")
    return model

if __name__ == "__main__":
    print("="*60)
    print(f"Model: {{MODEL_TYPE}}")
    print(f"Type: {{PROBLEM_TYPE}}")
    print(f"Target: {{TARGET_VARIABLE}}")
    print(f"Features: {{len(FEATURE_VARIABLES)}}")
    print("="*60)
    print("\\nUsage:")
    print("  df = pd.read_csv('data.csv')")
    print("  model, metrics = train_model(df)")
    print("  save_model(model, 'trained.pkl')")
    print("="*60)
"""
    return script


def get_imports(model_type: str, problem_type: str) -> str:
    """Get import statements"""
    imports = """import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import """
    
    if problem_type == "regression":
        imports += "mean_squared_error, r2_score, mean_absolute_error"
    else:
        imports += "accuracy_score, precision_score, recall_score, f1_score"
    
    if "RandomForest" in model_type:
        if problem_type == "classification":
            imports += "\nfrom sklearn.ensemble import RandomForestClassifier"
        else:
            imports += "\nfrom sklearn.ensemble import RandomForestRegressor"
    elif "LinearRegression" in model_type:
        imports += "\nfrom sklearn.linear_model import LinearRegression"
    elif "LogisticRegression" in model_type:
        imports += "\nfrom sklearn.linear_model import LogisticRegression"
    elif "XGB" in model_type:
        imports += "\nimport xgboost as xgb"
    elif "GradientBoosting" in model_type:
        if problem_type == "classification":
            imports += "\nfrom sklearn.ensemble import GradientBoostingClassifier"
        else:
            imports += "\nfrom sklearn.ensemble import GradientBoostingRegressor"
    else:
        if problem_type == "classification":
            imports += "\nfrom sklearn.ensemble import RandomForestClassifier"
        else:
            imports += "\nfrom sklearn.ensemble import RandomForestRegressor"
    
    imports += "\nimport joblib\nimport warnings\nwarnings.filterwarnings('ignore')"
    return imports


def format_feature_list(features: List[str]) -> str:
    """Format feature list for Python code"""
    if not features:
        return "[]"
    formatted = "[\n        " + ",\n        ".join([f"'{f}'" for f in features]) + "\n    ]"
    return formatted


def get_model_initialization(model_type: str, problem_type: str) -> str:
    """Get model initialization code"""
    if "RandomForest" in model_type:
        if problem_type == "classification":
            return "    model = RandomForestClassifier(**MODEL_PARAMS, random_state=random_state, n_jobs=-1)"
        return "    model = RandomForestRegressor(**MODEL_PARAMS, random_state=random_state, n_jobs=-1)"
    elif "LinearRegression" in model_type:
        return "    model = LinearRegression()"
    elif "LogisticRegression" in model_type:
        return "    model = LogisticRegression(**MODEL_PARAMS, random_state=random_state, max_iter=1000)"
    elif "XGB" in model_type:
        if problem_type == "classification":
            return "    model = xgb.XGBClassifier(**MODEL_PARAMS, random_state=random_state, n_jobs=-1)"
        return "    model = xgb.XGBRegressor(**MODEL_PARAMS, random_state=random_state, n_jobs=-1)"
    else:
        if problem_type == "classification":
            return "    model = RandomForestClassifier(random_state=random_state, n_jobs=-1)"
        return "    model = RandomForestRegressor(random_state=random_state, n_jobs=-1)"


def get_training_code(problem_type: str) -> str:
    """Get training and evaluation code"""
    if problem_type == "regression":
        return """    print("Training...")
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    
    metrics = {'r2_score': r2, 'rmse': rmse, 'mae': mae}
    print(f"\\nR² Score: {r2:.4f}")
    print(f"RMSE: {rmse:.4f}")
    print(f"MAE: {mae:.4f}")
    return model, metrics"""
    else:
        return """    print("Training...")
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
    
    metrics = {'accuracy': accuracy, 'precision': precision, 'recall': recall, 'f1_score': f1}
    print(f"\\nAccuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    return model, metrics"""
