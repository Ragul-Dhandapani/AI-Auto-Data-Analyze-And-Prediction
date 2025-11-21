#!/usr/bin/env python3
"""
AutoML Random Forest Test - Test with a model that has hyperparameters
"""

import requests
import json
import csv

BACKEND_URL = "https://mlexport-hub.preview.emergentagent.com/api"

# Create test data with more samples for Random Forest
data = [["x1", "x2", "y"]]
for i in range(50):  # More data for better training
    x1 = i / 10.0
    x2 = (i % 7) / 3.0
    y = x1 * 2 + x2 * 3 + (i % 3) * 0.1  # Some pattern
    data.append([x1, x2, y])

with open('/tmp/rf_test.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(data)

print("🧪 AutoML Random Forest Test")
print("=" * 40)

# Test: Random Forest with AutoML
payload = {
    "data_source": {"type": "file", "path": "/tmp/rf_test.csv"},
    "user_prompt": "Test Random Forest with AutoML optimization",
    "target_column": "y",
    "feature_columns": ["x1", "x2"],
    "models_to_train": ["random_forest"],
    "use_automl": True,
    "automl_optimization_level": "fast"
}

print("🔍 Testing Random Forest with AutoML...")
print(f"   Dataset: 50 rows, 2 features")
print(f"   use_automl: {payload['use_automl']}")
print(f"   automl_optimization_level: {payload['automl_optimization_level']}")

try:
    response = requests.post(f"{BACKEND_URL}/intelligent-prediction/train-and-predict", 
                           json=payload, timeout=60)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("status") == "success":
            result_data = data.get("data", {})
            training_summary = result_data.get("training_summary", {})
            
            print("✅ AutoML Random Forest completed")
            print(f"   Status: {data.get('status')}")
            print(f"   Models trained: {training_summary.get('models_trained', 0)}")
            print(f"   Execution time: {result_data.get('execution_time', 0):.2f}s")
            
            # Check model results
            model_comparison = result_data.get("model_comparison", [])
            if model_comparison:
                model = model_comparison[0]
                print(f"   Model score: {model.get('score', 0):.4f}")
                
                # Look for AutoML indicators in the response
                response_str = str(data)
                automl_indicators = []
                if "automl_optimized" in response_str:
                    automl_indicators.append("automl_optimized")
                if "best_params" in response_str:
                    automl_indicators.append("best_params")
                if "cv_score" in response_str:
                    automl_indicators.append("cv_score")
                
                if automl_indicators:
                    print(f"✅ AutoML indicators found: {', '.join(automl_indicators)}")
                    
                    # Try to extract best_params if available
                    if "best_params" in response_str:
                        # Look for best_params in the response
                        import re
                        params_match = re.search(r"'best_params':\s*({[^}]+})", response_str)
                        if params_match:
                            print(f"   Best params found: {params_match.group(1)[:100]}...")
                else:
                    print("⚠️  No AutoML indicators found in response")
            
            print("\n🎯 AUTOML RANDOM FOREST TEST RESULTS:")
            print("   ✅ Endpoint accepts AutoML parameters")
            print("   ✅ Random Forest training completed")
            if automl_indicators:
                print("   ✅ AutoML optimization detected")
                print("   ✅ Hyperparameters optimized")
            else:
                print("   ⚠️  AutoML optimization not clearly indicated")
            
        else:
            print(f"❌ Request failed with status: {data.get('status')}")
    else:
        print(f"❌ HTTP Error: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")

except requests.exceptions.Timeout:
    print("❌ Request timed out (>60s)")
except Exception as e:
    print(f"❌ Request failed: {str(e)}")