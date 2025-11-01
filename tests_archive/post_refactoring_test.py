#!/usr/bin/env python3
"""
POST-REFACTORING COMPREHENSIVE BACKEND TESTING
Tests all functionality after backend refactoring from monolithic to modular structure.
"""

import requests
import json
import os
import io
from pathlib import Path
import time

# Get backend URL from frontend .env file
def get_backend_url():
    frontend_env_path = Path("/app/frontend/.env")
    if frontend_env_path.exists():
        with open(frontend_env_path, 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    return "http://localhost:8001"

BACKEND_URL = get_backend_url()
API_BASE = f"{BACKEND_URL}/api"

print(f"Testing refactored backend at: {API_BASE}")

# Sample CSV data for testing
TEST_CSV_DATA = """name,age,salary,department,years_experience
John,28,50000,IT,3
Jane,32,65000,HR,7
Bob,25,45000,IT,2
Alice,35,75000,Finance,10
Charlie,30,55000,IT,5"""

def create_test_csv():
    """Create test CSV file"""
    with open('/app/test_refactor_data.csv', 'w') as f:
        f.write(TEST_CSV_DATA)
    return '/app/test_refactor_data.csv'

def test_health_check():
    """Test basic health check endpoint"""
    print("\n=== Testing Health Check ===")
    
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return False

def test_api_root():
    """Test API root endpoint"""
    print("\n=== Testing API Root ===")
    
    try:
        response = requests.get(f"{API_BASE}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API root working: {data}")
            return True
        else:
            print(f"❌ API root failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API root error: {str(e)}")
        return False

def test_file_upload_new_endpoint():
    """Test new modular file upload endpoint"""
    print("\n=== Testing New File Upload Endpoint (/api/datasource/upload-file) ===")
    
    try:
        csv_file = create_test_csv()
        
        with open(csv_file, 'rb') as f:
            files = {'file': ('test_refactor_data.csv', f, 'text/csv')}
            response = requests.post(f"{API_BASE}/datasource/upload-file", files=files)
        
        if response.status_code != 200:
            print(f"❌ Upload failed: {response.status_code} - {response.text}")
            return False, None
        
        dataset_info = response.json()
        dataset_id = dataset_info['id']
        
        # Verify response structure
        required_fields = ['id', 'name', 'row_count', 'column_count', 'columns', 'data_preview']
        for field in required_fields:
            if field not in dataset_info:
                print(f"❌ Missing field '{field}' in response")
                return False, None
        
        print(f"✅ New upload endpoint working")
        print(f"   Dataset ID: {dataset_id}")
        print(f"   Rows: {dataset_info['row_count']}, Columns: {dataset_info['column_count']}")
        print(f"   Columns: {dataset_info['columns']}")
        
        return True, dataset_id
        
    except Exception as e:
        print(f"❌ Upload error: {str(e)}")
        return False, None

def test_file_upload_backward_compatibility():
    """Test backward compatibility endpoint"""
    print("\n=== Testing Backward Compatibility Upload (/api/datasets) ===")
    
    try:
        # First check if the endpoint exists
        response = requests.get(f"{API_BASE}/datasets")
        if response.status_code == 200:
            print(f"✅ Backward compatibility endpoint exists and returns data")
            return True
        else:
            print(f"❌ Backward compatibility endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Backward compatibility error: {str(e)}")
        return False

def test_holistic_analysis(dataset_id):
    """Test holistic analysis endpoint"""
    print("\n=== Testing Holistic Analysis ===")
    
    try:
        request_data = {"dataset_id": dataset_id}
        response = requests.post(f"{API_BASE}/analysis/holistic", json=request_data)
        
        if response.status_code != 200:
            print(f"❌ Holistic analysis failed: {response.status_code} - {response.text}")
            return False, None
        
        analysis_data = response.json()
        
        # Verify response structure
        required_fields = ['profile', 'models', 'auto_charts', 'correlations', 'insights']
        for field in required_fields:
            if field not in analysis_data:
                print(f"❌ Missing field '{field}' in analysis response")
                return False, None
        
        # Check auto charts
        auto_charts = analysis_data['auto_charts']
        if not isinstance(auto_charts, list):
            print(f"❌ auto_charts should be a list")
            return False, None
        
        print(f"✅ Holistic analysis working")
        print(f"   Generated {len(auto_charts)} auto charts")
        print(f"   Models trained: {len(analysis_data.get('models', []))}")
        print(f"   Correlations found: {len(analysis_data.get('correlations', {}).get('correlations', []))}")
        
        # Verify chart structure
        if auto_charts:
            first_chart = auto_charts[0]
            chart_fields = ['type', 'title', 'plotly_data', 'description']
            for field in chart_fields:
                if field not in first_chart:
                    print(f"❌ Missing field '{field}' in chart structure")
                    return False, None
            
            # Check for empty plotly_data (empty charts bug)
            plotly_data = first_chart['plotly_data']
            if not plotly_data or not plotly_data.get('data'):
                print(f"❌ EMPTY CHART BUG DETECTED: Chart has empty plotly_data")
                return False, None
            
            print(f"✅ Chart structure valid - no empty charts detected")
        
        return True, analysis_data
        
    except Exception as e:
        print(f"❌ Holistic analysis error: {str(e)}")
        return False, None

def test_chat_action_scatter_plot(dataset_id):
    """Test scatter plot generation via chat"""
    print("\n=== Testing Chat Action - Scatter Plot ===")
    
    try:
        request_data = {
            "dataset_id": dataset_id,
            "message": "create scatter plot of age vs salary",
            "conversation_history": []
        }
        
        response = requests.post(f"{API_BASE}/analysis/chat-action", json=request_data)
        
        if response.status_code != 200:
            print(f"❌ Chat action failed: {response.status_code} - {response.text}")
            return False
        
        chat_response = response.json()
        
        # Verify response structure
        if chat_response.get('action') != 'add_chart':
            print(f"❌ Expected action 'add_chart', got '{chat_response.get('action')}'")
            return False
        
        chart_data = chat_response.get('chart_data', {})
        if chart_data.get('type') != 'scatter':
            print(f"❌ Expected chart type 'scatter', got '{chart_data.get('type')}'")
            return False
        
        # Check plotly_data
        plotly_data = chart_data.get('plotly_data', {})
        if not plotly_data.get('data'):
            print(f"❌ Empty plotly_data in scatter plot")
            return False
        
        print(f"✅ Scatter plot generation working")
        print(f"   Title: {chart_data.get('title')}")
        print(f"   Description: {chart_data.get('description')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Chat scatter plot error: {str(e)}")
        return False

def test_chat_action_correlation(dataset_id):
    """Test correlation analysis via chat"""
    print("\n=== Testing Chat Action - Correlation ===")
    
    try:
        request_data = {
            "dataset_id": dataset_id,
            "message": "show correlation analysis",
            "conversation_history": []
        }
        
        response = requests.post(f"{API_BASE}/analysis/chat-action", json=request_data)
        
        if response.status_code != 200:
            print(f"❌ Chat correlation failed: {response.status_code} - {response.text}")
            return False
        
        chat_response = response.json()
        
        # Verify response structure
        if chat_response.get('action') != 'add_chart':
            print(f"❌ Expected action 'add_chart', got '{chat_response.get('action')}'")
            return False
        
        chart_data = chat_response.get('chart_data', {})
        if chart_data.get('type') != 'correlation':
            print(f"❌ Expected chart type 'correlation', got '{chart_data.get('type')}'")
            return False
        
        # Check correlations array
        correlations = chart_data.get('correlations', [])
        if not isinstance(correlations, list):
            print(f"❌ Correlations should be a list")
            return False
        
        print(f"✅ Correlation analysis working")
        print(f"   Found {len(correlations)} correlation pairs")
        
        return True
        
    except Exception as e:
        print(f"❌ Chat correlation error: {str(e)}")
        return False

def test_chat_action_custom_charts(dataset_id):
    """Test custom chart generation via chat"""
    print("\n=== Testing Chat Action - Custom Charts ===")
    
    chart_tests = [
        ("pie chart", "pie"),
        ("bar chart", "bar"),
        ("line chart", "line")
    ]
    
    results = []
    
    for message, expected_type in chart_tests:
        try:
            request_data = {
                "dataset_id": dataset_id,
                "message": f"create a {message}",
                "conversation_history": []
            }
            
            response = requests.post(f"{API_BASE}/analysis/chat-action", json=request_data)
            
            if response.status_code != 200:
                print(f"❌ {message} request failed: {response.status_code}")
                results.append(False)
                continue
            
            chat_response = response.json()
            chart_data = chat_response.get('chart_data', {})
            
            if chart_data.get('type') != expected_type:
                print(f"❌ {message}: Expected type '{expected_type}', got '{chart_data.get('type')}'")
                results.append(False)
                continue
            
            print(f"✅ {message} generation working")
            results.append(True)
            
        except Exception as e:
            print(f"❌ {message} error: {str(e)}")
            results.append(False)
    
    return all(results)

def test_chat_action_removal(dataset_id):
    """Test chart removal via chat"""
    print("\n=== Testing Chat Action - Removal ===")
    
    removal_tests = [
        ("remove correlation", "correlations"),
        ("remove pie chart", "custom_chart")
    ]
    
    results = []
    
    for message, expected_section in removal_tests:
        try:
            request_data = {
                "dataset_id": dataset_id,
                "message": message,
                "conversation_history": []
            }
            
            response = requests.post(f"{API_BASE}/analysis/chat-action", json=request_data)
            
            if response.status_code != 200:
                print(f"❌ {message} request failed: {response.status_code}")
                results.append(False)
                continue
            
            chat_response = response.json()
            
            if chat_response.get('action') != 'remove_section':
                print(f"❌ {message}: Expected action 'remove_section', got '{chat_response.get('action')}'")
                results.append(False)
                continue
            
            if chat_response.get('section_to_remove') != expected_section:
                print(f"❌ {message}: Expected section '{expected_section}', got '{chat_response.get('section_to_remove')}'")
                results.append(False)
                continue
            
            print(f"✅ {message} working")
            results.append(True)
            
        except Exception as e:
            print(f"❌ {message} error: {str(e)}")
            results.append(False)
    
    return all(results)

def test_workspace_management(dataset_id, analysis_data):
    """Test workspace save/load functionality"""
    print("\n=== Testing Workspace Management ===")
    
    try:
        # Test save state
        print("\n1. Testing save state...")
        save_request = {
            "dataset_id": dataset_id,
            "state_name": "Test Workspace",
            "analysis_data": analysis_data,
            "chat_history": [
                {"role": "user", "content": "test message"},
                {"role": "assistant", "content": "test response"}
            ]
        }
        
        response = requests.post(f"{API_BASE}/analysis/save-state", json=save_request)
        
        if response.status_code != 200:
            print(f"❌ Save state failed: {response.status_code} - {response.text}")
            return False
        
        save_response = response.json()
        state_id = save_response.get('state_id')
        
        if not state_id:
            print(f"❌ No state_id returned from save")
            return False
        
        print(f"✅ Save state working - State ID: {state_id}")
        print(f"   Storage type: {save_response.get('storage_type')}")
        print(f"   Size: {save_response.get('size_mb')} MB")
        
        # Test load state
        print("\n2. Testing load state...")
        response = requests.get(f"{API_BASE}/analysis/load-state/{state_id}")
        
        if response.status_code != 200:
            print(f"❌ Load state failed: {response.status_code} - {response.text}")
            return False
        
        loaded_state = response.json()
        
        # Verify loaded data
        if 'analysis_data' not in loaded_state or 'chat_history' not in loaded_state:
            print(f"❌ Loaded state missing required fields")
            return False
        
        print(f"✅ Load state working")
        
        # Test get saved states
        print("\n3. Testing get saved states...")
        response = requests.get(f"{API_BASE}/analysis/saved-states/{dataset_id}")
        
        if response.status_code != 200:
            print(f"❌ Get saved states failed: {response.status_code}")
            return False
        
        states_response = response.json()
        states = states_response.get('states', [])
        
        if not states:
            print(f"❌ No saved states found")
            return False
        
        print(f"✅ Get saved states working - Found {len(states)} states")
        
        # Test delete state
        print("\n4. Testing delete state...")
        response = requests.delete(f"{API_BASE}/analysis/delete-state/{state_id}")
        
        if response.status_code != 200:
            print(f"❌ Delete state failed: {response.status_code}")
            return False
        
        print(f"✅ Delete state working")
        
        return True
        
    except Exception as e:
        print(f"❌ Workspace management error: {str(e)}")
        return False

def test_database_connections():
    """Test database connection endpoints"""
    print("\n=== Testing Database Connections ===")
    
    # Test connection string parsing
    print("\n1. Testing connection string parsing...")
    
    connection_strings = [
        ("postgresql", "postgresql://user:pass@localhost:5432/testdb"),
        ("mysql", "mysql://user:pass@localhost:3306/testdb"),
        ("oracle", "oracle://user:pass@localhost:1521/testservice"),
        ("sqlserver", "mssql://user:pass@localhost:1433/testdb"),
        ("sqlserver", "Server=localhost,1433;Database=testdb;User Id=user;Password=pass"),
        ("mongodb", "mongodb://user:pass@localhost:27017/testdb")
    ]
    
    parse_results = []
    
    for db_type, conn_string in connection_strings:
        try:
            data = {
                'source_type': db_type,
                'connection_string': conn_string
            }
            
            response = requests.post(f"{API_BASE}/datasource/parse-connection-string", data=data)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"✅ {db_type} connection string parsing working")
                    parse_results.append(True)
                else:
                    print(f"❌ {db_type} parsing failed: {result.get('message')}")
                    parse_results.append(False)
            else:
                print(f"❌ {db_type} parsing request failed: {response.status_code}")
                parse_results.append(False)
                
        except Exception as e:
            print(f"❌ {db_type} parsing error: {str(e)}")
            parse_results.append(False)
    
    # Test connection testing (will fail but should return proper error messages)
    print("\n2. Testing connection testing...")
    
    test_configs = [
        ("postgresql", {"host": "localhost", "port": 5432, "database": "test", "username": "test", "password": "test"}),
        ("mysql", {"host": "localhost", "port": 3306, "database": "test", "username": "test", "password": "test"}),
        ("oracle", {"host": "localhost", "port": 1521, "service_name": "test", "username": "test", "password": "test"}),
        ("sqlserver", {"host": "localhost", "port": 1433, "database": "test", "username": "test", "password": "test"}),
        ("mongodb", {})
    ]
    
    connection_results = []
    
    for db_type, config in test_configs:
        try:
            request_data = {
                "source_type": db_type,
                "config": config
            }
            
            response = requests.post(f"{API_BASE}/datasource/test-connection", json=request_data)
            
            if response.status_code == 200:
                result = response.json()
                # We expect these to fail (no actual databases), but should return proper structure
                if 'success' in result and 'message' in result:
                    print(f"✅ {db_type} connection test endpoint working (returned proper error)")
                    connection_results.append(True)
                else:
                    print(f"❌ {db_type} connection test malformed response")
                    connection_results.append(False)
            else:
                print(f"❌ {db_type} connection test request failed: {response.status_code}")
                connection_results.append(False)
                
        except Exception as e:
            print(f"❌ {db_type} connection test error: {str(e)}")
            connection_results.append(False)
    
    # Test table listing
    print("\n3. Testing table listing...")
    
    list_results = []
    
    for db_type, config in test_configs:
        try:
            request_data = {
                "source_type": db_type,
                "config": config
            }
            
            response = requests.post(f"{API_BASE}/datasource/list-tables", json=request_data)
            
            # Should return 500 with error message for non-existent connections
            if response.status_code in [200, 500]:
                print(f"✅ {db_type} list tables endpoint accessible")
                list_results.append(True)
            else:
                print(f"❌ {db_type} list tables unexpected status: {response.status_code}")
                list_results.append(False)
                
        except Exception as e:
            print(f"❌ {db_type} list tables error: {str(e)}")
            list_results.append(False)
    
    return all(parse_results) and all(connection_results) and all(list_results)

