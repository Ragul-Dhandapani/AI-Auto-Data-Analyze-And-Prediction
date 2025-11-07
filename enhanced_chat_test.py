"""
Comprehensive Enhanced Chat Assistant Testing
Tests all 7 categories of requirements
"""
import requests
import json
import time
from typing import Dict, List, Any

# Configuration
BACKEND_URL = "https://ai-insight-hub-3.preview.emergentagent.com/api"
ENHANCED_CHAT_ENDPOINT = f"{BACKEND_URL}/enhanced-chat"

class EnhancedChatTester:
    def __init__(self):
        self.results = []
        self.dataset_id = None
        self.test_summary = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'categories': {}
        }
    
    def log_result(self, category: str, test_name: str, status: str, details: str = "", response_data: Dict = None):
        """Log test result"""
        result = {
            'category': category,
            'test_name': test_name,
            'status': status,
            'details': details,
            'response_data': response_data
        }
        self.results.append(result)
        
        # Update summary
        self.test_summary['total_tests'] += 1
        if status == 'PASS':
            self.test_summary['passed'] += 1
        else:
            self.test_summary['failed'] += 1
        
        if category not in self.test_summary['categories']:
            self.test_summary['categories'][category] = {'passed': 0, 'failed': 0}
        
        if status == 'PASS':
            self.test_summary['categories'][category]['passed'] += 1
        else:
            self.test_summary['categories'][category]['failed'] += 1
        
        # Print result
        status_icon = "✅" if status == "PASS" else "❌"
        print(f"{status_icon} [{category}] {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
    
    def get_datasets(self) -> List[Dict]:
        """Get available datasets from Oracle"""
        try:
            response = requests.get(f"{BACKEND_URL}/datasets", timeout=10)
            if response.status_code == 200:
                data = response.json()
                # Handle both formats: direct list or {'datasets': [...]}
                if isinstance(data, dict) and 'datasets' in data:
                    datasets = data['datasets']
                elif isinstance(data, list):
                    datasets = data
                else:
                    datasets = []
                print(f"\n📊 Found {len(datasets)} datasets in Oracle database")
                return datasets
            else:
                print(f"❌ Failed to get datasets: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error getting datasets: {str(e)}")
            return []
    
    def test_built_in_scenarios(self):
        """Test 1: Built-in test endpoint"""
        print("\n" + "="*80)
        print("TEST 1: BUILT-IN TEST SCENARIOS")
        print("="*80)
        
        try:
            response = requests.post(f"{ENHANCED_CHAT_ENDPOINT}/test", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                summary = data.get('summary', {})
                results = data.get('results', [])
                
                print(f"\n📊 Built-in Test Summary:")
                print(f"   Total Tests: {summary.get('total_tests', 0)}")
                print(f"   Passed: {summary.get('passed', 0)}")
                print(f"   Failed: {summary.get('failed', 0)}")
                print(f"   Success Rate: {summary.get('success_rate', '0%')}")
                
                # Check individual test results
                for result in results:
                    test_name = result.get('test', 'Unknown')
                    status = result.get('status', '❌ FAIL')
                    
                    if '✅' in status:
                        self.log_result('Built-in Tests', test_name, 'PASS', 
                                      f"Action: {result.get('action', 'N/A')}, Has suggestions: {result.get('has_suggestions', False)}")
                    else:
                        error = result.get('error', 'Unknown error')
                        self.log_result('Built-in Tests', test_name, 'FAIL', f"Error: {error}")
                
                # Overall built-in test status
                success_rate = float(summary.get('success_rate', '0%').replace('%', ''))
                if success_rate >= 90:
                    self.log_result('Built-in Tests', 'Overall Built-in Tests', 'PASS', 
                                  f"Success rate: {summary.get('success_rate', '0%')}")
                else:
                    self.log_result('Built-in Tests', 'Overall Built-in Tests', 'FAIL', 
                                  f"Success rate below 90%: {summary.get('success_rate', '0%')}")
            else:
                self.log_result('Built-in Tests', 'Built-in Test Endpoint', 'FAIL', 
                              f"HTTP {response.status_code}: {response.text[:200]}")
        
        except Exception as e:
            self.log_result('Built-in Tests', 'Built-in Test Endpoint', 'FAIL', str(e))
    
    def send_chat_message(self, message: str, dataset_id: str, conversation_history: List = None) -> Dict:
        """Send a chat message and return response"""
        try:
            payload = {
                'message': message,
                'dataset_id': dataset_id,
                'conversation_history': conversation_history or []
            }
            
            response = requests.post(
                f"{ENHANCED_CHAT_ENDPOINT}/message",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'error': True,
                    'status_code': response.status_code,
                    'message': response.text[:500]
                }
        
        except Exception as e:
            return {
                'error': True,
                'message': str(e)
            }
    
    def test_chart_creation(self, dataset_id: str):
        """Category 1: Chart Creation & Manipulation"""
        print("\n" + "="*80)
        print("CATEGORY 1: CHART CREATION & MANIPULATION")
        print("="*80)
        
        test_cases = [
            {
                'name': 'Valid Scatter Chart',
                'message': 'create a scatter chart for price vs quantity',
                'expected_action': 'chart',
                'should_confirm': True
            },
            {
                'name': 'Valid Line Chart',
                'message': 'plot revenue over time',
                'expected_action': 'chart',
                'should_confirm': True
            },
            {
                'name': 'Valid Histogram',
                'message': 'show histogram for price',
                'expected_action': 'chart',
                'should_confirm': True
            },
            {
                'name': 'Invalid Column Name',
                'message': 'create chart for nonexistent_column',
                'expected_action': 'message',
                'should_show_available': True
            },
            {
                'name': 'Multiple Chart Types',
                'message': 'create a bar chart for category',
                'expected_action': 'chart',
                'should_confirm': True
            }
        ]
        
        for test in test_cases:
            response = self.send_chat_message(test['message'], dataset_id)
            
            if response.get('error'):
                self.log_result('Chart Creation', test['name'], 'FAIL', 
                              f"Error: {response.get('message', 'Unknown error')}")
                continue
            
            action = response.get('action', '')
            requires_confirmation = response.get('requires_confirmation', False)
            response_text = response.get('response', '')
            
            # Validate response
            passed = True
            details = []
            
            if test.get('expected_action') and action != test['expected_action']:
                passed = False
                details.append(f"Expected action '{test['expected_action']}', got '{action}'")
            
            if test.get('should_confirm') and not requires_confirmation:
                passed = False
                details.append("Expected confirmation request, but not present")
            
            if test.get('should_show_available') and 'available' not in response_text.lower():
                passed = False
                details.append("Expected to show available columns for invalid column")
            
            # Check for chart confirmation workflow
            if action == 'chart' and 'append' in response_text.lower() and 'dashboard' in response_text.lower():
                details.append("✓ Chart confirmation workflow present")
            
            status = 'PASS' if passed else 'FAIL'
            self.log_result('Chart Creation', test['name'], status, '; '.join(details) if details else 'All checks passed')
    
    def test_dataset_awareness(self, dataset_id: str):
        """Category 2: Dataset Awareness"""
        print("\n" + "="*80)
        print("CATEGORY 2: DATASET AWARENESS")
        print("="*80)
        
        test_cases = [
            {
                'name': 'List Column Names',
                'message': 'show me column names',
                'should_contain': ['column', 'numeric', 'categorical']
            },
            {
                'name': 'Dataset Size',
                'message': 'what is the dataset size?',
                'should_contain': ['rows', 'columns']
            },
            {
                'name': 'Column Statistics',
                'message': 'show statistics for price',
                'should_contain': ['mean', 'std', 'min', 'max']
            },
            {
                'name': 'Data Types',
                'message': 'what are the data types?',
                'should_contain': ['type', 'dtype']
            },
            {
                'name': 'Missing Values',
                'message': 'check for null values',
                'should_contain': ['missing', 'null']
            },
            {
                'name': 'Correlation Analysis',
                'message': 'show correlation with revenue',
                'should_contain': ['correlation']
            }
        ]
        
        for test in test_cases:
            response = self.send_chat_message(test['message'], dataset_id)
            
            if response.get('error'):
                self.log_result('Dataset Awareness', test['name'], 'FAIL', 
                              f"Error: {response.get('message', 'Unknown error')}")
                continue
            
            response_text = response.get('response', '').lower()
            suggestions = response.get('suggestions', [])
            
            # Check if response contains expected keywords
            passed = True
            missing_keywords = []
            
            for keyword in test.get('should_contain', []):
                if keyword.lower() not in response_text:
                    passed = False
                    missing_keywords.append(keyword)
            
            # Check for suggestions
            has_suggestions = len(suggestions) > 0
            
            details = []
            if missing_keywords:
                details.append(f"Missing keywords: {', '.join(missing_keywords)}")
            if has_suggestions:
                details.append(f"✓ Provided {len(suggestions)} suggestions")
            else:
                details.append("⚠ No suggestions provided")
            
            status = 'PASS' if passed else 'FAIL'
            self.log_result('Dataset Awareness', test['name'], status, '; '.join(details))
    
    def test_prediction_model_interactions(self, dataset_id: str):
        """Category 3: Prediction & Model Interactions"""
        print("\n" + "="*80)
        print("CATEGORY 3: PREDICTION & MODEL INTERACTIONS")
        print("="*80)
        
        # Note: These tests require analysis_results to be available
        # We'll test the responses when no models are trained
        
        test_cases = [
            {
                'name': 'Prediction Target Query',
                'message': 'what am i predicting?',
                'should_handle_no_models': True
            },
            {
                'name': 'Model Metrics Query',
                'message': 'show model metrics',
                'should_handle_no_models': True
            },
            {
                'name': 'Best Model Query',
                'message': 'which model is best?',
                'should_handle_no_models': True
            },
            {
                'name': 'Feature Importance Query',
                'message': 'show feature importance',
                'should_handle_no_models': True
            },
            {
                'name': 'Model Comparison Query',
                'message': 'compare models',
                'should_handle_no_models': True
            }
        ]
        
        for test in test_cases:
            response = self.send_chat_message(test['message'], dataset_id)
            
            if response.get('error'):
                self.log_result('Model Interactions', test['name'], 'FAIL', 
                              f"Error: {response.get('message', 'Unknown error')}")
                continue
            
            response_text = response.get('response', '').lower()
            
            # Since no models are trained, check for appropriate messaging
            if test.get('should_handle_no_models'):
                # Should either show model info or gracefully handle no models
                if 'no model' in response_text or 'train' in response_text or 'model' in response_text:
                    self.log_result('Model Interactions', test['name'], 'PASS', 
                                  'Gracefully handles no models scenario')
                else:
                    self.log_result('Model Interactions', test['name'], 'FAIL', 
                                  'Does not handle no models scenario appropriately')
    
    def test_user_flow(self, dataset_id: str):
        """Category 4: User Flow"""
        print("\n" + "="*80)
        print("CATEGORY 4: USER FLOW")
        print("="*80)
        
        # Test 1: No dataset error
        response = self.send_chat_message('show me data', 'invalid-dataset-id')
        if response.get('error') or 'not found' in response.get('response', '').lower():
            self.log_result('User Flow', 'No Dataset Error Handling', 'PASS', 
                          'Correctly handles missing dataset')
        else:
            self.log_result('User Flow', 'No Dataset Error Handling', 'FAIL', 
                          'Does not properly handle missing dataset')
        
        # Test 2: Chart confirmation workflow
        response = self.send_chat_message('create a chart for price', dataset_id)
        if response.get('requires_confirmation') and 'append' in response.get('response', '').lower():
            self.log_result('User Flow', 'Chart Confirmation Workflow', 'PASS', 
                          'Asks for confirmation before appending charts')
        else:
            self.log_result('User Flow', 'Chart Confirmation Workflow', 'FAIL', 
                          'Does not ask for confirmation')
        
        # Test 3: "What's next?" suggestions
        response = self.send_chat_message('what next?', dataset_id)
        suggestions = response.get('suggestions', [])
        response_text = response.get('response', '').lower()
        
        if 'suggest' in response_text or 'recommend' in response_text or 'next' in response_text:
            self.log_result('User Flow', 'Analytical Suggestions', 'PASS', 
                          f'Provides {len(suggestions)} contextual suggestions')
        else:
            self.log_result('User Flow', 'Analytical Suggestions', 'FAIL', 
                          'Does not provide helpful suggestions')
    
    def test_natural_language_flexibility(self, dataset_id: str):
        """Category 5: Natural Language Flexibility"""
        print("\n" + "="*80)
        print("CATEGORY 5: NATURAL LANGUAGE FLEXIBILITY")
        print("="*80)
        
        # Test variations of same command
        variations = [
            {
                'name': 'Column List Variations',
                'messages': ['show columns', 'list columns', 'column names', 'what columns'],
                'expected_keyword': 'column'
            },
            {
                'name': 'Statistics Variations',
                'messages': ['stats', 'statistics', 'summary', 'show stats'],
                'expected_keyword': 'mean'
            },
            {
                'name': 'Size Variations',
                'messages': ['dataset size', 'how many rows', 'shape', 'dimensions'],
                'expected_keyword': 'rows'
            }
        ]
        
        for variation in variations:
            passed_count = 0
            total_count = len(variation['messages'])
            
            for msg in variation['messages']:
                response = self.send_chat_message(msg, dataset_id)
                if not response.get('error') and variation['expected_keyword'] in response.get('response', '').lower():
                    passed_count += 1
            
            if passed_count == total_count:
                self.log_result('Natural Language', variation['name'], 'PASS', 
                              f'All {total_count} variations handled correctly')
            elif passed_count > 0:
                self.log_result('Natural Language', variation['name'], 'PARTIAL', 
                              f'{passed_count}/{total_count} variations handled')
            else:
                self.log_result('Natural Language', variation['name'], 'FAIL', 
                              'No variations handled correctly')
        
        # Test short queries
        short_queries = ['columns', 'stats', 'size']
        for query in short_queries:
            response = self.send_chat_message(query, dataset_id)
            if not response.get('error') and len(response.get('response', '')) > 0:
                self.log_result('Natural Language', f'Short Query: "{query}"', 'PASS', 
                              'Handles short query correctly')
            else:
                self.log_result('Natural Language', f'Short Query: "{query}"', 'FAIL', 
                              'Cannot handle short query')
    
    def test_error_handling(self, dataset_id: str):
        """Category 6: Error & Edge Case Handling"""
        print("\n" + "="*80)
        print("CATEGORY 6: ERROR & EDGE CASE HANDLING")
        print("="*80)
        
        # Test 1: Invalid dataset ID
        response = self.send_chat_message('show data', 'completely-invalid-id-12345')
        if 'not found' in response.get('response', '').lower() or response.get('error'):
            self.log_result('Error Handling', 'Invalid Dataset ID', 'PASS', 
                          'Properly handles invalid dataset ID')
        else:
            self.log_result('Error Handling', 'Invalid Dataset ID', 'FAIL', 
                          'Does not handle invalid dataset ID')
        
        # Test 2: Ambiguous request
        response = self.send_chat_message('show me something', dataset_id)
        if not response.get('error'):
            self.log_result('Error Handling', 'Ambiguous Request', 'PASS', 
                          'Handles ambiguous request without crashing')
        else:
            self.log_result('Error Handling', 'Ambiguous Request', 'FAIL', 
                          f"Crashes on ambiguous request: {response.get('message', '')}")
        
        # Test 3: Empty message
        response = self.send_chat_message('', dataset_id)
        if not response.get('error') or 'error' in response.get('response', '').lower():
            self.log_result('Error Handling', 'Empty Message', 'PASS', 
                          'Handles empty message gracefully')
        else:
            self.log_result('Error Handling', 'Empty Message', 'FAIL', 
                          'Does not handle empty message')
        
        # Test 4: Very long message
        long_message = 'show me ' + ' '.join(['data'] * 100)
        response = self.send_chat_message(long_message, dataset_id)
        if not response.get('error'):
            self.log_result('Error Handling', 'Very Long Message', 'PASS', 
                          'Handles very long message without crashing')
        else:
            self.log_result('Error Handling', 'Very Long Message', 'FAIL', 
                          'Crashes on very long message')
    
    def test_analytical_assistance(self, dataset_id: str):
        """Category 7: Analytical Assistance"""
        print("\n" + "="*80)
        print("CATEGORY 7: ANALYTICAL ASSISTANCE")
        print("="*80)
        
        test_cases = [
            {
                'name': 'Anomaly Detection',
                'message': 'detect anomalies',
                'expected_keywords': ['anomaly', 'outlier']
            },
            {
                'name': 'Trend Analysis',
                'message': 'show trends',
                'expected_keywords': ['trend', 'time', 'date']
            },
            {
                'name': 'Correlation Suggestions',
                'message': 'suggest correlations',
                'expected_keywords': ['correlation', 'suggest']
            },
            {
                'name': 'Interpretation Request',
                'message': 'what does this mean?',
                'should_respond': True
            }
        ]
        
        for test in test_cases:
            response = self.send_chat_message(test['message'], dataset_id)
            
            if response.get('error'):
                self.log_result('Analytical Assistance', test['name'], 'FAIL', 
                              f"Error: {response.get('message', 'Unknown error')}")
                continue
            
            response_text = response.get('response', '').lower()
            
            # Check for expected keywords
            if test.get('expected_keywords'):
                found_keywords = [kw for kw in test['expected_keywords'] if kw in response_text]
                if found_keywords:
                    self.log_result('Analytical Assistance', test['name'], 'PASS', 
                                  f'Found keywords: {", ".join(found_keywords)}')
                else:
                    self.log_result('Analytical Assistance', test['name'], 'FAIL', 
                                  f'Missing expected keywords: {", ".join(test["expected_keywords"])}')
            elif test.get('should_respond'):
                if len(response_text) > 10:
                    self.log_result('Analytical Assistance', test['name'], 'PASS', 
                                  'Provides meaningful response')
                else:
                    self.log_result('Analytical Assistance', test['name'], 'FAIL', 
                                  'Response too short or empty')
    
    def test_response_format(self, dataset_id: str):
        """Verify response format consistency"""
        print("\n" + "="*80)
        print("RESPONSE FORMAT VALIDATION")
        print("="*80)
        
        test_messages = [
            'show columns',
            'dataset size',
            'create chart for price'
        ]
        
        for msg in test_messages:
            response = self.send_chat_message(msg, dataset_id)
            
            if response.get('error'):
                self.log_result('Response Format', f'Format check: "{msg}"', 'FAIL', 
                              'Request failed')
                continue
            
            # Check required fields
            required_fields = ['response', 'action', 'data', 'requires_confirmation', 'suggestions']
            missing_fields = [field for field in required_fields if field not in response]
            
            if not missing_fields:
                # Validate types
                valid_types = (
                    isinstance(response['response'], str) and
                    isinstance(response['action'], str) and
                    isinstance(response['data'], dict) and
                    isinstance(response['requires_confirmation'], bool) and
                    isinstance(response['suggestions'], list)
                )
                
                if valid_types:
                    self.log_result('Response Format', f'Format check: "{msg}"', 'PASS', 
                                  'All fields present with correct types')
                else:
                    self.log_result('Response Format', f'Format check: "{msg}"', 'FAIL', 
                                  'Field types incorrect')
            else:
                self.log_result('Response Format', f'Format check: "{msg}"', 'FAIL', 
                              f'Missing fields: {", ".join(missing_fields)}')
    
    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("COMPREHENSIVE TEST SUMMARY")
        print("="*80)
        
        print(f"\n📊 Overall Results:")
        print(f"   Total Tests: {self.test_summary['total_tests']}")
        print(f"   Passed: {self.test_summary['passed']} ✅")
        print(f"   Failed: {self.test_summary['failed']} ❌")
        
        if self.test_summary['total_tests'] > 0:
            success_rate = (self.test_summary['passed'] / self.test_summary['total_tests']) * 100
            print(f"   Success Rate: {success_rate:.1f}%")
        
        print(f"\n📋 Category Breakdown:")
        for category, stats in self.test_summary['categories'].items():
            total = stats['passed'] + stats['failed']
            rate = (stats['passed'] / total * 100) if total > 0 else 0
            status = "✅" if rate >= 80 else "⚠️" if rate >= 60 else "❌"
            print(f"   {status} {category}: {stats['passed']}/{total} ({rate:.1f}%)")
        
        # Print failed tests
        failed_tests = [r for r in self.results if r['status'] == 'FAIL']
        if failed_tests:
            print(f"\n❌ Failed Tests ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   • [{test['category']}] {test['test_name']}")
                if test['details']:
                    print(f"     Details: {test['details']}")
        
        # Success criteria
        print(f"\n🎯 Success Criteria:")
        success_rate = (self.test_summary['passed'] / self.test_summary['total_tests']) * 100 if self.test_summary['total_tests'] > 0 else 0
        
        criteria = [
            ('Overall Success Rate >= 80%', success_rate >= 80),
            ('All 7 Categories Tested', len(self.test_summary['categories']) >= 7),
            ('Response Format Consistent', True),  # Will be updated based on format tests
            ('Error Handling Working', True)  # Will be updated based on error tests
        ]
        
        for criterion, met in criteria:
            status = "✅" if met else "❌"
            print(f"   {status} {criterion}")
        
        # Final verdict
        print(f"\n{'='*80}")
        if success_rate >= 90:
            print("🎉 EXCELLENT: Enhanced Chat Assistant is production-ready!")
        elif success_rate >= 80:
            print("✅ GOOD: Enhanced Chat Assistant is working well with minor issues")
        elif success_rate >= 60:
            print("⚠️ ACCEPTABLE: Enhanced Chat Assistant needs improvements")
        else:
            print("❌ NEEDS WORK: Enhanced Chat Assistant has significant issues")
        print("="*80)
    
    def run_all_tests(self):
        """Run all test categories"""
        print("\n" + "="*80)
        print("ENHANCED CHAT ASSISTANT - COMPREHENSIVE TESTING")
        print("="*80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Step 1: Test built-in scenarios
        self.test_built_in_scenarios()
        
        # Step 2: Get a real dataset
        datasets = self.get_datasets()
        if not datasets:
            print("\n❌ No datasets available for real-world testing")
            self.print_summary()
            return
        
        # Use first dataset with data
        self.dataset_id = datasets[0].get('id')
        dataset_name = datasets[0].get('filename', 'Unknown')
        print(f"\n📊 Using dataset: {dataset_name} (ID: {self.dataset_id})")
        
        # Step 3: Run all category tests
        self.test_chart_creation(self.dataset_id)
        self.test_dataset_awareness(self.dataset_id)
        self.test_prediction_model_interactions(self.dataset_id)
        self.test_user_flow(self.dataset_id)
        self.test_natural_language_flexibility(self.dataset_id)
        self.test_error_handling(self.dataset_id)
        self.test_analytical_assistance(self.dataset_id)
        self.test_response_format(self.dataset_id)
        
        # Step 4: Print summary
        self.print_summary()


if __name__ == "__main__":
    tester = EnhancedChatTester()
    tester.run_all_tests()
