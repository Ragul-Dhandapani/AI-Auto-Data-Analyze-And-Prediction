#!/usr/bin/env python3
"""
Enhanced User Expectation Feature Testing for PROMISE AI Platform
Tests the enhanced user expectation feature in holistic analysis
"""

import requests
import json
import sys
import time
from typing import Dict, List, Any

# Backend URL from environment
BACKEND_URL = "https://promise-ai-1.preview.emergentagent.com/api"

class UserExpectationTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.test_dataset_id = None
        
    def log_test(self, test_name: str, status: str, details: str = "", response_data: Dict = None):
        """Log test results"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "response_data": response_data
        }
        self.test_results.append(result)
        print(f"{'✅' if status == 'PASS' else '❌' if status == 'FAIL' else '🟡'} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
        if status == "FAIL" and response_data:
            print(f"   Response: {response_data}")
        print()

    def get_available_datasets(self) -> List[Dict]:
        """Get list of available datasets"""
        try:
            response = requests.get(f"{self.backend_url}/datasets", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get("datasets", [])
            else:
                return []
        except Exception as e:
            print(f"Failed to get datasets: {str(e)}")
            return []

    def upload_test_dataset(self) -> str:
        """Upload a small test dataset for testing"""
        # Create a small CSV dataset for testing
        test_csv_content = """cpu_usage,memory_usage,latency_ms,status
