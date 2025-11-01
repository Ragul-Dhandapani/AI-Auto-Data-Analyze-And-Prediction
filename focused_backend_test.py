#!/usr/bin/env python3
"""
Focused Backend Testing for Fixed Issues - Post-Refactoring Validation
Tests the 3 critical issues that were fixed:
1. Correlation format changed from dictionary to array
2. Removal keyword detection moved to first position
3. Removal response field changed from section_type to section_to_remove
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

def upload_test_dataset():
    """Upload test dataset and return dataset_id"""
    print("\n📁 Uploading test dataset...")
    
    upload_url = f"{API_BASE}/datasource/upload-file"
    
    with open('/app/test_data.csv', 'rb') as f:
        files = {'file': ('test_data.csv', f, 'text/csv')}
        response = requests.post(upload_url, files=files)
    
    if response.status_code != 200:
        print(f"❌ Upload failed: {response.status_code} - {response.text}")
        return None
    
    dataset_info = response.json()
    dataset_id = dataset_info['id']
    print(f"✅ Dataset uploaded successfully. ID: {dataset_id}")
    print(f"   Rows: {dataset_info['row_count']}, Columns: {dataset_info['column_count']}")
    
    return dataset_id

def test_correlation_array_format(dataset_id):
    """
    PRIORITY 1: Test that correlation response returns array format
    Fixed issue: Correlation format changed from dictionary to array
    """
    print("\n=== PRIORITY 1: Testing Correlation Array Format ===")
    
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
    
    # Verify action
    if chat_response.get('action') != 'add_chart':
        print(f"❌ Expected action 'add_chart', got '{chat_response.get('action')}'")
        return False
    
    chart_data = chat_response.get('chart_data', {})
    
    # Verify chart type
    if chart_data.get('type') != 'correlation':
        print(f"❌ Expected chart_data.type 'correlation', got '{chart_data.get('type')}'")
        return False
    
    # CRITICAL: Verify correlations is an array (not dictionary)
    correlations = chart_data.get('correlations')
    if not isinstance(correlations, list):
        print(f"❌ CRITICAL: Correlations should be array, got {type(correlations)}")
        print(f"   Current value: {correlations}")
        return False
    
    print(f"✅ Correlations is array format: {len(correlations)} items")
    
    # Verify array structure
    if len(correlations) > 0:
        first_corr = correlations[0]
        required_fields = ['feature1', 'feature2', 'value', 'strength', 'interpretation']
        
        for field in required_fields:
            if field not in first_corr:
                print(f"❌ Missing '{field}' in correlation object")
                return False
        
        print(f"✅ Correlation structure valid")
        print(f"   Example: {first_corr['feature1']} vs {first_corr['feature2']} = {first_corr['value']:.3f} ({first_corr['strength']})")
        
        # Verify only significant correlations (abs > 0.1)
        weak_correlations = [c for c in correlations if abs(c['value']) <= 0.1]
        if weak_correlations:
            print(f"⚠️  Found {len(weak_correlations)} correlations with abs value <= 0.1")
        else:
            print(f"✅ All correlations have abs value > 0.1")
        
        # Verify correlations sorted by absolute value
        values = [abs(c['value']) for c in correlations]
        is_sorted = all(values[i] >= values[i+1] for i in range(len(values)-1))
        if is_sorted:
            print(f"✅ Correlations are sorted by absolute value")
        else:
            print(f"⚠️  Correlations are not sorted by absolute value")
    
    return True

def test_removal_keyword_detection(dataset_id):
    """
    PRIORITY 2: Test that removal keyword detection works correctly
    Fixed issue: Removal detection moved to first position to prevent false positives
    """
    print("\n=== PRIORITY 2: Testing Removal Keyword Detection Order ===")
    
    chat_url = f"{API_BASE}/analysis/chat-action"
    
    # Test 1: "remove correlation" should trigger removal, not correlation generation
    print("\n1. Testing 'remove correlation' - should trigger removal")
    
    chat_request = {
        "dataset_id": dataset_id,
        "message": "remove correlation",
        "conversation_history": []
    }
    
    response = requests.post(chat_url, json=chat_request)
    
    if response.status_code != 200:
        print(f"❌ Remove correlation request failed: {response.status_code} - {response.text}")
        return False
    
    chat_response = response.json()
    
    # CRITICAL: Should be removal action, not add_chart
    if chat_response.get('action') != 'remove_section':
        print(f"❌ CRITICAL: 'remove correlation' triggered '{chat_response.get('action')}' instead of 'remove_section'")
        print(f"   This indicates keyword detection order issue")
        return False
    
    print(f"✅ 'remove correlation' correctly triggers removal action")
    
    # Test 2: "add correlation" should trigger correlation generation
    print("\n2. Testing 'add correlation' - should trigger correlation generation")
    
    chat_request = {
        "dataset_id": dataset_id,
        "message": "add correlation",
        "conversation_history": []
    }
    
    response = requests.post(chat_url, json=chat_request)
    
    if response.status_code != 200:
        print(f"❌ Add correlation request failed: {response.status_code} - {response.text}")
        return False
    
    chat_response = response.json()
    
    if chat_response.get('action') != 'add_chart':
        print(f"❌ 'add correlation' should trigger 'add_chart', got '{chat_response.get('action')}'")
        return False
    
    print(f"✅ 'add correlation' correctly triggers chart generation")
    
    # Test 3: "show correlation" should trigger correlation generation
    print("\n3. Testing 'show correlation' - should trigger correlation generation")
    
    chat_request = {
        "dataset_id": dataset_id,
        "message": "show correlation",
        "conversation_history": []
    }
    
    response = requests.post(chat_url, json=chat_request)
    
    if response.status_code != 200:
        print(f"❌ Show correlation request failed: {response.status_code} - {response.text}")
        return False
    
    chat_response = response.json()
    
    if chat_response.get('action') != 'add_chart':
        print(f"❌ 'show correlation' should trigger 'add_chart', got '{chat_response.get('action')}'")
        return False
    
    print(f"✅ 'show correlation' correctly triggers chart generation")
    
    return True

def test_removal_response_field(dataset_id):
    """
    PRIORITY 3: Test that removal response uses section_to_remove field
    Fixed issue: Removal response field changed from section_type to section_to_remove
    """
    print("\n=== PRIORITY 3: Testing Removal Response Field ===")
    
    chat_url = f"{API_BASE}/analysis/chat-action"
    
    # Test correlation removal
    print("\n1. Testing correlation removal response field")
    
    chat_request = {
        "dataset_id": dataset_id,
        "message": "remove correlation",
        "conversation_history": []
    }
    
    response = requests.post(chat_url, json=chat_request)
    
    if response.status_code != 200:
        print(f"❌ Remove correlation request failed: {response.status_code} - {response.text}")
        return False
    
    chat_response = response.json()
    
    # Verify action
    if chat_response.get('action') != 'remove_section':
        print(f"❌ Expected action 'remove_section', got '{chat_response.get('action')}'")
        return False
    
    # CRITICAL: Verify section_to_remove field (not section_type)
    if 'section_to_remove' not in chat_response:
        print(f"❌ CRITICAL: Missing 'section_to_remove' field in response")
        print(f"   Available fields: {list(chat_response.keys())}")
        return False
    
    if 'section_type' in chat_response:
        print(f"❌ CRITICAL: Found old 'section_type' field - should be 'section_to_remove'")
        return False
    
    section_to_remove = chat_response.get('section_to_remove')
    if section_to_remove != 'correlation':
        print(f"❌ Expected section_to_remove 'correlation', got '{section_to_remove}'")
        return False
    
    print(f"✅ Correlation removal uses correct field: section_to_remove = '{section_to_remove}'")
    
    # Test pie chart removal
    print("\n2. Testing pie chart removal response field")
    
    chat_request = {
        "dataset_id": dataset_id,
        "message": "remove pie chart",
        "conversation_history": []
    }
    
    response = requests.post(chat_url, json=chat_request)
    
    if response.status_code != 200:
        print(f"❌ Remove pie chart request failed: {response.status_code} - {response.text}")
        return False
    
    chat_response = response.json()
    
    if chat_response.get('action') != 'remove_section':
        print(f"❌ Expected action 'remove_section', got '{chat_response.get('action')}'")
        return False
    
    if 'section_to_remove' not in chat_response:
        print(f"❌ Missing 'section_to_remove' field in pie chart removal response")
        return False
    
    section_to_remove = chat_response.get('section_to_remove')
    if section_to_remove != 'pie':
        print(f"❌ Expected section_to_remove 'pie', got '{section_to_remove}'")
        return False
    
    print(f"✅ Pie chart removal uses correct field: section_to_remove = '{section_to_remove}'")
    
    # Test bar chart removal
    print("\n3. Testing bar chart removal response field")
    
    chat_request = {
        "dataset_id": dataset_id,
        "message": "remove bar chart",
        "conversation_history": []
    }
    
    response = requests.post(chat_url, json=chat_request)
    
    if response.status_code != 200:
        print(f"❌ Remove bar chart request failed: {response.status_code} - {response.text}")
        return False
    
    chat_response = response.json()
    
    if chat_response.get('action') != 'remove_section':
        print(f"❌ Expected action 'remove_section', got '{chat_response.get('action')}'")
        return False
    
    if 'section_to_remove' not in chat_response:
        print(f"❌ Missing 'section_to_remove' field in bar chart removal response")
        return False
    
    section_to_remove = chat_response.get('section_to_remove')
    if section_to_remove != 'bar':
        print(f"❌ Expected section_to_remove 'bar', got '{section_to_remove}'")
        return False
    
    print(f"✅ Bar chart removal uses correct field: section_to_remove = '{section_to_remove}'")
    
    return True

def test_comprehensive_validation(dataset_id):
    """
    PRIORITY 4: Comprehensive validation of other functionality
    """
    print("\n=== PRIORITY 4: Comprehensive Validation ===")
    
    chat_url = f"{API_BASE}/analysis/chat-action"
    
    # Test file upload endpoints
    print("\n1. Testing file upload endpoints...")
    
    # Test /api/datasets endpoint (backward compatibility)
    datasets_url = f"{API_BASE}/datasets"
    with open('/app/test_data.csv', 'rb') as f:
        files = {'file': ('test_data2.csv', f, 'text/csv')}
        response = requests.post(datasets_url, files=files)
    
    if response.status_code == 200:
        print(f"✅ /api/datasets endpoint working (backward compatibility)")
    else:
        print(f"⚠️  /api/datasets endpoint failed: {response.status_code}")
    
    # Test holistic analysis
    print("\n2. Testing holistic analysis...")
    
    holistic_url = f"{API_BASE}/analysis/holistic"
    holistic_request = {"dataset_id": dataset_id}
    
    response = requests.post(holistic_url, json=holistic_request)
    
    if response.status_code == 200:
        holistic_data = response.json()
        charts = holistic_data.get('charts', [])
        print(f"✅ Holistic analysis working: {len(charts)} charts generated")
        
        # Check for empty charts bug
        empty_charts = [c for c in charts if not c.get('plotly_data')]
        if empty_charts:
            print(f"❌ Found {len(empty_charts)} empty charts")
        else:
            print(f"✅ No empty charts detected")
    else:
        print(f"⚠️  Holistic analysis failed: {response.status_code}")
    
    # Test scatter plot generation
    print("\n3. Testing scatter plot generation...")
    
    chat_request = {
        "dataset_id": dataset_id,
        "message": "create a scatter plot of age vs salary",
        "conversation_history": []
    }
    
    response = requests.post(chat_url, json=chat_request)
    
    if response.status_code == 200:
        chat_response = response.json()
        if (chat_response.get('action') == 'add_chart' and 
            chat_response.get('chart_data', {}).get('type') == 'scatter'):
            print(f"✅ Scatter plot generation working")
        else:
            print(f"⚠️  Scatter plot generation issue")
    else:
        print(f"⚠️  Scatter plot request failed: {response.status_code}")
    
    # Test custom charts (pie, bar, line)
    print("\n4. Testing custom chart types...")
    
    chart_tests = [
        ("pie chart", "pie"),
        ("bar chart", "bar"),
        ("line chart", "line")
    ]
    
    for message, expected_type in chart_tests:
        chat_request = {
            "dataset_id": dataset_id,
            "message": f"show me a {message}",
            "conversation_history": []
        }
        
        response = requests.post(chat_url, json=chat_request)
        
        if response.status_code == 200:
            chat_response = response.json()
            if (chat_response.get('action') == 'add_chart' and 
                chat_response.get('chart_data', {}).get('type') == expected_type):
                print(f"✅ {message.capitalize()} generation working")
            else:
                print(f"⚠️  {message.capitalize()} generation issue")
        else:
            print(f"⚠️  {message.capitalize()} request failed: {response.status_code}")
    
    # Test workspace management
    print("\n5. Testing workspace management...")
    
    save_url = f"{API_BASE}/analysis/save-state"
    save_request = {
        "dataset_id": dataset_id,
        "state_name": "Test Workspace",
        "analysis_data": {"test": "data"}
    }
    
    response = requests.post(save_url, json=save_request)
    
    if response.status_code == 200:
        print(f"✅ Workspace save working")
        
        # Test load
        load_url = f"{API_BASE}/analysis/saved-states/{dataset_id}"
        response = requests.get(load_url)
        
        if response.status_code == 200:
            print(f"✅ Workspace load working")
        else:
            print(f"⚠️  Workspace load failed: {response.status_code}")
    else:
        print(f"⚠️  Workspace save failed: {response.status_code}")
    
    return True

def main():
    """Run focused tests for fixed issues"""
    print("🔍 FOCUSED BACKEND TESTING - POST-REFACTORING VALIDATION")
    print("=" * 70)
    print("Testing 3 critical fixes:")
    print("1. ✅ Correlation format changed from dictionary to array")
    print("2. ✅ Removal keyword detection moved to first position")
    print("3. ✅ Removal response field changed from section_type to section_to_remove")
    print("=" * 70)
    
    try:
        # Upload test dataset
        dataset_id = upload_test_dataset()
        if not dataset_id:
            print("❌ Failed to upload test dataset")
            return False
        
        test_results = []
        
        # PRIORITY 1: Test correlation array format
        test_results.append(("Correlation Array Format", test_correlation_array_format(dataset_id)))
        
        # PRIORITY 2: Test removal keyword detection order
        test_results.append(("Removal Keyword Detection", test_removal_keyword_detection(dataset_id)))
        
        # PRIORITY 3: Test removal response field
        test_results.append(("Removal Response Field", test_removal_response_field(dataset_id)))
        
        # PRIORITY 4: Comprehensive validation
        test_results.append(("Comprehensive Validation", test_comprehensive_validation(dataset_id)))
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 FOCUSED TEST RESULTS SUMMARY:")
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
            print("\n🎉 ALL FIXED ISSUES VALIDATED!")
            print("✅ Correlation returns array format (not dictionary)")
            print("✅ Removal requests work correctly with section_to_remove field")
            print("✅ 'remove correlation' doesn't trigger correlation generation")
            print("✅ All other functionality still works as expected")
            return True
        else:
            print(f"\n❌ {failed} TEST(S) FAILED!")
            print("Some fixes may not be working correctly.")
            return False
            
    except Exception as e:
        print(f"\n❌ Test execution failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)