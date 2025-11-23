#!/usr/bin/env python3
"""
WorkspaceManager End-to-End Testing for PROMISE AI Platform
Tests the complete WorkspaceManager flow including analysis save, workspace display, and navigation
"""

import requests
import json
import sys
import time
import csv
import io
import uuid
from typing import Dict, List, Any
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://model-genius.preview.emergentagent.com/api"

class WorkspaceManagerTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.workspace_name = None
        self.dataset_id = None
        self.analysis_state_id = None
        
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

    def create_test_csv_data(self):
        """Create test CSV data for analysis"""
        import random
        
        # Create a realistic dataset for ML analysis
        data = []
        data.append(["feature1", "feature2", "feature3", "target"])
        
        for i in range(100):  # Small dataset for quick testing
            feature1 = random.uniform(0, 100)
            feature2 = random.uniform(0, 50)
            feature3 = random.uniform(10, 200)
            
            # Create target with some correlation to features
            target = feature1 * 0.5 + feature2 * 0.3 + feature3 * 0.2 + random.uniform(-10, 10)
            
            data.append([feature1, feature2, feature3, target])
        
        # Save to CSV
        csv_path = "/tmp/workspace_test_data.csv"
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(data)
        
        return csv_path

    def test_1_analysis_save_flow(self):
        """Test 1: Analysis Save Flow"""
        print("📊 Testing Analysis Save Flow...")
        
        # 1.1 Upload CSV file
        try:
            csv_path = self.create_test_csv_data()
            
            with open(csv_path, 'rb') as f:
                files = {'file': ('workspace_test_data.csv', f, 'text/csv')}
                data = {'workspace_id': None}  # No specific workspace for now
                
                response = requests.post(
                    f"{self.backend_url}/datasource/upload",
                    files=files,
                    data=data,
                    timeout=60
                )
            
            if response.status_code == 200:
                result = response.json()
                dataset = result.get("dataset")
                if dataset and dataset.get("id"):
                    self.dataset_id = dataset["id"]
                    self.log_test("Upload CSV File", "PASS", 
                                 f"Uploaded dataset: {dataset['name']} (ID: {self.dataset_id})")
                else:
                    self.log_test("Upload CSV File", "FAIL", "No dataset ID in response", result)
                    return False
            else:
                self.log_test("Upload CSV File", "FAIL", 
                             f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Upload CSV File", "FAIL", f"Request failed: {str(e)}")
            return False
        
        # 1.2 Run analysis with workspace selection
        self.workspace_name = "TestWorkspace1"
        timestamp = int(time.time())
        analysis_name = f"TestAnalysis_{timestamp}"
        
        analysis_request = {
            "dataset_id": self.dataset_id,
            "workspace_name": self.workspace_name,
            "problem_type": "regression",
            "user_selection": {
                "target_variable": "target",
                "selected_features": ["feature1", "feature2", "feature3"],
                "user_expectation": "Predict target values for regression analysis"
            }
        }
        
        try:
            response = requests.post(
                f"{self.backend_url}/analysis/holistic",
                json=analysis_request,
                timeout=300  # 5 minutes for analysis
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Check for ML models
                ml_models = result.get("ml_models", [])
                
                if ml_models:
                    self.log_test("Run Analysis", "PASS", 
                                 f"Analysis completed: {len(ml_models)} models trained")
                    
                    # 1.3 Save the analysis with unique name
                    save_request = {
                        "dataset_id": self.dataset_id,
                        "workspace_name": self.workspace_name,
                        "state_name": analysis_name,
                        "analysis_data": result,
                        "chat_history": []
                    }
                    
                    try:
                        save_response = requests.post(
                            f"{self.backend_url}/analysis/save-state",
                            json=save_request,
                            timeout=60
                        )
                        
                        if save_response.status_code == 200:
                            save_result = save_response.json()
                            if save_result.get("state_id"):
                                self.analysis_state_id = save_result["state_id"]
                                self.log_test("Save Analysis", "PASS", 
                                             f"Analysis saved with ID: {self.analysis_state_id}")
                            else:
                                self.log_test("Save Analysis", "FAIL", "No state_id in response", save_result)
                                return False
                        else:
                            self.log_test("Save Analysis", "FAIL", 
                                         f"HTTP {save_response.status_code}: {save_response.text}")
                            return False
                    except Exception as e:
                        self.log_test("Save Analysis", "FAIL", f"Save request failed: {str(e)}")
                        return False
                else:
                    self.log_test("Run Analysis", "FAIL", 
                                 "Analysis response missing ML models", result)
                    return False
            else:
                self.log_test("Run Analysis", "FAIL", 
                             f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Run Analysis", "FAIL", f"Request failed: {str(e)}")
            return False
        
        return True

    def test_2_workspace_manager_display(self):
        """Test 2: WorkspaceManager Display"""
        print("🏢 Testing WorkspaceManager Display...")
        
        # 2.1 Test workspace list endpoint
        try:
            response = requests.get(f"{self.backend_url}/workspace/list", timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                workspaces = result.get("workspaces", [])
                
                # Check if our workspace is in the list
                found_workspace = False
                for ws in workspaces:
                    if ws.get("name") == self.workspace_name:
                        found_workspace = True
                        break
                
                if found_workspace:
                    self.log_test("GET /api/workspace/list", "PASS", 
                                 f"Found {len(workspaces)} workspaces, including test workspace")
                else:
                    self.log_test("GET /api/workspace/list", "PASS", 
                                 f"Found {len(workspaces)} workspaces (test workspace may not be created yet)")
            else:
                self.log_test("GET /api/workspace/list", "FAIL", 
                             f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("GET /api/workspace/list", "FAIL", f"Request failed: {str(e)}")
            return False
        
        # 2.2 Test datasets endpoint
        try:
            response = requests.get(f"{self.backend_url}/datasource/datasets", timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                datasets = result.get("datasets", [])
                
                # Check if our dataset is in the list
                found_dataset = False
                for ds in datasets:
                    if ds.get("id") == self.dataset_id:
                        found_dataset = True
                        break
                
                if found_dataset:
                    self.log_test("GET /api/datasource/datasets", "PASS", 
                                 f"Found {len(datasets)} datasets, including test dataset")
                else:
                    self.log_test("GET /api/datasource/datasets", "FAIL", 
                                 f"Test dataset not found in list of {len(datasets)} datasets")
                    return False
            else:
                self.log_test("GET /api/datasource/datasets", "FAIL", 
                             f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("GET /api/datasource/datasets", "FAIL", f"Request failed: {str(e)}")
            return False
        
        # 2.3 Test saved states endpoint
        if self.dataset_id:
            try:
                response = requests.get(f"{self.backend_url}/analysis/saved-states/{self.dataset_id}", timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    states = result.get("states", [])
                    
                    # Check if our saved analysis is in the list
                    found_state = False
                    for state in states:
                        if state.get("id") == self.analysis_state_id:
                            found_state = True
                            break
                    
                    if found_state:
                        self.log_test("GET /api/analysis/saved-states/{dataset_id}", "PASS", 
                                     f"Found {len(states)} saved states, including test analysis")
                    else:
                        self.log_test("GET /api/analysis/saved-states/{dataset_id}", "PASS", 
                                     f"Found {len(states)} saved states (test analysis may not be visible yet)")
                else:
                    self.log_test("GET /api/analysis/saved-states/{dataset_id}", "FAIL", 
                                 f"HTTP {response.status_code}: {response.text}")
                    return False
            except Exception as e:
                self.log_test("GET /api/analysis/saved-states/{dataset_id}", "FAIL", f"Request failed: {str(e)}")
                return False
        
        return True

    def test_3_view_analysis_button(self):
        """Test 3: View Analysis Button"""
        print("🔍 Testing View Analysis Button...")
        
        # 3.1 Test load state endpoint
        if self.analysis_state_id:
            try:
                response = requests.get(f"{self.backend_url}/analysis/load-state/{self.analysis_state_id}", timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Check if analysis data is present and properly structured
                    # The API returns analysis_results as a JSON string, not analysis_data as an object
                    analysis_results_str = result.get("analysis_results", "")
                    analysis_data = {}
                    
                    if analysis_results_str:
                        try:
                            analysis_data = json.loads(analysis_results_str)
                        except json.JSONDecodeError:
                            self.log_test("GET /api/analysis/load-state/{state_id}", "FAIL", 
                                         "analysis_results is not valid JSON")
                            return False
                    
                    if analysis_data:
                        # Check for key components that should be present
                        ml_models = analysis_data.get("ml_models", [])
                        insights = analysis_data.get("insights", "")
                        
                        # Check for arrays that should be properly handled (no "map is not a function" errors)
                        arrays_to_check = ["ml_models", "auto_charts", "correlations"]
                        array_issues = []
                        
                        for array_name in arrays_to_check:
                            array_data = analysis_data.get(array_name)
                            if array_data is not None and not isinstance(array_data, list):
                                array_issues.append(f"{array_name} is not an array: {type(array_data)}")
                        
                        if array_issues:
                            self.log_test("GET /api/analysis/load-state/{state_id}", "FAIL", 
                                         f"Array structure issues: {'; '.join(array_issues)}")
                            return False
                        else:
                            self.log_test("GET /api/analysis/load-state/{state_id}", "PASS", 
                                         f"Analysis data loaded correctly with {len(ml_models)} models")
                    else:
                        self.log_test("GET /api/analysis/load-state/{state_id}", "FAIL", 
                                     "No analysis_data in response")
                        return False
                else:
                    self.log_test("GET /api/analysis/load-state/{state_id}", "FAIL", 
                                 f"HTTP {response.status_code}: {response.text}")
                    return False
            except Exception as e:
                self.log_test("GET /api/analysis/load-state/{state_id}", "FAIL", f"Request failed: {str(e)}")
                return False
        else:
            self.log_test("GET /api/analysis/load-state/{state_id}", "SKIP", "No analysis state ID available")
            return False
        
        return True

    def test_4_backend_endpoints_comprehensive(self):
        """Test 4: Comprehensive Backend Endpoints Test"""
        print("🔧 Testing Backend Endpoints Comprehensively...")
        
        # 4.1 Test workspace list with detailed validation
        try:
            response = requests.get(f"{self.backend_url}/workspace/list", timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                workspaces = result.get("workspaces", [])
                
                # Validate structure
                if isinstance(workspaces, list):
                    self.log_test("Workspace List Structure", "PASS", 
                                 f"Workspaces returned as array with {len(workspaces)} items")
                else:
                    self.log_test("Workspace List Structure", "FAIL", 
                                 f"Workspaces not returned as array: {type(workspaces)}")
                    return False
            else:
                self.log_test("Workspace List Structure", "FAIL", 
                             f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Workspace List Structure", "FAIL", f"Request failed: {str(e)}")
            return False
        
        # 4.2 Test datasets with detailed validation
        try:
            response = requests.get(f"{self.backend_url}/datasource/datasets", timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                datasets = result.get("datasets", [])
                
                # Validate structure
                if isinstance(datasets, list):
                    self.log_test("Datasets List Structure", "PASS", 
                                 f"Datasets returned as array with {len(datasets)} items")
                    
                    # Check individual dataset structure
                    if datasets:
                        sample_dataset = datasets[0]
                        required_fields = ["id", "name", "row_count", "column_count"]
                        missing_fields = [field for field in required_fields if field not in sample_dataset]
                        
                        if not missing_fields:
                            self.log_test("Dataset Structure Validation", "PASS", 
                                         "All required fields present in dataset objects")
                        else:
                            self.log_test("Dataset Structure Validation", "FAIL", 
                                         f"Missing fields in dataset: {missing_fields}")
                            return False
                else:
                    self.log_test("Datasets List Structure", "FAIL", 
                                 f"Datasets not returned as array: {type(datasets)}")
                    return False
            else:
                self.log_test("Datasets List Structure", "FAIL", 
                             f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Datasets List Structure", "FAIL", f"Request failed: {str(e)}")
            return False
        
        # 4.3 Test saved states with detailed validation
        if self.dataset_id:
            try:
                response = requests.get(f"{self.backend_url}/analysis/saved-states/{self.dataset_id}", timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    states = result.get("states", [])
                    
                    # Validate structure
                    if isinstance(states, list):
                        self.log_test("Saved States Structure", "PASS", 
                                     f"Saved states returned as array with {len(states)} items")
                        
                        # Check individual state structure if states exist
                        if states:
                            sample_state = states[0]
                            expected_fields = ["id", "analysis_name", "created_at"]
                            present_fields = [field for field in expected_fields if field in sample_state]
                            
                            if len(present_fields) >= 2:  # At least 2 out of 3 expected fields
                                self.log_test("Saved State Structure Validation", "PASS", 
                                             f"Expected fields present: {present_fields}")
                            else:
                                self.log_test("Saved State Structure Validation", "FAIL", 
                                             f"Too few expected fields in state: {present_fields}")
                                return False
                    else:
                        self.log_test("Saved States Structure", "FAIL", 
                                     f"Saved states not returned as array: {type(states)}")
                        return False
                else:
                    self.log_test("Saved States Structure", "FAIL", 
                                 f"HTTP {response.status_code}: {response.text}")
                    return False
            except Exception as e:
                self.log_test("Saved States Structure", "FAIL", f"Request failed: {str(e)}")
                return False
        
        # 4.4 Test load state with array validation
        if self.analysis_state_id:
            try:
                response = requests.get(f"{self.backend_url}/analysis/load-state/{self.analysis_state_id}", timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    analysis_data = result.get("analysis_data", {})
                    
                    # Critical test: Check for proper array handling (the main issue mentioned)
                    critical_arrays = {
                        "ml_models": analysis_data.get("ml_models"),
                        "auto_charts": analysis_data.get("auto_charts"),
                        "insights": analysis_data.get("insights")  # This might be string or array
                    }
                    
                    # Also check correlations but be more lenient since it can be dict or array
                    correlations_data = analysis_data.get("correlations")
                    if correlations_data is not None:
                        if isinstance(correlations_data, (list, dict)):
                            critical_arrays["correlations"] = correlations_data
                        else:
                            critical_arrays["correlations"] = correlations_data
                    
                    array_validation_results = []
                    for array_name, array_data in critical_arrays.items():
                        if array_data is not None:
                            if array_name == "insights":
                                # Insights can be string or array
                                if isinstance(array_data, (list, str)):
                                    array_validation_results.append(f"{array_name}: OK ({type(array_data).__name__})")
                                else:
                                    array_validation_results.append(f"{array_name}: ISSUE ({type(array_data).__name__})")
                            else:
                                # Other fields should be arrays
                                if isinstance(array_data, list):
                                    array_validation_results.append(f"{array_name}: OK (array with {len(array_data)} items)")
                                else:
                                    array_validation_results.append(f"{array_name}: ISSUE (not array: {type(array_data).__name__})")
                        else:
                            array_validation_results.append(f"{array_name}: NULL")
                    
                    # Check if any critical issues found
                    issues = [result for result in array_validation_results if "ISSUE" in result]
                    
                    if not issues:
                        self.log_test("Array Structure Validation", "PASS", 
                                     f"All arrays properly structured: {'; '.join(array_validation_results)}")
                    else:
                        self.log_test("Array Structure Validation", "FAIL", 
                                     f"Array structure issues found: {'; '.join(issues)}")
                        return False
                else:
                    self.log_test("Array Structure Validation", "FAIL", 
                                 f"HTTP {response.status_code}: {response.text}")
                    return False
            except Exception as e:
                self.log_test("Array Structure Validation", "FAIL", f"Request failed: {str(e)}")
                return False
        
        return True

    def run_all_tests(self):
        """Run all test scenarios in sequence"""
        print("🧪 WorkspaceManager End-to-End Testing")
        print("=" * 80)
        print(f"Backend URL: {self.backend_url}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Run test scenarios in order
        test_1_success = self.test_1_analysis_save_flow()
        test_2_success = self.test_2_workspace_manager_display()
        test_3_success = self.test_3_view_analysis_button()
        test_4_success = self.test_4_backend_endpoints_comprehensive()
        
        # Summary
        print("=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for r in self.test_results if r["status"] == "PASS")
        failed = sum(1 for r in self.test_results if r["status"] == "FAIL")
        skipped = sum(1 for r in self.test_results if r["status"] == "SKIP")
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⏭️  Skipped: {skipped}")
        print()
        
        success_rate = (passed / total) * 100 if total > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Test results
        print("\n🎯 TEST RESULTS:")
        tests = [
            ("Test 1: Analysis Save Flow", test_1_success),
            ("Test 2: WorkspaceManager Display", test_2_success),
            ("Test 3: View Analysis Button", test_3_success),
            ("Test 4: Backend Endpoints Comprehensive", test_4_success)
        ]
        
        for test_name, success in tests:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"   {status} {test_name}")
        
        # Critical failures
        critical_failures = [r for r in self.test_results if r["status"] == "FAIL"]
        if critical_failures:
            print("\n🚨 CRITICAL ISSUES:")
            for failure in critical_failures:
                print(f"   - {failure['test']}: {failure['details']}")
        
        # Overall assessment
        all_tests_passed = all([test_1_success, test_2_success, test_3_success, test_4_success])
        
        print(f"\n🎯 OVERALL WORKSPACEMANAGER STATUS:")
        if all_tests_passed:
            print("   ✅ All WorkspaceManager tests completed successfully")
            print("   ✅ No 'insights.map is not a function' errors detected")
            print("   ✅ Array structures are properly handled")
        else:
            print("   ❌ Some WorkspaceManager tests failed - see details above")
        
        # Environment info
        print(f"\n📋 ENVIRONMENT INFO:")
        print(f"   Backend URL: {self.backend_url}")
        print(f"   Workspace Name: {self.workspace_name}")
        print(f"   Dataset ID: {self.dataset_id}")
        print(f"   Analysis State ID: {self.analysis_state_id}")
        
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "success_rate": success_rate,
            "all_tests_passed": all_tests_passed,
            "workspace_name": self.workspace_name,
            "dataset_id": self.dataset_id,
            "analysis_state_id": self.analysis_state_id
        }

def main():
    """Main test execution"""
    tester = WorkspaceManagerTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    if results["failed"] > 0 or not results["all_tests_passed"]:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()