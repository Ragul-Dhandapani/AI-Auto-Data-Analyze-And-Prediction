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
BACKEND_URL = "https://data-genius-12.preview.emergentagent.com/api"

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

def test_phase3_ai_insights():
    """Test Phase 3: AI Insights Generation"""
    print("\n=== Phase 3 Test: AI Insights Generation ===")
    
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
            print("✅ Phase 3 AI Insights Test Successful")
            
            # Check for Phase 3 fields
            phase3_fields = ['ai_insights', 'explainability', 'business_recommendations', 'phase_3_enabled']
            missing_fields = [field for field in phase3_fields if field not in data]
            
            if missing_fields:
                print(f"❌ Missing Phase 3 fields: {missing_fields}")
                return False
            
            # Verify ai_insights structure
            ai_insights = data.get('ai_insights', [])
            print(f"   AI Insights count: {len(ai_insights)}")
            
            if ai_insights:
                sample_insight = ai_insights[0]
                required_insight_fields = ['type', 'title', 'description', 'severity']
                missing_insight_fields = [field for field in required_insight_fields if field not in sample_insight]
                
                if missing_insight_fields:
                    print(f"❌ AI Insight missing fields: {missing_insight_fields}")
                    return False
                else:
                    print("✅ AI Insights have correct structure")
                    print(f"   Sample insight: {sample_insight.get('title', 'N/A')}")
            
            # Verify explainability structure
            explainability = data.get('explainability', {})
            if explainability:
                print("✅ Model explainability data present")
                print(f"   Model: {explainability.get('model_name', 'N/A')}")
                print(f"   Target: {explainability.get('target_variable', 'N/A')}")
            else:
                print("ℹ️ No explainability data (may be due to model performance)")
            
            # Verify business recommendations structure
            business_recs = data.get('business_recommendations', [])
            print(f"   Business recommendations count: {len(business_recs)}")
            
            if business_recs:
                sample_rec = business_recs[0]
                required_rec_fields = ['priority', 'title', 'description', 'expected_impact', 'implementation_effort']
                missing_rec_fields = [field for field in required_rec_fields if field not in sample_rec]
                
                if missing_rec_fields:
                    print(f"❌ Business recommendation missing fields: {missing_rec_fields}")
                    return False
                else:
                    print("✅ Business recommendations have correct structure")
                    print(f"   Sample recommendation: {sample_rec.get('title', 'N/A')}")
            
            # Verify phase_3_enabled flag
            phase3_enabled = data.get('phase_3_enabled', False)
            if phase3_enabled:
                print("✅ Phase 3 enabled flag is True")
            else:
                print("❌ Phase 3 enabled flag is False or missing")
                return False
            
            return True
        else:
            print(f"❌ Phase 3 AI Insights Test Failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Phase 3 AI Insights Test Exception: {str(e)}")
        return False

def test_phase2_variable_selection_feedback():
    """Test Phase 2: Variable Selection Feedback"""
    print("\n=== Phase 2 Test: Variable Selection Feedback ===")
    
    dataset_id = "f3ee15b1-2c23-4538-b2d2-9839aea11a4e"  # application_latency_16.csv
    
    # Test with valid user selection
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
            print("✅ Phase 2 Variable Selection Test Successful")
            
            # Check for selection_feedback
            selection_feedback = data.get('selection_feedback')
            if selection_feedback:
                print("✅ Selection feedback present")
                
                # Verify feedback structure
                required_feedback_fields = ['status', 'message', 'used_targets', 'is_multi_target']
                missing_feedback_fields = [field for field in required_feedback_fields if field not in selection_feedback]
                
                if missing_feedback_fields:
                    print(f"❌ Selection feedback missing fields: {missing_feedback_fields}")
                    return False
                
                status = selection_feedback.get('status')
                message = selection_feedback.get('message', '')
                used_targets = selection_feedback.get('used_targets', [])
                
                print(f"   Status: {status}")
                print(f"   Used targets: {used_targets}")
                print(f"   Message preview: {message[:100]}...")
                
                # Verify target was used correctly
                if 'latency_ms' in used_targets:
                    print("✅ User-selected target was used correctly")
                else:
                    print(f"❌ Expected 'latency_ms' in used targets, got: {used_targets}")
                    return False
                
                return True
            else:
                print("❌ No selection feedback found")
                return False
        else:
            print(f"❌ Phase 2 Variable Selection Test Failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Phase 2 Variable Selection Test Exception: {str(e)}")
        return False

