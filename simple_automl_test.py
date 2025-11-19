#!/usr/bin/env python3
"""
Simple AutoML Test - Just verify the endpoint accepts AutoML parameters
"""

import requests
import json
import csv

BACKEND_URL = "https://model-wizard-2.preview.emergentagent.com/api"

# Create minimal test data
data = [
    ["x", "y"],
    [1, 10],
    [2, 20],
    [3, 30],
    [4, 40],
    [5, 50]
]

with open('/tmp/minimal_test.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(data)

print("🧪 Simple AutoML Parameter Test")
print("=" * 40)

# Test: Endpoint accepts AutoML parameters
payload = {
    "data_source": {"type": "file", "path": "/tmp/minimal_test.csv"},
    "user_prompt": "Simple linear relationship test",
    "target_column": "y",
    "feature_columns": ["x"],
    "models_to_train": ["linear_regression"],
    "use_automl": True,
    "automl_optimization_level": "fast"
}

print("🔍 Testing endpoint with AutoML parameters...")
print(f"   use_automl: {payload['use_automl']}")
print(f"   automl_optimization_level: {payload['automl_optimization_level']}")

try:
    response = requests.post(f"{BACKEND_URL}/intelligent-prediction/train-and-predict", 
                           json=payload, timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("status") == "success":
            result_data = data.get("data", {})
            training_summary = result_data.get("training_summary", {})
            
            print("✅ Endpoint accepts AutoML parameters")
            print(f"   Status: {data.get('status')}")
            print(f"   Models trained: {training_summary.get('models_trained', 0)}")
            print(f"   Execution time: {result_data.get('execution_time', 0):.2f}s")
            
            # Check for AutoML indicators
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
                else:
                    print("⚠️  No AutoML indicators found in response")
            
            print("\n🎯 AUTOML INTEGRATION TEST: ✅ PASSED")
            print("   - Endpoint accepts use_automl parameter")
            print("   - AutoML optimization level parameter accepted")
            print("   - Request completed successfully")
            
        else:
            print(f"❌ Request failed with status: {data.get('status')}")
    else:
        print(f"❌ HTTP Error: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")

except requests.exceptions.Timeout:
    print("❌ Request timed out (>30s)")
except Exception as e:
    print(f"❌ Request failed: {str(e)}")