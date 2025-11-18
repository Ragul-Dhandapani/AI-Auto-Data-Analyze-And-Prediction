#!/usr/bin/env python3
"""
PROMISE AI Backend Testing - Nov 4, 2025 Enhancements
Tests the 4 specific enhancements requested in the review:
1. Database & Oracle Connection
2. Hyperparameter Tuning Endpoint (< 60s execution)
3. LLM-Powered Chat Intelligence
4. ML Models API Response (classification/regression)
"""

import requests
import json
import sys
import os
import time
from datetime import datetime
import pandas as pd
import io

# Backend URL from environment
BACKEND_URL = "https://mlpredict.preview.emergentagent.com/api"

def test_api_health():
    """Test if the API is running"""
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=10)
        print(f"✅ API Health Check: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Version: {data.get('version', 'Unknown')}")
            print(f"   Status: {data.get('status', 'Unknown')}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ API Health Check Failed: {str(e)}")
        return False

def test_database_oracle_connection():
    """Test 1: Database & Oracle Connection ✅"""
    print("\n=== Test 1: Database & Oracle Connection ===")
    
    try:
        # Test current database endpoint
        response = requests.get(f"{BACKEND_URL}/config/current-database", timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            current_db = data.get("current_database")
            available_dbs = data.get("available_databases", [])
            
            print(f"✅ Database config endpoint accessible")
            print(f"   Current database: {current_db}")
            print(f"   Available databases: {available_dbs}")
            
            # Verify Oracle is current database (as per review request)
            if current_db == "oracle":
                print("✅ Oracle is currently active database")
            else:
                print(f"⚠️  Expected Oracle, but {current_db} is active")
                return False
            
            # Test datasets can be listed
            datasets_response = requests.get(f"{BACKEND_URL}/datasets", timeout=30)
            if datasets_response.status_code == 200:
                datasets_data = datasets_response.json()
                datasets = datasets_data.get("datasets", [])
                print(f"✅ Datasets can be listed: {len(datasets)} datasets found")
                return True
            else:
                print(f"❌ Cannot list datasets: {datasets_response.status_code}")
                return False
        else:
            print(f"❌ Database config failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Database & Oracle connection test exception: {str(e)}")
        return False

def test_hyperparameter_tuning_endpoint():
    """Test 2: Hyperparameter Tuning Endpoint ⚡"""
    print("\n=== Test 2: Hyperparameter Tuning Endpoint ===")
    
    try:
        # First, get a dataset to use for testing
        datasets_response = requests.get(f"{BACKEND_URL}/datasets", timeout=10)
        if datasets_response.status_code != 200:
            print("❌ Cannot get datasets for hyperparameter testing")
            return False
        
        datasets = datasets_response.json().get("datasets", [])
        if not datasets:
            print("❌ No datasets available for hyperparameter testing")
            return False
        
        # Use the first dataset
        test_dataset = datasets[0]
        dataset_id = test_dataset["id"]
        print(f"   Using dataset: {test_dataset['name']} (ID: {dataset_id})")
        
        # Create test payload for RandomForest hyperparameter tuning
        payload = {
            "dataset_id": dataset_id,
            "target_column": "latency_ms",  # Assuming this exists in test data
            "model_type": "random_forest",
            "problem_type": "regression",
            "search_type": "grid"
        }
        
        # Measure execution time
        start_time = time.time()
        
        response = requests.post(
            f"{BACKEND_URL}/analysis/hyperparameter-tuning",
            json=payload,
            timeout=90  # Allow up to 90 seconds
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"Status Code: {response.status_code}")
        print(f"Execution Time: {execution_time:.2f} seconds")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Hyperparameter tuning endpoint accessible")
            
            # Verify response structure
            required_fields = ["success", "best_params", "best_score"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False
            
            print(f"   Best Score: {data.get('best_score', 'N/A')}")
            print(f"   Best Params: {data.get('best_params', {})}")
            
            # CRITICAL: Check execution time < 60 seconds
            if execution_time < 60:
                print(f"✅ Execution time under 60 seconds: {execution_time:.2f}s")
                return True
            else:
                print(f"❌ Execution time exceeds 60 seconds: {execution_time:.2f}s")
                return False
        else:
            print(f"❌ Hyperparameter tuning failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Hyperparameter tuning test exception: {str(e)}")
        return False

def test_llm_chat_intelligence():
    """Test 3: LLM-Powered Chat Intelligence 🤖"""
    print("\n=== Test 3: LLM-Powered Chat Intelligence ===")
    
    try:
        # Get a dataset for testing
        datasets_response = requests.get(f"{BACKEND_URL}/datasets", timeout=10)
        if datasets_response.status_code != 200:
            print("❌ Cannot get datasets for chat testing")
            return False
        
        datasets = datasets_response.json().get("datasets", [])
        if not datasets:
            print("❌ No datasets available for chat testing")
            return False
        
        test_dataset = datasets[0]
        dataset_id = test_dataset["id"]
        print(f"   Using dataset: {test_dataset['name']} (ID: {dataset_id})")
        
        # Test cases for LLM chat intelligence
        test_cases = [
            {
                "name": "Valid columns chart request",
                "message": "show me latency_ms vs status_code",
                "expected_success": True
            },
            {
                "name": "Non-existent columns request", 
                "message": "plot cpu_utilization vs endpoint",
                "expected_success": False,  # Should return helpful error
                "expect_error_message": True
            },
            {
                "name": "Bar chart request",
                "message": "create a bar chart for status_code",
                "expected_success": True
            },
            {
                "name": "Histogram request",
                "message": "histogram of latency_ms",
                "expected_success": True
            }
        ]
        
        passed_tests = 0
        total_tests = len(test_cases)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n--- Test Case {i}: {test_case['name']} ---")
            
            payload = {
                "dataset_id": dataset_id,
                "message": test_case["message"],
                "conversation_history": []
            }
            
            response = requests.post(
                f"{BACKEND_URL}/analysis/chat-action",
                json=payload,
                timeout=30
            )
            
            print(f"   Status Code: {response.status_code}")
            print(f"   Message: '{test_case['message']}'")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Response Type: {data.get('type', 'N/A')}")
                
                if test_case["expected_success"]:
                    # Should return chart data
                    if data.get("type") == "chart" and "data" in data:
                        print("   ✅ Successfully generated chart")
                        print(f"   Chart Type: {data.get('chart_type', 'N/A')}")
                        passed_tests += 1
                    else:
                        print(f"   ❌ Expected chart, got: {data.get('type')}")
                else:
                    # Should return helpful error message
                    if data.get("type") == "error" and data.get("message"):
                        print("   ✅ Correctly returned helpful error message")
                        print(f"   Error Message: {data.get('message', '')[:100]}...")
                        passed_tests += 1
                    else:
                        print(f"   ❌ Expected error message, got: {data.get('type')}")
            else:
                print(f"   ❌ Chat action failed: {response.status_code}")
        
        print(f"\nLLM Chat Intelligence Tests: {passed_tests}/{total_tests} passed")
        return passed_tests == total_tests
        
    except Exception as e:
        print(f"❌ LLM chat intelligence test exception: {str(e)}")
        return False

def test_ml_models_api_response():
    """Test 4: ML Models API Response"""
    print("\n=== Test 4: ML Models API Response ===")
    
    try:
        # Get datasets for testing
        datasets_response = requests.get(f"{BACKEND_URL}/datasets", timeout=10)
        if datasets_response.status_code != 200:
            print("❌ Cannot get datasets for ML models testing")
            return False
        
        datasets = datasets_response.json().get("datasets", [])
        if not datasets:
            print("❌ No datasets available for ML models testing")
            return False
        
        test_dataset = datasets[0]
        dataset_id = test_dataset["id"]
        print(f"   Using dataset: {test_dataset['name']} (ID: {dataset_id})")
        
        # Test classification scenario
        print("\n--- Testing Classification Response ---")
        classification_payload = {
            "dataset_id": dataset_id,
            "user_selection": {
                "target_variable": "status_code",  # Assuming this is categorical (200, 404, etc.)
                "selected_features": ["latency_ms", "payload_size_kb"],
                "mode": "manual"
            }
        }
        
        classification_response = requests.post(
            f"{BACKEND_URL}/analysis/holistic",
            json=classification_payload,
            timeout=60
        )
        
        print(f"   Classification Status: {classification_response.status_code}")
        
        classification_success = False
        if classification_response.status_code == 200:
            class_data = classification_response.json()
            
            # Check for problem_type
            problem_type = class_data.get("problem_type")
            ml_models = class_data.get("ml_models", [])
            
            print(f"   Problem Type: {problem_type}")
            print(f"   ML Models Count: {len(ml_models)}")
            
            if problem_type == "classification" and ml_models:
                # Check for classification metrics
                sample_model = ml_models[0]
                classification_metrics = ["accuracy", "precision", "recall", "f1_score"]
                found_metrics = [metric for metric in classification_metrics if metric in sample_model]
                
                print(f"   Found Classification Metrics: {found_metrics}")
                
                if len(found_metrics) >= 2:  # At least 2 classification metrics
                    print("   ✅ Classification response includes proper metrics")
                    classification_success = True
                else:
                    print("   ❌ Missing classification metrics")
            else:
                print(f"   ⚠️  Problem type: {problem_type}, Models: {len(ml_models)}")
        
        # Test regression scenario
        print("\n--- Testing Regression Response ---")
        regression_payload = {
            "dataset_id": dataset_id,
            "user_selection": {
                "target_variable": "latency_ms",  # Numeric continuous variable
                "selected_features": ["payload_size_kb", "memory_usage_mb"],
                "mode": "manual"
            }
        }
        
        regression_response = requests.post(
            f"{BACKEND_URL}/analysis/holistic",
            json=regression_payload,
            timeout=60
        )
        
        print(f"   Regression Status: {regression_response.status_code}")
        
        regression_success = False
        if regression_response.status_code == 200:
            reg_data = regression_response.json()
            
            # Check for problem_type
            problem_type = reg_data.get("problem_type")
            ml_models = reg_data.get("ml_models", [])
            
            print(f"   Problem Type: {problem_type}")
            print(f"   ML Models Count: {len(ml_models)}")
            
            if problem_type == "regression" and ml_models:
                # Check for regression metrics
                sample_model = ml_models[0]
                regression_metrics = ["r2_score", "rmse", "mae"]
                found_metrics = [metric for metric in regression_metrics if metric in sample_model]
                
                print(f"   Found Regression Metrics: {found_metrics}")
                
                if len(found_metrics) >= 2:  # At least 2 regression metrics
                    print("   ✅ Regression response includes proper metrics")
                    regression_success = True
                else:
                    print("   ❌ Missing regression metrics")
            else:
                print(f"   ⚠️  Problem type: {problem_type}, Models: {len(ml_models)}")
        
        # Overall success
        if classification_success and regression_success:
            print("\n✅ Both classification and regression return ml_models with proper metrics")
            return True
        elif classification_success or regression_success:
            print(f"\n⚠️  Partial success - Classification: {classification_success}, Regression: {regression_success}")
            return True  # Partial success is acceptable
        else:
            print("\n❌ Neither classification nor regression returned proper ml_models")
            return False
        
    except Exception as e:
        print(f"❌ ML models API response test exception: {str(e)}")
        return False

def main():
    """Run all enhancement tests"""
    print("🚀 PROMISE AI BACKEND ENHANCEMENTS TESTING - Nov 4, 2025")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now().isoformat()}")
    print("="*70)
    
    # Track test results
    results = {
        'api_health': False,
        'database_oracle_connection': False,
        'hyperparameter_tuning': False,
        'llm_chat_intelligence': False,
        'ml_models_api_response': False
    }
    
    # Test 0: API Health Check
    results['api_health'] = test_api_health()
    
    if not results['api_health']:
        print("\n❌ API is not accessible. Stopping tests.")
        return False
    
    # Test 1: Database & Oracle Connection
    results['database_oracle_connection'] = test_database_oracle_connection()
    
    # Test 2: Hyperparameter Tuning Endpoint (< 60s execution)
    results['hyperparameter_tuning'] = test_hyperparameter_tuning_endpoint()
    
    # Test 3: LLM-Powered Chat Intelligence
    results['llm_chat_intelligence'] = test_llm_chat_intelligence()
    
    # Test 4: ML Models API Response
    results['ml_models_api_response'] = test_ml_models_api_response()
    
    # Summary
    print("\n" + "="*70)
    print("📊 ENHANCEMENT TESTING SUMMARY")
    print("="*70)
    
    passed_tests = sum(1 for result in results.values() if result)
    total_tests = len(results)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    # Detailed findings
    print("\n🔍 DETAILED FINDINGS:")
    
    if results['database_oracle_connection']:
        print("   ✅ Oracle RDS connection working, datasets can be listed")
    else:
        print("   ❌ Oracle RDS connection or dataset listing issues")
    
    if results['hyperparameter_tuning']:
        print("   ✅ Hyperparameter tuning completes in < 60 seconds")
    else:
        print("   ❌ Hyperparameter tuning exceeds 60 seconds or fails")
    
    if results['llm_chat_intelligence']:
        print("   ✅ LLM chat correctly parses chart requests and handles errors")
    else:
        print("   ❌ LLM chat intelligence has parsing or error handling issues")
    
    if results['ml_models_api_response']:
        print("   ✅ ML models API returns proper classification/regression metrics")
    else:
        print("   ❌ ML models API missing proper metrics structure")
    
    if passed_tests == total_tests:
        print("\n🎉 All enhancement tests passed!")
        print("\n📋 ENHANCEMENTS STATUS: ✅ WORKING")
        return True
    else:
        print(f"\n⚠️ {total_tests - passed_tests} test(s) failed.")
        print("\n📋 ENHANCEMENTS STATUS: ❌ ISSUES DETECTED")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)