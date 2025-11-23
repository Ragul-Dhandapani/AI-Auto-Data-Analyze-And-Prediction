#!/usr/bin/env python3
"""
Enhanced User Experience: Domain Guidance & Expectation Persistence Testing
Tests the expectation persistence and domain guidance features
"""

import requests
import json
import sys
import time
from typing import Dict, List, Any

# Backend URL from environment
BACKEND_URL = "https://aiworkbench-2.preview.emergentagent.com/api"

class ExpectationPersistenceTester:
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
            response = requests.get(f"{self.backend_url}/datasource/datasets", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get("datasets", [])
            else:
                return []
        except Exception as e:
            print(f"Failed to get datasets: {str(e)}")
            return []

    def get_dataset_by_id(self, dataset_id: str) -> Dict:
        """Get dataset by ID"""
        try:
            response = requests.get(f"{self.backend_url}/datasource/datasets/{dataset_id}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get("dataset", {})
            else:
                return {}
        except Exception as e:
            print(f"Failed to get dataset {dataset_id}: {str(e)}")
            return {}

    def update_dataset_expectation(self, dataset_id: str, user_expectation: str) -> Dict:
        """Update dataset expectation"""
        try:
            payload = {"user_expectation": user_expectation}
            response = requests.put(
                f"{self.backend_url}/datasource/datasets/{dataset_id}/expectation",
                json=payload,
                timeout=10
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

    def run_holistic_analysis(self, dataset_id: str, user_selection: Dict = None) -> Dict:
        """Run holistic analysis with optional user selection"""
        payload = {
            "dataset_id": dataset_id,
            "workspace_name": "test_workspace_expectation_persistence",
            "problem_type": "auto"
        }
        
        if user_selection:
            payload["user_selection"] = user_selection
        
        try:
            response = requests.post(
                f"{self.backend_url}/analysis/holistic",
                json=payload,
                timeout=120  # Longer timeout for analysis
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
        # Look for existing test dataset
        datasets = self.get_available_datasets()
        
        # Look for a suitable dataset with enough data
        suitable_dataset = None
        for dataset in datasets:
            name = dataset.get("name", "").lower()
            row_count = dataset.get("row_count", 0)
            
            # Look for any dataset with reasonable amount of data
            if row_count >= 50:  # Need enough data for analysis
                suitable_dataset = dataset
                break
        
        if suitable_dataset:
            self.test_dataset_id = suitable_dataset.get("id")
            self.log_test("Setup Test Dataset", "PASS", 
                         f"Using existing dataset: {suitable_dataset.get('name')} (ID: {self.test_dataset_id}, {suitable_dataset.get('row_count')} rows)")
        else:
            self.log_test("Setup Test Dataset", "FAIL", "No suitable dataset found for testing")

    def test_dataset_expectation_update_it_banking(self):
        """Test 2: Test Dataset Expectation Update - IT Investment Banking"""
        if not self.test_dataset_id:
            self.log_test("Dataset Expectation Update (IT Banking)", "SKIP", "No test dataset available")
            return
        
        expectation = "IT - Investment Banking: Predict the trade latency of E2E for the client/product wise"
        
        print(f"🔄 Updating dataset expectation to: {expectation}")
        response = self.update_dataset_expectation(self.test_dataset_id, expectation)
        
        if "error" in response:
            self.log_test("Dataset Expectation Update (IT Banking)", "FAIL", 
                         f"Error: {response['error']}", response)
            return
        
        # Check if update was successful
        if response.get("success"):
            self.log_test("Dataset Expectation Update (IT Banking)", "PASS", 
                         f"✅ Successfully updated expectation: {expectation}")
            self.it_banking_expectation = expectation
        else:
            self.log_test("Dataset Expectation Update (IT Banking)", "FAIL", 
                         "Update response did not indicate success", response)

    def test_expectation_persistence_retrieval(self):
        """Test 3: Test Expectation Persistence - Verify dataset returns stored expectation"""
        if not self.test_dataset_id or not hasattr(self, 'it_banking_expectation'):
            self.log_test("Expectation Persistence Retrieval", "SKIP", "No dataset or expectation available")
            return
        
        print(f"🔍 Retrieving dataset to verify expectation persistence...")
        dataset = self.get_dataset_by_id(self.test_dataset_id)
        
        if not dataset:
            self.log_test("Expectation Persistence Retrieval", "FAIL", "Could not retrieve dataset")
            return
        
        # Check if last_user_expectation field exists and matches
        stored_expectation = dataset.get("last_user_expectation")
        
        if stored_expectation:
            if stored_expectation == self.it_banking_expectation:
                self.log_test("Expectation Persistence Retrieval", "PASS", 
                             f"✅ Expectation persisted correctly: {stored_expectation}")
            else:
                self.log_test("Expectation Persistence Retrieval", "FAIL", 
                             f"Expectation mismatch. Expected: {self.it_banking_expectation}, Got: {stored_expectation}")
        else:
            self.log_test("Expectation Persistence Retrieval", "FAIL", 
                         "No last_user_expectation field found in dataset")

    def test_different_domain_expectation(self):
        """Test 4: Test with Different Domain - Food Industry"""
        if not self.test_dataset_id:
            self.log_test("Different Domain Expectation", "SKIP", "No test dataset available")
            return
        
        expectation = "Food: Predict the price and revenue for 2026"
        
        print(f"🔄 Updating dataset expectation to different domain: {expectation}")
        response = self.update_dataset_expectation(self.test_dataset_id, expectation)
        
        if "error" in response:
            self.log_test("Different Domain Expectation", "FAIL", 
                         f"Error: {response['error']}", response)
            return
        
        # Verify the new expectation is stored
        if response.get("success"):
            # Retrieve dataset to verify new expectation
            dataset = self.get_dataset_by_id(self.test_dataset_id)
            stored_expectation = dataset.get("last_user_expectation")
            
            if stored_expectation == expectation:
                self.log_test("Different Domain Expectation", "PASS", 
                             f"✅ Successfully updated to different domain: {expectation}")
                self.food_expectation = expectation
            else:
                self.log_test("Different Domain Expectation", "FAIL", 
                             f"New expectation not stored correctly. Expected: {expectation}, Got: {stored_expectation}")
        else:
            self.log_test("Different Domain Expectation", "FAIL", 
                         "Update response did not indicate success", response)

    def test_full_flow_with_expectation(self):
        """Test 5: Test Full Flow with Expectation - E-commerce Domain"""
        if not self.test_dataset_id:
            self.log_test("Full Flow with Expectation", "SKIP", "No test dataset available")
            return
        
        # Update expectation to e-commerce domain
        expectation = "E-commerce: Predict customer churn to improve retention"
        
        print(f"🔄 Setting e-commerce expectation: {expectation}")
        update_response = self.update_dataset_expectation(self.test_dataset_id, expectation)
        
        if "error" in update_response:
            self.log_test("Full Flow with Expectation", "FAIL", 
                         f"Failed to update expectation: {update_response['error']}")
            return
        
        # Run holistic analysis with this expectation
        user_selection = {
            "user_expectation": expectation,
            "mode": "auto"
        }
        
        print(f"🔍 Running holistic analysis with e-commerce expectation...")
        analysis_response = self.run_holistic_analysis(self.test_dataset_id, user_selection)
        
        if "error" in analysis_response:
            self.log_test("Full Flow with Expectation", "FAIL", 
                         f"Analysis failed: {analysis_response['error']}")
            return
        
        # Check if domain is detected as "ecommerce"
        detected_domain = analysis_response.get("detected_domain")
        insights = analysis_response.get("insights", "")
        
        # Check for e-commerce terminology in insights
        ecommerce_terms = ["churn", "customer", "retention", "ecommerce", "e-commerce"]
        found_terms = [term for term in ecommerce_terms if term.lower() in insights.lower()]
        
        if detected_domain == "ecommerce" or found_terms:
            self.log_test("Full Flow with Expectation", "PASS", 
                         f"✅ E-commerce domain detected or terminology found. Domain: {detected_domain}, Terms: {found_terms}")
            self.ecommerce_analysis = analysis_response
        else:
            self.log_test("Full Flow with Expectation", "PARTIAL", 
                         f"Analysis completed but e-commerce context unclear. Domain: {detected_domain}")

    def test_expectation_in_analysis_response(self):
        """Test 6: Test Expectation in Analysis Response"""
        if not hasattr(self, 'ecommerce_analysis'):
            self.log_test("Expectation in Analysis Response", "SKIP", "No e-commerce analysis available")
            return
        
        analysis_response = self.ecommerce_analysis
        
        # Check if user_expectation is included in response
        response_expectation = analysis_response.get("user_expectation")
        
        if response_expectation:
            expected_expectation = "E-commerce: Predict customer churn to improve retention"
            if response_expectation == expected_expectation:
                self.log_test("Expectation in Analysis Response", "PASS", 
                             f"✅ User expectation correctly included in response: {response_expectation}")
            else:
                self.log_test("Expectation in Analysis Response", "PARTIAL", 
                             f"User expectation found but different: {response_expectation}")
        else:
            self.log_test("Expectation in Analysis Response", "FAIL", 
                         "User expectation not found in analysis response")

    def test_analysis_with_user_selection_expectation(self):
        """Test 7: Test Analysis with user_expectation in user_selection"""
        if not self.test_dataset_id:
            self.log_test("Analysis with User Selection Expectation", "SKIP", "No test dataset available")
            return
        
        # Test with user_expectation in user_selection
        user_selection = {
            "user_expectation": "Healthcare: Predict patient readmission risk for better care planning",
            "mode": "auto"
        }
        
        print(f"🔍 Running analysis with user_expectation in user_selection...")
        analysis_response = self.run_holistic_analysis(self.test_dataset_id, user_selection)
        
        if "error" in analysis_response:
            self.log_test("Analysis with User Selection Expectation", "FAIL", 
                         f"Analysis failed: {analysis_response['error']}")
            return
        
        # Check if user_expectation is available for frontend display
        response_expectation = analysis_response.get("user_expectation")
        insights = analysis_response.get("insights", "")
        
        # Check for healthcare terminology
        healthcare_terms = ["patient", "readmission", "healthcare", "care", "medical"]
        found_terms = [term for term in healthcare_terms if term.lower() in insights.lower()]
        
        if response_expectation or found_terms:
            self.log_test("Analysis with User Selection Expectation", "PASS", 
                         f"✅ Analysis with user_expectation working. Response expectation: {response_expectation}, Healthcare terms: {found_terms}")
        else:
            self.log_test("Analysis with User Selection Expectation", "PARTIAL", 
                         "Analysis completed but expectation context unclear")

    def test_error_handling(self):
        """Test 8: Error Handling"""
        # Test with invalid dataset ID
        print("🔍 Testing error handling with invalid dataset ID...")
        
        invalid_response = self.update_dataset_expectation("invalid-dataset-id", "Test expectation")
        
        if "error" in invalid_response:
            self.log_test("Error Handling", "PASS", 
                         f"✅ Proper error handling for invalid dataset ID: {invalid_response['error']}")
        else:
            self.log_test("Error Handling", "FAIL", 
                         "Should have returned error for invalid dataset ID")

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🧪 Enhanced User Experience: Domain Guidance & Expectation Persistence Testing")
        print("=" * 80)
        print(f"Backend URL: {self.backend_url}")
        print()
        
        # Run tests in order
        self.test_setup_dataset()
        self.test_dataset_expectation_update_it_banking()
        self.test_expectation_persistence_retrieval()
        self.test_different_domain_expectation()
        self.test_full_flow_with_expectation()
        self.test_expectation_in_analysis_response()
        self.test_analysis_with_user_selection_expectation()
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
        
        # Expectation persistence feature status
        expectation_tests = [r for r in self.test_results if "Expectation" in r["test"] or "Domain" in r["test"]]
        expectation_working = sum(1 for r in expectation_tests if r["status"] in ["PASS", "PARTIAL"])
        
        print(f"\n🎯 EXPECTATION PERSISTENCE FEATURE STATUS:")
        if expectation_working >= len(expectation_tests) * 0.7:  # 70% threshold
            print("   ✅ Expectation persistence feature is working")
        else:
            print("   ❌ Expectation persistence feature needs attention")
        
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "partial": partial,
            "success_rate": success_rate,
            "expectation_working": expectation_working >= len(expectation_tests) * 0.7
        }

def main():
    """Main test execution"""
    tester = ExpectationPersistenceTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    if results["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()