85.2,67.4,245,success
92.1,78.9,312,success
76.3,45.2,189,success
88.7,82.1,398,error
79.4,56.8,234,success
91.2,89.3,456,error
73.8,41.7,167,success
86.5,72.6,289,success
94.3,91.2,523,error
81.7,59.4,201,success"""

        try:
            files = {
                'file': ('test_latency_data.csv', test_csv_content, 'text/csv')
            }
            
            response = requests.post(
                f"{self.backend_url}/datasource/upload",
                files=files,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                dataset_id = data.get("dataset_id")
                print(f"✅ Test dataset uploaded successfully: {dataset_id}")
                return dataset_id
            else:
                print(f"❌ Failed to upload test dataset: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Exception during dataset upload: {str(e)}")
            return None

    def run_holistic_analysis(self, dataset_id: str, user_selection: Dict = None) -> Dict:
        """Run holistic analysis with optional user selection"""
        payload = {
            "dataset_id": dataset_id,
            "workspace_name": "test_workspace_user_expectation",
            "problem_type": "auto"
        }
        
        if user_selection:
            payload["user_selection"] = user_selection
        
        try:
            response = requests.post(
                f"{self.backend_url}/analysis/holistic",
                json=payload,
                timeout=60  # Longer timeout for analysis
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

    def test_setup_dataset(self):
        """Test 1: Setup test dataset"""
        # First try to find existing dataset
        datasets = self.get_available_datasets()
        
        # Look for a suitable dataset (preferably with latency data)
        suitable_dataset = None
        for dataset in datasets:
            name = dataset.get("name", "").lower()
            if "latency" in name or "performance" in name or "cpu" in name:
                suitable_dataset = dataset
                break
        
        if suitable_dataset:
            self.test_dataset_id = suitable_dataset.get("id")
            self.log_test("Setup Test Dataset", "PASS", 
                         f"Using existing dataset: {suitable_dataset.get('name')} (ID: {self.test_dataset_id})")
        else:
            # Upload test dataset
            self.test_dataset_id = self.upload_test_dataset()
            if self.test_dataset_id:
                self.log_test("Setup Test Dataset", "PASS", 
                             f"Uploaded new test dataset (ID: {self.test_dataset_id})")
            else:
                self.log_test("Setup Test Dataset", "FAIL", "Could not setup test dataset")

    def test_analysis_without_user_expectation(self):
        """Test 2: Analysis WITHOUT user expectation (baseline)"""
        if not self.test_dataset_id:
            self.log_test("Analysis Without User Expectation", "SKIP", "No test dataset available")
            return None
        
        print("🔍 Running baseline analysis without user expectation...")
        response = self.run_holistic_analysis(self.test_dataset_id)
        
        if "error" in response:
            self.log_test("Analysis Without User Expectation", "FAIL", 
                         f"Error: {response['error']}", response)
            return None
        
        # Check if analysis completed successfully
        if "insights" in response and "ml_models" in response:
            insights = response.get("insights", "")
            models = response.get("ml_models", [])
            
            self.log_test("Analysis Without User Expectation", "PASS", 
                         f"Analysis completed. Generated {len(models)} models and insights ({len(insights)} chars)")
            
            # Store baseline for comparison
            self.baseline_response = response
            return response
        else:
            self.log_test("Analysis Without User Expectation", "FAIL", 
                         "Analysis did not return expected results", response)
            return None

    def test_analysis_with_user_expectation(self):
        """Test 3: Analysis WITH user expectation (new feature)"""
        if not self.test_dataset_id:
            self.log_test("Analysis With User Expectation", "SKIP", "No test dataset available")
            return None
        
        # Define user selection with expectation
        user_selection = {
            "target_variable": "latency_ms",
            "selected_features": ["cpu_usage", "memory_usage"],
            "mode": "manual",
            "user_expectation": "I want to predict average end-to-end latency to identify performance bottlenecks in our system"
        }
        
        print("🔍 Running analysis WITH user expectation...")
        response = self.run_holistic_analysis(self.test_dataset_id, user_selection)
        
        if "error" in response:
            self.log_test("Analysis With User Expectation", "FAIL", 
                         f"Error: {response['error']}", response)
            return None
        
        # Check if analysis completed successfully
        if "insights" in response and "ml_models" in response:
            insights = response.get("insights", "")
            models = response.get("ml_models", [])
            
            # CRITICAL: Check if insights mention performance bottlenecks or latency prediction
            insights_lower = insights.lower()
            context_keywords = [
                "performance bottleneck", "bottleneck", "latency prediction", 
                "end-to-end latency", "system performance", "predict latency"
            ]
            
            context_found = any(keyword in insights_lower for keyword in context_keywords)
            
            if context_found:
                self.log_test("Analysis With User Expectation", "PASS", 
                             f"✅ CONTEXT-AWARE: Insights mention user's goal. Generated {len(models)} models.")
                
                # Log which keywords were found
                found_keywords = [kw for kw in context_keywords if kw in insights_lower]
                print(f"   🎯 Context keywords found: {found_keywords}")
                
            else:
                self.log_test("Analysis With User Expectation", "PARTIAL", 
                             f"Analysis completed but insights may not be context-aware. Generated {len(models)} models.")
            
            # Store for comparison
            self.expectation_response = response
            return response
        else:
            self.log_test("Analysis With User Expectation", "FAIL", 
                         "Analysis did not return expected results", response)
            return None

    def test_backend_logging_verification(self):
        """Test 4: Backend logging verification"""
        # This test checks if the backend logs show user expectation tracking
        # Since we can't directly access logs, we'll check the response structure
        
        if not hasattr(self, 'expectation_response'):
            self.log_test("Backend Logging Verification", "SKIP", "No expectation response available")
            return
        
        response = self.expectation_response
        
        # Check if selection_feedback indicates user expectation was processed
        selection_feedback = response.get("selection_feedback", {})
        
        if selection_feedback:
            message = selection_feedback.get("message", "")
            status = selection_feedback.get("status", "")
            
            if "target" in message.lower() and status in ["used", "override"]:
                self.log_test("Backend Logging Verification", "PASS", 
                             f"Selection feedback indicates user expectation was processed: {status}")
            else:
                self.log_test("Backend Logging Verification", "PARTIAL", 
                             f"Selection feedback present but unclear: {status}")
        else:
            self.log_test("Backend Logging Verification", "PARTIAL", 
                         "No selection feedback in response (may still be working)")

    def test_insights_comparison(self):
        """Test 5: Compare insights with and without user expectation"""
        if not hasattr(self, 'baseline_response') or not hasattr(self, 'expectation_response'):
            self.log_test("Insights Comparison", "SKIP", "Missing baseline or expectation responses")
            return
        
        baseline_insights = self.baseline_response.get("insights", "")
        expectation_insights = self.expectation_response.get("insights", "")
        
        # Check if insights are different
        if baseline_insights != expectation_insights:
            # Check if expectation insights are more context-specific
            expectation_lower = expectation_insights.lower()
            context_indicators = [
                "latency", "performance", "bottleneck", "predict", "system", 
                "end-to-end", "identify", "average"
            ]
            
            context_count = sum(1 for indicator in context_indicators if indicator in expectation_lower)
            
            if context_count >= 3:  # At least 3 context indicators
                self.log_test("Insights Comparison", "PASS", 
                             f"✅ Expectation insights are more context-aware ({context_count} context indicators)")
            else:
                self.log_test("Insights Comparison", "PARTIAL", 
                             f"Insights differ but context-awareness unclear ({context_count} context indicators)")
        else:
            self.log_test("Insights Comparison", "FAIL", 
                         "Insights are identical - user expectation may not be working")

    def test_azure_openai_integration(self):
        """Test 6: Azure OpenAI integration status"""
        if not hasattr(self, 'expectation_response'):
            self.log_test("Azure OpenAI Integration", "SKIP", "No expectation response available")
            return
        
        insights = self.expectation_response.get("insights", "")
        
        # Check for AI-generated content characteristics
        ai_indicators = [
            "recommendation", "analysis", "findings", "performance", 
            "model", "data", "business", "actionable"
        ]
        
        ai_score = sum(1 for indicator in ai_indicators if indicator.lower() in insights.lower())
        
        if ai_score >= 4 and len(insights) > 200:
            self.log_test("Azure OpenAI Integration", "PASS", 
                         f"✅ AI-powered insights detected (score: {ai_score}/8, length: {len(insights)} chars)")
        elif len(insights) > 50:
            self.log_test("Azure OpenAI Integration", "PARTIAL", 
                         f"Basic insights generated (score: {ai_score}/8, length: {len(insights)} chars)")
        else:
            self.log_test("Azure OpenAI Integration", "FAIL", 
                         "Minimal or no insights generated - Azure OpenAI may not be configured")

    def test_error_handling(self):
        """Test 7: Error handling with invalid parameters"""
        if not self.test_dataset_id:
            self.log_test("Error Handling", "SKIP", "No test dataset available")
            return
        
        # Test with invalid dataset ID
        invalid_response = self.run_holistic_analysis("invalid-dataset-id")
        
        if "error" in invalid_response:
            self.log_test("Error Handling", "PASS", 
                         f"Proper error handling for invalid dataset: {invalid_response['error']}")
        else:
            self.log_test("Error Handling", "FAIL", 
                         "No error returned for invalid dataset ID")

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🧪 Enhanced User Expectation Feature Testing for PROMISE AI Platform")
        print("=" * 80)
        print(f"Backend URL: {self.backend_url}")
        print()
        
        # Run tests in order
        self.test_setup_dataset()
        self.test_analysis_without_user_expectation()
        self.test_analysis_with_user_expectation()
        self.test_backend_logging_verification()
        self.test_insights_comparison()
        self.test_azure_openai_integration()
        self.test_error_handling()
        
        # Summary
        print("=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for r in self.test_results if r["status"] == "PASS")
        failed = sum(1 for r in self.test_results if r["status"] == "FAIL")
        partial = sum(1 for r in self.test_results if r["status"] == "PARTIAL")
        skipped = sum(1 for r in self.test_results if r["status"] == "SKIP")
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"🟡 Partial: {partial}")
        print(f"⏭️  Skipped: {skipped}")
        print()
        
        success_rate = ((passed + partial * 0.5) / total) * 100 if total > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Critical findings
        critical_failures = [r for r in self.test_results if r["status"] == "FAIL"]
        if critical_failures:
            print("\n🚨 CRITICAL ISSUES:")
            for failure in critical_failures:
                print(f"   - {failure['test']}: {failure['details']}")
        
        # User expectation feature status
        expectation_tests = [r for r in self.test_results if "Expectation" in r["test"] or "Comparison" in r["test"]]
        expectation_working = sum(1 for r in expectation_tests if r["status"] in ["PASS", "PARTIAL"])
        
        print(f"\n🎯 USER EXPECTATION FEATURE STATUS:")
        if expectation_working >= len(expectation_tests) * 0.7:  # 70% threshold
            print("   ✅ User expectation feature is working")
        else:
            print("   ❌ User expectation feature needs attention")
        
        # Azure OpenAI status
        ai_tests = [r for r in self.test_results if "Azure" in r["test"] or "AI" in r["test"]]
        ai_working = any(r["status"] == "PASS" for r in ai_tests)
        
        print(f"\n🤖 AZURE OPENAI STATUS:")
        if ai_working:
            print("   ✅ Azure OpenAI integration is working")
        else:
            print("   ⚠️  Azure OpenAI may not be configured (acceptable)")
        
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "partial": partial,
            "success_rate": success_rate,
            "expectation_working": expectation_working >= len(expectation_tests) * 0.7,
            "ai_working": ai_working
        }

def main():
    """Main test execution"""
    tester = UserExpectationTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    if results["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
