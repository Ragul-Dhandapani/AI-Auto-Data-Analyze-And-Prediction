#!/usr/bin/env python3
"""
Backend API Testing for Custom Query Dataset Naming Feature
Tests the new endpoints: execute-query-preview and save-query-dataset
"""

import requests
import json
import sys
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://promise-ai.preview.emergentagent.com/api"

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

def main():
    """Run all tests"""
    print("🚀 Starting Backend API Tests for Custom Query Dataset Naming")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now().isoformat()}")
    
    # Track test results
    results = {
        'api_health': False,
        'query_preview': False,
        'save_dataset': False,
        'verify_dataset': False,
        'error_handling': False
    }
    
    # Test 0: API Health Check
    results['api_health'] = test_api_health()
    
    if not results['api_health']:
        print("\n❌ API is not accessible. Stopping tests.")
        return False
    
    # Test 1: Execute Query Preview
    results['query_preview'] = test_execute_query_preview()
    
    # Test 2: Save Query Dataset
    save_success, dataset_id = test_save_query_dataset()
    results['save_dataset'] = save_success
    
    # Test 3: Verify Saved Dataset (only if save was successful)
    if save_success and dataset_id:
        results['verify_dataset'] = test_verify_saved_dataset(dataset_id)
    else:
        print("\n⏭️  Skipping dataset verification (save failed)")
    
    # Test 4: Error Handling
    results['error_handling'] = test_error_handling()
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    
    passed_tests = sum(1 for result in results.values() if result)
    total_tests = len(results)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed!")
        return True
    else:
        print("⚠️  Some tests failed. Check the details above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)