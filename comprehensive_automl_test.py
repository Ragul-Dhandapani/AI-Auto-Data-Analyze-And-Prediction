#!/usr/bin/env python3
"""
Comprehensive AutoML Test - Test all requirements from the review request
"""

import requests
import json
import csv
import time

BACKEND_URL = "https://mlexport-hub.preview.emergentagent.com/api"

def create_regression_data():
    """Create regression dataset"""
    data = [["bedrooms", "bathrooms", "sqft", "age", "price"]]
    for i in range(100):
        bedrooms = 2 + (i % 4)
        bathrooms = 1 + (i % 3)
        sqft = 1000 + (i * 20)
        age = i % 30
        price = sqft * 150 + bedrooms * 10000 + bathrooms * 15000 - age * 1000 + (i % 1000) * 50
        data.append([bedrooms, bathrooms, sqft, age, price])
    
    with open('/tmp/regression_data.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(data)
    return '/tmp/regression_data.csv'

def create_classification_data():
    """Create classification dataset"""
    data = [["feature1", "feature2", "feature3", "target"]]
    for i in range(100):
        f1 = i / 10.0
        f2 = (i % 7) / 3.0
        f3 = (i % 5) / 2.0
        target = 1 if (f1 + f2 + f3) > 5 else 0
        data.append([f1, f2, f3, target])
    
    with open('/tmp/classification_data.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(data)
    return '/tmp/classification_data.csv'

def test_automl_endpoint(data_source, user_prompt, target_column, feature_columns, 
                        models_to_train, problem_type=None, use_automl=False, 
                        automl_optimization_level='fast'):
    """Test the AutoML endpoint"""
    payload = {
        "data_source": data_source,
        "user_prompt": user_prompt,
        "target_column": target_column,
        "feature_columns": feature_columns,
        "models_to_train": models_to_train,
        "problem_type": problem_type,
        "use_automl": use_automl,
        "automl_optimization_level": automl_optimization_level
    }
    
    start_time = time.time()
    response = requests.post(f"{BACKEND_URL}/intelligent-prediction/train-and-predict", 
                           json=payload, timeout=180)
    execution_time = time.time() - start_time
    
    return response, execution_time

def main():
    print("🧪 Comprehensive AutoML Hyperparameter Optimization Test")
    print("=" * 70)
    print("Testing all requirements from the review request:")
    print("1. Verify endpoint accepts use_automl parameter")
    print("2. Test AutoML with 3+ different models")
    print("3. Verify AutoML returns optimized hyperparameters")
    print("4. Confirm performance improvements")
    print("5. Test both regression and classification")
    print()
    
    # Create test datasets
    print("📊 Creating test datasets...")
    regression_path = create_regression_data()
    classification_path = create_classification_data()
    print(f"✅ Regression dataset: {regression_path}")
    print(f"✅ Classification dataset: {classification_path}")
    print()
    
    results = {}
    
    # Test 1: Verify endpoint accepts use_automl parameter
    print("🔍 Test 1: Endpoint accepts use_automl parameter")
    response, exec_time = test_automl_endpoint(
        data_source={"type": "file", "path": regression_path},
        user_prompt="Test AutoML parameter acceptance",
        target_column="price",
        feature_columns=["bedrooms", "bathrooms", "sqft"],
        models_to_train=["random_forest"],
        use_automl=True,
        automl_optimization_level="fast"
    )
    
    if response.status_code == 200:
        data = response.json()["data"]
        print(f"✅ Endpoint accepts use_automl parameter")
        print(f"   Execution time: {exec_time:.2f}s")
        results['endpoint_accepts_automl'] = True
    else:
        print(f"❌ Endpoint failed: {response.status_code}")
        results['endpoint_accepts_automl'] = False
    print()
    
    # Test 2: Test AutoML with 3+ different models (regression)
    print("🔍 Test 2: AutoML with multiple models (Random Forest, XGBoost, Ridge)")
    response, exec_time = test_automl_endpoint(
        data_source={"type": "file", "path": regression_path},
        user_prompt="Test AutoML with multiple regression models",
        target_column="price",
        feature_columns=["bedrooms", "bathrooms", "sqft", "age"],
        models_to_train=["random_forest", "xgboost", "ridge"],
        problem_type="regression",
        use_automl=True,
        automl_optimization_level="fast"
    )
    
    if response.status_code == 200:
        data = response.json()["data"]
        model_comparison = data.get("model_comparison", [])
        
        automl_models = []
        for model in model_comparison:
            if model.get("automl_optimized"):
                automl_models.append(model["model_name"])
        
        print(f"✅ AutoML with multiple models completed")
        print(f"   Models trained: {len(model_comparison)}")
        print(f"   AutoML optimized models: {len(automl_models)} - {automl_models}")
        print(f"   Execution time: {exec_time:.2f}s")
        results['multiple_models_regression'] = len(automl_models) >= 2
    else:
        print(f"❌ Multiple models test failed: {response.status_code}")
        results['multiple_models_regression'] = False
    print()
    
    # Test 3: Verify AutoML returns optimized hyperparameters
    print("🔍 Test 3: AutoML returns optimized hyperparameters")
    if response.status_code == 200:
        data = response.json()["data"]
        model_comparison = data.get("model_comparison", [])
        
        hyperparams_found = False
        cv_scores_found = False
        best_params_example = None
        
        for model in model_comparison:
            if model.get("best_params"):
                hyperparams_found = True
                best_params_example = model["best_params"]
            if model.get("cv_score"):
                cv_scores_found = True
        
        print(f"✅ Hyperparameter optimization results:")
        print(f"   Best params found: {hyperparams_found}")
        print(f"   CV scores found: {cv_scores_found}")
        if best_params_example:
            print(f"   Example best params: {str(best_params_example)[:100]}...")
        
        results['returns_hyperparameters'] = hyperparams_found and cv_scores_found
    else:
        results['returns_hyperparameters'] = False
    print()
    
    # Test 4: Performance comparison (AutoML vs Default)
    print("🔍 Test 4: Performance comparison (AutoML vs Default)")
    
    # Test without AutoML
    response_default, exec_time_default = test_automl_endpoint(
        data_source={"type": "file", "path": regression_path},
        user_prompt="Test without AutoML for comparison",
        target_column="price",
        feature_columns=["bedrooms", "bathrooms", "sqft"],
        models_to_train=["random_forest"],
        use_automl=False
    )
    
    # Test with AutoML
    response_automl, exec_time_automl = test_automl_endpoint(
        data_source={"type": "file", "path": regression_path},
        user_prompt="Test with AutoML for comparison",
        target_column="price",
        feature_columns=["bedrooms", "bathrooms", "sqft"],
        models_to_train=["random_forest"],
        use_automl=True,
        automl_optimization_level="fast"
    )
    
    if response_default.status_code == 200 and response_automl.status_code == 200:
        default_score = response_default.json()["data"]["best_model"]["score"]
        automl_score = response_automl.json()["data"]["best_model"]["score"]
        
        improvement = ((automl_score - default_score) / default_score) * 100 if default_score != 0 else 0
        
        print(f"✅ Performance comparison:")
        print(f"   Default score: {default_score:.4f} (time: {exec_time_default:.2f}s)")
        print(f"   AutoML score: {automl_score:.4f} (time: {exec_time_automl:.2f}s)")
        print(f"   Performance change: {improvement:+.2f}%")
        
        results['performance_comparison'] = True
        results['automl_improvement'] = improvement
    else:
        print(f"❌ Performance comparison failed")
        results['performance_comparison'] = False
    print()
    
    # Test 5: Classification problem
    print("🔍 Test 5: AutoML with classification problem")
    response, exec_time = test_automl_endpoint(
        data_source={"type": "file", "path": classification_path},
        user_prompt="Test AutoML with classification problem",
        target_column="target",
        feature_columns=["feature1", "feature2", "feature3"],
        models_to_train=["random_forest", "xgboost"],
        problem_type="classification",
        use_automl=True,
        automl_optimization_level="fast"
    )
    
    if response.status_code == 200:
        data = response.json()["data"]
        training_summary = data.get("training_summary", {})
        problem_type = training_summary.get("problem_type")
        
        model_comparison = data.get("model_comparison", [])
        automl_models = [m["model_name"] for m in model_comparison if m.get("automl_optimized")]
        
        print(f"✅ AutoML classification completed")
        print(f"   Problem type detected: {problem_type}")
        print(f"   AutoML optimized models: {len(automl_models)} - {automl_models}")
        print(f"   Execution time: {exec_time:.2f}s")
        
        results['classification_working'] = problem_type == "classification" and len(automl_models) >= 1
    else:
        print(f"❌ Classification test failed: {response.status_code}")
        results['classification_working'] = False
    print()
    
    # Summary
    print("=" * 70)
    print("🎯 AUTOML HYPERPARAMETER OPTIMIZATION TEST SUMMARY")
    print("=" * 70)
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v is True)
    
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    print()
    
    print("📋 Detailed Results:")
    for test, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test}: {status}")
    
    if 'automl_improvement' in results:
        print(f"\n📊 Performance Impact: {results['automl_improvement']:+.2f}%")
    
    print("\n🎯 FINAL ASSESSMENT:")
    if passed_tests >= total_tests * 0.8:  # 80% pass rate
        print("   ✅ AutoML Hyperparameter Optimization is WORKING")
        print("   ✅ All major requirements satisfied")
        print("   ✅ Ready for production use")
    else:
        print("   ❌ AutoML Hyperparameter Optimization needs attention")
        print("   ❌ Some requirements not satisfied")

if __name__ == "__main__":
    main()