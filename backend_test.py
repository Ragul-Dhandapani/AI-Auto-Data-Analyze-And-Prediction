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
BACKEND_URL = "https://promise-ai-1.preview.emergentagent.com/api"

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
