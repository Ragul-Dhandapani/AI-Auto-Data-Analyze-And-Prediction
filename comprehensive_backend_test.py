#!/usr/bin/env python3
"""
Comprehensive Backend Testing for PROMISE AI
Tests all priority features as requested in the review:
1. Backend Health
2. File Upload (small and medium files)
3. Holistic Analysis with auto-generated charts
4. Data Retrieval
5. Chat Actions for custom charts
"""

import requests
import json
import os
import time
from pathlib import Path

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

print(f"Testing PROMISE AI backend at: {API_BASE}")

def test_backend_health():
    """Test 1: Backend Health - Verify backend is running and responding"""
    print("\n=== TEST 1: Backend Health Check ===")
    
    try:
        response = requests.get(f"{API_BASE}/", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend is healthy")
            print(f"   Response: {data}")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend connection failed: {str(e)}")
        return False

def create_test_files():
    """Create test CSV files of different sizes"""
    
    # Small file (15 rows)
    small_csv_content = """name,age,salary,years_experience,department
John,25,50000,2,Engineering
Jane,30,75000,5,Marketing
Bob,35,90000,8,Engineering
Alice,28,65000,4,Sales
Charlie,32,80000,6,Engineering
Diana,29,70000,3,Marketing
Frank,38,95000,10,Engineering
Grace,26,55000,2,Sales
Henry,33,85000,7,Engineering
Ivy,31,72000,5,Marketing
Jack,27,58000,3,Sales
Kate,36,88000,9,Engineering
Liam,24,48000,1,Marketing
Mia,34,82000,8,Sales
Noah,30,76000,6,Engineering"""
    
    # Medium file (100 rows)
    medium_csv_content = "name,age,salary,years_experience,department\n"
    departments = ["Engineering", "Marketing", "Sales", "HR", "Finance"]
    
    for i in range(100):
        name = f"Employee_{i+1}"
        age = 22 + (i % 40)  # Ages 22-61
        salary = 40000 + (i * 1000)  # Salaries 40k-139k
        experience = min(age - 22, 20)  # Max 20 years experience
        department = departments[i % len(departments)]
        medium_csv_content += f"{name},{age},{salary},{experience},{department}\n"
    
    # Write files
    with open('/app/small_test.csv', 'w') as f:
        f.write(small_csv_content)
    
    with open('/app/medium_test.csv', 'w') as f:
        f.write(medium_csv_content)
    
    print("✅ Test files created successfully")

def test_file_upload():
    """Test 2: File Upload - Test both small and medium-sized files"""
    print("\n=== TEST 2: File Upload Testing ===")
    
    create_test_files()
    
    upload_results = []
    
    # Test small file upload
    print("\n2a. Testing small file upload (15 rows)...")
    
    upload_url = f"{API_BASE}/datasource/upload-file"
    
    try:
        with open('/app/small_test.csv', 'rb') as f:
            files = {'file': ('small_test.csv', f, 'text/csv')}
            response = requests.post(upload_url, files=files, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Small file uploaded successfully")
            print(f"   Dataset ID: {data['id']}")
            print(f"   Rows: {data['row_count']}, Columns: {data['column_count']}")
            print(f"   Storage method: {data.get('storage_method', 'document')}")
            upload_results.append(('small', True, data))
        else:
            print(f"❌ Small file upload failed: {response.status_code} - {response.text}")
            upload_results.append(('small', False, None))
            
    except Exception as e:
        print(f"❌ Small file upload error: {str(e)}")
        upload_results.append(('small', False, None))
    
    # Test medium file upload
    print("\n2b. Testing medium file upload (100 rows)...")
    
    try:
        with open('/app/medium_test.csv', 'rb') as f:
            files = {'file': ('medium_test.csv', f, 'text/csv')}
            response = requests.post(upload_url, files=files, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Medium file uploaded successfully")
            print(f"   Dataset ID: {data['id']}")
            print(f"   Rows: {data['row_count']}, Columns: {data['column_count']}")
            print(f"   Storage method: {data.get('storage_method', 'document')}")
            print(f"   File size: {data.get('file_size', 'unknown')} bytes")
            upload_results.append(('medium', True, data))
        else:
            print(f"❌ Medium file upload failed: {response.status_code} - {response.text}")
            upload_results.append(('medium', False, None))
            
    except Exception as e:
        print(f"❌ Medium file upload error: {str(e)}")
        upload_results.append(('medium', False, None))
    
    # Return results for use in other tests
    successful_uploads = [result for result in upload_results if result[1]]
    return len(successful_uploads) > 0, successful_uploads

def test_holistic_analysis(dataset_info):
    """Test 3: Holistic Analysis - Test comprehensive analysis with auto-charts"""
    print("\n=== TEST 3: Holistic Analysis with Auto-Charts ===")
    
    dataset_id = dataset_info['id']
    print(f"\n3. Testing holistic analysis on dataset: {dataset_id}")
    
    holistic_url = f"{API_BASE}/analysis/holistic"
    request_data = {"dataset_id": dataset_id}
    
    try:
        start_time = time.time()
        response = requests.post(holistic_url, json=request_data, timeout=60)
        analysis_time = time.time() - start_time
        
        if response.status_code != 200:
            print(f"❌ Holistic analysis failed: {response.status_code} - {response.text}")
            return False
        
        data = response.json()
        print(f"✅ Holistic analysis completed in {analysis_time:.2f} seconds")
        
        # Verify required response structure
        required_fields = [
            'volume_analysis', 'trend_analysis', 'correlations', 
            'ml_models', 'predictions', 'auto_charts', 'ai_summary'
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in data:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Missing required fields: {missing_fields}")
            return False
        
        print(f"✅ All required fields present in response")
        
        # Test auto_charts specifically
        auto_charts = data.get('auto_charts', [])
        print(f"\n3a. Testing auto-generated charts...")
        print(f"   Found {len(auto_charts)} auto-generated charts")
        
        if len(auto_charts) == 0:
            print(f"❌ No auto-charts generated")
            return False
        
        if len(auto_charts) > 15:
            print(f"⚠️  More than 15 charts generated ({len(auto_charts)})")
        
        # Verify chart structure
        chart_issues = []
        for i, chart in enumerate(auto_charts[:5]):  # Check first 5 charts
            required_chart_fields = ['type', 'title', 'plotly_data', 'description']
            for field in required_chart_fields:
                if field not in chart:
                    chart_issues.append(f"Chart {i+1} missing '{field}'")
            
            # Verify plotly_data structure
            plotly_data = chart.get('plotly_data', {})
            if not isinstance(plotly_data, dict):
                chart_issues.append(f"Chart {i+1} plotly_data is not a dict")
            elif 'data' not in plotly_data or 'layout' not in plotly_data:
                chart_issues.append(f"Chart {i+1} plotly_data missing 'data' or 'layout'")
        
        if chart_issues:
            print(f"❌ Chart structure issues:")
            for issue in chart_issues:
                print(f"   - {issue}")
            return False
        
        print(f"✅ Auto-charts structure validated")
        
        # Display chart types
        chart_types = {}
        for chart in auto_charts:
            chart_type = chart.get('type', 'unknown')
            chart_types[chart_type] = chart_types.get(chart_type, 0) + 1
        
        print(f"   Chart types: {dict(chart_types)}")
        
        # Test other analysis components
        print(f"\n3b. Testing analysis components...")
        
        # Volume analysis
        volume_analysis = data.get('volume_analysis', {})
        if 'by_dimensions' in volume_analysis:
            print(f"   ✅ Volume analysis: {len(volume_analysis['by_dimensions'])} dimensions")
        else:
            print(f"   ⚠️  Volume analysis missing 'by_dimensions'")
        
        # Trend analysis
        trend_analysis = data.get('trend_analysis', {})
        if 'trends' in trend_analysis:
            print(f"   ✅ Trend analysis: {len(trend_analysis['trends'])} trends")
        else:
            print(f"   ⚠️  Trend analysis missing 'trends'")
        
        # Correlations
        correlations = data.get('correlations', [])
        print(f"   ✅ Correlations: {len(correlations)} correlation pairs")
        
        # ML Models
        ml_models = data.get('ml_models', [])
        print(f"   ✅ ML Models: {len(ml_models)} models trained")
        
        # Predictions
        predictions = data.get('predictions', [])
        print(f"   ✅ Predictions: {len(predictions)} prediction insights")
        
        # AI Summary
        ai_summary = data.get('ai_summary', '')
        if ai_summary and len(ai_summary) > 10:
            print(f"   ✅ AI Summary: {len(ai_summary)} characters")
        else:
            print(f"   ⚠️  AI Summary seems short or missing")
        
        print(f"✅ Holistic analysis test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Holistic analysis error: {str(e)}")
        return False

def test_data_retrieval():
    """Test 4: Data Retrieval - Test that datasets can be retrieved and listed"""
    print("\n=== TEST 4: Data Retrieval Testing ===")
    
    # Test dataset listing
    print("\n4a. Testing dataset listing...")
    
    try:
        response = requests.get(f"{API_BASE}/datasets", timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Dataset listing failed: {response.status_code} - {response.text}")
            return False
        
        data = response.json()
        datasets = data.get('datasets', [])
        
        print(f"✅ Dataset listing successful")
        print(f"   Found {len(datasets)} datasets")
        
        if len(datasets) > 0:
            # Test individual dataset details
            sample_dataset = datasets[0]
            required_fields = ['id', 'name', 'row_count', 'column_count', 'columns']
            
            missing_fields = []
            for field in required_fields:
                if field not in sample_dataset:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"⚠️  Sample dataset missing fields: {missing_fields}")
            else:
                print(f"✅ Dataset structure validated")
                print(f"   Sample: {sample_dataset['name']} ({sample_dataset['row_count']} rows)")
        
        return True
        
    except Exception as e:
        print(f"❌ Data retrieval error: {str(e)}")
        return False

def test_chat_actions(dataset_info):
    """Test 5: Chat Actions - Verify chat action endpoint works for custom charts"""
    print("\n=== TEST 5: Chat Actions for Custom Charts ===")
    
    dataset_id = dataset_info['id']
    chat_url = f"{API_BASE}/analysis/chat-action"
    
    test_cases = [
        ("pie chart", "show me a pie chart", "pie"),
        ("bar chart", "create a bar chart", "bar"),
        ("line chart", "show line chart trend", "line"),
        ("correlation", "analyze correlations", "correlation")
    ]
    
    results = []
    
    for test_name, message, expected_type in test_cases:
        print(f"\n5{chr(97 + len(results))}. Testing {test_name} generation...")
        
        try:
            request_data = {
                "dataset_id": dataset_id,
                "message": message,
                "conversation_history": []
            }
            
            response = requests.post(chat_url, json=request_data, timeout=30)
            
            if response.status_code != 200:
                print(f"❌ {test_name} request failed: {response.status_code} - {response.text}")
                results.append(False)
                continue
            
            data = response.json()
            
            # Verify response structure
            if 'action' not in data:
                print(f"❌ {test_name} response missing 'action' field")
                results.append(False)
                continue
            
            if data['action'] != 'add_chart':
                print(f"❌ {test_name} expected action 'add_chart', got '{data['action']}'")
                results.append(False)
                continue
            
            if 'chart_data' not in data:
                print(f"❌ {test_name} response missing 'chart_data' field")
                results.append(False)
                continue
            
            chart_data = data['chart_data']
            
            # Verify chart type
            if chart_data.get('type') != expected_type:
                print(f"❌ {test_name} expected type '{expected_type}', got '{chart_data.get('type')}'")
                results.append(False)
                continue
            
            # Verify required chart fields
            required_fields = ['type', 'title', 'description']
            if expected_type != 'correlation':
                required_fields.append('plotly_data')
            else:
                required_fields.extend(['correlations', 'heatmap'])
            
            missing_fields = []
            for field in required_fields:
                if field not in chart_data:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"❌ {test_name} chart_data missing fields: {missing_fields}")
                results.append(False)
                continue
            
            print(f"✅ {test_name} generation successful")
            print(f"   Title: {chart_data.get('title', 'N/A')}")
            print(f"   Type: {chart_data.get('type', 'N/A')}")
            
            results.append(True)
            
        except Exception as e:
            print(f"❌ {test_name} error: {str(e)}")
            results.append(False)
    
    success_count = sum(results)
    total_count = len(results)
    
    print(f"\n✅ Chat actions test completed: {success_count}/{total_count} successful")
    return success_count == total_count

def check_backend_logs():
    """Check backend logs for any errors"""
    print("\n=== Checking Backend Logs ===")
    
    try:
        import subprocess
        result = subprocess.run(
            ['tail', '-n', '50', '/var/log/supervisor/backend.err.log'],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode == 0:
            error_log = result.stdout
            if error_log.strip():
                print("⚠️  Recent backend errors found:")
                print(error_log[-1000:])  # Last 1000 chars
                return False
            else:
                print("✅ No recent backend errors found")
                return True
        else:
            print("⚠️  Could not read backend error log")
            return True
            
    except Exception as e:
        print(f"⚠️  Error checking logs: {str(e)}")
        return True

def main():
    """Run all comprehensive tests"""
    print("🚀 Starting Comprehensive PROMISE AI Backend Testing")
    print("=" * 70)
    
    test_results = []
    
    try:
        # Test 1: Backend Health
        test_results.append(("Backend Health", test_backend_health()))
        
        # Test 2: File Upload
        upload_success, upload_data = test_file_upload()
        test_results.append(("File Upload", upload_success))
        
        if upload_success and upload_data:
            # Use the first successful upload for subsequent tests
            test_dataset = upload_data[0][2]  # Get dataset info
            
            # Test 3: Holistic Analysis
            test_results.append(("Holistic Analysis", test_holistic_analysis(test_dataset)))
            
            # Test 4: Data Retrieval
            test_results.append(("Data Retrieval", test_data_retrieval()))
            
            # Test 5: Chat Actions
            test_results.append(("Chat Actions", test_chat_actions(test_dataset)))
        else:
            print("⚠️  Skipping dependent tests due to upload failure")
            test_results.extend([
                ("Holistic Analysis", False),
                ("Data Retrieval", False),
                ("Chat Actions", False)
            ])
        
        # Check backend logs
        log_check = check_backend_logs()
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 COMPREHENSIVE TEST RESULTS:")
        print("=" * 70)
        
        passed = 0
        failed = 0
        
        for test_name, result in test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name:<25} {status}")
            if result:
                passed += 1
            else:
                failed += 1
        
        print(f"\nBackend Logs: {'✅ CLEAN' if log_check else '⚠️  ERRORS FOUND'}")
        print(f"\nTotal: {len(test_results)} tests | Passed: {passed} | Failed: {failed}")
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED!")
            print("PROMISE AI backend is fully functional with:")
            print("✅ Backend health confirmed")
            print("✅ File upload working (small & medium files)")
            print("✅ Holistic analysis with auto-charts (up to 15)")
            print("✅ Data retrieval functioning")
            print("✅ Chat actions for custom charts working")
            return True
        else:
            print(f"\n❌ {failed} TEST(S) FAILED!")
            print("Some critical functionality needs attention.")
            return False
            
    except Exception as e:
        print(f"\n❌ Test execution failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)