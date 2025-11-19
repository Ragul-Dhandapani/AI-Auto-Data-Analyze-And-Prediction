"""
Model Export Route
Generates production-ready Python code for trained models
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, List, Any
import os
import json
from pathlib import Path
import tempfile
import zipfile
import io

router = APIRouter()


class ModelExportRequest(BaseModel):
    dataset_id: str
    model_names: List[str]  # Multiple models: ["random_forest", "xgboost", "linear_regression"]
    include_preprocessing: bool = True
    include_evaluation: bool = True
    target_column: str
    feature_columns: List[str]
    analysis_results: Optional[Dict[str, Any]] = None  # Full analysis results for model comparison


@router.post("/export/code")
async def export_model_code(request: ModelExportRequest):
    """
    Generate production-ready Python code for trained models
    
    Supports exporting multiple models at once!
    
    Returns a ZIP file containing:
    - model_code.py (main model file for each model)
    - train_full_dataset.py (script to train on full data)
    - predict.py (prediction script)
    - requirements.txt (dependencies for all models)
    - README.md (comprehensive usage instructions with model selection rationale)
    - trained model .pkl files
    """
    
    if not request.model_names or len(request.model_names) == 0:
        raise HTTPException(status_code=400, detail="At least one model must be selected")
    
    # Load model metadata
    metadata_path = Path(f"/app/backend/models/{request.dataset_id}/model_metadata.json")
    metadata = {}
    if metadata_path.exists():
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
    
    # Get info for all selected models
    all_model_info = []
    model_files = []
    
    for model_name in request.model_names:
        model_path = Path(f"/app/backend/models/{request.dataset_id}/{model_name}.pkl")
        
        if model_path.exists():
            model_info = next((m for m in metadata.get('models', []) if m.get('model_name') == model_name), {})
            if not model_info and request.analysis_results:
                # Try to get from analysis_results
                ml_models = request.analysis_results.get('ml_models', [])
                model_info = next((m for m in ml_models if m.get('model_name') == model_name), {})
            
            all_model_info.append({
                'name': model_name,
                'path': model_path,
                'info': model_info
            })
            model_files.append((model_path, model_name))
    
    if not all_model_info:
        raise HTTPException(status_code=404, detail="No valid models found")
    
    # Generate comprehensive README with model comparison
    readme = generate_comprehensive_readme(request, all_model_info)
    
    # Generate requirements for all models
    requirements = generate_requirements_for_multiple(request.model_names)
    
    # Create ZIP file in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add README (most important file)
        zip_file.writestr('README.md', readme)
        
        # Add requirements.txt
        zip_file.writestr('requirements.txt', requirements)
        
        # Add model code files for each model
        for model_data in all_model_info:
            model_name = model_data['name']
            model_info = model_data['info']
            
            # Generate code specific to this model
            model_code = generate_model_code_v2(request, model_info, model_name)
            zip_file.writestr(f'{model_name}_model.py', model_code)
            
            # Include the trained model file
            if model_data['path'].exists():
                zip_file.write(model_data['path'], arcname=f"models/{model_name}.pkl")
        
        # Add universal training script (works with any model)
        training_script = generate_universal_training_script(request, all_model_info)
        zip_file.writestr('train_full_dataset.py', training_script)
        
        # Add universal prediction script
        prediction_script = generate_universal_prediction_script(request, all_model_info)
        zip_file.writestr('predict.py', prediction_script)
    
    zip_buffer.seek(0)
    
    # Generate filename based on number of models
    if len(request.model_names) == 1:
        filename = f"{request.model_names[0]}_export.zip"
    else:
        filename = f"promise_ai_{len(request.model_names)}_models_export.zip"
    
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


def generate_model_code(request: ModelExportRequest, model_info: Dict) -> str:
    """Generate the main model code"""
    
    model_name = request.model_name
    target = request.target_column
    features = request.feature_columns
    
    # Model-specific imports and initialization
    if 'random_forest' in model_name.lower():
        model_import = "from sklearn.ensemble import RandomForestRegressor"
        model_class = "RandomForestRegressor"
        hyperparams = """
    n_estimators=100,
    max_depth=10,
    min_samples_split=5,
    max_features='sqrt',
    random_state=42,
    n_jobs=-1
