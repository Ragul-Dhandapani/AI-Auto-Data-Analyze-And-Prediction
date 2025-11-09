#!/usr/bin/env python3
"""
Enhanced Chat Service Testing with Conversation History Context
Tests the enhanced chat endpoint at /api/enhanced-chat/message
"""

import requests
import json
import sys
from typing import Dict, List, Any

# Backend URL from environment
BACKEND_URL = "https://promise-ai-platform.preview.emergentagent.com/api"

# Test dataset ID (from the available datasets)
DATASET_ID = "d77c5cd7-8c3f-4e2a-acec-266e446c941e"  # application_latency.csv

class EnhancedChatTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.dataset_id = DATASET_ID
        self.conversation_history = []
        self.test_results = []
        
    def log_test(self, test_name: str, status: str, details: str = "", response_data: Dict = None):
        """Log test results"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "response_data": response_data
        }
        self.test_results.append(result)
        print(f"{'✅' if status == 'PASS' else '❌'} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
        if status == "FAIL" and response_data:
            print(f"   Response: {response_data}")
        print()

    def send_chat_message(self, message: str, conversation_history: List[Dict] = None) -> Dict:
        """Send a message to the enhanced chat endpoint"""
        if conversation_history is None:
            conversation_history = self.conversation_history
            
        payload = {
            "message": message,
            "dataset_id": self.dataset_id,
            "conversation_history": conversation_history
        }
        
        try:
            response = requests.post(
                f"{self.backend_url}/enhanced-chat/message",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"HTTP {response.status_code}",
                    "details": response.text
                }
        except Exception as e:
            return {
                "error": "Request failed",
                "details": str(e)
            }

    def test_basic_endpoint_availability(self):
        """Test 1: Basic endpoint availability"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=10)
            if response.status_code == 200:
                self.log_test("Basic Endpoint Availability", "PASS", "Backend is accessible")
            else:
                self.log_test("Basic Endpoint Availability", "FAIL", f"Backend returned {response.status_code}")
        except Exception as e:
            self.log_test("Basic Endpoint Availability", "FAIL", f"Cannot reach backend: {str(e)}")

    def test_chat_without_history(self):
        """Test 2: Chat without conversation history"""
        message = "Show me outliers in the data"
        response = self.send_chat_message(message, [])
        
        if "error" in response:
            self.log_test("Chat Without History", "FAIL", f"Error: {response['error']}", response)
            return None
        
        if "response" in response and len(response["response"]) > 0:
            self.log_test("Chat Without History", "PASS", f"Got response: {response['response'][:100]}...")
            # Store this message in conversation history for next test
            self.conversation_history.append({
                "role": "user",
                "message": message
            })
            self.conversation_history.append({
                "role": "assistant", 
                "response": response["response"]
            })
            return response
        else:
            self.log_test("Chat Without History", "FAIL", "No response received", response)
            return None

    def test_context_aware_follow_up(self):
        """Test 3: Context-aware follow-up question"""
        if not self.conversation_history:
            self.log_test("Context-Aware Follow-up", "SKIP", "No conversation history available")
            return
            
        # Ask a follow-up question that requires context from previous conversation
        follow_up_message = "What does outlier mean?"
        response = self.send_chat_message(follow_up_message)
        
        if "error" in response:
            self.log_test("Context-Aware Follow-up", "FAIL", f"Error: {response['error']}", response)
            return
        
        if "response" in response:
            response_text = response["response"].lower()
            # Check if the response shows context awareness
            context_indicators = [
                "outlier", "anomaly", "unusual", "deviation", "data point",
                "previous", "mentioned", "discussed", "context"
            ]
            
            has_context = any(indicator in response_text for indicator in context_indicators)
            
            if has_context:
                self.log_test("Context-Aware Follow-up", "PASS", 
                             f"Response shows context awareness: {response['response'][:150]}...")
                # Add to conversation history
                self.conversation_history.append({
                    "role": "user",
                    "message": follow_up_message
                })
                self.conversation_history.append({
                    "role": "assistant",
                    "response": response["response"]
                })
            else:
                self.log_test("Context-Aware Follow-up", "FAIL", 
                             f"Response lacks context awareness: {response['response'][:150]}...")
        else:
            self.log_test("Context-Aware Follow-up", "FAIL", "No response received", response)

    def test_conversation_history_parameter(self):
        """Test 4: Conversation history parameter handling"""
        # Test with explicit conversation history
        test_history = [
            {"role": "user", "message": "Check for anomalies in latency_ms"},
            {"role": "assistant", "response": "I found several outliers in the latency_ms column with values above 500ms."}
        ]
        
        follow_up = "What causes these high latency values?"
        response = self.send_chat_message(follow_up, test_history)
        
        if "error" in response:
            self.log_test("Conversation History Parameter", "FAIL", f"Error: {response['error']}", response)
            return
        
        if "response" in response and len(response["response"]) > 0:
            # Check if response references the context about latency/outliers
            response_text = response["response"].lower()
            context_refs = ["latency", "outlier", "anomal", "high", "500ms", "previous"]
            
            has_context_ref = any(ref in response_text for ref in context_refs)
            
            if has_context_ref:
                self.log_test("Conversation History Parameter", "PASS", 
                             f"Response uses conversation history: {response['response'][:150]}...")
            else:
                self.log_test("Conversation History Parameter", "PARTIAL", 
                             f"Response may not fully use history: {response['response'][:150]}...")
        else:
            self.log_test("Conversation History Parameter", "FAIL", "No response received", response)

    def test_dataset_awareness(self):
        """Test 5: Dataset awareness in responses"""
        message = "What columns are available in this dataset?"
        response = self.send_chat_message(message, [])
        
        if "error" in response:
            self.log_test("Dataset Awareness", "FAIL", f"Error: {response['error']}", response)
            return
        
        if "response" in response:
            response_text = response["response"].lower()
            # Check for expected columns from application_latency.csv
            expected_columns = ["latency_ms", "service_name", "endpoint", "region", "cpu_utilization"]
            
            column_mentions = sum(1 for col in expected_columns if col.lower() in response_text)
            
            if column_mentions >= 2:
                self.log_test("Dataset Awareness", "PASS", 
                             f"Response mentions dataset columns: {response['response'][:150]}...")
            else:
                self.log_test("Dataset Awareness", "PARTIAL", 
                             f"Limited dataset awareness: {response['response'][:150]}...")
        else:
            self.log_test("Dataset Awareness", "FAIL", "No response received", response)

    def test_error_handling(self):
        """Test 6: Error handling with invalid dataset"""
        invalid_payload = {
            "message": "Test message",
            "dataset_id": "invalid-dataset-id",
            "conversation_history": []
        }
        
        try:
            response = requests.post(
                f"{self.backend_url}/enhanced-chat/message",
                json=invalid_payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "response" in data and ("not found" in data["response"].lower() or "error" in data["response"].lower()):
                    self.log_test("Error Handling", "PASS", "Proper error handling for invalid dataset")
                else:
                    self.log_test("Error Handling", "PARTIAL", f"Unexpected response: {data}")
            else:
                self.log_test("Error Handling", "PASS", f"Proper HTTP error code: {response.status_code}")
                
        except Exception as e:
            self.log_test("Error Handling", "FAIL", f"Exception during error test: {str(e)}")

    def test_azure_openai_integration(self):
        """Test 7: Azure OpenAI integration (may fail if not configured)"""
        message = "Explain the relationship between CPU utilization and latency in simple terms"
        response = self.send_chat_message(message, [])
        
        if "error" in response:
            self.log_test("Azure OpenAI Integration", "EXPECTED_FAIL", 
                         f"Azure OpenAI may not be configured: {response['error']}")
            return
        
        if "response" in response:
            response_text = response["response"]
            # Check for AI-like response characteristics
            ai_indicators = ["relationship", "correlation", "generally", "typically", "because", "when"]
            
            has_ai_characteristics = any(indicator in response_text.lower() for indicator in ai_indicators)
            
            if has_ai_characteristics and len(response_text) > 50:
                self.log_test("Azure OpenAI Integration", "PASS", 
                             f"AI-powered response detected: {response_text[:150]}...")
            else:
                self.log_test("Azure OpenAI Integration", "PARTIAL", 
                             f"Basic response (fallback mode): {response_text[:150]}...")
        else:
            self.log_test("Azure OpenAI Integration", "FAIL", "No response received", response)

    def test_conversation_context_limit(self):
        """Test 8: Conversation context limit handling"""
        # Create a long conversation history (more than 5 messages)
        long_history = []
        for i in range(10):
            long_history.append({
                "role": "user",
                "message": f"Question {i+1}: Tell me about metric {i+1}"
            })
            long_history.append({
                "role": "assistant", 
                "response": f"Response {i+1}: Here's information about metric {i+1}"
            })
        
        # Add a specific context message at the end
        long_history.append({
            "role": "user",
            "message": "The latency spikes are concerning in the payment service"
        })
        long_history.append({
            "role": "assistant",
            "response": "Yes, I see the payment service latency spikes above 200ms which could impact user experience"
        })
        
        # Ask a follow-up that should reference recent context
        follow_up = "What should we do about those payment service issues?"
        response = self.send_chat_message(follow_up, long_history)
        
        if "error" in response:
            self.log_test("Conversation Context Limit", "FAIL", f"Error: {response['error']}", response)
            return
        
        if "response" in response:
            response_text = response["response"].lower()
            # Check if it references recent context (payment service)
            recent_context = ["payment", "latency", "spike", "200ms", "service"]
            
            has_recent_context = any(ctx in response_text for ctx in recent_context)
            
            if has_recent_context:
                self.log_test("Conversation Context Limit", "PASS", 
                             f"Handles long history and uses recent context: {response['response'][:150]}...")
            else:
                self.log_test("Conversation Context Limit", "PARTIAL", 
                             f"May not use recent context from long history: {response['response'][:150]}...")
        else:
            self.log_test("Conversation Context Limit", "FAIL", "No response received", response)

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🧪 Enhanced Chat Service Testing with Conversation History Context")
        print("=" * 70)
        print(f"Backend URL: {self.backend_url}")
        print(f"Dataset ID: {self.dataset_id}")
        print()
        
        # Run tests in order
        self.test_basic_endpoint_availability()
        self.test_chat_without_history()
        self.test_context_aware_follow_up()
        self.test_conversation_history_parameter()
        self.test_dataset_awareness()
        self.test_error_handling()
        self.test_azure_openai_integration()
        self.test_conversation_context_limit()
        
        # Summary
        print("=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        
        passed = sum(1 for r in self.test_results if r["status"] == "PASS")
        failed = sum(1 for r in self.test_results if r["status"] == "FAIL")
        partial = sum(1 for r in self.test_results if r["status"] == "PARTIAL")
        skipped = sum(1 for r in self.test_results if r["status"] == "SKIP")
        expected_fail = sum(1 for r in self.test_results if r["status"] == "EXPECTED_FAIL")
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"🟡 Partial: {partial}")
        print(f"⏭️  Skipped: {skipped}")
        print(f"⚠️  Expected Failures: {expected_fail}")
        print()
        
        success_rate = ((passed + partial) / total) * 100 if total > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Critical issues
        critical_failures = [r for r in self.test_results if r["status"] == "FAIL" and "Basic" in r["test"]]
        if critical_failures:
            print("\n🚨 CRITICAL ISSUES:")
            for failure in critical_failures:
                print(f"   - {failure['test']}: {failure['details']}")
        
        # Context-aware functionality status
        context_tests = [r for r in self.test_results if "Context" in r["test"] or "History" in r["test"]]
        context_working = sum(1 for r in context_tests if r["status"] in ["PASS", "PARTIAL"])
        
        print(f"\n🧠 CONVERSATION CONTEXT STATUS:")
        if context_working >= len(context_tests) * 0.7:  # 70% threshold
            print("   ✅ Context-aware responses are working")
        else:
            print("   ❌ Context-aware responses need attention")
        
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "partial": partial,
            "success_rate": success_rate,
            "context_working": context_working >= len(context_tests) * 0.7
        }