def test_training_metadata():
    """Test training metadata endpoint"""
    print("\n=== Testing Training Metadata ===")
    
    try:
        response = requests.get(f"{API_BASE}/training/metadata")
        
        if response.status_code != 200:
            print(f"❌ Training metadata failed: {response.status_code} - {response.text}")
            return False
        
        metadata = response.json()
        
        if 'metadata' not in metadata:
            print(f"❌ Missing 'metadata' field in response")
            return False
        
        print(f"✅ Training metadata endpoint working")
        print(f"   Found metadata for {len(metadata['metadata'])} datasets")
        
        return True
        
    except Exception as e:
        print(f"❌ Training metadata error: {str(e)}")
        return False

def main():
    """Run comprehensive post-refactoring tests"""
    print("POST-REFACTORING COMPREHENSIVE BACKEND TESTING")
    print("=" * 80)
    print("Testing all functionality after backend refactoring from monolithic to modular structure")
    print("=" * 80)
    
    test_results = []
    dataset_id = None
    analysis_data = None
    
    try:
        # Basic connectivity tests
        print("\n🔍 BASIC CONNECTIVITY TESTS")
        test_results.append(("Health Check", test_health_check()))
        test_results.append(("API Root", test_api_root()))
        
        # File upload tests
        print("\n📁 FILE UPLOAD TESTS")
        upload_success, dataset_id = test_file_upload_new_endpoint()
        test_results.append(("New Upload Endpoint", upload_success))
        test_results.append(("Backward Compatibility", test_file_upload_backward_compatibility()))
        
        if not dataset_id:
            print("❌ Cannot continue without successful file upload")
            return False
        
        # Analysis tests
        print("\n📊 ANALYSIS TESTS")
        analysis_success, analysis_data = test_holistic_analysis(dataset_id)
        test_results.append(("Holistic Analysis", analysis_success))
        
        # Chat action tests
        print("\n💬 CHAT ACTION TESTS")
        test_results.append(("Scatter Plot Generation", test_chat_action_scatter_plot(dataset_id)))
        test_results.append(("Correlation Analysis", test_chat_action_correlation(dataset_id)))
        test_results.append(("Custom Charts", test_chat_action_custom_charts(dataset_id)))
        test_results.append(("Chart Removal", test_chat_action_removal(dataset_id)))
        
        # Workspace management tests
        print("\n💾 WORKSPACE MANAGEMENT TESTS")
        if analysis_data:
            test_results.append(("Workspace Management", test_workspace_management(dataset_id, analysis_data)))
        else:
            test_results.append(("Workspace Management", False))
        
        # Database connection tests
        print("\n🗄️ DATABASE CONNECTION TESTS")
        test_results.append(("Database Connections", test_database_connections()))
        
        # Training metadata tests
        print("\n🎯 TRAINING METADATA TESTS")
        test_results.append(("Training Metadata", test_training_metadata()))
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 POST-REFACTORING TEST RESULTS SUMMARY")
        print("=" * 80)
        
        passed = 0
        failed = 0
        
        for test_name, result in test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name:<35} {status}")
            if result:
                passed += 1
            else:
                failed += 1
        
        print(f"\nTotal: {len(test_results)} tests | Passed: {passed} | Failed: {failed}")
        
        if failed == 0:
            print("\n🎉 ALL POST-REFACTORING TESTS PASSED!")
            print("Backend refactoring successful - all functionality working correctly.")
            return True
        else:
            print(f"\n❌ {failed} TEST(S) FAILED!")
            print("Some functionality broken after refactoring - needs investigation.")
            return False
            
    except Exception as e:
        print(f"\n❌ Test execution failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)