#!/usr/bin/env python3
"""
Backend API Testing for Custom Chart Generation and Removal via Chat Interface
Tests Phase 1 & 3 implementation: Custom chart generation and removal via chat interface.
"""

import requests
import json
import os
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

print(f"Testing backend at: {API_BASE}")

def test_correlation_analysis():
    """Test the correlation analysis feature via chat interface"""
    
    print("\n=== Testing Correlation Analysis via Chat Interface ===")
    
    # Step 1: Upload test dataset
    print("\n1. Uploading test dataset...")
    
    upload_url = f"{API_BASE}/datasource/upload-file"
    
    with open('/app/test_data.csv', 'rb') as f:
        files = {'file': ('test_data.csv', f, 'text/csv')}
        response = requests.post(upload_url, files=files)
    
    if response.status_code != 200:
        print(f"❌ Upload failed: {response.status_code} - {response.text}")
        return False
    
    dataset_info = response.json()
    dataset_id = dataset_info['id']
    print(f"✅ Dataset uploaded successfully. ID: {dataset_id}")
    print(f"   Rows: {dataset_info['row_count']}, Columns: {dataset_info['column_count']}")
    print(f"   Columns: {dataset_info['columns']}")
    
    # Step 2: Test correlation analysis via chat
    print("\n2. Testing correlation analysis via chat...")
    
    chat_url = f"{API_BASE}/analysis/chat-action"
    chat_request = {
        "dataset_id": dataset_id,
        "message": "Please analyze the correlations between all numeric variables",
        "conversation_history": []
    }
    
    response = requests.post(chat_url, json=chat_request)
    
    if response.status_code != 200:
        print(f"❌ Chat request failed: {response.status_code} - {response.text}")
        return False
    
    chat_response = response.json()
    print(f"✅ Chat request successful")
    
    # Step 3: Verify response structure
    print("\n3. Verifying response structure...")
    
    # Check if it's an action response
    if 'action' not in chat_response:
        print(f"❌ Missing 'action' field in response")
        print(f"Response: {json.dumps(chat_response, indent=2)}")
        return False
    
    if chat_response['action'] != 'add_chart':
        print(f"❌ Expected action 'add_chart', got '{chat_response['action']}'")
        return False
    
    print(f"✅ Action field correct: {chat_response['action']}")
    
    # Check message
    if 'message' not in chat_response:
        print(f"❌ Missing 'message' field in response")
        return False
    
    print(f"✅ Message: {chat_response['message']}")
    
    # Check chart_data structure
    if 'chart_data' not in chat_response:
        print(f"❌ Missing 'chart_data' field in response")
        return False
    
    chart_data = chat_response['chart_data']
    
    # Verify chart_data.type
    if chart_data.get('type') != 'correlation':
        print(f"❌ Expected chart_data.type 'correlation', got '{chart_data.get('type')}'")
        return False
    
    print(f"✅ Chart type correct: {chart_data['type']}")
    
    # Verify correlations array
    if 'correlations' not in chart_data:
        print(f"❌ Missing 'correlations' field in chart_data")
        return False
    
    correlations = chart_data['correlations']
    if not isinstance(correlations, list):
        print(f"❌ Correlations should be a list, got {type(correlations)}")
        return False
    
    print(f"✅ Found {len(correlations)} correlation pairs")
    
    # Verify correlation structure
    if len(correlations) > 0:
        first_corr = correlations[0]
        required_fields = ['feature1', 'feature2', 'value', 'strength', 'interpretation']
        
        for field in required_fields:
            if field not in first_corr:
                print(f"❌ Missing '{field}' in correlation object")
                return False
        
        print(f"✅ Correlation structure valid")
        print(f"   Example: {first_corr['feature1']} vs {first_corr['feature2']} = {first_corr['value']:.3f} ({first_corr['strength']})")
        
        # Check that only significant correlations are included (abs > 0.1)
        weak_correlations = [c for c in correlations if abs(c['value']) <= 0.1]
        if weak_correlations:
            print(f"⚠️  Found {len(weak_correlations)} correlations with abs value <= 0.1")
        else:
            print(f"✅ All correlations have abs value > 0.1")
        
        # Check if correlations are sorted by absolute value
        values = [abs(c['value']) for c in correlations]
        is_sorted = all(values[i] >= values[i+1] for i in range(len(values)-1))
        if is_sorted:
            print(f"✅ Correlations are sorted by absolute value")
        else:
            print(f"⚠️  Correlations are not sorted by absolute value")
    
    # Verify heatmap data
    if 'heatmap' not in chart_data:
        print(f"❌ Missing 'heatmap' field in chart_data")
        return False
    
    heatmap = chart_data['heatmap']
    if not isinstance(heatmap, dict):
        print(f"❌ Heatmap should be a dict, got {type(heatmap)}")
        return False
    
    # Check Plotly structure
    if 'data' not in heatmap or 'layout' not in heatmap:
        print(f"❌ Heatmap missing 'data' or 'layout' fields (Plotly format)")
        return False
    
    print(f"✅ Heatmap has valid Plotly structure")
    
    # Check heatmap data structure
    heatmap_data = heatmap['data']
    if not isinstance(heatmap_data, list) or len(heatmap_data) == 0:
        print(f"❌ Heatmap data should be non-empty list")
        return False
    
    first_trace = heatmap_data[0]
    if first_trace.get('type') != 'heatmap':
        print(f"❌ Expected heatmap type, got {first_trace.get('type')}")
        return False
    
    print(f"✅ Heatmap data structure valid")
    
    # Step 4: Test correlation calculation accuracy
    print("\n4. Testing correlation calculation accuracy...")
    
    # We know our test data should have some correlations
    # Check if we got reasonable results
    expected_numeric_cols = ['age', 'salary', 'years_experience', 'satisfaction_score', 'performance_rating']
    
    # Check if we have correlations for expected columns
    found_columns = set()
    for corr in correlations:
        found_columns.add(corr['feature1'])
        found_columns.add(corr['feature2'])
    
    missing_cols = set(expected_numeric_cols) - found_columns
    if missing_cols:
        print(f"⚠️  Some expected columns not found in correlations: {missing_cols}")
    else:
        print(f"✅ All expected numeric columns found in correlations")
    
    # Look for expected strong correlations (age vs years_experience, salary vs years_experience)
    strong_correlations = [c for c in correlations if c['strength'] == 'Strong']
    print(f"✅ Found {len(strong_correlations)} strong correlations")
    
    if strong_correlations:
        for corr in strong_correlations[:3]:  # Show top 3
            print(f"   {corr['feature1']} ↔ {corr['feature2']}: {corr['value']:.3f}")
    
    print(f"\n✅ Correlation analysis test completed successfully!")
    return True

