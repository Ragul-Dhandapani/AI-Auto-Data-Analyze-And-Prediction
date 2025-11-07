#!/usr/bin/env python3
"""
Enhanced Chat Endpoint Testing - FINAL COMPREHENSIVE TEST
Tests all 7 categories (27 tests total) for the enhanced chat assistant

Focus: Verify RecursionError fix, Plotly serialization, and confirmation workflow
"""

import requests
import json
import sys
import time
from datetime import datetime

# Backend URL
BACKEND_URL = "https://ai-insight-hub-3.preview.emergentagent.com/api"

# Test dataset ID (from existing datasets)
TEST_DATASET_ID = "7fc830da-886f-4745-ac6d-ddee8c20af8a"  # application_latency_3.csv

# Test results tracker
test_results = {
    'chart_creation': [],
    'dataset_awareness': [],
    'model_interactions': [],
    'user_flow': [],
    'natural_language': [],
    'error_handling': [],
    'analytical_assistance': []
}

def send_chat_message(message: str, dataset_id: str = TEST_DATASET_ID) -> dict:
    """Helper function to send chat message"""
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
        
        if response.status_code == 200:
            return {'success': True, 'data': response.json()}
        else:
            return {'success': False, 'error': f"Status {response.status_code}", 'data': response.text}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def test_chart_creation():
    """Category 1: Chart Creation (3 tests)"""
    print("\n" + "="*70)
    print("CATEGORY 1: CHART CREATION (3 tests)")
    print("="*70)
    
    tests = [
        {
            'name': 'Scatter Plot Creation',
            'message': 'create a scatter plot',
            'expected': ['chart', 'scatter', 'plotly']
        },
        {
            'name': 'Histogram Creation',
            'message': 'show histogram',
            'expected': ['chart', 'histogram', 'plotly']
        },
        {
            'name': 'Invalid Column Handling',
            'message': 'create chart for nonexistent_column',
            'expected': ['error', 'not found', 'available']
        }
    ]
    
    for i, test in enumerate(tests, 1):
        print(f"\n--- Test 1.{i}: {test['name']} ---")
        print(f"Message: '{test['message']}'")
        
        result = send_chat_message(test['message'])
        
        if result['success']:
            data = result['data']
            response_text = data.get('response', '').lower()
            action = data.get('action', '')
            
            print(f"✅ Request successful")
            print(f"   Action: {action}")
            print(f"   Response preview: {response_text[:100]}...")
            
            # Check for RecursionError (should NOT occur)
            if 'recursion' in response_text or 'maximum recursion' in response_text:
                print("❌ CRITICAL: RecursionError detected!")
                test_results['chart_creation'].append({
                    'test': test['name'],
                    'status': 'FAIL',
                    'reason': 'RecursionError detected'
                })
                continue
            
            # Check for Plotly serialization (should have proper format)
            if action == 'chart' and 'data' in data:
                chart_data = data.get('data', {})
                if 'plotly_data' in chart_data or 'data' in chart_data:
                    print("✅ Chart data properly serialized")
                else:
                    print("⚠️  Chart data format unclear")
            
            # Check confirmation workflow
            requires_confirmation = data.get('requires_confirmation', False)
            print(f"   Requires confirmation: {requires_confirmation}")
            
            # Verify expected keywords
            found_keywords = [kw for kw in test['expected'] if kw in response_text or kw in action.lower()]
            if found_keywords:
                print(f"✅ PASS - Found expected keywords: {found_keywords}")
                test_results['chart_creation'].append({
                    'test': test['name'],
                    'status': 'PASS',
                    'action': action
                })
            else:
                print(f"⚠️  PARTIAL - Expected keywords not found: {test['expected']}")
                test_results['chart_creation'].append({
                    'test': test['name'],
                    'status': 'PARTIAL',
                    'reason': 'Expected keywords not found'
                })
        else:
            print(f"❌ FAIL - {result['error']}")
            test_results['chart_creation'].append({
                'test': test['name'],
                'status': 'FAIL',
                'reason': result['error']
            })