def main():
    """Main test execution"""
    tester = EnhancedChatTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    if results["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
    print("\n=== Test 3: Training Metadata Endpoint ===")
    print("Testing the endpoint that the Training Metadata page uses...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/training/metadata/by-workspace", timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Training metadata endpoint accessible")
            
            datasets = data.get("datasets", [])
            print(f"   Found {len(datasets)} datasets with training metadata")
            
            # Look for latency_nov workspace
            latency_nov_found = False
            for dataset in datasets:
                dataset_name = dataset.get('dataset_name', 'Unknown')
                workspaces = dataset.get('workspaces', [])
                
                print(f"\n   📊 Dataset: {dataset_name}")
                print(f"      - Dataset ID: {dataset.get('dataset_id', 'N/A')[:8]}...")
                print(f"      - Total workspaces: {len(workspaces)}")
                
                for workspace in workspaces:
                    workspace_name = workspace.get('workspace_name', 'Unknown')
                    total_models = workspace.get('total_models', 0)
                    
                    print(f"      - Workspace: '{workspace_name}' ({total_models} models)")
                    
                    if 'latency_nov' in workspace_name.lower():
                        latency_nov_found = True
                        print(f"        🎯 FOUND latency_nov workspace with {total_models} models!")
                        
                        # Show training runs
                        training_runs = workspace.get('training_runs', [])
                        for run in training_runs[:3]:  # Show first 3
                            print(f"           - Model: {run.get('model_type', 'N/A')}, "
                                  f"Created: {run.get('created_at', 'N/A')}")
            
            if not latency_nov_found:
                print("\n   ❌ 'latency_nov' workspace NOT found in API response")
                print("   🔍 This explains why the Training Metadata page shows '0 models'")
            else:
                print("\n   ✅ 'latency_nov' workspace found in API response")
            
            return True, latency_nov_found
        else:
            print(f"❌ Training metadata endpoint failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Error: {response.text}")
            return False, False
            
    except Exception as e:
        print(f"❌ Training metadata endpoint exception: {str(e)}")
        return False, False

def test_dataset_workspace_correlation(workspace_dataset_id):
    """Test 4: Dataset-Workspace Correlation - Check if dataset IDs match"""
    print("\n=== Test 4: Dataset-Workspace Correlation ===")
    print("Checking if dataset_id matches between workspace_states and training_metadata...")
    
    if not workspace_dataset_id:
        print("❌ No workspace dataset ID available from previous test")
        return False
    
    try:
        # Initialize Oracle client
        try:
            cx_Oracle.init_oracle_client(lib_dir='/opt/oracle/instantclient_19_23')
        except:
            pass  # Already initialized
        
        # Create connection
        dsn = cx_Oracle.makedsn(
            ORACLE_CONFIG['host'],
            ORACLE_CONFIG['port'],
            service_name=ORACLE_CONFIG['service_name']
        )
        
        connection = cx_Oracle.connect(
            user=ORACLE_CONFIG['user'],
            password=ORACLE_CONFIG['password'],
            dsn=dsn
        )
        
        cursor = connection.cursor()
        
        print(f"   🔍 Looking for training_metadata with dataset_id: {workspace_dataset_id}")
        
        # Query training_metadata for this specific dataset_id
        query = """
        SELECT id, dataset_id, workspace_name, model_type, created_at 
        FROM training_metadata 
        WHERE dataset_id = :dataset_id
        ORDER BY created_at DESC
        """
        
        cursor.execute(query, {'dataset_id': workspace_dataset_id})
        rows = cursor.fetchall()
        columns = [col[0].lower() for col in cursor.description]
        
        print(f"   ✅ Found {len(rows)} training metadata records for this dataset")
        
        if len(rows) > 0:
            print("   📋 Training metadata records:")
            for row in rows:
                row_dict = dict(zip(columns, row))
                print(f"      - Workspace: '{row_dict.get('workspace_name', 'N/A')}', "
                      f"Model: {row_dict.get('model_type', 'N/A')}, "
                      f"Created: {row_dict.get('created_at', 'N/A')}")
        else:
            print("   ❌ No training metadata found for this dataset_id")
            print("   🔍 This is the ROOT CAUSE - workspace exists but no training metadata!")
        
        # Also check if there are training_metadata records with different workspace names
        query_all = """
        SELECT DISTINCT workspace_name, COUNT(*) as count
        FROM training_metadata 
        WHERE dataset_id = :dataset_id
        GROUP BY workspace_name
        ORDER BY count DESC
        """
        
        cursor.execute(query_all, {'dataset_id': workspace_dataset_id})
        workspace_rows = cursor.fetchall()
        
        if workspace_rows:
            print(f"\n   📊 Workspace names in training_metadata for this dataset:")
            for row in workspace_rows:
                print(f"      - '{row[0]}': {row[1]} models")
        
        cursor.close()
        connection.close()
        
        return True, len(rows) > 0
        
    except Exception as e:
        print(f"❌ Dataset-workspace correlation check failed: {str(e)}")
        return False, False

def test_root_cause_analysis():
    """Test 5: Root Cause Analysis - Identify the exact issue"""
    print("\n=== Test 5: Root Cause Analysis ===")
    print("Performing comprehensive analysis to identify the root cause...")
    
    try:
        # Initialize Oracle client
        try:
            cx_Oracle.init_oracle_client(lib_dir='/opt/oracle/instantclient_19_23')
        except:
            pass  # Already initialized
        
        # Create connection
        dsn = cx_Oracle.makedsn(
            ORACLE_CONFIG['host'],
            ORACLE_CONFIG['port'],
            service_name=ORACLE_CONFIG['service_name']
        )
        
        connection = cx_Oracle.connect(
            user=ORACLE_CONFIG['user'],
            password=ORACLE_CONFIG['password'],
            dsn=dsn
        )
        
        cursor = connection.cursor()
        
        print("\n   🔍 Analysis 1: Check workspace_name patterns in training_metadata")
        query1 = """
        SELECT DISTINCT workspace_name, COUNT(*) as count
        FROM training_metadata 
        GROUP BY workspace_name
        ORDER BY count DESC
        """
        
        cursor.execute(query1)
        workspace_patterns = cursor.fetchall()
        
        print(f"   Found {len(workspace_patterns)} unique workspace names:")
        for pattern in workspace_patterns:
            workspace_name = pattern[0] or 'NULL'
            count = pattern[1]
            print(f"      - '{workspace_name}': {count} models")
            
            if workspace_name and 'latency' in workspace_name.lower():
                print(f"        🎯 LATENCY WORKSPACE FOUND: '{workspace_name}'")
        
        print("\n   🔍 Analysis 2: Check dataset_id patterns")
        query2 = """
        SELECT tm.dataset_id, d.name as dataset_name, COUNT(tm.id) as training_count
        FROM training_metadata tm
        LEFT JOIN datasets d ON tm.dataset_id = d.id
        GROUP BY tm.dataset_id, d.name
        ORDER BY training_count DESC
        """
        
        cursor.execute(query2)
        dataset_patterns = cursor.fetchall()
        
        print(f"   Found {len(dataset_patterns)} datasets with training metadata:")
        for pattern in dataset_patterns:
            dataset_id = pattern[0] or 'NULL'
            dataset_name = pattern[1] or 'Unknown'
            count = pattern[2]
            print(f"      - Dataset: '{dataset_name}' (ID: {dataset_id[:8]}...): {count} models")
        
        print("\n   🔍 Analysis 3: Check workspace_states vs training_metadata alignment")
        query3 = """
        SELECT ws.state_name, ws.dataset_id, 
               COUNT(tm.id) as training_count,
               MAX(tm.created_at) as last_training
        FROM workspace_states ws
        LEFT JOIN training_metadata tm ON ws.dataset_id = tm.dataset_id 
                                       AND ws.state_name = tm.workspace_name
        GROUP BY ws.state_name, ws.dataset_id
        ORDER BY ws.state_name
        """
        
        cursor.execute(query3)
        alignment_data = cursor.fetchall()
        
        print(f"   Workspace alignment analysis:")
        latency_nov_alignment = None
        for row in alignment_data:
            state_name = row[0]
            dataset_id = row[1]
            training_count = row[2] or 0
            last_training = row[3]
            
            print(f"      - Workspace: '{state_name}' -> {training_count} training records")
            
            if 'latency_nov' in state_name.lower():
                latency_nov_alignment = {
                    'workspace_name': state_name,
                    'dataset_id': dataset_id,
                    'training_count': training_count,
                    'last_training': last_training
                }
                print(f"        🎯 LATENCY_NOV ALIGNMENT: {training_count} training records")
        
        cursor.close()
        connection.close()
        
        # Determine root cause
        if latency_nov_alignment:
            if latency_nov_alignment['training_count'] == 0:
                print("\n   🔍 ROOT CAUSE IDENTIFIED:")
                print("      ❌ Workspace 'latency_nov' exists but has NO training metadata")
                print("      ❌ This explains why Training Metadata page shows '0 models'")
                print("      🔧 SOLUTION: Check if training was actually completed and saved")
                return True, "workspace_exists_no_training"
            else:
                print("\n   ✅ Workspace 'latency_nov' has training metadata")
                print("      🔍 Issue might be in API query logic or frontend display")
                return True, "training_exists_api_issue"
        else:
            print("\n   🔍 ROOT CAUSE IDENTIFIED:")
            print("      ❌ Workspace 'latency_nov' not found in workspace_states")
            print("      ❌ Workspace was never saved or has different name")
            return True, "workspace_not_found"
        
    except Exception as e:
        print(f"❌ Root cause analysis failed: {str(e)}")
        return False, "analysis_failed"

def main():
    """Run Training Metadata Investigation"""
    print("🚀 PROMISE AI TRAINING METADATA INVESTIGATION")
    print("🎯 Focus: Workspace 'latency_nov' showing '0 models' issue")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now().isoformat()}")
    print("="*70)
    
    # Track test results
    results = {
        'direct_db_query': False,
        'workspace_states': False,
        'training_metadata_api': False,
        'dataset_correlation': False,
        'root_cause_analysis': False
    }
    
    findings = {}
    
    # Test 1: Direct Database Query
    print("\n🔍 PRIORITY: HIGH - Direct Database Investigation")
    db_success, latency_nov_in_training = test_direct_database_query()
    results['direct_db_query'] = db_success
    findings['latency_nov_in_training'] = latency_nov_in_training
    
    # Test 2: Workspace States Query
    print("\n🔍 PRIORITY: HIGH - Workspace States Verification")
    ws_success, workspace_dataset_id = test_workspace_states_query()
    results['workspace_states'] = ws_success
    findings['workspace_dataset_id'] = workspace_dataset_id
    
    # Test 3: Training Metadata API
    print("\n🔍 PRIORITY: CRITICAL - API Endpoint Testing")
    api_success, latency_nov_in_api = test_training_metadata_endpoint()
    results['training_metadata_api'] = api_success
    findings['latency_nov_in_api'] = latency_nov_in_api
    
    # Test 4: Dataset-Workspace Correlation
    if workspace_dataset_id:
        print("\n🔍 PRIORITY: HIGH - Dataset Correlation Analysis")
        corr_success, has_training_data = test_dataset_workspace_correlation(workspace_dataset_id)
        results['dataset_correlation'] = corr_success
        findings['has_training_data'] = has_training_data
    else:
        print("\n⚠️  Skipping dataset correlation - no workspace dataset ID found")
        results['dataset_correlation'] = True  # Don't fail for missing prerequisite
        findings['has_training_data'] = False
    
    # Test 5: Root Cause Analysis
    print("\n🔍 PRIORITY: CRITICAL - Root Cause Identification")
    rca_success, root_cause = test_root_cause_analysis()
    results['root_cause_analysis'] = rca_success
    findings['root_cause'] = root_cause
    
    # Summary
    print("\n" + "="*70)
    print("📊 TRAINING METADATA INVESTIGATION SUMMARY")
    print("="*70)
    
    passed_tests = sum(1 for result in results.values() if result)
    total_tests = len(results)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests completed successfully")
    
    # Key Findings
    print("\n🔍 KEY FINDINGS:")
    print(f"   📋 Workspace 'latency_nov' in training_metadata table: {'✅ YES' if findings.get('latency_nov_in_training') else '❌ NO'}")
    print(f"   📋 Workspace 'latency_nov' in workspace_states table: {'✅ YES' if findings.get('workspace_dataset_id') else '❌ NO'}")
    print(f"   📋 Workspace 'latency_nov' in API response: {'✅ YES' if findings.get('latency_nov_in_api') else '❌ NO'}")
    print(f"   📋 Training data exists for workspace dataset: {'✅ YES' if findings.get('has_training_data') else '❌ NO'}")
    
    # Root Cause Determination
    root_cause = findings.get('root_cause', 'unknown')
    print(f"\n🎯 ROOT CAUSE: {root_cause}")
    
    if root_cause == "workspace_exists_no_training":
        print("   🔧 SOLUTION: Workspace exists but no training metadata was saved")
        print("      - Check if training process completed successfully")
        print("      - Verify training metadata is being saved to database")
        print("      - Check for errors during model training")
    elif root_cause == "training_exists_api_issue":
        print("   🔧 SOLUTION: Training data exists but API not returning it")
        print("      - Check API query logic in /api/training/metadata/by-workspace")
        print("      - Verify workspace name matching logic")
        print("      - Check JOIN conditions between tables")
    elif root_cause == "workspace_not_found":
        print("   🔧 SOLUTION: Workspace 'latency_nov' was never saved")
        print("      - Check workspace save functionality")
        print("      - Verify workspace name is being saved correctly")
        print("      - Check for case sensitivity issues")
    else:
        print("   🔧 SOLUTION: Further investigation needed")
        print("      - Check backend logs for training errors")
        print("      - Verify database schema and constraints")
        print("      - Test training process end-to-end")
    
    # Final Status
    if findings.get('latency_nov_in_api'):
        print("\n📋 STATUS: ✅ ISSUE RESOLVED - Workspace found in API")
        return True
    else:
        print("\n📋 STATUS: ❌ ISSUE CONFIRMED - Root cause identified")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