def test_edge_cases():
    """Test edge cases for correlation analysis"""
    
    print("\n=== Testing Edge Cases ===")
    
    # Test with non-existent dataset
    print("\n1. Testing with non-existent dataset...")
    
    chat_url = f"{API_BASE}/analysis/chat-action"
    chat_request = {
        "dataset_id": "non-existent-id",
        "message": "analyze correlations",
        "conversation_history": []
    }
    
    response = requests.post(chat_url, json=chat_request)
    
    if response.status_code == 404:
        print(f"✅ Correctly returned 404 for non-existent dataset")
    else:
        print(f"⚠️  Expected 404, got {response.status_code}")
    
    return True

def test_pie_chart_generation():
    """Test pie chart generation via chat interface"""
    
    print("\n=== Testing Pie Chart Generation ===")
    
    # Step 1: Upload test dataset
    print("\n1. Uploading test dataset...")
    
    upload_url = f"{API_BASE}/datasource/upload-file"
    
    with open('/app/test_data.csv', 'rb') as f:
        files = {'file': ('test_data.csv', f, 'text/csv')}
        response = requests.post(upload_url, files=files)
    
    if response.status_code != 200:
        print(f"❌ Upload failed: {response.status_code} - {response.text}")
        return False
    
    dataset_info = response.json()
    dataset_id = dataset_info['id']
    print(f"✅ Dataset uploaded successfully. ID: {dataset_id}")
    
    # Step 2: Test pie chart request
    print("\n2. Testing pie chart request...")
    
    chat_url = f"{API_BASE}/analysis/chat-action"
    chat_request = {
        "dataset_id": dataset_id,
        "message": "show me a pie chart",
        "conversation_history": []
    }
    
    response = requests.post(chat_url, json=chat_request)
    
    if response.status_code != 200:
        print(f"❌ Pie chart request failed: {response.status_code} - {response.text}")
        return False
    
    chat_response = response.json()
    print(f"✅ Pie chart request successful")
    print(f"Response: {json.dumps(chat_response, indent=2)}")
    
    # Step 3: Verify response structure
    print("\n3. Verifying pie chart response structure...")
    
    # Check required fields
    required_fields = ['action', 'message', 'chart_data']
    for field in required_fields:
        if field not in chat_response:
            print(f"❌ Missing '{field}' field in response")
            print(f"Available fields: {list(chat_response.keys())}")
            return False
    
    if chat_response['action'] != 'add_chart':
        print(f"❌ Expected action 'add_chart', got '{chat_response['action']}'")
        return False
    
    chart_data = chat_response['chart_data']
    
    if chart_data.get('type') != 'pie':
        print(f"❌ Expected chart_data.type 'pie', got '{chart_data.get('type')}'")
        return False
    
    # Check for required chart_data fields
    chart_required_fields = ['type', 'title', 'plotly_data', 'description']
    for field in chart_required_fields:
        if field not in chart_data:
            print(f"❌ Missing '{field}' field in chart_data")
            return False
    
    # Verify Plotly data structure
    plotly_data = chart_data['plotly_data']
    if 'data' not in plotly_data or 'layout' not in plotly_data:
        print(f"❌ Plotly data missing 'data' or 'layout' fields")
        return False
    
    # Check if it's actually a pie chart
    pie_traces = [trace for trace in plotly_data['data'] if trace.get('type') == 'pie']
    if not pie_traces:
        print(f"❌ No pie chart traces found in Plotly data")
        return False
    
    print(f"✅ Pie chart generation test passed!")
    print(f"   Title: {chart_data['title']}")
    print(f"   Description: {chart_data['description']}")
    
    return True

