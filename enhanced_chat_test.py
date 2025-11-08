#!/usr/bin/env python3
"""
Enhanced Chat Testing - Final Verification
Tests all 7 scenarios for the enhanced-chat endpoint with fixes applied
"""
import requests
import json
import sys
from datetime import datetime

# Backend URL
BACKEND_URL = "https://ai-insight-hub-4.preview.emergentagent.com/api"

# Test dataset ID (from Oracle/MongoDB)
DATASET_ID = "7fc830da-886f-4745-ac6d-ddee8c20af8a"  # application_latency_3.csv

def print_test_header(test_num, test_name):
    """Print formatted test header"""
    print(f"\n{'='*70}")
    print(f"TEST {test_num}: {test_name}")
    print(f"{'='*70}")

def send_chat_message(message, dataset_id=DATASET_ID):
    """Send a message to enhanced-chat endpoint"""
    try:
        payload = {
            "message": message,
            "dataset_id": dataset_id,
            "conversation_history": []
        }
        
        response = requests.post(
            f"{BACKEND_URL}/enhanced-chat/message",
            json=payload,
            timeout=30
        )
        
        return response.status_code, response.json() if response.status_code == 200 else response.text
    except Exception as e:
        return None, str(e)

def test_1_model_interaction_no_models():
    """
    Fix 1 Test 1: "what am i predicting?" with no models trained
    Expected: Should return "No models have been trained yet" message
    """
    print_test_header(1, "Model Interaction - No Models Trained")
    
    message = "what am i predicting?"
    print(f"Message: '{message}'")
    
    status, response = send_chat_message(message)
    
    if status == 200:
        response_text = response.get('response', '')
        action = response.get('action', '')
        
        print(f"\nStatus: {status}")
        print(f"Action: {action}")
        print(f"Response: {response_text[:200]}...")
        
        # Check for expected keywords
        keywords_found = []
        expected_keywords = ['no models', 'not trained', 'train', 'predictive analysis']
        
        for keyword in expected_keywords:
            if keyword.lower() in response_text.lower():
                keywords_found.append(keyword)
        
        print(f"\nExpected keywords found: {keywords_found}")
        
        # Success criteria
        if 'no models' in response_text.lower() or 'not trained' in response_text.lower():
            print("✅ PASS: Correctly indicates no models trained")
            return True
        else:
            print("❌ FAIL: Does not clearly indicate no models trained")
            return False
    else:
        print(f"❌ FAIL: Request failed with status {status}")
        print(f"Error: {response}")
        return False

def test_2_model_metrics_no_models():
    """
    Fix 1 Test 2: "show model metrics" with no models trained
    Expected: Should return clear guidance about training models
    """
    print_test_header(2, "Model Metrics - No Models Trained")
    
    message = "show model metrics"
    print(f"Message: '{message}'")
    
    status, response = send_chat_message(message)
    
    if status == 200:
        response_text = response.get('response', '')
        action = response.get('action', '')
        suggestions = response.get('suggestions', [])
        
        print(f"\nStatus: {status}")
        print(f"Action: {action}")
        print(f"Response: {response_text[:200]}...")
        print(f"Suggestions: {suggestions}")
        
        # Check for guidance keywords
        guidance_keywords = ['train', 'predictive analysis', 'select', 'run analysis', 'models']
        keywords_found = [kw for kw in guidance_keywords if kw.lower() in response_text.lower()]
        
        print(f"\nGuidance keywords found: {keywords_found}")
        
        # Success criteria
        if ('no models' in response_text.lower() or 'not trained' in response_text.lower()) and len(keywords_found) >= 2:
            print("✅ PASS: Provides clear guidance about training models")
            return True
        else:
            print("❌ FAIL: Does not provide clear guidance")
            return False
    else:
        print(f"❌ FAIL: Request failed with status {status}")
        return False