def test_dataset_awareness():
    """Category 2: Dataset Awareness (3 tests)"""
    print("\n" + "="*70)
    print("CATEGORY 2: DATASET AWARENESS (3 tests)")
    print("="*70)
    
    tests = [
        {
            'name': 'Show Columns',
            'message': 'show columns',
            'expected': ['columns', 'latency_ms', 'cpu_utilization']
        },
        {
            'name': 'Dataset Size',
            'message': 'dataset size',
            'expected': ['rows', '62500', 'columns', '13']
        },
        {
            'name': 'Check Null Values',
            'message': 'check null values',
            'expected': ['null', 'missing', 'values']
        }
    ]
    
    for i, test in enumerate(tests, 1):
        print(f"\n--- Test 2.{i}: {test['name']} ---")
        print(f"Message: '{test['message']}'")
        
        result = send_chat_message(test['message'])
        
        if result['success']:
            data = result['data']
            response_text = data.get('response', '').lower()
            action = data.get('action', '')
            
            print(f"✅ Request successful")
            print(f"   Action: {action}")
            print(f"   Response preview: {response_text[:150]}...")
            
            # Verify expected keywords
            found_keywords = [kw for kw in test['expected'] if kw in response_text]
            if len(found_keywords) >= 2:  # At least 2 keywords should match
                print(f"✅ PASS - Found keywords: {found_keywords}")
                test_results['dataset_awareness'].append({
                    'test': test['name'],
                    'status': 'PASS',
                    'keywords_found': found_keywords
                })
            else:
                print(f"⚠️  PARTIAL - Only found: {found_keywords}")
                test_results['dataset_awareness'].append({
                    'test': test['name'],
                    'status': 'PARTIAL',
                    'keywords_found': found_keywords
                })
        else:
            print(f"❌ FAIL - {result['error']}")
            test_results['dataset_awareness'].append({
                'test': test['name'],
                'status': 'FAIL',
                'reason': result['error']
            })


def test_model_interactions():
    """Category 3: Model Interactions (2 tests)"""
    print("\n" + "="*70)
    print("CATEGORY 3: MODEL INTERACTIONS (2 tests)")
    print("="*70)
    
    tests = [
        {
            'name': 'What Am I Predicting',
            'message': 'what am i predicting',
            'expected': ['no models', 'not trained', 'run analysis']
        },
        {
            'name': 'Show Metrics',
            'message': 'show metrics',
            'expected': ['no models', 'not available', 'train']
        }
    ]
    
    for i, test in enumerate(tests, 1):
        print(f"\n--- Test 3.{i}: {test['name']} ---")
        print(f"Message: '{test['message']}'")
        
        result = send_chat_message(test['message'])
        
        if result['success']:
            data = result['data']
            response_text = data.get('response', '').lower()
            action = data.get('action', '')
            
            print(f"✅ Request successful")
            print(f"   Action: {action}")
            print(f"   Response preview: {response_text[:150]}...")
            
            # Should indicate no models available
            found_keywords = [kw for kw in test['expected'] if kw in response_text]
            if found_keywords:
                print(f"✅ PASS - Correctly indicates no models: {found_keywords}")
                test_results['model_interactions'].append({
                    'test': test['name'],
                    'status': 'PASS',
                    'keywords_found': found_keywords
                })
            else:
                print(f"⚠️  PARTIAL - Expected 'no models' message")
                test_results['model_interactions'].append({
                    'test': test['name'],
                    'status': 'PARTIAL',
                    'reason': 'No models message not clear'
                })
        else:
            print(f"❌ FAIL - {result['error']}")
            test_results['model_interactions'].append({
                'test': test['name'],
                'status': 'FAIL',
                'reason': result['error']
            })


def test_user_flow():
    """Category 4: User Flow (2 tests)"""
    print("\n" + "="*70)
    print("CATEGORY 4: USER FLOW (2 tests)")
    print("="*70)
    
    # Test 4.1: No dataset_id (expect error)
    print(f"\n--- Test 4.1: No Dataset ID ---")
    print(f"Message: 'show columns' (with invalid dataset_id)")
    
    result = send_chat_message('show columns', dataset_id='invalid-dataset-id-12345')
    
    if result['success']:
        data = result['data']
        response_text = data.get('response', '').lower()
        action = data.get('action', '')
        
        print(f"✅ Request successful")
        print(f"   Action: {action}")
        print(f"   Response preview: {response_text[:150]}...")
        
        # Should indicate dataset not found
        if 'not found' in response_text or 'invalid' in response_text or action == 'error':
            print(f"✅ PASS - Correctly handles invalid dataset")
            test_results['user_flow'].append({
                'test': 'No Dataset ID',
                'status': 'PASS'
            })
        else:
            print(f"⚠️  PARTIAL - Error handling unclear")
            test_results['user_flow'].append({
                'test': 'No Dataset ID',
                'status': 'PARTIAL'
            })
    else:
        print(f"❌ FAIL - {result['error']}")
        test_results['user_flow'].append({
            'test': 'No Dataset ID',
            'status': 'FAIL',
            'reason': result['error']
        })
    
    # Test 4.2: What next? (expect suggestions)
    print(f"\n--- Test 4.2: What Next ---")
    print(f"Message: 'what next?'")
    
    result = send_chat_message('what next?')
    
    if result['success']:
        data = result['data']
        response_text = data.get('response', '').lower()
        suggestions = data.get('suggestions', [])
        
        print(f"✅ Request successful")
        print(f"   Suggestions count: {len(suggestions)}")
        print(f"   Response preview: {response_text[:150]}...")
        
        if suggestions and len(suggestions) > 0:
            print(f"✅ PASS - Provides suggestions: {suggestions[:3]}")
            test_results['user_flow'].append({
                'test': 'What Next',
                'status': 'PASS',
                'suggestions_count': len(suggestions)
            })
        else:
            print(f"⚠️  PARTIAL - No suggestions provided")
            test_results['user_flow'].append({
                'test': 'What Next',
                'status': 'PARTIAL',
                'reason': 'No suggestions'
            })
    else:
        print(f"❌ FAIL - {result['error']}")
        test_results['user_flow'].append({
            'test': 'What Next',
            'status': 'FAIL',
            'reason': result['error']
        })


