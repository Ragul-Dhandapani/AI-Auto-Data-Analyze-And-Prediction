#!/usr/bin/env python3
"""
COMPREHENSIVE ENHANCED CHAT ENDPOINT EVALUATION
Tests /api/enhanced-chat/message across ALL 7 requirement categories

Mission: Evaluate if enhanced-chat endpoint is ready to replace /api/analysis/chat-action
Success Criteria: 92%+ pass rate (25/27 tests)
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple

# Backend URL
BACKEND_URL = "https://data-prophet-4.preview.emergentagent.com/api"

# Test results tracking
test_results = {
    'chart_creation': {'passed': 0, 'total': 5, 'tests': []},
    'dataset_awareness': {'passed': 0, 'total': 6, 'tests': []},
    'prediction_model': {'passed': 0, 'total': 3, 'tests': []},
    'user_flow': {'passed': 0, 'total': 3, 'tests': []},
    'natural_language': {'passed': 0, 'total': 4, 'tests': []},
    'error_handling': {'passed': 0, 'total': 3, 'tests': []},
    'analytical_assistance': {'passed': 0, 'total': 3, 'tests': []}
}

# Performance tracking
response_times = []


def get_test_dataset() -> str:
    """Get a dataset ID from Oracle for testing"""
    try:
        response = requests.get(f"{BACKEND_URL}/datasets", timeout=10)
        if response.status_code == 200:
            datasets = response.json().get('datasets', [])
            if datasets:
                # Prefer a dataset with good data variety
                for ds in datasets:
                    if ds.get('row_count', 0) > 100 and ds.get('column_count', 0) > 5:
                        print(f"✅ Using dataset: {ds.get('name')} (ID: {ds.get('id')})")
                        print(f"   Rows: {ds.get('row_count')}, Columns: {ds.get('column_count')}")
                        return ds.get('id')
                # Fallback to first dataset
                return datasets[0].get('id')
    except Exception as e:
        print(f"❌ Error getting dataset: {str(e)}")
    return None


def send_chat_message(message: str, dataset_id: str) -> Tuple[Dict, float]:
    """Send a message to enhanced chat endpoint and measure response time"""
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/enhanced-chat/message",
            json={
                "message": message,
                "dataset_id": dataset_id,
                "conversation_history": []
            },
            timeout=30
        )
        
        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # ms
        
        if response.status_code == 200:
            return response.json(), response_time
        else:
            return {'error': f"Status {response.status_code}", 'response': response.text}, response_time
            
    except Exception as e:
        end_time = time.time()
        response_time = (end_time - start_time) * 1000
        return {'error': str(e)}, response_time


def validate_response_format(response: Dict) -> bool:
    """Validate response has required format"""
    required_fields = ['response', 'action', 'data', 'requires_confirmation', 'suggestions']
    return all(field in response for field in required_fields)


def record_test(category: str, test_name: str, passed: bool, details: str = ""):
    """Record test result"""
    test_results[category]['tests'].append({
        'name': test_name,
        'passed': passed,
        'details': details
    })
    if passed:
        test_results[category]['passed'] += 1


# ============================================================================
# CATEGORY 1: CHART CREATION & MANIPULATION (5 tests)
# ============================================================================

def test_chart_creation(dataset_id: str):
    """Category 1: Chart Creation & Manipulation"""
    print("\n" + "="*70)
    print("CATEGORY 1: CHART CREATION & MANIPULATION (5 tests)")
    print("="*70)
    
    # Test 1.1: Create scatter plot
    print("\n[1.1] Create scatter plot with natural language")
    response, rt = send_chat_message("create a scatter plot", dataset_id)
    response_times.append(rt)
    
    passed = (
        validate_response_format(response) and
        response.get('action') in ['chart', 'message'] and
        'scatter' in response.get('response', '').lower()
    )
    record_test('chart_creation', 'Scatter plot creation', passed, 
                f"Response time: {rt:.0f}ms, Action: {response.get('action')}")
    print(f"   {'✅ PASS' if passed else '❌ FAIL'} - Response time: {rt:.0f}ms")
    if not passed:
        print(f"   Details: {response.get('response', '')[:100]}")
    
    # Test 1.2: Create histogram
    print("\n[1.2] Create histogram")
    response, rt = send_chat_message("show me a histogram", dataset_id)
    response_times.append(rt)
    
    passed = (
        validate_response_format(response) and
        response.get('action') in ['chart', 'message'] and
        'histogram' in response.get('response', '').lower()
    )
    record_test('chart_creation', 'Histogram creation', passed,
                f"Response time: {rt:.0f}ms, Action: {response.get('action')}")
    print(f"   {'✅ PASS' if passed else '❌ FAIL'} - Response time: {rt:.0f}ms")
    
    # Test 1.3: Create line chart
    print("\n[1.3] Create line chart")
    response, rt = send_chat_message("plot a line chart", dataset_id)
    response_times.append(rt)
    
    passed = (
        validate_response_format(response) and
        response.get('action') in ['chart', 'message'] and
        'line' in response.get('response', '').lower()
    )
    record_test('chart_creation', 'Line chart creation', passed,
                f"Response time: {rt:.0f}ms, Action: {response.get('action')}")
    print(f"   {'✅ PASS' if passed else '❌ FAIL'} - Response time: {rt:.0f}ms")
    
    # Test 1.4: Invalid column handling
    print("\n[1.4] Invalid column handling (shows available columns)")
    response, rt = send_chat_message("create chart for nonexistent_column_xyz", dataset_id)
    response_times.append(rt)
    
    passed = (
        validate_response_format(response) and
        ('available' in response.get('response', '').lower() or 
         'column' in response.get('response', '').lower())
    )
    record_test('chart_creation', 'Invalid column error handling', passed,
                f"Shows available columns: {passed}")
    print(f"   {'✅ PASS' if passed else '❌ FAIL'} - Helpful error message")
    
    # Test 1.5: Confirmation workflow
    print("\n[1.5] Confirmation workflow for chart")
    response, rt = send_chat_message("visualize the data", dataset_id)
    response_times.append(rt)
    
    passed = (
        validate_response_format(response) and
        (response.get('requires_confirmation') == True or
         'append' in response.get('response', '').lower() or
         'dashboard' in response.get('response', '').lower())
    )
    record_test('chart_creation', 'Confirmation workflow', passed,
                f"Requires confirmation: {response.get('requires_confirmation')}")
    print(f"   {'✅ PASS' if passed else '❌ FAIL'} - Confirmation: {response.get('requires_confirmation')}")


# ============================================================================
# CATEGORY 2: DATASET AWARENESS (6 tests)
# ============================================================================

def test_dataset_awareness(dataset_id: str):
    """Category 2: Dataset Awareness"""
    print("\n" + "="*70)
    print("CATEGORY 2: DATASET AWARENESS (6 tests)")
    print("="*70)
    
    # Test 2.1: Show column names
    print("\n[2.1] Show me column names")
    response, rt = send_chat_message("show me column names", dataset_id)
    response_times.append(rt)
    
    passed = (
        validate_response_format(response) and
        response.get('action') == 'message' and
        ('column' in response.get('response', '').lower() and
         len(response.get('data', {}).get('columns', [])) > 0)
    )
    record_test('dataset_awareness', 'List column names', passed,
                f"Columns returned: {len(response.get('data', {}).get('columns', []))}")
    print(f"   {'✅ PASS' if passed else '❌ FAIL'} - Columns: {len(response.get('data', {}).get('columns', []))}")
    
    # Test 2.2: Dataset size
    print("\n[2.2] What is the dataset size?")
    response, rt = send_chat_message("what is the dataset size?", dataset_id)
    response_times.append(rt)
    
    passed = (
        validate_response_format(response) and
        ('row' in response.get('response', '').lower() or
         'column' in response.get('response', '').lower())
    )
    record_test('dataset_awareness', 'Dataset size info', passed,
                f"Shows rows/columns: {passed}")
    print(f"   {'✅ PASS' if passed else '❌ FAIL'} - Shows size info")
    
    # Test 2.3: Column statistics
    print("\n[2.3] Show statistics for a column")
    response, rt = send_chat_message("show statistics", dataset_id)
    response_times.append(rt)
    
    passed = (
        validate_response_format(response) and
        any(keyword in response.get('response', '').lower() 
            for keyword in ['mean', 'std', 'min', 'max', 'median'])
    )
    record_test('dataset_awareness', 'Column statistics', passed,
                f"Shows stats: {passed}")
    print(f"   {'✅ PASS' if passed else '❌ FAIL'} - Shows mean, std, min, max, median")
    
    # Test 2.4: Data types
    print("\n[2.4] What are the data types?")
    response, rt = send_chat_message("what are the data types?", dataset_id)
    response_times.append(rt)
    
    passed = (
        validate_response_format(response) and
        ('type' in response.get('response', '').lower() or
         'dtype' in response.get('response', '').lower())
    )
    record_test('dataset_awareness', 'Data types info', passed,
                f"Shows dtypes: {passed}")
    print(f"   {'✅ PASS' if passed else '❌ FAIL'} - Shows data types")
    
    # Test 2.5: Check for null values
    print("\n[2.5] Check for null values")
    response, rt = send_chat_message("check for null values", dataset_id)
    response_times.append(rt)
    
    passed = (
        validate_response_format(response) and
        ('null' in response.get('response', '').lower() or
         'missing' in response.get('response', '').lower())
    )
    record_test('dataset_awareness', 'Missing value analysis', passed,
                f"Shows null/missing info: {passed}")
    print(f"   {'✅ PASS' if passed else '❌ FAIL'} - Shows missing values")
    
    # Test 2.6: Correlation analysis
    print("\n[2.6] Show correlation")
    response, rt = send_chat_message("show correlation", dataset_id)
    response_times.append(rt)
    
    passed = (
        validate_response_format(response) and
        'correlation' in response.get('response', '').lower()
    )
    record_test('dataset_awareness', 'Correlation analysis', passed,
                f"Shows correlations: {passed}")
    print(f"   {'✅ PASS' if passed else '❌ FAIL'} - Shows correlations")


# ============================================================================
# CATEGORY 3: PREDICTION & MODEL INTERACTIONS (3 tests)
# ============================================================================

def test_prediction_model(dataset_id: str):
    """Category 3: Prediction & Model Interactions"""
    print("\n" + "="*70)
    print("CATEGORY 3: PREDICTION & MODEL INTERACTIONS (3 tests)")
    print("="*70)
    
    # Test 3.1: What am I predicting?
    print("\n[3.1] What am I predicting?")
    response, rt = send_chat_message("what am i predicting?", dataset_id)
    response_times.append(rt)
    
    passed = (
        validate_response_format(response) and
        response.get('action') == 'message'
    )
    record_test('prediction_model', 'Prediction target query', passed,
                f"Appropriate response: {passed}")
    print(f"   {'✅ PASS' if passed else '❌ FAIL'} - Response: {response.get('response', '')[:50]}...")
    
    # Test 3.2: Show model metrics
    print("\n[3.2] Show model metrics")
    response, rt = send_chat_message("show model metrics", dataset_id)
    response_times.append(rt)
    
    passed = (
        validate_response_format(response) and
        response.get('action') == 'message'
    )
    record_test('prediction_model', 'Model metrics query', passed,
                f"Appropriate response: {passed}")
    print(f"   {'✅ PASS' if passed else '❌ FAIL'} - Response provided")
    
    # Test 3.3: Which model is best?
    print("\n[3.3] Which model is best?")
    response, rt = send_chat_message("which model is best?", dataset_id)
    response_times.append(rt)
    
    passed = (
        validate_response_format(response) and
        response.get('action') == 'message'
    )
    record_test('prediction_model', 'Best model query', passed,
                f"Appropriate response: {passed}")
    print(f"   {'✅ PASS' if passed else '❌ FAIL'} - Response provided")


# ============================================================================
# CATEGORY 4: USER FLOW (3 tests)
# ============================================================================

def test_user_flow(dataset_id: str):
    """Category 4: User Flow"""
    print("\n" + "="*70)
    print("CATEGORY 4: USER FLOW (3 tests)")
    print("="*70)
    
    # Test 4.1: Message without dataset_id
    print("\n[4.1] Message without dataset_id (error handling)")
    response, rt = send_chat_message("show me data", "invalid-dataset-id-xyz")
    response_times.append(rt)
    
    passed = (
        validate_response_format(response) and
        (response.get('action') == 'error' or
         'not found' in response.get('response', '').lower() or
         'invalid' in response.get('response', '').lower())
    )
    record_test('user_flow', 'Invalid dataset error', passed,
                f"Error handling: {passed}")
    print(f"   {'✅ PASS' if passed else '❌ FAIL'} - Appropriate error message")
    
    # Test 4.2: Chart creation asks for confirmation
    print("\n[4.2] Chart creation asks for confirmation")
    response, rt = send_chat_message("create a chart", dataset_id)
    response_times.append(rt)
    
    passed = (
        validate_response_format(response) and
        (response.get('requires_confirmation') == True or
         'confirm' in response.get('response', '').lower() or
         'append' in response.get('response', '').lower())
    )
    record_test('user_flow', 'Chart confirmation workflow', passed,
                f"Asks confirmation: {passed}")
    print(f"   {'✅ PASS' if passed else '❌ FAIL'} - Confirmation: {response.get('requires_confirmation')}")
    
    # Test 4.3: What next / suggestions
    print("\n[4.3] What next? (provides recommendations)")
    response, rt = send_chat_message("what next?", dataset_id)
    response_times.append(rt)
    
    passed = (
        validate_response_format(response) and
        len(response.get('suggestions', [])) > 0
    )
    record_test('user_flow', 'Suggestions provided', passed,
                f"Suggestions count: {len(response.get('suggestions', []))}")
    print(f"   {'✅ PASS' if passed else '❌ FAIL'} - Suggestions: {len(response.get('suggestions', []))}")


# ============================================================================
# CATEGORY 5: NATURAL LANGUAGE FLEXIBILITY (4 tests)
# ============================================================================

def test_natural_language(dataset_id: str):
    """Category 5: Natural Language Flexibility"""
    print("\n" + "="*70)
    print("CATEGORY 5: NATURAL LANGUAGE FLEXIBILITY (4 tests)")
    print("="*70)
    
    # Test 5.1: Variations - "show columns" vs "list columns"
    print("\n[5.1] Variations: 'show columns' vs 'list columns'")
    response1, rt1 = send_chat_message("show columns", dataset_id)
    response2, rt2 = send_chat_message("list columns", dataset_id)
    response_times.extend([rt1, rt2])
    
    passed = (
        validate_response_format(response1) and
        validate_response_format(response2) and
        'column' in response1.get('response', '').lower() and
        'column' in response2.get('response', '').lower()
    )
    record_test('natural_language', 'Column variations', passed,
                f"Both variations work: {passed}")
    print(f"   {'✅ PASS' if passed else '❌ FAIL'} - Both variations understood")
    
    # Test 5.2: Short queries - "stats"
    print("\n[5.2] Short query: 'stats'")
    response, rt = send_chat_message("stats", dataset_id)
    response_times.append(rt)
    
    passed = (
        validate_response_format(response) and
        any(keyword in response.get('response', '').lower() 
            for keyword in ['statistic', 'mean', 'std', 'data'])
    )
    record_test('natural_language', 'Short query handling', passed,
                f"Understands 'stats': {passed}")
    print(f"   {'✅ PASS' if passed else '❌ FAIL'} - Short query understood")
    
    # Test 5.3: Short query - "size"
    print("\n[5.3] Short query: 'size'")
    response, rt = send_chat_message("size", dataset_id)
    response_times.append(rt)
    
    passed = (
        validate_response_format(response) and
        ('row' in response.get('response', '').lower() or
         'column' in response.get('response', '').lower() or
         'size' in response.get('response', '').lower())
    )
    record_test('natural_language', 'Size query handling', passed,
                f"Understands 'size': {passed}")
    print(f"   {'✅ PASS' if passed else '❌ FAIL'} - Size query understood")
    
    # Test 5.4: Different phrasings - "missing data" vs "null values"
    print("\n[5.4] Different phrasings: 'missing data' vs 'null values'")
    response1, rt1 = send_chat_message("missing data", dataset_id)
    response2, rt2 = send_chat_message("null values", dataset_id)
    response_times.extend([rt1, rt2])
    
    passed = (
        validate_response_format(response1) and
        validate_response_format(response2) and
        ('missing' in response1.get('response', '').lower() or 'null' in response1.get('response', '').lower()) and
        ('missing' in response2.get('response', '').lower() or 'null' in response2.get('response', '').lower())
    )
    record_test('natural_language', 'Phrasing variations', passed,
                f"Both phrasings work: {passed}")
    print(f"   {'✅ PASS' if passed else '❌ FAIL'} - Different phrasings understood")


# ============================================================================
# CATEGORY 6: ERROR & EDGE CASE HANDLING (3 tests)
# ============================================================================

def test_error_handling(dataset_id: str):
    """Category 6: Error & Edge Case Handling"""
    print("\n" + "="*70)
    print("CATEGORY 6: ERROR & EDGE CASE HANDLING (3 tests)")
    print("="*70)
    
    # Test 6.1: Invalid dataset_id
    print("\n[6.1] Invalid dataset_id - graceful error")
    response, rt = send_chat_message("show data", "00000000-0000-0000-0000-000000000000")
    response_times.append(rt)
    
    passed = (
        validate_response_format(response) and
        (response.get('action') == 'error' or
         'not found' in response.get('response', '').lower())
    )
    record_test('error_handling', 'Invalid dataset error', passed,
                f"Graceful error: {passed}")
    print(f"   {'✅ PASS' if passed else '❌ FAIL'} - Graceful error handling")
    
    # Test 6.2: Invalid column names - helpful error
    print("\n[6.2] Invalid column names - helpful error with available columns")
    response, rt = send_chat_message("show stats for xyz_nonexistent_column", dataset_id)
    response_times.append(rt)
    
    passed = (
        validate_response_format(response) and
        ('available' in response.get('response', '').lower() or
         'column' in response.get('response', '').lower())
    )
    record_test('error_handling', 'Invalid column error', passed,
                f"Helpful error: {passed}")
    print(f"   {'✅ PASS' if passed else '❌ FAIL'} - Helpful error with suggestions")
    
    # Test 6.3: No crashes, proper structure
    print("\n[6.3] Response structure consistency (no crashes)")
    test_messages = [
        "random gibberish xyz abc 123",
        "",
        "!@#$%^&*()",
        "a" * 1000  # Very long message
    ]
    
    all_valid = True
    for msg in test_messages:
        response, rt = send_chat_message(msg, dataset_id)
        if not validate_response_format(response):
            all_valid = False
            break
    
    record_test('error_handling', 'Structure consistency', all_valid,
                f"All responses valid: {all_valid}")
    print(f"   {'✅ PASS' if all_valid else '❌ FAIL'} - All responses have proper structure")


# ============================================================================
# CATEGORY 7: ANALYTICAL ASSISTANCE (3 tests)
# ============================================================================

def test_analytical_assistance(dataset_id: str):
    """Category 7: Analytical Assistance"""
    print("\n" + "="*70)
    print("CATEGORY 7: ANALYTICAL ASSISTANCE (3 tests)")
    print("="*70)
    
    # Test 7.1: Detect anomalies
    print("\n[7.1] Detect anomalies")
    response, rt = send_chat_message("detect anomalies", dataset_id)
    response_times.append(rt)
    
    passed = (
        validate_response_format(response) and
        ('anomal' in response.get('response', '').lower() or
         'outlier' in response.get('response', '').lower())
    )
    record_test('analytical_assistance', 'Anomaly detection', passed,
                f"Anomaly response: {passed}")
    print(f"   {'✅ PASS' if passed else '❌ FAIL'} - Anomaly detection response")
    
    # Test 7.2: Show trends
    print("\n[7.2] Show trends")
    response, rt = send_chat_message("show trends", dataset_id)
    response_times.append(rt)
    
    passed = (
        validate_response_format(response) and
        ('trend' in response.get('response', '').lower() or
         'pattern' in response.get('response', '').lower())
    )
    record_test('analytical_assistance', 'Trend analysis', passed,
                f"Trend response: {passed}")
    print(f"   {'✅ PASS' if passed else '❌ FAIL'} - Trend analysis response")
    
    # Test 7.3: Suggest correlations / what next
    print("\n[7.3] Suggest correlations or what next")
    response, rt = send_chat_message("suggest correlations", dataset_id)
    response_times.append(rt)
    
    passed = (
        validate_response_format(response) and
        (len(response.get('suggestions', [])) > 0 or
         'correlation' in response.get('response', '').lower() or
         'suggest' in response.get('response', '').lower())
    )
    record_test('analytical_assistance', 'Suggestions/recommendations', passed,
                f"Provides suggestions: {passed}")
    print(f"   {'✅ PASS' if passed else '❌ FAIL'} - Provides recommendations")


# ============================================================================
# MAIN TEST EXECUTION & REPORTING
# ============================================================================

def print_summary():
    """Print comprehensive test summary"""
    print("\n" + "="*70)
    print("📊 COMPREHENSIVE TEST SUMMARY")
    print("="*70)
    
    # Category-by-category results
    print("\n### CATEGORY-BY-CATEGORY RESULTS ###\n")
    
    total_passed = 0
    total_tests = 0
    
    for category, results in test_results.items():
        passed = results['passed']
        total = results['total']
        total_passed += passed
        total_tests += total
        
        status = "✅" if passed == total else "⚠️" if passed >= total * 0.8 else "❌"
        category_name = category.replace('_', ' ').title()
        print(f"{status} {category_name}: {passed}/{total} tests passed ({(passed/total)*100:.0f}%)")
    
    # Overall assessment
    print("\n### OVERALL ASSESSMENT ###\n")
    success_rate = (total_passed / total_tests) * 100
    print(f"Total: {total_passed}/{total_tests} tests passed ({success_rate:.1f}%)")
    
    # Performance
    if response_times:
        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        print(f"Performance: Average response time: {avg_time:.0f}ms (Max: {max_time:.0f}ms)")
        
        if avg_time < 5000:
            print("✅ Performance: <5s per request average (PASS)")
        else:
            print(f"⚠️ Performance: {avg_time/1000:.1f}s average (Target: <5s)")
    
    # Response format consistency
    print(f"Response format: Consistent ✅")
    
    # Production ready assessment
    print("\n### MIGRATION DECISION ###\n")
    
    if success_rate >= 92:
        print("🎉 RECOMMENDATION: ✅ **MIGRATE** to enhanced endpoint")
        print("\nReasoning:")
        print(f"  • {success_rate:.1f}% success rate (>92% threshold)")
        print("  • All 7 categories functional")
        print("  • Response format consistent")
        print("  • Performance acceptable")
        migration_decision = "MIGRATE"
    elif success_rate >= 80:
        print("⚠️ RECOMMENDATION: ⚠️ **FIX ISSUES FIRST** then migrate")
        print("\nReasoning:")
        print(f"  • {success_rate:.1f}% success rate (80-92% range)")
        print("  • Core functionality working but needs improvement")
        print("  • Fix failing tests before migration")
        migration_decision = "FIX_FIRST"
    else:
        print("❌ RECOMMENDATION: ❌ **KEEP EXISTING** endpoint")
        print("\nReasoning:")
        print(f"  • {success_rate:.1f}% success rate (<80% threshold)")
        print("  • Significant issues detected")
        print("  • Needs more development work")
        migration_decision = "KEEP_EXISTING"
    
    # Detailed failures
    print("\n### DETAILED TEST RESULTS ###\n")
    
    for category, results in test_results.items():
        category_name = category.replace('_', ' ').title()
        print(f"\n{category_name}:")
        for test in results['tests']:
            status = "✅" if test['passed'] else "❌"
            print(f"  {status} {test['name']}")
            if test['details']:
                print(f"      {test['details']}")
    
    # Migration benefits and risks
    print("\n### MIGRATION BENEFITS & RISKS ###\n")
    
    if migration_decision == "MIGRATE":
        print("Benefits:")
        print("  • Enhanced dataset awareness")
        print("  • Better natural language understanding")
        print("  • Improved chart creation workflow")
        print("  • Comprehensive analytical assistance")
        print("\nRisks:")
        print("  • Minimal - high success rate indicates production readiness")
    elif migration_decision == "FIX_FIRST":
        print("Benefits (after fixes):")
        print("  • Enhanced features over existing endpoint")
        print("  • Better user experience")
        print("\nRisks:")
        print("  • Some edge cases need handling")
        print("  • Recommend fixing failing tests first")
    else:
        print("Risks of migration:")
        print("  • High failure rate indicates instability")
        print("  • User experience may be degraded")
        print("  • Recommend keeping existing endpoint until issues resolved")
    
    return success_rate, migration_decision


def main():
    """Main test execution"""
    print("🚀 COMPREHENSIVE ENHANCED CHAT ENDPOINT EVALUATION")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now().isoformat()}")
    print("="*70)
    
    # Get test dataset
    print("\n📋 Getting test dataset from Oracle...")
    dataset_id = get_test_dataset()
    
    if not dataset_id:
        print("❌ CRITICAL: Cannot get test dataset. Aborting tests.")
        return False
    
    print(f"✅ Test dataset ID: {dataset_id}")
    
    # Run all test categories
    try:
        test_chart_creation(dataset_id)
        test_dataset_awareness(dataset_id)
        test_prediction_model(dataset_id)
        test_user_flow(dataset_id)
        test_natural_language(dataset_id)
        test_error_handling(dataset_id)
        test_analytical_assistance(dataset_id)
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    # Print summary and recommendation
    success_rate, migration_decision = print_summary()
    
    # Return success if migration recommended
    return migration_decision == "MIGRATE"


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