def test_3_chart_nonexistent_column():
    """
    Fix 2 Test 1: "create chart for nonexistent_column_xyz"
    Expected: Should return error with available columns
    """
    print_test_header(3, "Chart Creation - Nonexistent Column")
    
    message = "create chart for nonexistent_column_xyz"
    print(f"Message: '{message}'")
    
    status, response = send_chat_message(message)
    
    if status == 200:
        response_text = response.get('response', '')
        action = response.get('action', '')
        data = response.get('data', {})
        
        print(f"\nStatus: {status}")
        print(f"Action: {action}")
        print(f"Response: {response_text[:300]}...")
        
        # Check for error indication and available columns
        has_error = 'not found' in response_text.lower() or 'column' in response_text.lower()
        has_available_columns = 'available columns' in response_text.lower() or 'available_columns' in data
        
        print(f"\nHas error indication: {has_error}")
        print(f"Shows available columns: {has_available_columns}")
        
        if 'available_columns' in data:
            print(f"Available columns count: {len(data['available_columns'])}")
        
        # Success criteria
        if has_error and has_available_columns:
            print("✅ PASS: Returns error with available columns")
            return True
        else:
            print("❌ FAIL: Does not properly show error or available columns")
            return False
    else:
        print(f"❌ FAIL: Request failed with status {status}")
        return False

def test_4_statistics_invalid_column():
    """
    Fix 2 Test 2: "show statistics for invalid_col_999"
    Expected: General stats OR error (both OK)
    """
    print_test_header(4, "Statistics - Invalid Column")
    
    message = "show statistics for invalid_col_999"
    print(f"Message: '{message}'")
    
    status, response = send_chat_message(message)
    
    if status == 200:
        response_text = response.get('response', '')
        action = response.get('action', '')
        
        print(f"\nStatus: {status}")
        print(f"Action: {action}")
        print(f"Response: {response_text[:300]}...")
        
        # Both general stats or error are acceptable
        has_general_stats = 'statistics' in response_text.lower() or 'mean' in response_text.lower()
        has_error = 'not found' in response_text.lower() or 'invalid' in response_text.lower()
        
        print(f"\nShows general statistics: {has_general_stats}")
        print(f"Shows error: {has_error}")
        
        # Success criteria: Either general stats OR error message
        if has_general_stats or has_error:
            print("✅ PASS: Returns general stats or error (both acceptable)")
            return True
        else:
            print("❌ FAIL: No meaningful response")
            return False
    else:
        print(f"❌ FAIL: Request failed with status {status}")
        return False

def test_5_create_scatter_plot():
    """
    No Regression Test 1: "create a scatter plot"
    Expected: Should work with confirmation
    """
    print_test_header(5, "No Regression - Create Scatter Plot")
    
    message = "create a scatter plot"
    print(f"Message: '{message}'")
    
    status, response = send_chat_message(message)
    
    if status == 200:
        response_text = response.get('response', '')
        action = response.get('action', '')
        requires_confirmation = response.get('requires_confirmation', False)
        data = response.get('data', {})
        
        print(f"\nStatus: {status}")
        print(f"Action: {action}")
        print(f"Requires confirmation: {requires_confirmation}")
        print(f"Response: {response_text[:200]}...")
        
        # Check if chart was created
        has_chart_data = bool(data) and ('data' in data or 'layout' in data)
        is_chart_action = action == 'chart'
        
        print(f"\nHas chart data: {has_chart_data}")
        print(f"Is chart action: {is_chart_action}")
        
        # Success criteria
        if is_chart_action or has_chart_data or 'created' in response_text.lower():
            print("✅ PASS: Scatter plot creation works")
            return True
        else:
            print("❌ FAIL: Scatter plot creation failed")
            return False
    else:
        print(f"❌ FAIL: Request failed with status {status}")
        return False