"""
    elif 'xgboost' in model_name.lower():
        model_import = "from xgboost import XGBRegressor"
        model_class = "XGBRegressor"
        hyperparams = """
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    random_state=42,
    n_jobs=-1
"""
    elif 'linear' in model_name.lower():
        model_import = "from sklearn.linear_model import LinearRegression"
        model_class = "LinearRegression"
        hyperparams = """
    n_jobs=-1
"""
    elif 'lstm' in model_name.lower():
        model_import = "from tensorflow.keras.models import Sequential\nfrom tensorflow.keras.layers import LSTM, Dense"
        model_class = "Sequential"
        hyperparams = ""
    else:
        model_import = "from sklearn.ensemble import RandomForestRegressor"
        model_class = "RandomForestRegressor"
        hyperparams = """
    n_estimators=100,
    random_state=42
"""
    
    r2_score = model_info.get('r2_score', 0.0)
    
    code = f'''"""
Production Model Code - Generated by PROMISE AI
Model: {model_name}
Performance: R² = {r2_score:.4f}
Target: {target}
Features: {', '.join(features)}
"""

{model_import}
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np
import joblib
from pathlib import Path

# Configuration
TARGET_COLUMN = "{target}"
FEATURE_COLUMNS = {features}
MODEL_NAME = "{model_name}"

class ProductionModel:
    """Production-ready model wrapper"""
    
    def __init__(self, model_path: str = None):
        """
        Initialize model
        
        Args:
            model_path: Path to saved model (optional, will create new if None)
        """
        self.scaler = StandardScaler()
        
        if model_path and Path(model_path).exists():
            # Load pre-trained model
            self.model = joblib.load(model_path)
            print(f"✅ Loaded model from {{model_path}}")
        else:
            # Create new model
            self.model = {model_class}({hyperparams})
            print("✅ Created new model instance")
    
    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess data before training/prediction
        
        Args:
            df: Input DataFrame
        
        Returns:
            Preprocessed DataFrame
        """
        df = df.copy()
        
        # Handle missing values
        for col in FEATURE_COLUMNS:
            if col in df.columns:
                if df[col].dtype in ['float64', 'int64']:
                    df[col].fillna(df[col].median(), inplace=True)
                else:
                    df[col].fillna(df[col].mode()[0], inplace=True)
        
        # Remove outliers (optional - adjust threshold as needed)
        for col in FEATURE_COLUMNS:
            if col in df.columns and df[col].dtype in ['float64', 'int64']:
                q1 = df[col].quantile(0.01)
                q99 = df[col].quantile(0.99)
                df = df[(df[col] >= q1) & (df[col] <= q99)]
        
        return df
    
    def train(self, X: pd.DataFrame, y: pd.Series):
        """
        Train the model
        
        Args:
            X: Feature DataFrame
            y: Target Series
        """
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled, y)
        
        print(f"✅ Model trained on {{len(X):,}} samples")
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Make predictions
        
        Args:
            X: Feature DataFrame
        
        Returns:
            Predictions array
        """
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Predict
        predictions = self.model.predict(X_scaled)
        
        return predictions
    
    def save(self, output_path: str = "production_model.pkl"):
        """
        Save model to disk
        
        Args:
            output_path: Where to save the model
        """
        joblib.dump(self.model, output_path)
        joblib.dump(self.scaler, output_path.replace('.pkl', '_scaler.pkl'))
        
        print(f"✅ Model saved to {{output_path}}")


# Example usage
if __name__ == "__main__":
    # Load your data
    df = pd.read_csv("your_training_data.csv")
    
    # Initialize model
    model = ProductionModel()
    
    # Preprocess
    df = model.preprocess(df)
    
    # Prepare features and target
    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]
    
    # Train
    model.train(X, y)
    
    # Save
    model.save("production_model.pkl")
    
    # Test prediction
    predictions = model.predict(X.head())
    print(f"Sample predictions: {{predictions[:5]}}")
'''
    
    return code


def generate_training_script(request: ModelExportRequest, model_info: Dict) -> str:
    """Generate script for training on full dataset"""
    
    code = f'''"""
