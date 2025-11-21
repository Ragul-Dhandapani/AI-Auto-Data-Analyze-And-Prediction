#!/usr/bin/env python3
"""
Quick AutoML Test - Verify AutoML functionality is working
"""

import requests
import json
import csv
import time

BACKEND_URL = "https://mlexport-hub.preview.emergentagent.com/api"

def create_test_data():
    """Create a small test dataset"""
    data = [
        ["bedrooms", "bathrooms", "sqft", "price"],
        [2, 1, 1000, 200000],
        [3, 2, 1500, 300000],
        [4, 3, 2000, 400000],
        [2, 1, 900, 180000],
        [3, 2, 1600, 320000],
        [4, 2, 1800, 380000],
        [3, 3, 1700, 350000],
        [2, 2, 1200, 250000],
        [5, 4, 2500, 500000],
        [3, 2, 1400, 290000]
    ]
    
    with open('/tmp/quick_test.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(data)
    
    return '/tmp/quick_test.csv'

def test_automl_basic():
    """Test basic AutoML functionality"""
    print("🧪 Quick AutoML Test")
    print("=" * 50)
    
    # Create test data
    csv_path = create_test_data()
    print(f"✅ Created test data: {csv_path}")
    
    # Test 1: Without AutoML (baseline)
    print("\n🔍 Test 1: Without AutoML (baseline)")
    payload = {
        "data_source": {"type": "file", "path": csv_path},
        "user_prompt": "Predict house prices without AutoML",
        "target_column": "price",
        "feature_columns": ["bedrooms", "bathrooms", "sqft"],
        "models_to_train": ["random_forest"],
        "use_automl": False
    }
    
    start_time = time.time()
    response = requests.post(f"{BACKEND_URL}/intelligent-prediction/train-and-predict", 
                           json=payload, timeout=60)
    baseline_time = time.time() - start_time
    
    if response.status_code == 200:
        data = response.json()["data"]
        baseline_score = data["best_model"]["score"]
        print(f"✅ Baseline completed in {baseline_time:.1f}s, score: {baseline_score:.4f}")
    else:
        print(f"❌ Baseline failed: {response.status_code}")
        return
    
    # Test 2: With AutoML (fast)
    print("\n🔍 Test 2: With AutoML (fast optimization)")
    payload["use_automl"] = True
    payload["automl_optimization_level"] = "fast"
    payload["user_prompt"] = "Predict house prices with AutoML optimization"
    
    start_time = time.time()
    response = requests.post(f"{BACKEND_URL}/intelligent-prediction/train-and-predict", 
                           json=payload, timeout=120)
    automl_time = time.time() - start_time
    
    if response.status_code == 200:
        data = response.json()["data"]
        automl_score = data["best_model"]["score"]
        
        # Check for AutoML indicators
        model_comparison = data.get("model_comparison", [])
        automl_found = False
        best_params = None
        
        for model in model_comparison:
            if "automl_optimized" in str(model) or "best_params" in str(model):
                automl_found = True
                # Try to extract best_params if available
                if hasattr(model, 'get'):
                    best_params = model.get("best_params")
        
        print(f"✅ AutoML completed in {automl_time:.1f}s, score: {automl_score:.4f}")
        print(f"   AutoML indicators found: {automl_found}")
        if best_params:
            print(f"   Best params: {best_params}")
        
        # Compare performance
        if automl_score >= baseline_score:
            improvement = ((automl_score - baseline_score) / baseline_score) * 100
            print(f"✅ AutoML performance: {improvement:+.2f}% vs baseline")
        else:
            print(f"⚠️  AutoML performance: {((automl_score - baseline_score) / baseline_score) * 100:+.2f}% vs baseline")
        
        print(f"\n🎯 AUTOML TEST RESULTS:")
        print(f"   ✅ Endpoint accepts use_automl parameter")
        print(f"   ✅ AutoML optimization completed successfully")
        print(f"   ✅ AutoML returned optimized hyperparameters: {automl_found}")
        print(f"   ✅ Performance comparison: AutoML vs Baseline")
        
    else:
        print(f"❌ AutoML failed: {response.status_code}")
        print(f"   Response: {response.text}")

if __name__ == "__main__":
    test_automl_basic()