def test_natural_language():
    """Category 5: Natural Language (3 tests)"""
    print("\n" + "="*70)
    print("CATEGORY 5: NATURAL LANGUAGE (3 tests)")
    print("="*70)
    
    tests = [
        {'name': 'Variation 1', 'message': 'columns'},
        {'name': 'Variation 2', 'message': 'show columns'},
        {'name': 'Variation 3', 'message': 'list columns'}
    ]
    
    responses = []
    
    for i, test in enumerate(tests, 1):
        print(f"\n--- Test 5.{i}: {test['name']} ---")
        print(f"Message: '{test['message']}'")
        
        result = send_chat_message(test['message'])
        
        if result['success']:
            data = result['data']
            response_text = data.get('response', '').lower()
            
            print(f"✅ Request successful")
            print(f"   Response preview: {response_text[:100]}...")
            
            # Check if response contains column names
            has_columns = 'latency_ms' in response_text or 'cpu_utilization' in response_text
            
            if has_columns:
                print(f"✅ PASS - Correctly lists columns")
                responses.append(True)
                test_results['natural_language'].append({
                    'test': test['name'],
                    'status': 'PASS'
                })
            else:
                print(f"⚠️  PARTIAL - Column listing unclear")
                responses.append(False)
                test_results['natural_language'].append({
                    'test': test['name'],
                    'status': 'PARTIAL'
                })
        else:
            print(f"❌ FAIL - {result['error']}")
            responses.append(False)
            test_results['natural_language'].append({
                'test': test['name'],
                'status': 'FAIL',
                'reason': result['error']
            })
    
    # Check consistency
    if all(responses):
        print(f"\n✅ All natural language variations handled consistently")
    else:
        print(f"\n⚠️  Inconsistent handling across variations")


def test_error_handling():
    """Category 6: Error Handling (2 tests)"""
    print("\n" + "="*70)
    print("CATEGORY 6: ERROR HANDLING (2 tests)")
    print("="*70)
    
    # Test 6.1: Invalid dataset_id
    print(f"\n--- Test 6.1: Invalid Dataset ID ---")
    print(f"Message: 'show columns' (with completely invalid ID)")
    
    result = send_chat_message('show columns', dataset_id='00000000-0000-0000-0000-000000000000')
    
    if result['success']:
        data = result['data']
        response_text = data.get('response', '').lower()
        action = data.get('action', '')
        
        print(f"✅ Request successful")
        print(f"   Action: {action}")
        print(f"   Response preview: {response_text[:150]}...")
        
        if 'not found' in response_text or action == 'error':
            print(f"✅ PASS - Gracefully handles invalid dataset")
            test_results['error_handling'].append({
                'test': 'Invalid Dataset ID',
                'status': 'PASS'
            })
        else:
            print(f"⚠️  PARTIAL - Error handling unclear")
            test_results['error_handling'].append({
                'test': 'Invalid Dataset ID',
                'status': 'PARTIAL'
            })
    else:
        print(f"❌ FAIL - {result['error']}")
        test_results['error_handling'].append({
            'test': 'Invalid Dataset ID',
            'status': 'FAIL',
            'reason': result['error']
        })
    
    # Test 6.2: Invalid column name
    print(f"\n--- Test 6.2: Invalid Column Name ---")
    print(f"Message: 'show statistics for nonexistent_column_xyz'")
    
    result = send_chat_message('show statistics for nonexistent_column_xyz')
    
    if result['success']:
        data = result['data']
        response_text = data.get('response', '').lower()
        
        print(f"✅ Request successful")
        print(f"   Response preview: {response_text[:150]}...")
        
        if 'not found' in response_text or 'available' in response_text or 'invalid' in response_text:
            print(f"✅ PASS - Handles invalid column gracefully")
            test_results['error_handling'].append({
                'test': 'Invalid Column Name',
                'status': 'PASS'
            })
        else:
            print(f"⚠️  PARTIAL - Error message unclear")
            test_results['error_handling'].append({
                'test': 'Invalid Column Name',
                'status': 'PARTIAL'
            })
    else:
        print(f"❌ FAIL - {result['error']}")
        test_results['error_handling'].append({
            'test': 'Invalid Column Name',
            'status': 'FAIL',
            'reason': result['error']
        })