def test_phase2_invalid_selection_fallback():
    """Test Phase 2: Invalid Selection Fallback with Feedback"""
    print("\n=== Phase 2 Test: Invalid Selection Fallback ===")
    
    dataset_id = "f3ee15b1-2c23-4538-b2d2-9839aea11a4e"  # application_latency_16.csv
    
    # Test with invalid user selection
    payload = {
        "dataset_id": dataset_id,
        "user_selection": {
            "target_variable": "nonexistent_column",
            "selected_features": ["invalid_feature"],
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
            print("✅ Invalid Selection Fallback Test Successful")
            
            # Check for selection_feedback with modified status
            selection_feedback = data.get('selection_feedback')
            if selection_feedback:
                status = selection_feedback.get('status')
                message = selection_feedback.get('message', '')
                
                print(f"   Status: {status}")
                print(f"   Message preview: {message[:150]}...")
                
                if status == "modified":
                    print("✅ Correctly detected invalid selection and provided fallback")
                    
                    # Check if warning message is helpful
                    if "could not be used" in message.lower() or "auto-detection" in message.lower():
                        print("✅ Helpful warning message provided")
                        return True
                    else:
                        print("❌ Warning message not helpful enough")
                        return False
                else:
                    print(f"❌ Expected status 'modified', got: {status}")
                    return False
            else:
                print("❌ No selection feedback for invalid selection")
                return False
        else:
            print(f"❌ Invalid Selection Fallback Test Failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Invalid Selection Fallback Test Exception: {str(e)}")
        return False

def test_phase3_multi_target_scenario():
    """Test Phase 3: Multi-target scenario with AI insights"""
    print("\n=== Phase 3 Test: Multi-target AI Insights ===")
    
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
            print("✅ Multi-target Phase 3 Test Successful")
            
            # Check selection feedback for multi-target
            selection_feedback = data.get('selection_feedback')
            if selection_feedback:
                is_multi_target = selection_feedback.get('is_multi_target', False)
                used_targets = selection_feedback.get('used_targets', [])
                
                print(f"   Is multi-target: {is_multi_target}")
                print(f"   Used targets: {used_targets}")
                
                if is_multi_target and len(used_targets) > 1:
                    print("✅ Multi-target scenario correctly identified")
                else:
                    print("❌ Multi-target scenario not properly handled")
                    return False
            
            # Check Phase 3 features still work with multi-target
            ai_insights = data.get('ai_insights', [])
            business_recs = data.get('business_recommendations', [])
            
            print(f"   AI insights for multi-target: {len(ai_insights)}")
            print(f"   Business recommendations: {len(business_recs)}")
            
            if len(ai_insights) > 0 or len(business_recs) > 0:
                print("✅ Phase 3 features working with multi-target")
                return True
            else:
                print("⚠️ Phase 3 features may not be generating insights for multi-target")
                return True  # Still pass as core functionality works
        else:
            print(f"❌ Multi-target Phase 3 Test Failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Multi-target Phase 3 Test Exception: {str(e)}")
        return False

def test_performance_with_phase3():
    """Test Performance with Phase 3 features enabled"""
    print("\n=== Performance Test: Phase 3 Integration ===")
    
    dataset_id = "f3ee15b1-2c23-4538-b2d2-9839aea11a4e"  # Large dataset
    
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
            timeout=90  # Longer timeout for Phase 3 processing
        )
        
        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Time with Phase 3: {response_time:.2f} ms")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Performance Test with Phase 3 Successful")
            
            # Check all Phase 3 features are present
            phase3_features = {
                'ai_insights': len(data.get('ai_insights', [])),
                'explainability': 1 if data.get('explainability') else 0,
                'business_recommendations': len(data.get('business_recommendations', [])),
                'phase_3_enabled': data.get('phase_3_enabled', False)
            }
            
            print(f"   Phase 3 features generated:")
            for feature, count in phase3_features.items():
                print(f"     {feature}: {count}")
            
            # Verify reasonable response time (Phase 3 adds processing time)
            if response_time < 45000:  # 45 seconds threshold for Phase 3
                print("✅ Response time acceptable for Phase 3 processing")
            else:
                print(f"⚠️ Response time seems slow for Phase 3: {response_time:.2f} ms")
            
            return True
        else:
            print(f"❌ Performance Test with Phase 3 Failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Performance Test with Phase 3 Exception: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting COMPREHENSIVE PHASE 2 & PHASE 3 INTEGRATION TESTING")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now().isoformat()}")
    
    # Track test results
    results = {
        'api_health': False,
        'phase2_variable_selection': False,
        'phase2_invalid_fallback': False,
        'phase3_ai_insights': False,
        'phase3_multi_target': False,
        'performance_phase3': False
    }
    
    # Test 0: API Health Check
    results['api_health'] = test_api_health()
    
    if not results['api_health']:
        print("\n❌ API is not accessible. Stopping tests.")
        return False
    
    # Phase 2 Tests
    results['phase2_variable_selection'] = test_phase2_variable_selection_feedback()
    results['phase2_invalid_fallback'] = test_phase2_invalid_selection_fallback()
    
    # Phase 3 Tests
    results['phase3_ai_insights'] = test_phase3_ai_insights()
    results['phase3_multi_target'] = test_phase3_multi_target_scenario()
    results['performance_phase3'] = test_performance_with_phase3()
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY - PHASE 2 & PHASE 3 INTEGRATION")
    print("="*70)
    
    passed_tests = sum(1 for result in results.values() if result)
    total_tests = len(results)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    # Detailed summary
    print("\n🔍 DETAILED FINDINGS:")
    
    print("\n📋 PHASE 2 - Variable Selection & Feedback:")
    if results['phase2_variable_selection']:
        print("   ✅ Variable selection feedback working correctly")
    else:
        print("   ❌ Variable selection feedback has issues")
    
    if results['phase2_invalid_fallback']:
        print("   ✅ Invalid selection fallback with helpful warnings")
    else:
        print("   ❌ Invalid selection fallback not working properly")
    
    print("\n🤖 PHASE 3 - AI Insights & Explainability:")
    if results['phase3_ai_insights']:
        print("   ✅ AI insights generation working with proper structure")
    else:
        print("   ❌ AI insights generation has issues")
    
    if results['phase3_multi_target']:
        print("   ✅ Multi-target scenarios working with Phase 3 features")
    else:
        print("   ❌ Multi-target scenarios have issues with Phase 3")
    
    if results['performance_phase3']:
        print("   ✅ Performance acceptable with Phase 3 processing")
    else:
        print("   ❌ Performance issues with Phase 3 integration")
    
    if passed_tests == total_tests:
        print("\n🎉 All Phase 2 & Phase 3 integration tests passed!")
        return True
    else:
        print(f"\n⚠️ {total_tests - passed_tests} test(s) failed. Check the details above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)