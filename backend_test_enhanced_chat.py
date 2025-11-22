#!/usr/bin/env python3
"""
Enhanced Chat Assistant Testing - Chart Creation Focus
Tests the comprehensive fix for chart creation with Azure OpenAI and fallback pattern matching
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any, List

# Backend URL
BACKEND_URL = "https://oracle-ml-hub.preview.emergentagent.com/api"

# Test dataset ID (Application Latency dataset from MongoDB)
DATASET_ID = "7fc830da-886f-4745-ac6d-ddee8c20af8a"

# Real column names from the dataset
COLUMNS = {
    'numeric': ['latency_ms', 'cpu_utilization', 'memory_usage_mb', 'payload_size_kb', 
                'active_connections', 'request_rate', 'error_rate'],
    'categorical': ['service_name', 'endpoint', 'status_code']
}


class TestResults:
    """Track test results"""
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.results = []
    
    def add_result(self, test_name: str, passed: bool, details: str = ""):
        self.total += 1
        if passed:
            self.passed += 1
            status = "✅ PASS"
        else:
            self.failed += 1
            status = "❌ FAIL"
        
        self.results.append({
            'test': test_name,
            'status': status,
            'passed': passed,
            'details': details
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"   {details}")
    
    def print_summary(self):
        print("\n" + "="*70)
        print("📊 TEST SUMMARY")
        print("="*70)
        print(f"Total Tests: {self.total}")
        print(f"Passed: {self.passed} ({(self.passed/self.total*100):.1f}%)")
        print(f"Failed: {self.failed} ({(self.failed/self.total*100):.1f}%)")
        print("="*70)
        
        if self.failed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.results:
                if not result['passed']:
                    print(f"  • {result['test']}")
                    if result['details']:
                        print(f"    {result['details']}")


def send_chat_message(message: str, dataset_id: str = DATASET_ID) -> Dict[str, Any]:
    """Send a chat message to the enhanced chat endpoint"""
    try:
        payload = {
            "message": message,
            "dataset_id": dataset_id
        }
        
        response = requests.post(
            f"{BACKEND_URL}/analysis/chat-action",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result is None:
                return {'error': True, 'message': 'Empty response from server'}
            return result
        else:
            return {
                'error': True,
                'status_code': response.status_code,
                'message': response.text
            }
    except Exception as e:
        return {
            'error': True,
            'message': str(e)
        }


def test_chart_creation_scatter(results: TestResults):
    """Test 1: Scatter Plot Creation"""
    print("\n=== Test 1: Scatter Plot Creation ===")
    
    message = f"create a scatter plot of {COLUMNS['numeric'][0]} vs {COLUMNS['numeric'][1]}"
    response = send_chat_message(message)
    
    if response.get('error'):
        results.add_result("Scatter Plot", False, f"Error: {response.get('message', 'Unknown error')}")
        return
    
    # Check for chart action
    action = response.get('action')
    data = response.get('data', {})
    response_text = response.get('response', '')
    
    if action == 'chart' and data and 'data' in data and 'layout' in data:
        results.add_result("Scatter Plot", True, "Chart created successfully with Plotly format")
    elif 'chart' in response_text.lower() and 'created' in response_text.lower():
        results.add_result("Scatter Plot", True, "Chart creation confirmed in response")
    else:
        results.add_result("Scatter Plot", False, f"Action: {action}, Response: {response_text[:100]}")


def test_chart_creation_line(results: TestResults):
    """Test 2: Line Chart Creation"""
    print("\n=== Test 2: Line Chart Creation ===")
    
    message = f"show line chart for {COLUMNS['numeric'][2]} over {COLUMNS['numeric'][3]}"
    response = send_chat_message(message)
    
    if response.get('error'):
        results.add_result("Line Chart", False, f"Error: {response.get('message', 'Unknown error')}")
        return
    
    action = response.get('action')
    data = response.get('data', {})
    response_text = response.get('response', '')
    
    if action == 'chart' and data and 'data' in data and 'layout' in data:
        results.add_result("Line Chart", True, "Chart created successfully")
    elif 'chart' in response_text.lower() and 'created' in response_text.lower():
        results.add_result("Line Chart", True, "Chart creation confirmed")
    else:
        results.add_result("Line Chart", False, f"Action: {action}, Response: {response_text[:100]}")


def test_chart_creation_bar(results: TestResults):
    """Test 3: Bar Chart Creation"""
    print("\n=== Test 3: Bar Chart Creation ===")
    
    message = f"create bar chart for {COLUMNS['numeric'][4]}"
    response = send_chat_message(message)
    
    if response.get('error'):
        results.add_result("Bar Chart", False, f"Error: {response.get('message', 'Unknown error')}")
        return
    
    action = response.get('action')
    data = response.get('data', {})
    response_text = response.get('response', '')
    
    if action == 'chart' and data and 'data' in data and 'layout' in data:
        results.add_result("Bar Chart", True, "Chart created successfully")
    elif 'chart' in response_text.lower() and 'created' in response_text.lower():
        results.add_result("Bar Chart", True, "Chart creation confirmed")
    else:
        results.add_result("Bar Chart", False, f"Action: {action}, Response: {response_text[:100]}")


def test_chart_creation_histogram(results: TestResults):
    """Test 4: Histogram Creation"""
    print("\n=== Test 4: Histogram Creation ===")
    
    message = f"show histogram of {COLUMNS['numeric'][5]}"
    response = send_chat_message(message)
    
    if response.get('error'):
        results.add_result("Histogram", False, f"Error: {response.get('message', 'Unknown error')}")
        return
    
    action = response.get('action')
    data = response.get('data', {})
    response_text = response.get('response', '')
    
    if action == 'chart' and data and 'data' in data and 'layout' in data:
        results.add_result("Histogram", True, "Chart created successfully")
    elif 'chart' in response_text.lower() and 'created' in response_text.lower():
        results.add_result("Histogram", True, "Chart creation confirmed")
    else:
        results.add_result("Histogram", False, f"Action: {action}, Response: {response_text[:100]}")


def test_chart_creation_box(results: TestResults):
    """Test 5: Box Plot Creation"""
    print("\n=== Test 5: Box Plot Creation ===")
    
    message = f"create box plot for {COLUMNS['numeric'][6]}"
    response = send_chat_message(message)
    
    if response.get('error'):
        results.add_result("Box Plot", False, f"Error: {response.get('message', 'Unknown error')}")
        return
    
    action = response.get('action')
    data = response.get('data', {})
    response_text = response.get('response', '')
    
    if action == 'chart' and data and 'data' in data and 'layout' in data:
        results.add_result("Box Plot", True, "Chart created successfully")
    elif 'chart' in response_text.lower() and 'created' in response_text.lower():
        results.add_result("Box Plot", True, "Chart creation confirmed")
    else:
        results.add_result("Box Plot", False, f"Action: {action}, Response: {response_text[:100]}")


def test_invalid_columns(results: TestResults):
    """Test 6: Invalid Column Handling"""
    print("\n=== Test 6: Invalid Column Handling ===")
    
    message = "plot nonexistent_col1 vs nonexistent_col2"
    response = send_chat_message(message)
    
    if response.get('error'):
        results.add_result("Invalid Columns", False, f"Error: {response.get('message', 'Unknown error')}")
        return
    
    response_text = response.get('response', '')
    data = response.get('data', {})
    
    # Should show error message with available columns
    if 'not found' in response_text.lower() or 'available columns' in response_text.lower():
        if 'available_columns' in data or any(col in response_text for col in COLUMNS['numeric'][:3]):
            results.add_result("Invalid Columns", True, "Shows available columns")
        else:
            results.add_result("Invalid Columns", True, "Shows error message")
    else:
        results.add_result("Invalid Columns", False, f"Response: {response_text[:100]}")


def test_natural_language_variations(results: TestResults):
    """Test 7: Natural Language Variations"""
    print("\n=== Test 7: Natural Language Variations ===")
    
    variations = [
        f"plot {COLUMNS['numeric'][0]} against {COLUMNS['numeric'][1]}",
        f"visualize distribution of {COLUMNS['numeric'][2]}",
        f"show relationship between {COLUMNS['numeric'][3]} and {COLUMNS['numeric'][4]}",
        f"draw chart for {COLUMNS['numeric'][5]}"
    ]
    
    passed_count = 0
    for i, message in enumerate(variations, 1):
        response = send_chat_message(message)
        
        if response.get('error'):
            print(f"  Variation {i}: ❌ Error")
            continue
        
        action = response.get('action')
        response_text = response.get('response', '')
        
        if action == 'chart' or ('chart' in response_text.lower() and 'created' in response_text.lower()):
            print(f"  Variation {i}: ✅ Understood")
            passed_count += 1
        else:
            print(f"  Variation {i}: ❌ Not understood")
    
    if passed_count >= 3:
        results.add_result("Natural Language Variations", True, f"{passed_count}/4 variations worked")
    else:
        results.add_result("Natural Language Variations", False, f"Only {passed_count}/4 variations worked")


def test_dataset_awareness(results: TestResults):
    """Test 8: Dataset Awareness (Quick)"""
    print("\n=== Test 8: Dataset Awareness ===")
    
    message = "what columns are available?"
    response = send_chat_message(message)
    
    if response.get('error'):
        results.add_result("Dataset Awareness", False, f"Error: {response.get('message')}")
        return
    
    response_text = response.get('response', '')
    
    # Check if response contains actual column names
    if any(col in response_text for col in COLUMNS['numeric'][:3]):
        results.add_result("Dataset Awareness", True, "Lists actual columns")
    else:
        results.add_result("Dataset Awareness", False, "Doesn't list columns")


def test_statistics_request(results: TestResults):
    """Test 9: Statistics Request (Quick)"""
    print("\n=== Test 9: Statistics Request ===")
    
    message = f"show statistics for {COLUMNS['numeric'][0]}"
    response = send_chat_message(message)
    
    if response.get('error'):
        results.add_result("Statistics", False, f"Error: {response.get('message')}")
        return
    
    response_text = response.get('response', '')
    
    # Check for statistical keywords
    if any(keyword in response_text.lower() for keyword in ['mean', 'std', 'min', 'max', 'median']):
        results.add_result("Statistics", True, "Provides statistics")
    else:
        results.add_result("Statistics", False, "No statistics provided")


def test_missing_values(results: TestResults):
    """Test 10: Missing Values Check (Quick)"""
    print("\n=== Test 10: Missing Values Check ===")
    
    message = "check for missing values"
    response = send_chat_message(message)
    
    if response.get('error'):
        results.add_result("Missing Values", False, f"Error: {response.get('message')}")
        return
    
    response_text = response.get('response', '')
    
    # Check for missing value keywords
    if any(keyword in response_text.lower() for keyword in ['missing', 'null', 'complete', 'no missing']):
        results.add_result("Missing Values", True, "Analyzes missing values")
    else:
        results.add_result("Missing Values", False, "No missing value analysis")


def test_correlation_analysis(results: TestResults):
    """Test 11: Correlation Analysis (Quick)"""
    print("\n=== Test 11: Correlation Analysis ===")
    
    message = f"show correlation with {COLUMNS['numeric'][0]}"
    response = send_chat_message(message)
    
    if response.get('error'):
        results.add_result("Correlation", False, f"Error: {response.get('message')}")
        return
    
    response_text = response.get('response', '')
    
    # Check for correlation keywords
    if 'correlation' in response_text.lower() or any(col in response_text for col in COLUMNS['numeric'][1:4]):
        results.add_result("Correlation", True, "Shows correlations")
    else:
        results.add_result("Correlation", False, "No correlation analysis")


def test_error_handling(results: TestResults):
    """Test 12: Error Handling (Quick)"""
    print("\n=== Test 12: Error Handling ===")
    
    # Test with invalid dataset ID
    message = "show me the data"
    response = send_chat_message(message, dataset_id="invalid-id-12345")
    
    if response.get('error') or response.get('status_code') in [400, 404, 500]:
        results.add_result("Error Handling", True, "Handles invalid dataset gracefully")
    else:
        # Check if response indicates error
        response_text = response.get('response', '')
        if 'error' in response_text.lower() or 'not found' in response_text.lower():
            results.add_result("Error Handling", True, "Returns error message")
        else:
            results.add_result("Error Handling", False, "No error handling detected")


def test_performance(results: TestResults):
    """Test 13: Performance Check"""
    print("\n=== Test 13: Performance Check ===")
    
    import time
    
    message = f"create scatter plot of {COLUMNS['numeric'][0]} vs {COLUMNS['numeric'][1]}"
    
    start_time = time.time()
    response = send_chat_message(message)
    end_time = time.time()
    
    response_time = (end_time - start_time) * 1000  # ms
    
    print(f"   Response time: {response_time:.0f}ms")
    
    if response.get('error'):
        results.add_result("Performance", False, f"Error: {response.get('message')}")
        return
    
    # Should respond within 5 seconds
    if response_time < 5000:
        results.add_result("Performance", True, f"Response time: {response_time:.0f}ms")
    else:
        results.add_result("Performance", False, f"Too slow: {response_time:.0f}ms")


def main():
    """Run all tests"""
    print("🚀 ENHANCED CHAT ASSISTANT TESTING - CHART CREATION FOCUS")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Dataset ID: {DATASET_ID}")
    print(f"Test Time: {datetime.now().isoformat()}")
    print("="*70)
    
    results = TestResults()
    
    # PRIMARY FOCUS: Chart Creation (7 tests)
    print("\n" + "="*70)
    print("📊 PRIMARY FOCUS: CHART CREATION & MANIPULATION")
    print("="*70)
    
    test_chart_creation_scatter(results)
    test_chart_creation_line(results)
    test_chart_creation_bar(results)
    test_chart_creation_histogram(results)
    test_chart_creation_box(results)
    test_invalid_columns(results)
    test_natural_language_variations(results)
    
    # SECONDARY: Quick validation of other features (5 tests)
    print("\n" + "="*70)
    print("🔍 SECONDARY: OTHER FEATURES VALIDATION")
    print("="*70)
    
    test_dataset_awareness(results)
    test_statistics_request(results)
    test_missing_values(results)
    test_correlation_analysis(results)
    test_error_handling(results)
    
    # Performance test
    print("\n" + "="*70)
    print("⚡ PERFORMANCE TEST")
    print("="*70)
    
    test_performance(results)
    
    # Print summary
    results.print_summary()
    
    # Success criteria
    chart_tests = 7
    chart_passed = sum(1 for r in results.results[:7] if r['passed'])
    chart_success_rate = (chart_passed / chart_tests) * 100
    
    print("\n" + "="*70)
    print("🎯 SUCCESS CRITERIA EVALUATION")
    print("="*70)
    print(f"Chart Creation: {chart_passed}/{chart_tests} ({chart_success_rate:.0f}%)")
    print(f"Overall: {results.passed}/{results.total} ({(results.passed/results.total*100):.0f}%)")
    
    if chart_success_rate >= 85:
        print("\n✅ SUCCESS: Chart creation meets 85%+ success rate requirement")
        print("✅ System is production ready for chart creation")
    else:
        print(f"\n❌ FAILURE: Chart creation only {chart_success_rate:.0f}% (need 85%+)")
        print("❌ System needs more work on chart creation")
    
    return chart_success_rate >= 85


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