Train Model on Full Dataset
Use this script to train the model on your complete TB-scale data
"""

from model_code import ProductionModel, FEATURE_COLUMNS, TARGET_COLUMN
import pandas as pd
from pathlib import Path
import time

def train_on_full_dataset(
    data_path: str,
    output_model_path: str = "trained_model.pkl",
    chunksize: int = 100000
):
    """
    Train model on large dataset using chunked processing
    
    Args:
        data_path: Path to your full dataset
        output_model_path: Where to save trained model
        chunksize: Rows to process at once (for memory efficiency)
    """
    
    print("🚀 Starting training on full dataset...")
    print(f"📊 Data source: {{data_path}}")
    start_time = time.time()
    
    # Initialize model
    model = ProductionModel()
    
    # Option 1: Load entire dataset (if it fits in memory)
    if Path(data_path).stat().st_size < 5 * 1024**3:  # < 5GB
        print("📥 Loading entire dataset into memory...")
        df = pd.read_csv(data_path)
        df = model.preprocess(df)
        
        X = df[FEATURE_COLUMNS]
        y = df[TARGET_COLUMN]
        
        model.train(X, y)
    
    # Option 2: Chunked processing (for large files)
    else:
        print("📥 Processing dataset in chunks...")
        all_X = []
        all_y = []
        
        for i, chunk in enumerate(pd.read_csv(data_path, chunksize=chunksize)):
            chunk = model.preprocess(chunk)
            
            X_chunk = chunk[FEATURE_COLUMNS]
            y_chunk = chunk[TARGET_COLUMN]
            
            all_X.append(X_chunk)
            all_y.append(y_chunk)
            
            if (i + 1) % 10 == 0:
                print(f"  Processed {{(i+1) * chunksize:,}} rows...")
        
        # Concatenate all chunks
        X = pd.concat(all_X, ignore_index=True)
        y = pd.concat(all_y, ignore_index=True)
        
        print(f"✅ Loaded {{len(X):,}} total rows")
        
        # Train model
        model.train(X, y)
    
    # Save trained model
    model.save(output_model_path)
    
    # Calculate training time
    elapsed = time.time() - start_time
    print(f"\\n✅ Training complete!")
    print(f"⏱️  Time: {{elapsed/60:.1f}} minutes")
    print(f"💾 Model saved to: {{output_model_path}}")


if __name__ == "__main__":
    # CONFIGURE THESE PATHS
    DATA_PATH = "/path/to/your/full_dataset.csv"  # Change this
    OUTPUT_PATH = "trained_model.pkl"
    
    # Run training
    train_on_full_dataset(DATA_PATH, OUTPUT_PATH)
'''
    
    return code


def generate_prediction_script(request: ModelExportRequest, model_info: Dict) -> str:
    """Generate prediction script"""
    
    code = f'''"""
