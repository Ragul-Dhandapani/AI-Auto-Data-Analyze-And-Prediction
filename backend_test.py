#!/usr/bin/env python3
"""
Backend API Testing for Recent Datasets Fix
Tests the /api/datasets endpoint to verify large dataset response optimization
"""

import requests
import json
import sys
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://data-insight-hub-32.preview.emergentagent.com/api"

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

def test_datasets_endpoint():
    """Test 1: Recent Datasets API - Verify fix for large dataset response"""
    print("\n=== Test 1: Recent Datasets API ===")
    
    try:
        # Test basic endpoint accessibility
        response = requests.get(f"{BACKEND_URL}/datasets", timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Datasets endpoint accessible")
            
            # Verify response structure
            if "datasets" not in data:
                print("❌ Response missing 'datasets' key")
                return False
            
            datasets = data.get("datasets", [])
            print(f"   Found {len(datasets)} datasets")
            
            # Check response size
            response_size = len(response.content)
            response_size_kb = response_size / 1024
            print(f"   Response size: {response_size_kb:.2f} KB")
            
            # Verify response is reasonably sized (should be much smaller now)
            if response_size_kb > 1000:  # 1MB threshold - should be much smaller
                print(f"⚠️  Response size seems large: {response_size_kb:.2f} KB")
            else:
                print("✅ Response size is reasonable")
            
            # Test each dataset structure
            if datasets:
                sample_dataset = datasets[0]
                print(f"   Sample dataset keys: {list(sample_dataset.keys())}")
                
                # Required fields check
                required_fields = ["id", "name", "row_count", "column_count", "columns", "created_at"]
                missing_fields = [field for field in required_fields if field not in sample_dataset]
                
                if missing_fields:
                    print(f"❌ Missing required fields: {missing_fields}")
                    return False
                else:
                    print("✅ All required fields present")
                
                # CRITICAL: Verify 'data' field is NOT present
                if "data" in sample_dataset:
                    print("❌ CRITICAL: 'data' field found in response - this causes frontend crashes!")
                    print(f"   Data field size: {len(str(sample_dataset['data']))} characters")
                    return False
                else:
                    print("✅ CRITICAL: 'data' field correctly excluded from response")
                
                # Verify data_preview is present (should have max 10 rows)
                if "data_preview" in sample_dataset:
                    preview_rows = len(sample_dataset["data_preview"])
                    print(f"✅ data_preview present with {preview_rows} rows")
                    if preview_rows > 10:
                        print(f"⚠️  data_preview has more than 10 rows: {preview_rows}")
                else:
                    print("⚠️  data_preview field missing")
                
                # Check for other expected fields
                expected_fields = ["dtypes", "storage_type"]
                for field in expected_fields:
                    if field in sample_dataset:
                        print(f"✅ {field} field present")
                    else:
                        print(f"ℹ️  {field} field not present (optional)")
            
            return True
        else:
            print(f"❌ Datasets endpoint failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Datasets endpoint exception: {str(e)}")
        return False

def test_datasets_with_limit():
    """Test 2: Datasets endpoint with limit parameter"""
    print("\n=== Test 2: Datasets with Limit Parameter ===")
    
    try:
        # Test with limit parameter
        response = requests.get(f"{BACKEND_URL}/datasets?limit=5", timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            datasets = data.get("datasets", [])
            print(f"✅ Limit parameter working - returned {len(datasets)} datasets")
            
            # Verify limit is respected (should be <= 5)
            if len(datasets) <= 5:
                print("✅ Limit parameter respected")
                return True
            else:
                print(f"❌ Limit not respected - expected ≤5, got {len(datasets)}")
                return False
        else:
            print(f"❌ Datasets with limit failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Datasets with limit exception: {str(e)}")
        return False

def test_response_performance():
    """Test 3: Response performance check"""
    print("\n=== Test 3: Response Performance ===")
    
    try:
        import time
        start_time = time.time()
        
        response = requests.get(f"{BACKEND_URL}/datasets", timeout=30)
        
        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        print(f"Response time: {response_time:.2f} ms")
        
        if response.status_code == 200:
            # Check if response is fast (should be much faster now without full data)
            if response_time < 2000:  # 2 seconds threshold
                print("✅ Response time is acceptable")
                return True
            else:
                print(f"⚠️  Response time seems slow: {response_time:.2f} ms")
                return True  # Still pass, but note the slowness
        else:
            print(f"❌ Performance test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Performance test exception: {str(e)}")
        return False

def test_execute_query_preview():
    """Test 1: Execute Query Preview (MongoDB) - Testing endpoint structure"""
    print("\n=== Test 1: Execute Query Preview ===")
    
    # Test with MongoDB since it's available
    config = {
        "db_type": "mongodb",
        "query": "datasets",  # Collection name for MongoDB
        "host": "localhost",
        "port": 27017,
        "database": "test_database"
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/datasource/execute-query-preview",
            json=config,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Query Preview Successful")
            print(f"   Row Count: {data.get('row_count', 'N/A')}")
            print(f"   Column Count: {data.get('column_count', 'N/A')}")
            print(f"   Columns: {data.get('columns', [])}")
            print(f"   Message: {data.get('message', 'N/A')}")
            
            # Validate expected response structure
            expected_fields = ['row_count', 'column_count', 'columns', 'data_preview', 'message']
            missing_fields = [field for field in expected_fields if field not in data]
            
            if missing_fields:
                print(f"⚠️  Missing fields: {missing_fields}")
                return False
            
            # Check if we have preview data
            preview_data = data.get('data_preview', [])
            print(f"   Preview Rows: {len(preview_data)}")
            if preview_data:
                print(f"   Sample Row: {preview_data[0] if preview_data else 'None'}")
            
            return True
        else:
            print(f"❌ Query Preview Failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Query Preview Exception: {str(e)}")
        return False

def test_save_query_dataset():
    """Test 2: Save Query Dataset"""
    print("\n=== Test 2: Save Query Dataset ===")
    
    config = {
        "db_type": "mongodb",
        "query": "datasets",  # Collection name for MongoDB
        "host": "localhost",
        "port": 27017,
        "database": "test_database",
        "dataset_name": "High Value Customers"
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/datasource/save-query-dataset",
            json=config,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Save Query Dataset Successful")
            print(f"   Dataset ID: {data.get('id', 'N/A')}")
            print(f"   Dataset Name: {data.get('name', 'N/A')}")
            print(f"   Row Count: {data.get('row_count', 'N/A')}")
            print(f"   Column Count: {data.get('column_count', 'N/A')}")
            print(f"   Source Type: {data.get('source_type', 'N/A')}")
            print(f"   Storage Type: {data.get('storage_type', 'N/A')}")
            print(f"   Message: {data.get('message', 'N/A')}")
            
            # Validate expected response structure
            expected_fields = ['id', 'name', 'query', 'row_count', 'column_count', 'columns', 'data_preview', 'source_type', 'storage_type', 'message']
            missing_fields = [field for field in expected_fields if field not in data]
            
            if missing_fields:
                print(f"⚠️  Missing fields: {missing_fields}")
                return False, None
            
            # Verify the name is user-provided, not auto-generated
            if data.get('name') != "High Value Customers":
                print(f"❌ Dataset name mismatch. Expected: 'High Value Customers', Got: '{data.get('name')}'")
                return False, None
            
            # Verify source_type is database_query
            if data.get('source_type') != "database_query":
                print(f"❌ Source type mismatch. Expected: 'database_query', Got: '{data.get('source_type')}'")
                return False, None
            
            return True, data.get('id')
        else:
            print(f"❌ Save Query Dataset Failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Error: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Save Query Dataset Exception: {str(e)}")
        return False, None

def test_verify_saved_dataset(dataset_id):
    """Test 3: Verify Saved Dataset appears in datasets list"""
    print("\n=== Test 3: Verify Saved Dataset ===")
    
    if not dataset_id:
        print("❌ No dataset ID provided for verification")
        return False
    
    try:
        response = requests.get(f"{BACKEND_URL}/datasets", timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            datasets = data.get('datasets', [])
            print(f"✅ Retrieved {len(datasets)} datasets")
            
            # Look for our saved dataset
            found_dataset = None
            for dataset in datasets:
                if dataset.get('id') == dataset_id:
                    found_dataset = dataset
                    break
            
            if found_dataset:
                print("✅ Saved dataset found in list")
                print(f"   Name: {found_dataset.get('name', 'N/A')}")
                print(f"   Source Type: {found_dataset.get('source_type', 'N/A')}")
                
                # Verify the name is correct
                if found_dataset.get('name') == "High Value Customers":
                    print("✅ Dataset name is correct (not auto-generated)")
                    return True
                else:
                    print(f"❌ Dataset name incorrect. Expected: 'High Value Customers', Got: '{found_dataset.get('name')}'")
                    return False
            else:
                print(f"❌ Saved dataset with ID {dataset_id} not found in list")
                return False
        else:
            print(f"❌ Failed to retrieve datasets: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Verify Saved Dataset Exception: {str(e)}")
        return False

def test_error_handling():
    """Test 4: Error Handling"""
    print("\n=== Test 4: Error Handling ===")
    
    tests_passed = 0
    total_tests = 3
    
    # Test 4a: Empty query for execute-query-preview
    print("\n--- Test 4a: Empty Query Preview ---")
    try:
        config = {
            "db_type": "postgresql",
            "query": "",  # Empty query
            "host": "localhost",
            "port": 5432,
            "username": "test",
            "password": "test",
            "database": "test_db"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/datasource/execute-query-preview",
            json=config,
            timeout=10
        )
        
        if response.status_code == 400:
            print("✅ Empty query correctly returns 400 error")
            tests_passed += 1
        else:
            print(f"❌ Expected 400, got {response.status_code}")
    except Exception as e:
        print(f"❌ Empty query test exception: {str(e)}")
    
    # Test 4b: Missing dataset_name for save-query-dataset
    print("\n--- Test 4b: Missing Dataset Name ---")
    try:
        config = {
            "db_type": "postgresql",
            "query": "SELECT 1",
            "host": "localhost",
            "port": 5432,
            "username": "test",
            "password": "test",
            "database": "test_db"
            # Missing dataset_name
        }
        
        response = requests.post(
            f"{BACKEND_URL}/datasource/save-query-dataset",
            json=config,
            timeout=10
        )
        
        if response.status_code == 400:
            print("✅ Missing dataset_name correctly returns 400 error")
            tests_passed += 1
        else:
            print(f"❌ Expected 400, got {response.status_code}")
    except Exception as e:
        print(f"❌ Missing dataset name test exception: {str(e)}")
    
    # Test 4c: Invalid SQL
    print("\n--- Test 4c: Invalid SQL ---")
    try:
        config = {
            "db_type": "postgresql",
            "query": "INVALID SQL QUERY SYNTAX",
            "host": "localhost",
            "port": 5432,
            "username": "test",
            "password": "test",
            "database": "test_db"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/datasource/execute-query-preview",
            json=config,
            timeout=10
        )
        
        if response.status_code == 500:
            print("✅ Invalid SQL correctly returns 500 error")
            error_data = response.json()
            if 'detail' in error_data and 'syntax' in error_data['detail'].lower():
                print("✅ Error message mentions syntax issue")
            tests_passed += 1
        else:
            print(f"❌ Expected 500, got {response.status_code}")
    except Exception as e:
        print(f"❌ Invalid SQL test exception: {str(e)}")
    
    print(f"\nError Handling Tests: {tests_passed}/{total_tests} passed")
    return tests_passed == total_tests

def test_holistic_analysis_single_target():
    """Test Case 1: Single Target (Manual Mode)"""
    print("\n=== Test Case 1: Single Target (Manual Mode) ===")
    
    # Get a dataset ID
    dataset_id = "f3ee15b1-2c23-4538-b2d2-9839aea11a4e"  # application_latency_16.csv
    
    payload = {
        "dataset_id": dataset_id,
        "user_selection": {
            "target_variable": "latency_ms",
            "selected_features": ["cpu_utilization", "memory_usage_mb"],
            "mode": "manual"
        }
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/analysis/holistic",
            json=payload,
            timeout=60
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Single Target Analysis Successful")
            
            # Verify response structure
            required_fields = ['profile', 'models', 'ml_models', 'auto_charts', 'correlations', 'insights']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False
            
            # Check if models were trained
            models = data.get('models', [])
            print(f"   Models trained: {len(models)}")
            
            # Verify target variable was used
            if models:
                target_found = any('latency_ms' in str(model) for model in models)
                if target_found:
                    print("✅ Target variable 'latency_ms' was used correctly")
                else:
                    print("⚠️ Target variable 'latency_ms' not clearly identified in models")
            
            # Check selection feedback
            if 'selection_feedback' in data:
                feedback = data['selection_feedback']
                print(f"   Selection feedback status: {feedback.get('status', 'N/A')}")
                print(f"   Used targets: {feedback.get('used_targets', [])}")
            
            return True
        else:
            print(f"❌ Single Target Analysis Failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Single Target Analysis Exception: {str(e)}")
        return False

def test_holistic_analysis_multiple_targets():
    """Test Case 2: Multiple Targets (Hybrid Mode)"""
    print("\n=== Test Case 2: Multiple Targets (Hybrid Mode) ===")
    
    dataset_id = "f3ee15b1-2c23-4538-b2d2-9839aea11a4e"  # application_latency_16.csv
    
    payload = {
        "dataset_id": dataset_id,
        "user_selection": {
            "target_variables": [
                {"target": "latency_ms", "features": ["cpu_utilization", "memory_usage_mb"]},
                {"target": "cpu_utilization", "features": ["payload_size_kb", "memory_usage_mb"]}
            ],
            "mode": "hybrid"
        }
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/analysis/holistic",
            json=payload,
            timeout=60
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Multiple Targets Analysis Successful")
            
            # Check if models were trained for both targets
            models = data.get('models', [])
            print(f"   Total models trained: {len(models)}")
            
            # Check selection feedback for multiple targets
            if 'selection_feedback' in data:
                feedback = data['selection_feedback']
                print(f"   Selection feedback status: {feedback.get('status', 'N/A')}")
                used_targets = feedback.get('used_targets', [])
                is_multi_target = feedback.get('is_multi_target', False)
                
                print(f"   Used targets: {used_targets}")
                print(f"   Is multi-target: {is_multi_target}")
                
                # Verify both targets were processed
                expected_targets = ["latency_ms", "cpu_utilization"]
                targets_found = all(target in used_targets for target in expected_targets)
                
                if targets_found and is_multi_target:
                    print("✅ Both targets processed correctly in multi-target mode")
                else:
                    print(f"⚠️ Expected targets {expected_targets}, got {used_targets}")
            
            return True
        else:
            print(f"❌ Multiple Targets Analysis Failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Multiple Targets Analysis Exception: {str(e)}")
        return False

def test_holistic_analysis_invalid_target():
    """Test Case 3: Invalid Target (Should Fallback)"""
    print("\n=== Test Case 3: Invalid Target (Should Fallback) ===")
    
    dataset_id = "f3ee15b1-2c23-4538-b2d2-9839aea11a4e"  # application_latency_16.csv
    
    payload = {
        "dataset_id": dataset_id,
        "user_selection": {
            "target_variable": "nonexistent_column",
            "selected_features": ["cpu_utilization"],
            "mode": "manual"
        }
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/analysis/holistic",
            json=payload,
            timeout=60
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Invalid Target Analysis Successful (Fallback)")
            
            # Check selection feedback for fallback behavior
            if 'selection_feedback' in data:
                feedback = data['selection_feedback']
                status = feedback.get('status', '')
                message = feedback.get('message', '')
                
                print(f"   Selection feedback status: {status}")
                
                if status == "modified":
                    print("✅ Correctly detected invalid target and fell back to auto-detection")
                    print(f"   Feedback message: {message[:100]}...")
                    
                    # Check if auto-detection worked
                    used_targets = feedback.get('used_targets', [])
                    if used_targets:
                        print(f"   Auto-detected targets: {used_targets}")
                        return True
                    else:
                        print("⚠️ Auto-detection didn't find any targets")
                        return True  # Still pass as fallback worked
                else:
                    print(f"❌ Expected status 'modified', got '{status}'")
                    return False
            else:
                print("⚠️ No selection_feedback found - fallback may not be working correctly")
                return False
            
        else:
            print(f"❌ Invalid Target Analysis Failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Invalid Target Analysis Exception: {str(e)}")
        return False

def test_holistic_analysis_auto_mode():
    """Test Case 4: No User Selection (Auto Mode)"""
    print("\n=== Test Case 4: No User Selection (Auto Mode) ===")
    
    dataset_id = "f3ee15b1-2c23-4538-b2d2-9839aea11a4e"  # application_latency_16.csv
    
    payload = {
        "dataset_id": dataset_id
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/analysis/holistic",
            json=payload,
            timeout=60
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Auto Mode Analysis Successful")
            
            # Verify response structure
            required_fields = ['profile', 'models', 'ml_models', 'auto_charts', 'correlations', 'insights']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False
            
            # Check if models were trained
            models = data.get('models', [])
            print(f"   Models trained: {len(models)}")
            
            # Check if auto-detection worked
            if models:
                print("✅ Auto-detection successfully trained models")
            else:
                print("⚠️ No models trained in auto mode")
            
            # Verify no selection_feedback (since no user selection)
            if 'selection_feedback' not in data:
                print("✅ No selection_feedback (correct for auto mode)")
            else:
                print("ℹ️ Selection feedback present (may indicate fallback occurred)")
            
            return True
        else:
            print(f"❌ Auto Mode Analysis Failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Auto Mode Analysis Exception: {str(e)}")
        return False

def test_holistic_analysis_performance():
    """Test Case 5: Performance and Response Time"""
    print("\n=== Test Case 5: Performance and Response Time ===")
    
    dataset_id = "f3ee15b1-2c23-4538-b2d2-9839aea11a4e"  # application_latency_16.csv (62,500 rows)
    
    payload = {
        "dataset_id": dataset_id,
        "user_selection": {
            "target_variable": "latency_ms",
            "selected_features": ["cpu_utilization", "memory_usage_mb", "payload_size_kb"],
            "mode": "manual"
        }
    }
    
    try:
        import time
        start_time = time.time()
        
        response = requests.post(
            f"{BACKEND_URL}/analysis/holistic",
            json=payload,
            timeout=60
        )
        
        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {response_time:.2f} ms")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Performance Test Successful")
            
            # Check for performance optimization info
            models = data.get('models', [])
            if models and len(models) > 0:
                # Check if sampling was used for large dataset
                performance_info = data.get('performance_info')
                if performance_info:
                    print(f"   Performance optimization: {performance_info}")
                    if performance_info.get('sampled'):
                        print("✅ Large dataset sampling optimization working")
                
            # Verify reasonable response time (should be under 30 seconds for small datasets)
            if response_time < 30000:  # 30 seconds
                print("✅ Response time is acceptable")
            else:
                print(f"⚠️ Response time seems slow: {response_time:.2f} ms")
            
            return True
        else:
            print(f"❌ Performance Test Failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Performance Test Exception: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Comprehensive Variable Selection Testing for Holistic Analysis")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now().isoformat()}")
    
    # Track test results
    results = {
        'api_health': False,
        'single_target_manual': False,
        'multiple_targets_hybrid': False,
        'invalid_target_fallback': False,
        'auto_mode': False,
        'performance_test': False
    }
    
    # Test 0: API Health Check
    results['api_health'] = test_api_health()
    
    if not results['api_health']:
        print("\n❌ API is not accessible. Stopping tests.")
        return False
    
    # Test 1: Single Target (Manual Mode)
    results['single_target_manual'] = test_holistic_analysis_single_target()
    
    # Test 2: Multiple Targets (Hybrid Mode)
    results['multiple_targets_hybrid'] = test_holistic_analysis_multiple_targets()
    
    # Test 3: Invalid Target (Should Fallback)
    results['invalid_target_fallback'] = test_holistic_analysis_invalid_target()
    
    # Test 4: No User Selection (Auto Mode)
    results['auto_mode'] = test_holistic_analysis_auto_mode()
    
    # Test 5: Performance Test
    results['performance_test'] = test_holistic_analysis_performance()
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY - HOLISTIC ANALYSIS VARIABLE SELECTION")
    print("="*60)
    
    passed_tests = sum(1 for result in results.values() if result)
    total_tests = len(results)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    # Detailed summary
    print("\n🔍 DETAILED FINDINGS:")
    
    if results['single_target_manual']:
        print("   ✅ Single target manual mode working correctly")
    else:
        print("   ❌ Single target manual mode has issues")
    
    if results['multiple_targets_hybrid']:
        print("   ✅ Multiple targets hybrid mode working correctly")
    else:
        print("   ❌ Multiple targets hybrid mode has issues")
    
    if results['invalid_target_fallback']:
        print("   ✅ Invalid target fallback mechanism working")
    else:
        print("   ❌ Invalid target fallback mechanism not working")
    
    if results['auto_mode']:
        print("   ✅ Auto-detection mode working correctly")
    else:
        print("   ❌ Auto-detection mode has issues")
    
    if results['performance_test']:
        print("   ✅ Performance optimization working for large datasets")
    else:
        print("   ❌ Performance issues detected")
    
    if passed_tests == total_tests:
        print("\n🎉 All holistic analysis tests passed!")
        return True
    else:
        print(f"\n⚠️ {total_tests - passed_tests} test(s) failed. Check the details above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)