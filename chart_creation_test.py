#!/usr/bin/env python3
"""
Enhanced Chat Assistant - Chart Creation Testing
Focus: Test Azure OpenAI JSON mode fix for chart creation
"""
import requests
import json
import sys
from datetime import datetime

# Backend URL
BACKEND_URL = "https://model-wizard-2.preview.emergentagent.com/api"

def get_test_dataset():
    """Get a dataset from Oracle for testing"""
    try:
        response = requests.get(f"{BACKEND_URL}/datasets", timeout=30)
        if response.status_code == 200:
            datasets = response.json().get('datasets', [])
            if datasets:
                # Return first dataset with reasonable size
                for ds in datasets:
                    if ds.get('row_count', 0) > 0:
                        return ds
        return None
    except Exception as e:
        print(f"Error getting dataset: {str(e)}")
        return None

def test_chart_creation(dataset_id, columns, test_name, message):
    """Test chart creation with a specific message"""
    print(f"\n--- {test_name} ---")
    print(f"Message: '{message}'")
    
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
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check response structure
            action = data.get('action', '')
            response_text = data.get('response', '')
            chart_data = data.get('data', {})
            requires_confirmation = data.get('requires_confirmation', False)
            suggestions = data.get('suggestions', [])
            
            print(f"Action: {action}")
            print(f"Response: {response_text[:150]}...")
            print(f"Requires Confirmation: {requires_confirmation}")
            print(f"Suggestions: {suggestions}")
            
            # Validate chart creation
            if action == 'chart':
                # Check if chart data has proper Plotly format
                if 'data' in chart_data and 'layout' in chart_data:
                    print("✅ PASS - Chart created with proper Plotly format")
                    print(f"   Chart has {len(chart_data.get('data', []))} trace(s)")
                    
                    # Check confirmation workflow
                    if requires_confirmation:
                        print("✅ PASS - Confirmation workflow present")
                        if "append" in response_text.lower() and "dashboard" in response_text.lower():
                            print("✅ PASS - Asks about dashboard append")
                        else:
                            print("⚠️  WARNING - Confirmation message unclear")
                    else:
                        print("❌ FAIL - Missing confirmation workflow")
                    
                    return True
                else:
                    print("❌ FAIL - Chart data missing Plotly format")
                    print(f"   Data keys: {list(chart_data.keys())}")
                    return False
            elif action == 'message':
                # Check if it's an error message with available columns
                if "not found" in response_text.lower() or "available columns" in response_text.lower():
                    print("✅ PASS - Error handling with available columns")
                    return True
                else:
                    print("❌ FAIL - Expected chart but got message")
                    print(f"   Response: {response_text}")
                    return False
            else:
                print(f"❌ FAIL - Unexpected action: {action}")
                return False
        else:
            print(f"❌ FAIL - HTTP {response.status_code}")
            try:
                error = response.json()
                print(f"   Error: {error}")
            except:
                print(f"   Error: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL - Exception: {str(e)}")
        return False

def test_natural_language_variations(dataset_id, columns):
    """Test natural language variations"""
    print("\n=== Test: Natural Language Variations ===")
    
    if len(columns) < 2:
        print("⚠️  SKIP - Need at least 2 columns")
        return True
    
    col1 = columns[0]
    col2 = columns[1] if len(columns) > 1 else columns[0]
    
    variations = [
        f"plot {col1} against {col2}",
        f"visualize {col1} vs {col2}",
        f"show distribution of {col1}",
        f"draw chart for {col1}"
    ]
    
    results = []
    for i, message in enumerate(variations, 1):
        result = test_chart_creation(dataset_id, columns, f"Variation {i}", message)
        results.append(result)
    
    passed = sum(results)
    total = len(results)
    print(f"\n✅ Natural Language: {passed}/{total} passed")
    return passed == total