Make Predictions with Trained Model
Use this script to make predictions on new data
"""

from model_code import ProductionModel, FEATURE_COLUMNS, TARGET_COLUMN
import pandas as pd
import time

def predict_on_new_data(
    model_path: str,
    data_path: str,
    output_path: str = "predictions.csv"
):
    """
    Make predictions on new data
    
    Args:
        model_path: Path to trained model
        data_path: Path to new data (CSV)
        output_path: Where to save predictions
    """
    
    print("🚀 Starting prediction...")
    start_time = time.time()
    
    # Load model
    model = ProductionModel(model_path=model_path)
    
    # Load new data
    print(f"📥 Loading data from {{data_path}}...")
    df = pd.read_csv(data_path)
    print(f"✅ Loaded {{len(df):,}} rows")
    
    # Preprocess
    df = model.preprocess(df)
    
    # Extract features
    X = df[FEATURE_COLUMNS]
    
    # Make predictions
    print("🔮 Making predictions...")
    predictions = model.predict(X)
    
    # Add predictions to DataFrame
    df['predicted_{{TARGET_COLUMN}}'] = predictions
    
    # Save results
    df.to_csv(output_path, index=False)
    
    elapsed = time.time() - start_time
    print(f"\\n✅ Predictions complete!")
    print(f"⏱️  Time: {{elapsed:.1f}} seconds")
    print(f"📊 Processed {{len(df):,}} rows")
    print(f"💾 Results saved to: {{output_path}}")
    
    # Show summary statistics
    print(f"\\n📈 Prediction Summary:")
    print(f"   Mean: {{predictions.mean():.2f}}")
    print(f"   Median: {{pd.Series(predictions).median():.2f}}")
    print(f"   Min: {{predictions.min():.2f}}")
    print(f"   Max: {{predictions.max():.2f}}")


if __name__ == "__main__":
    # CONFIGURE THESE PATHS
    MODEL_PATH = "trained_model.pkl"  # Your trained model
    DATA_PATH = "/path/to/new_data.csv"  # New data to predict
    OUTPUT_PATH = "predictions.csv"  # Where to save results
    
    # Run predictions
    predict_on_new_data(MODEL_PATH, DATA_PATH, OUTPUT_PATH)
'''
    
    return code


def generate_requirements(model_name: str) -> str:
    """Generate requirements.txt"""
    
    base_requirements = """# Core ML libraries
pandas>=1.5.0
numpy>=1.23.0
scikit-learn>=1.2.0
joblib>=1.2.0

# Model-specific libraries
"""
    
    if 'xgboost' in model_name.lower():
        base_requirements += "xgboost>=1.7.0\n"
    
    if 'lstm' in model_name.lower():
        base_requirements += """tensorflow>=2.12.0
keras>=2.12.0
"""
    
    base_requirements += """