def test_bar_chart_generation():
    """Test bar chart generation via chat interface"""
    
    print("\n=== Testing Bar Chart Generation ===")
    
    # Step 1: Upload test dataset
    print("\n1. Uploading test dataset...")
    
    upload_url = f"{API_BASE}/datasource/upload-file"
    
    with open('/app/test_data.csv', 'rb') as f:
        files = {'file': ('test_data.csv', f, 'text/csv')}
        response = requests.post(upload_url, files=files)
    
    if response.status_code != 200:
        print(f"❌ Upload failed: {response.status_code} - {response.text}")
        return False
    
    dataset_info = response.json()
    dataset_id = dataset_info['id']
    print(f"✅ Dataset uploaded successfully. ID: {dataset_id}")
    
    # Step 2: Test bar chart request
    print("\n2. Testing bar chart request...")
    
    chat_url = f"{API_BASE}/analysis/chat-action"
    chat_request = {
        "dataset_id": dataset_id,
        "message": "create a bar chart",
        "conversation_history": []
    }
    
    response = requests.post(chat_url, json=chat_request)
    
    if response.status_code != 200:
        print(f"❌ Bar chart request failed: {response.status_code} - {response.text}")
        return False
    
    chat_response = response.json()
    print(f"✅ Bar chart request successful")
    print(f"Response: {json.dumps(chat_response, indent=2)}")
    
    # Step 3: Verify response structure
    print("\n3. Verifying bar chart response structure...")
    
    # Check required fields
    if chat_response.get('action') != 'add_chart':
        print(f"❌ Expected action 'add_chart', got '{chat_response.get('action')}'")
        print(f"Available fields: {list(chat_response.keys())}")
        return False
    
    chart_data = chat_response['chart_data']
    
    if chart_data.get('type') != 'bar':
        print(f"❌ Expected chart_data.type 'bar', got '{chart_data.get('type')}'")
        return False
    
    # Check for required chart_data fields
    chart_required_fields = ['type', 'title', 'plotly_data', 'description']
    for field in chart_required_fields:
        if field not in chart_data:
            print(f"❌ Missing '{field}' field in chart_data")
            return False
    
    # Verify Plotly data structure
    plotly_data = chart_data['plotly_data']
    if 'data' not in plotly_data or 'layout' not in plotly_data:
        print(f"❌ Plotly data missing 'data' or 'layout' fields")
        return False
    
    # Check if it's actually a bar chart
    bar_traces = [trace for trace in plotly_data['data'] if trace.get('type') == 'bar']
    if not bar_traces:
        print(f"❌ No bar chart traces found in Plotly data")
        return False
    
    print(f"✅ Bar chart generation test passed!")
    print(f"   Title: {chart_data['title']}")
    print(f"   Description: {chart_data['description']}")
    
    return True

