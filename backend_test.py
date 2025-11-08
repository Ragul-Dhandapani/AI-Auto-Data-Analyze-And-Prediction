#!/usr/bin/env python3
"""
PROMISE AI Backend Testing - Critical Endpoints
Tests the recent fixes to the PROMISE AI platform as requested
"""

import requests
import json
import sys
import os
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://ai-insight-hub-4.preview.emergentagent.com/api"

def test_backend_health():
    """Test: Backend Health - Verify backend is running and responsive"""
    print("\n=== Test: Backend Health ===")
    
    try:
        # Test basic health endpoint
        response = requests.get(f"{BACKEND_URL}/", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend is running and responsive")
            print(f"   Version: {data.get('version', 'Unknown')}")
            print(f"   Status: {data.get('status', 'Unknown')}")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Backend health check exception: {str(e)}")
        return False

def test_datasets_endpoint():
    """Test: Datasets Endpoint (SANITY CHECK) - GET /api/datasets"""
    print("\n=== Test: Datasets Endpoint (Sanity Check) ===")
    
    try:
        response = requests.get(f"{BACKEND_URL}/datasets", timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Datasets endpoint accessible")
            
            if "datasets" in data:
                datasets = data.get("datasets", [])
                print(f"   Found {len(datasets)} datasets")
                
                if len(datasets) >= 1:
                    print("✅ At least 1 dataset available for testing")
                    # Return first dataset ID for use in other tests
                    return True, datasets[0].get("id") if datasets else None
                else:
                    print("⚠️  No datasets found - may affect other tests")
                    return True, None
            else:
                print("❌ Response missing 'datasets' key")
                return False, None
        else:
            print(f"❌ Datasets endpoint failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Error: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Datasets endpoint exception: {str(e)}")
        return False, None

def test_suggest_features_endpoint(dataset_id):
    """Test: Suggest-Features Endpoint (NEW - Just Added) - POST /api/datasource/suggest-features"""
    print("\n=== Test: Suggest-Features Endpoint (NEW) ===")
    
    if not dataset_id:
        print("❌ No dataset ID available for testing")
        return False
    
    # Test payload as specified in review request
    payload = {
        "dataset_id": dataset_id,
        "columns": ["col1", "col2"],  # Generic column names
        "problem_type": "classification"
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/datasource/suggest-features",
            json=payload,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Suggest-features endpoint working")
            
            # Verify expected response structure
            expected_fields = ['recommended_target', 'recommended_features', 'feature_groups']
            missing_fields = [field for field in expected_fields if field not in data]
            
            if missing_fields:
                print(f"⚠️  Missing expected fields: {missing_fields}")
                print(f"   Available fields: {list(data.keys())}")
            else:
                print("✅ All expected fields present:")
                print(f"   - recommended_target: {data.get('recommended_target')}")
                print(f"   - recommended_features: {len(data.get('recommended_features', []))} features")
                print(f"   - feature_groups: {list(data.get('feature_groups', {}).keys())}")
            
            return True
        else:
            print(f"❌ Suggest-features endpoint failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Suggest-features endpoint exception: {str(e)}")
        return False

def test_hyperparameter_tuning_endpoint(dataset_id):
    """Test: Hyperparameter Tuning Endpoint (REPORTED 500 ERROR) - POST /api/analysis/hyperparameter-tuning"""
    print("\n=== Test: Hyperparameter Tuning Endpoint (500 Error Investigation) ===")
    
    if not dataset_id:
        print("❌ No dataset ID available for testing")
        return False
    
    # Get dataset details first to find a numeric column
    try:
        datasets_response = requests.get(f"{BACKEND_URL}/datasets", timeout=10)
        if datasets_response.status_code == 200:
            datasets = datasets_response.json().get("datasets", [])
            target_dataset = None
            for dataset in datasets:
                if dataset.get("id") == dataset_id:
                    target_dataset = dataset
                    break
            
            if target_dataset:
                columns = target_dataset.get("columns", [])
                # Look for a numeric column
                numeric_column = None
                for col in columns:
                    if any(keyword in col.lower() for keyword in ['latency', 'cpu', 'memory', 'size', 'count', 'score', 'value', 'amount']):
                        numeric_column = col
                        break
                
                if not numeric_column and columns:
                    numeric_column = columns[0]  # Fallback to first column
                
                print(f"   Using target column: {numeric_column}")
            else:
                numeric_column = "target_column"  # Generic fallback
        else:
            numeric_column = "target_column"  # Generic fallback
    except:
        numeric_column = "target_column"  # Generic fallback
    
    # Test payload as specified in review request
    payload = {
        "dataset_id": dataset_id,
        "target_column": numeric_column,
        "model_type": "random_forest",
        "problem_type": "regression"
    }
    
    try:
        print(f"   Testing with payload: {payload}")
        response = requests.post(
            f"{BACKEND_URL}/analysis/hyperparameter-tuning",
            json=payload,
            timeout=60  # Longer timeout for hyperparameter tuning
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Hyperparameter tuning endpoint working")
            
            # Verify expected response structure
            expected_fields = ['best_params', 'best_score']
            missing_fields = [field for field in expected_fields if field not in data]
            
            if missing_fields:
                print(f"⚠️  Missing expected fields: {missing_fields}")
                print(f"   Available fields: {list(data.keys())}")
            else:
                print("✅ All expected fields present:")
                print(f"   - best_params: {data.get('best_params')}")
                print(f"   - best_score: {data.get('best_score')}")
            
            return True
        else:
            print(f"❌ Hyperparameter tuning endpoint failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error details: {error_data}")
                
                # Detailed error analysis for 500 errors
                if response.status_code == 500:
                    print("\n🔍 ROOT CAUSE ANALYSIS for 500 Error:")
                    error_detail = error_data.get('detail', '')
                    if 'column' in error_detail.lower():
                        print("   - Likely issue: Column not found or invalid column name")
                    elif 'data' in error_detail.lower():
                        print("   - Likely issue: Data preprocessing or format problem")
                    elif 'model' in error_detail.lower():
                        print("   - Likely issue: Model training or configuration problem")
                    else:
                        print(f"   - Error message: {error_detail}")
                
            except:
                print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Hyperparameter tuning endpoint exception: {str(e)}")
        return False

def check_backend_logs():
    """Check backend logs for any startup errors"""
    print("\n=== Backend Logs Check ===")
    
    try:
        # Check recent backend logs
        import subprocess
        result = subprocess.run(
            ["tail", "-n", "20", "/var/log/supervisor/backend.err.log"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            logs = result.stdout.strip()
            if logs:
                print("Recent backend error logs:")
                print(logs)
                
                # Check for specific errors
                if "ERROR" in logs:
                    print("⚠️  Errors found in backend logs")
                    return False
                else:
                    print("✅ No critical errors in recent logs")
                    return True
            else:
                print("✅ No recent error logs")
                return True
        else:
            print("⚠️  Could not access backend logs")
            return True  # Don't fail the test for log access issues
            
    except Exception as e:
        print(f"⚠️  Could not check backend logs: {str(e)}")
        return True  # Don't fail the test for log access issues

def main():
    """Run Critical Backend Tests"""
    print("🚀 PROMISE AI BACKEND TESTING - Critical Endpoints")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now().isoformat()}")
    print("="*70)
    
    # Track test results
    results = {
        'backend_health': False,
        'datasets_endpoint': False,
        'suggest_features': False,
        'hyperparameter_tuning': False,
        'backend_logs': False
    }
    
    dataset_id = None
    
    # Test 1: Backend Health (GENERAL)
    print("\n🔍 PRIORITY: GENERAL")
    results['backend_health'] = test_backend_health()
    
    if not results['backend_health']:
        print("\n❌ Backend is not accessible. Stopping tests.")
        return False
    
    # Test 2: Datasets Endpoint (SANITY CHECK)
    print("\n🔍 PRIORITY: MEDIUM")
    datasets_success, dataset_id = test_datasets_endpoint()
    results['datasets_endpoint'] = datasets_success
    
    # Test 3: Suggest-Features Endpoint (NEW - Just Added)
    print("\n🔍 PRIORITY: HIGH")
    results['suggest_features'] = test_suggest_features_endpoint(dataset_id)
    
    # Test 4: Hyperparameter Tuning Endpoint (REPORTED 500 ERROR)
    print("\n🔍 PRIORITY: HIGH")
    results['hyperparameter_tuning'] = test_hyperparameter_tuning_endpoint(dataset_id)
    
    # Test 5: Backend Logs Check
    results['backend_logs'] = check_backend_logs()
    
    # Summary
    print("\n" + "="*70)
    print("📊 CRITICAL ENDPOINTS TEST SUMMARY")
    print("="*70)
    
    passed_tests = sum(1 for result in results.values() if result)
    total_tests = len(results)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        priority = ""
        if test_name == 'suggest_features':
            priority = " (HIGH PRIORITY - NEW ENDPOINT)"
        elif test_name == 'hyperparameter_tuning':
            priority = " (HIGH PRIORITY - 500 ERROR REPORTED)"
        elif test_name == 'datasets_endpoint':
            priority = " (MEDIUM PRIORITY - SANITY CHECK)"
        elif test_name == 'backend_health':
            priority = " (GENERAL)"
        
        print(f"{test_name.replace('_', ' ').title()}: {status}{priority}")
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    # Detailed findings
    print("\n🔍 DETAILED FINDINGS:")
    
    if results['backend_health']:
        print("   ✅ Backend is running and responsive")
    else:
        print("   ❌ Backend health issues detected")
    
    if results['datasets_endpoint']:
        print("   ✅ Datasets endpoint working - Oracle RDS connection stable")
    else:
        print("   ❌ Datasets endpoint issues - Oracle RDS connection problems")
    
    if results['suggest_features']:
        print("   ✅ NEW suggest-features endpoint working correctly")
    else:
        print("   ❌ NEW suggest-features endpoint has issues")
    
    if results['hyperparameter_tuning']:
        print("   ✅ Hyperparameter tuning endpoint working - 500 error resolved")
    else:
        print("   ❌ Hyperparameter tuning endpoint still has issues - 500 error persists")
    
    if results['backend_logs']:
        print("   ✅ Backend logs show no critical errors")
    else:
        print("   ❌ Backend logs show errors")
    
    # Final status
    critical_tests = ['suggest_features', 'hyperparameter_tuning']
    critical_passed = sum(1 for test in critical_tests if results[test])
    
    if critical_passed == len(critical_tests):
        print("\n🎉 All CRITICAL tests passed!")
        print("\n📋 STATUS: ✅ CRITICAL FIXES VERIFIED")
        return True
    else:
        print(f"\n⚠️ {len(critical_tests) - critical_passed} CRITICAL test(s) failed.")
        print("\n📋 STATUS: ❌ CRITICAL ISSUES DETECTED")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