# Optional but recommended
matplotlib>=3.6.0  # For visualization
seaborn>=0.12.0   # For advanced plots
"""
    
    return base_requirements


def generate_readme(request: ModelExportRequest, model_info: Dict) -> str:
    """Generate README.md"""
    
    r2_score = model_info.get('r2_score', 0.0)
    
    readme = f'''# {request.model_name.replace('_', ' ').title()} - Production Model

## 📊 Model Information

- **Model Type**: {request.model_name.replace('_', ' ').title()}
- **Performance**: R² = {r2_score:.4f}
- **Target Variable**: `{request.target_column}`
- **Features**: {', '.join(f"`{f}`" for f in request.feature_columns)}
- **Generated by**: PROMISE AI
- **Date**: {Path('/app/backend').stat().st_mtime}

## 🚀 Quick Start

### 1. Installation

```bash
pip install -r requirements.txt
```

### 2. Train on Your Full Dataset

```bash
# Edit train_full_dataset.py to set your data path
python train_full_dataset.py
```

### 3. Make Predictions

```bash
# Edit predict.py to set your data path
python predict.py
```

## 📁 Files Included

- **model_code.py**: Core model class with preprocessing and training logic
- **train_full_dataset.py**: Script to train on your full TB-scale dataset
- **predict.py**: Script to make predictions on new data
- **{request.model_name}.pkl**: Pre-trained model (trained on sample data)
- **requirements.txt**: Python dependencies
- **README.md**: This file

## 🎯 Usage Examples

### Example 1: Train on Full Dataset

```python
from train_full_dataset import train_on_full_dataset

# Train on your complete data
train_on_full_dataset(
    data_path="/data/full_dataset.csv",
    output_model_path="production_model.pkl"
)
```

### Example 2: Make Predictions

```python
from predict import predict_on_new_data

# Predict on new data
predict_on_new_data(
    model_path="production_model.pkl",
    data_path="/data/new_data.csv",
    output_path="predictions.csv"
)
```

### Example 3: Custom Prediction

```python
from model_code import ProductionModel
import pandas as pd

# Load model
model = ProductionModel(model_path="production_model.pkl")

# Load your data
df = pd.read_csv("new_data.csv")

# Preprocess
df = model.preprocess(df)

# Make predictions
predictions = model.predict(df[{request.feature_columns}])

print(f"Predictions: {{predictions[:10]}}")
```

## 🔧 Customization

### Adjust Preprocessing

Edit `model_code.py` → `preprocess()` method:

```python
def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
    # Add your custom preprocessing here
    df = df.copy()
    
    # Example: Custom outlier removal
    df = df[df['your_column'] < threshold]
    
    # Example: Feature engineering
    df['new_feature'] = df['feature1'] * df['feature2']
    
    return df
```

### Tune Hyperparameters

Edit `model_code.py` → Model initialization:

```python
self.model = {model_info.get('model_class', 'RandomForestRegressor')}(
    n_estimators=200,      # Increase for better accuracy
    max_depth=15,          # Adjust based on your data
    min_samples_split=10,  # Prevent overfitting
    random_state=42
)
```

## 📊 Performance Tips

### For Large Datasets (> 10GB)

1. **Use Chunked Processing**:
   ```python
   train_on_full_dataset(data_path="large_data.csv", chunksize=50000)
   ```

2. **Use Parquet Format** (faster than CSV):
   ```python
   df.to_parquet("data.parquet")
   df = pd.read_parquet("data.parquet")
   ```

3. **Use Dask for Distributed Processing**:
   ```python
   import dask.dataframe as dd
   ddf = dd.read_csv("large_data.csv")
   ```

### For Production Deployment

1. **API Endpoint** (Flask example):
   ```python
   from flask import Flask, request, jsonify
   from model_code import ProductionModel
   
   app = Flask(__name__)
   model = ProductionModel(model_path="production_model.pkl")
   
   @app.route('/predict', methods=['POST'])
   def predict():
       data = request.json
       df = pd.DataFrame([data])
       predictions = model.predict(df)
       return jsonify({{'prediction': float(predictions[0])}})
   
   app.run(host='0.0.0.0', port=5000)
   ```

2. **Batch Prediction** (scheduled job):
   ```python
   import schedule
   
   def daily_predictions():
       predict_on_new_data(
           model_path="production_model.pkl",
           data_path="/data/daily_data.csv",
           output_path=f"/output/predictions_{{date.today()}}.csv"
       )
   
   schedule.every().day.at("02:00").do(daily_predictions)
   ```

## 🐛 Troubleshooting

### Issue: MemoryError

**Solution**: Use chunked processing or reduce data size

```python
train_on_full_dataset(data_path="data.csv", chunksize=50000)
```

### Issue: Poor Performance

**Solution**: Tune hyperparameters or collect more training data

```python
# Try different parameters
model.model.set_params(n_estimators=200, max_depth=20)
```

### Issue: Predictions are off

**Solution**: Ensure new data matches training data distribution

```python
# Check feature statistics
print(df[FEATURE_COLUMNS].describe())
```

## 📚 Additional Resources

- **Scikit-learn Documentation**: https://scikit-learn.org/stable/
- **Pandas User Guide**: https://pandas.pydata.org/docs/user_guide/
- **PROMISE AI Application**: https://model-wizard-2.preview.emergentagent.com

## 🆘 Support

For questions or issues:
1. Check PROMISE AI documentation
2. Review model performance in PROMISE AI interface
3. Validate your data matches the training schema

---

**Generated by PROMISE AI** - Your ML Model Discovery Platform 🚀
'''
    
    return readme