def test_line_chart_generation():
    """Test line chart generation via chat interface"""
    
    print("\n=== Testing Line Chart Generation ===")
    
    # Step 1: Upload test dataset
    print("\n1. Uploading test dataset...")
    
    upload_url = f"{API_BASE}/datasource/upload-file"
    
    with open('/app/test_data.csv', 'rb') as f:
        files = {'file': ('test_data.csv', f, 'text/csv')}
        response = requests.post(upload_url, files=files)
    
    if response.status_code != 200:
        print(f"❌ Upload failed: {response.status_code} - {response.text}")
        return False
    
    dataset_info = response.json()
    dataset_id = dataset_info['id']
    print(f"✅ Dataset uploaded successfully. ID: {dataset_id}")
    
    # Step 2: Test line chart request
    print("\n2. Testing line chart request...")
    
    chat_url = f"{API_BASE}/analysis/chat-action"
    chat_request = {
        "dataset_id": dataset_id,
        "message": "show line chart trend",
        "conversation_history": []
    }
    
    response = requests.post(chat_url, json=chat_request)
    
    if response.status_code != 200:
        print(f"❌ Line chart request failed: {response.status_code} - {response.text}")
        return False
    
    chat_response = response.json()
    print(f"✅ Line chart request successful")
    
    # Step 3: Verify response structure
    print("\n3. Verifying line chart response structure...")
    
    # Check required fields
    if chat_response.get('action') != 'add_chart':
        print(f"❌ Expected action 'add_chart', got '{chat_response.get('action')}'")
        return False
    
    chart_data = chat_response['chart_data']
    
    if chart_data.get('type') != 'line':
        print(f"❌ Expected chart_data.type 'line', got '{chart_data.get('type')}'")
        return False
    
    # Check for required chart_data fields
    chart_required_fields = ['type', 'title', 'plotly_data', 'description']
    for field in chart_required_fields:
        if field not in chart_data:
            print(f"❌ Missing '{field}' field in chart_data")
            return False
    
    # Verify Plotly data structure
    plotly_data = chart_data['plotly_data']
    if 'data' not in plotly_data or 'layout' not in plotly_data:
        print(f"❌ Plotly data missing 'data' or 'layout' fields")
        return False
    
    # Check if it's actually a line chart (scatter with lines)
    line_traces = [trace for trace in plotly_data['data'] if trace.get('type') == 'scatter' and 'lines' in trace.get('mode', '')]
    if not line_traces:
        print(f"❌ No line chart traces found in Plotly data")
        return False
    
    print(f"✅ Line chart generation test passed!")
    print(f"   Title: {chart_data['title']}")
    print(f"   Description: {chart_data['description']}")
    
    return True

def test_correlation_request():
    """Test correlation analysis request via chat interface"""
    
    print("\n=== Testing Correlation Analysis Request ===")
    
    # Step 1: Upload test dataset
    print("\n1. Uploading test dataset...")
    
    upload_url = f"{API_BASE}/datasource/upload-file"
    
    with open('/app/test_data.csv', 'rb') as f:
        files = {'file': ('test_data.csv', f, 'text/csv')}
        response = requests.post(upload_url, files=files)
    
    if response.status_code != 200:
        print(f"❌ Upload failed: {response.status_code} - {response.text}")
        return False
    
    dataset_info = response.json()
    dataset_id = dataset_info['id']
    print(f"✅ Dataset uploaded successfully. ID: {dataset_id}")
    
    # Step 2: Test correlation request
    print("\n2. Testing correlation analysis request...")
    
    chat_url = f"{API_BASE}/analysis/chat-action"
    chat_request = {
        "dataset_id": dataset_id,
        "message": "show correlation analysis",
        "conversation_history": []
    }
    
    response = requests.post(chat_url, json=chat_request)
    
    if response.status_code != 200:
        print(f"❌ Correlation request failed: {response.status_code} - {response.text}")
        return False
    
    chat_response = response.json()
    print(f"✅ Correlation request successful")
    
    # Step 3: Verify response structure
    print("\n3. Verifying correlation response structure...")
    
    # Check required fields
    if chat_response.get('action') != 'add_chart':
        print(f"❌ Expected action 'add_chart', got '{chat_response.get('action')}'")
        return False
    
    chart_data = chat_response['chart_data']
    
    if chart_data.get('type') != 'correlation':
        print(f"❌ Expected chart_data.type 'correlation', got '{chart_data.get('type')}'")
        return False
    
    # Check for correlations array
    if 'correlations' not in chart_data:
        print(f"❌ Missing 'correlations' field in chart_data")
        return False
    
    # Check for heatmap data
    if 'heatmap' not in chart_data:
        print(f"❌ Missing 'heatmap' field in chart_data")
        return False
    
    print(f"✅ Correlation analysis test passed!")
    print(f"   Found {len(chart_data['correlations'])} correlation pairs")
    
    return True