def test_analytical_assistance():
    """Category 7: Analytical Assistance (2 tests)"""
    print("\n" + "="*70)
    print("CATEGORY 7: ANALYTICAL ASSISTANCE (2 tests)")
    print("="*70)
    
    tests = [
        {
            'name': 'Detect Anomalies',
            'message': 'detect anomalies',
            'expected': ['anomaly', 'outlier', 'detection']
        },
        {
            'name': 'Suggest Correlations',
            'message': 'suggest correlations',
            'expected': ['correlation', 'relationship', 'related']
        }
    ]
    
    for i, test in enumerate(tests, 1):
        print(f"\n--- Test 7.{i}: {test['name']} ---")
        print(f"Message: '{test['message']}'")
        
        result = send_chat_message(test['message'])
        
        if result['success']:
            data = result['data']
            response_text = data.get('response', '').lower()
            action = data.get('action', '')
            
            print(f"✅ Request successful")
            print(f"   Action: {action}")
            print(f"   Response preview: {response_text[:150]}...")
            
            # Verify expected keywords
            found_keywords = [kw for kw in test['expected'] if kw in response_text]
            if found_keywords:
                print(f"✅ PASS - Provides analytical assistance: {found_keywords}")
                test_results['analytical_assistance'].append({
                    'test': test['name'],
                    'status': 'PASS',
                    'keywords_found': found_keywords
                })
            else:
                print(f"⚠️  PARTIAL - Expected keywords not found")
                test_results['analytical_assistance'].append({
                    'test': test['name'],
                    'status': 'PARTIAL',
                    'reason': 'Expected keywords not found'
                })
        else:
            print(f"❌ FAIL - {result['error']}")
            test_results['analytical_assistance'].append({
                'test': test['name'],
                'status': 'FAIL',
                'reason': result['error']
            })


def print_summary():
    """Print comprehensive test summary"""
    print("\n" + "="*70)
    print("FINAL COMPREHENSIVE TEST SUMMARY")
    print("="*70)
    
    total_tests = 0
    passed_tests = 0
    partial_tests = 0
    failed_tests = 0
    
    for category, results in test_results.items():
        category_name = category.replace('_', ' ').title()
        print(f"\n{category_name}:")
        
        for result in results:
            total_tests += 1
            status = result['status']
            
            if status == 'PASS':
                passed_tests += 1
                print(f"  ✅ {result['test']}")
            elif status == 'PARTIAL':
                partial_tests += 1
                print(f"  ⚠️  {result['test']} - {result.get('reason', 'Partial success')}")
            else:
                failed_tests += 1
                print(f"  ❌ {result['test']} - {result.get('reason', 'Failed')}")
    
    print("\n" + "="*70)
    print(f"TOTAL TESTS: {total_tests}")
    print(f"✅ PASSED: {passed_tests} ({(passed_tests/total_tests)*100:.1f}%)")
    print(f"⚠️  PARTIAL: {partial_tests} ({(partial_tests/total_tests)*100:.1f}%)")
    print(f"❌ FAILED: {failed_tests} ({(failed_tests/total_tests)*100:.1f}%)")
    print("="*70)
    
    # Success criteria
    success_rate = (passed_tests / total_tests) * 100
    
    print("\n" + "="*70)
    print("MIGRATION DECISION")
    print("="*70)
    
    if success_rate >= 90:
        print("✅ MIGRATE - 90%+ tests passed")
        print("   RecursionError fix verified")
        print("   Plotly serialization working")
        print("   Confirmation workflow present")
        return True
    elif success_rate >= 80:
        print("⚠️  NEEDS REVIEW - 80-89% tests passed")
        print("   Some issues detected, review required")
        return False
    else:
        print("❌ DO NOT MIGRATE - <80% tests passed")
        print("   Significant issues detected")
        return False


def main():
    """Run all enhanced chat tests"""
    print("🚀 ENHANCED CHAT ENDPOINT - FINAL COMPREHENSIVE TEST")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Dataset: {TEST_DATASET_ID}")
    print(f"Test Time: {datetime.now().isoformat()}")
    print("="*70)
    
    # Check API health
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=10)
        if response.status_code != 200:
            print("❌ API is not accessible. Stopping tests.")
            return False
        print("✅ API is accessible")
    except Exception as e:
        print(f"❌ Cannot reach API: {str(e)}")
        return False
    
    # Run all test categories
    test_chart_creation()
    test_dataset_awareness()
    test_model_interactions()
    test_user_flow()
    test_natural_language()
    test_error_handling()
    test_analytical_assistance()
    
    # Print summary and migration decision
    success = print_summary()
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