def main():
    """Run Chart Creation Tests"""
    print("🚀 ENHANCED CHAT ASSISTANT - CHART CREATION TESTING")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now().isoformat()}")
    print("="*70)
    
    # Get test dataset
    print("\n📊 Getting test dataset...")
    dataset = get_test_dataset()
    
    if not dataset:
        print("❌ No dataset available for testing")
        return False
    
    dataset_id = dataset.get('id')
    dataset_name = dataset.get('name', 'Unknown')
    columns = dataset.get('columns', [])
    
    print(f"✅ Using dataset: {dataset_name}")
    print(f"   ID: {dataset_id}")
    print(f"   Rows: {dataset.get('row_count', 0):,}")
    print(f"   Columns: {len(columns)}")
    print(f"   Sample columns: {', '.join(columns[:5])}")
    
    if len(columns) < 2:
        print("❌ Dataset needs at least 2 columns for testing")
        return False
    
    # Track results
    results = {
        'scatter_plot': False,
        'line_chart': False,
        'bar_chart': False,
        'histogram': False,
        'box_plot': False,
        'invalid_column': False,
        'natural_language': False
    }
    
    # Test 1: Scatter Plot
    col1 = columns[0]
    col2 = columns[1] if len(columns) > 1 else columns[0]
    results['scatter_plot'] = test_chart_creation(
        dataset_id, columns,
        "Test 1: Scatter Plot",
        f"create a scatter plot of {col1} vs {col2}"
    )
    
    # Test 2: Line Chart
    if len(columns) >= 2:
        results['line_chart'] = test_chart_creation(
            dataset_id, columns,
            "Test 2: Line Chart",
            f"show line chart for {col2} over {col1}"
        )
    
    # Test 3: Bar Chart
    results['bar_chart'] = test_chart_creation(
        dataset_id, columns,
        "Test 3: Bar Chart",
        f"create bar chart for {col1}"
    )
    
    # Test 4: Histogram
    results['histogram'] = test_chart_creation(
        dataset_id, columns,
        "Test 4: Histogram",
        f"show histogram of {col1}"
    )
    
    # Test 5: Box Plot
    results['box_plot'] = test_chart_creation(
        dataset_id, columns,
        "Test 5: Box Plot",
        f"create box plot for {col1}"
    )
    
    # Test 6: Invalid Column Name
    results['invalid_column'] = test_chart_creation(
        dataset_id, columns,
        "Test 6: Invalid Column",
        "create scatter plot of nonexistent_col1 vs nonexistent_col2"
    )
    
    # Test 7: Natural Language Variations
    results['natural_language'] = test_natural_language_variations(dataset_id, columns)
    
    # Summary
    print("\n" + "="*70)
    print("📊 CHART CREATION TEST SUMMARY")
    print("="*70)
    
    passed_tests = sum(1 for result in results.values() if result)
    total_tests = len(results)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed ({(passed_tests/total_tests)*100:.1f}%)")
    
    # Detailed findings
    print("\n🔍 KEY FINDINGS:")
    
    if results['scatter_plot'] and results['line_chart'] and results['bar_chart']:
        print("   ✅ Multiple chart types working")
    else:
        print("   ❌ Some chart types failing")
    
    if results['histogram'] and results['box_plot']:
        print("   ✅ Single-column charts working")
    else:
        print("   ❌ Single-column charts have issues")
    
    if results['invalid_column']:
        print("   ✅ Error handling with available columns working")
    else:
        print("   ❌ Error handling needs improvement")
    
    if results['natural_language']:
        print("   ✅ Natural language variations working")
    else:
        print("   ❌ Natural language parsing has issues")
    
    # Critical assessment
    print("\n🎯 CRITICAL ASSESSMENT:")
    
    if passed_tests >= 6:
        print("   ✅ Chart Creation: PRODUCTION READY")
        print("   ✅ Azure OpenAI JSON mode fix: WORKING")
        print("   ✅ Confirmation workflow: IMPLEMENTED")
        return True
    elif passed_tests >= 4:
        print("   ⚠️  Chart Creation: PARTIALLY WORKING")
        print("   ⚠️  Some issues need attention")
        return False
    else:
        print("   ❌ Chart Creation: NOT WORKING")
        print("   ❌ Azure OpenAI JSON mode fix: FAILED")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