def test_removal_requests():
    """Test chart removal functionality via chat interface"""
    
    print("\n=== Testing Chart Removal Functionality ===")
    
    # Step 1: Upload test dataset
    print("\n1. Uploading test dataset...")
    
    upload_url = f"{API_BASE}/datasource/upload-file"
    
    with open('/app/test_data.csv', 'rb') as f:
        files = {'file': ('test_data.csv', f, 'text/csv')}
        response = requests.post(upload_url, files=files)
    
    if response.status_code != 200:
        print(f"❌ Upload failed: {response.status_code} - {response.text}")
        return False
    
    dataset_info = response.json()
    dataset_id = dataset_info['id']
    print(f"✅ Dataset uploaded successfully. ID: {dataset_id}")
    
    # Step 2: Test correlation removal
    print("\n2. Testing correlation removal...")
    
    chat_url = f"{API_BASE}/analysis/chat-action"
    chat_request = {
        "dataset_id": dataset_id,
        "message": "remove correlation",
        "conversation_history": []
    }
    
    response = requests.post(chat_url, json=chat_request)
    
    if response.status_code != 200:
        print(f"❌ Correlation removal request failed: {response.status_code} - {response.text}")
        return False
    
    chat_response = response.json()
    
    # Verify removal response structure
    if chat_response.get('action') != 'remove_section':
        print(f"❌ Expected action 'remove_section', got '{chat_response.get('action')}'")
        return False
    
    if chat_response.get('section_to_remove') != 'correlations':
        print(f"❌ Expected section_to_remove 'correlations', got '{chat_response.get('section_to_remove')}'")
        return False
    
    print(f"✅ Correlation removal test passed!")
    
    # Step 3: Test custom chart removal
    print("\n3. Testing custom chart removal...")
    
    chat_request = {
        "dataset_id": dataset_id,
        "message": "remove pie chart",
        "conversation_history": []
    }
    
    response = requests.post(chat_url, json=chat_request)
    
    if response.status_code != 200:
        print(f"❌ Custom chart removal request failed: {response.status_code} - {response.text}")
        return False
    
    chat_response = response.json()
    
    # Verify removal response structure
    if chat_response.get('action') != 'remove_section':
        print(f"❌ Expected action 'remove_section', got '{chat_response.get('action')}'")
        return False
    
    if chat_response.get('section_to_remove') != 'custom_chart':
        print(f"❌ Expected section_to_remove 'custom_chart', got '{chat_response.get('section_to_remove')}'")
        return False
    
    print(f"✅ Custom chart removal test passed!")
    
    return True

def main():
    """Run all tests"""
    print("Starting Backend API Tests for Custom Chart Generation and Removal")
    print("=" * 70)
    
    try:
        test_results = []
        
        # Test all chart generation types
        print("\n🔍 Testing Chart Generation...")
        test_results.append(("Pie Chart Generation", test_pie_chart_generation()))
        test_results.append(("Bar Chart Generation", test_bar_chart_generation()))
        test_results.append(("Line Chart Generation", test_line_chart_generation()))
        test_results.append(("Correlation Analysis", test_correlation_request()))
        
        # Test removal functionality
        print("\n🗑️  Testing Removal Functionality...")
        test_results.append(("Chart Removal", test_removal_requests()))
        
        # Test edge cases
        print("\n⚠️  Testing Edge Cases...")
        test_results.append(("Edge Cases", test_edge_cases()))
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 TEST RESULTS SUMMARY:")
        print("=" * 70)
        
        passed = 0
        failed = 0
        
        for test_name, result in test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name:<30} {status}")
            if result:
                passed += 1
            else:
                failed += 1
        
        print(f"\nTotal: {len(test_results)} tests | Passed: {passed} | Failed: {failed}")
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED!")
            print("Custom chart generation and removal via chat interface is working correctly.")
            return True
        else:
            print(f"\n❌ {failed} TEST(S) FAILED!")
            print("Some functionality needs to be addressed.")
            return False
            
    except Exception as e:
        print(f"\n❌ Test execution failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)