def test_6_show_columns():
    """
    No Regression Test 2: "show columns"
    Expected: Should list columns
    """
    print_test_header(6, "No Regression - Show Columns")
    
    message = "show columns"
    print(f"Message: '{message}'")
    
    status, response = send_chat_message(message)
    
    if status == 200:
        response_text = response.get('response', '')
        action = response.get('action', '')
        data = response.get('data', {})
        
        print(f"\nStatus: {status}")
        print(f"Action: {action}")
        print(f"Response: {response_text[:300]}...")
        
        # Check if columns are listed
        has_columns_in_response = 'columns' in response_text.lower()
        has_columns_in_data = 'columns' in data
        
        print(f"\nColumns in response text: {has_columns_in_response}")
        print(f"Columns in data: {has_columns_in_data}")
        
        if has_columns_in_data:
            print(f"Columns count: {len(data.get('columns', []))}")
        
        # Success criteria
        if has_columns_in_response or has_columns_in_data:
            print("✅ PASS: Columns are listed")
            return True
        else:
            print("❌ FAIL: Columns not listed")
            return False
    else:
        print(f"❌ FAIL: Request failed with status {status}")
        return False

def test_7_short_query_columns():
    """
    No Regression Test 3: "columns" (short query)
    Expected: Should work
    """
    print_test_header(7, "No Regression - Short Query 'columns'")
    
    message = "columns"
    print(f"Message: '{message}'")
    
    status, response = send_chat_message(message)
    
    if status == 200:
        response_text = response.get('response', '')
        action = response.get('action', '')
        data = response.get('data', {})
        
        print(f"\nStatus: {status}")
        print(f"Action: {action}")
        print(f"Response: {response_text[:300]}...")
        
        # Check if columns are listed
        has_columns_in_response = 'columns' in response_text.lower() or 'column' in response_text.lower()
        has_columns_in_data = 'columns' in data
        
        print(f"\nColumns in response text: {has_columns_in_response}")
        print(f"Columns in data: {has_columns_in_data}")
        
        # Success criteria
        if has_columns_in_response or has_columns_in_data:
            print("✅ PASS: Short query works")
            return True
        else:
            print("❌ FAIL: Short query failed")
            return False
    else:
        print(f"❌ FAIL: Request failed with status {status}")
        return False

def main():
    """Run all 7 test scenarios"""
    print("🚀 ENHANCED CHAT TESTING - FINAL VERIFICATION")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Dataset ID: {DATASET_ID}")
    print(f"Test Time: {datetime.now().isoformat()}")
    print("="*70)
    
    # Track results
    results = {}
    
    # Run all tests
    print("\n📋 RUNNING ALL 7 TEST SCENARIOS...")
    
    results['test_1_no_models_predicting'] = test_1_model_interaction_no_models()
    results['test_2_no_models_metrics'] = test_2_model_metrics_no_models()
    results['test_3_nonexistent_column'] = test_3_chart_nonexistent_column()
    results['test_4_invalid_column_stats'] = test_4_statistics_invalid_column()
    results['test_5_scatter_plot'] = test_5_create_scatter_plot()
    results['test_6_show_columns'] = test_6_show_columns()
    results['test_7_short_query'] = test_7_short_query_columns()
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    success_rate = (passed / total) * 100
    
    print(f"\n✅ Passed: {passed}/{total} ({success_rate:.1f}%)")
    print(f"❌ Failed: {total - passed}/{total}")
    
    print("\n📋 DETAILED RESULTS:")
    print("-" * 70)
    
    test_names = {
        'test_1_no_models_predicting': 'Fix 1.1: "what am i predicting?" (no models)',
        'test_2_no_models_metrics': 'Fix 1.2: "show model metrics" (no models)',
        'test_3_nonexistent_column': 'Fix 2.1: Chart with nonexistent column',
        'test_4_invalid_column_stats': 'Fix 2.2: Stats for invalid column',
        'test_5_scatter_plot': 'No Regression 1: Create scatter plot',
        'test_6_show_columns': 'No Regression 2: Show columns',
        'test_7_short_query': 'No Regression 3: Short query "columns"'
    }
    
    for test_key, test_name in test_names.items():
        status = "✅ PASS" if results[test_key] else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    # Final verdict
    print("\n" + "="*70)
    if passed == total:
        print("🎉 ALL TESTS PASSED - PRODUCTION READY")
        print("="*70)
        return True
    else:
        print(f"⚠️  {total - passed} TEST(S) FAILED - NEEDS ATTENTION")
        print("="*70)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
