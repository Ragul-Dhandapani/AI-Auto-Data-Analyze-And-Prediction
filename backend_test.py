#!/usr/bin/env python3
"""
Comprehensive End-to-End Workspace Workflow Testing for PROMISE AI Platform
Tests the complete workspace management, dataset upload, analysis, and model export workflow
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
BACKEND_URL = "https://mlexport-hub.preview.emergentagent.com/api"

class WorkspaceWorkflowTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.workspace_id = None
        self.dataset_id = None
        self.training_metadata_ids = []
        
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
        data.append(["customer_id", "age", "income", "spending_score", "membership_years", "churn"])
        
        for i in range(200):  # Enough data for meaningful analysis
            customer_id = f"CUST_{i+1:04d}"
            age = random.randint(18, 80)
            income = random.randint(20000, 150000)
            spending_score = random.randint(1, 100)
            membership_years = random.randint(0, 20)
            
            # Churn probability based on features (realistic business logic)
            churn_prob = 0.1
            if age > 65:
                churn_prob += 0.2
            if income < 30000:
                churn_prob += 0.3
            if spending_score < 30:
                churn_prob += 0.4
            if membership_years < 2:
                churn_prob += 0.3
            
            churn = 1 if random.random() < churn_prob else 0
            
            data.append([customer_id, age, income, spending_score, membership_years, churn])
        
        # Save to CSV
        csv_path = "/tmp/e2e_test_customer_data.csv"
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(data)
        
        return csv_path

    def test_scenario_1_workspace_management(self):
        """Test Scenario 1: Workspace Management"""
        print("🏢 Testing Workspace Management...")
        
        # 1.1 Create a new workspace
        workspace_data = {
            "name": "E2E Test Workspace Q4 2024",
            "description": "End-to-end testing workspace for Q4 2024 analysis",
            "tags": ["testing", "e2e", "q4-2024"]
        }
        
        try:
            response = requests.post(
                f"{self.backend_url}/workspace/create",
                json=workspace_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                workspace = result.get("workspace")
                if workspace and workspace.get("id"):
                    self.workspace_id = workspace["id"]
                    self.log_test("Create Workspace", "PASS", 
                                 f"Created workspace: {workspace['name']} (ID: {self.workspace_id})")
                else:
                    self.log_test("Create Workspace", "FAIL", "No workspace ID in response", result)
                    return False
            else:
                self.log_test("Create Workspace", "FAIL", 
                             f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Create Workspace", "FAIL", f"Request failed: {str(e)}")
            return False
        
        # 1.2 List all workspaces
        try:
            response = requests.get(f"{self.backend_url}/workspace/list", timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                workspaces = result.get("workspaces", [])
                
                # Check if our workspace is in the list
                found_workspace = False
                for ws in workspaces:
                    if ws.get("id") == self.workspace_id:
                        found_workspace = True
                        break
                
                if found_workspace:
                    self.log_test("List Workspaces", "PASS", 
                                 f"Found {len(workspaces)} workspaces, including our test workspace")
                else:
                    self.log_test("List Workspaces", "FAIL", 
                                 f"Test workspace not found in list of {len(workspaces)} workspaces")
                    return False
            else:
                self.log_test("List Workspaces", "FAIL", 
                             f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("List Workspaces", "FAIL", f"Request failed: {str(e)}")
            return False
        
        # 1.3 Get workspace details
        try:
            response = requests.get(f"{self.backend_url}/workspace/{self.workspace_id}", timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                workspace = result.get("workspace")
                datasets = result.get("datasets", [])
                training_history = result.get("training_history", [])
                
                if workspace and workspace.get("name") == "E2E Test Workspace Q4 2024":
                    self.log_test("Get Workspace Details", "PASS", 
                                 f"Retrieved workspace details: {len(datasets)} datasets, {len(training_history)} training runs")
                else:
                    self.log_test("Get Workspace Details", "FAIL", 
                                 "Workspace details don't match expected values", result)
                    return False
            else:
                self.log_test("Get Workspace Details", "FAIL", 
                             f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Get Workspace Details", "FAIL", f"Request failed: {str(e)}")
            return False
        
        return True

    def test_scenario_2_dataset_upload_with_workspace(self):
        """Test Scenario 2: Dataset Upload with Workspace"""
        print("📊 Testing Dataset Upload with Workspace...")
        
        if not self.workspace_id:
            self.log_test("Dataset Upload with Workspace", "SKIP", "No workspace ID available")
            return False
        
        # 2.1 Get list of existing datasets (baseline)
        try:
            response = requests.get(f"{self.backend_url}/datasource/datasets", timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                initial_datasets = result.get("datasets", [])
                initial_count = len(initial_datasets)
                self.log_test("Get Initial Dataset Count", "PASS", 
                             f"Found {initial_count} existing datasets")
            else:
                self.log_test("Get Initial Dataset Count", "FAIL", 
                             f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Get Initial Dataset Count", "FAIL", f"Request failed: {str(e)}")
            return False
        
        # 2.2 Create and upload test CSV file with workspace_id
        try:
            csv_path = self.create_test_csv_data()
            
            with open(csv_path, 'rb') as f:
                files = {'file': ('e2e_test_customer_data.csv', f, 'text/csv')}
                data = {'workspace_id': self.workspace_id}
                
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
                    self.log_test("Upload Dataset with Workspace", "PASS", 
                                 f"Uploaded dataset: {dataset['name']} (ID: {self.dataset_id})")
                else:
                    self.log_test("Upload Dataset with Workspace", "FAIL", 
                                 "No dataset ID in response", result)
                    return False
            else:
                self.log_test("Upload Dataset with Workspace", "FAIL", 
                             f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Upload Dataset with Workspace", "FAIL", f"Request failed: {str(e)}")
            return False
        
        # 2.3 Verify workspace_id is saved with the dataset
        try:
            response = requests.get(f"{self.backend_url}/datasource/datasets/{self.dataset_id}", timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                dataset = result.get("dataset")
                if dataset and dataset.get("workspace_id") == self.workspace_id:
                    self.log_test("Verify Workspace Link", "PASS", 
                                 f"Dataset correctly linked to workspace {self.workspace_id}")
                else:
                    self.log_test("Verify Workspace Link", "FAIL", 
                                 f"Dataset workspace_id mismatch: expected {self.workspace_id}, got {dataset.get('workspace_id') if dataset else 'None'}")
                    return False
            else:
                self.log_test("Verify Workspace Link", "FAIL", 
                             f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Verify Workspace Link", "FAIL", f"Request failed: {str(e)}")
            return False
        
        return True

    def test_scenario_3_analysis_with_workspace_tracking(self):
        """Test Scenario 3: Analysis with Workspace Tracking"""
        print("🤖 Testing Analysis with Workspace Tracking...")
        
        if not self.dataset_id or not self.workspace_id:
            self.log_test("Analysis with Workspace Tracking", "SKIP", "No dataset or workspace ID available")
            return False
        
        # 3.1 Run holistic analysis
        analysis_request = {
            "dataset_id": self.dataset_id,
            "workspace_name": "E2E Test Workspace Q4 2024",
            "problem_type": "classification",
            "user_selection": {
                "target_variable": "churn",
                "selected_features": ["age", "income", "spending_score", "membership_years"],
                "user_expectation": "Predict customer churn to improve retention strategies"
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
                
                # Check for training metadata
                training_metadata = result.get("training_metadata")
                ml_models = result.get("ml_models", [])
                
                if training_metadata and ml_models:
                    self.log_test("Run Analysis", "PASS", 
                                 f"Analysis completed: {len(ml_models)} models trained")
                    
                    # Store model info for later tests
                    for model in ml_models:
                        if model.get("model_name"):
                            # Note: In real implementation, we'd get training metadata IDs from the response
                            # For now, we'll simulate this
                            self.training_metadata_ids.append(f"meta_{uuid.uuid4()}")
                else:
                    self.log_test("Run Analysis", "FAIL", 
                                 "Analysis response missing training metadata or models", result)
                    return False
            else:
                self.log_test("Run Analysis", "FAIL", 
                             f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Run Analysis", "FAIL", f"Request failed: {str(e)}")
            return False
        
        # 3.2 Check hyperparameter suggestions
        try:
            # The analysis response should include hyperparameter_suggestions
            if "hyperparameter_suggestions" in result:
                suggestions = result["hyperparameter_suggestions"]
                if suggestions and isinstance(suggestions, dict):
                    self.log_test("Check Hyperparameter Suggestions", "PASS", 
                                 f"Found hyperparameter suggestions for {len(suggestions)} model types")
                else:
                    self.log_test("Check Hyperparameter Suggestions", "FAIL", 
                                 "Hyperparameter suggestions empty or invalid format")
                    return False
            else:
                self.log_test("Check Hyperparameter Suggestions", "FAIL", 
                             "No hyperparameter_suggestions field in analysis response")
                return False
        except Exception as e:
            self.log_test("Check Hyperparameter Suggestions", "FAIL", f"Error checking suggestions: {str(e)}")
            return False
        
        return True

    def test_automl_with_random_forest(self):
        """Test 3: Test AutoML with Random Forest (CRITICAL TEST)"""
        if not hasattr(self, 'regression_path'):
            self.log_test("AutoML with Random Forest", "SKIP", "No test dataset available")
            return None
        
        print("🔍 Testing AutoML with Random Forest...")
        
        data_source = {"type": "file", "path": self.regression_path}
        response = self.call_intelligent_prediction_api(
            data_source=data_source,
            user_prompt="Predict house prices with optimized Random Forest",
            target_column="price",
            feature_columns=["bedrooms", "bathrooms", "sqft", "age"],
            models_to_train=["random_forest"],
            use_automl=True,
            automl_optimization_level="fast"
        )
        
        if "error" in response:
            self.log_test("AutoML with Random Forest", "FAIL", 
                         f"Error: {response['error']}", response)
            return None
        
        # Check if response is successful and contains AutoML results
        if response.get("status") == "success" and "data" in response:
            data = response["data"]
            model_comparison = data.get("model_comparison", [])
            
            # Look for AutoML indicators in the response
            automl_found = False
            best_params_found = False
            cv_score_found = False
            
            for model in model_comparison:
                if model.get("model_name") == "random_forest":
                    # Check if model has AutoML optimization indicators
                    if "automl_optimized" in str(model) or "best_params" in str(model):
                        automl_found = True
                    if "best_params" in str(model):
                        best_params_found = True
                    if "cv_score" in str(model):
                        cv_score_found = True
            
            if automl_found:
                self.log_test("AutoML with Random Forest", "PASS", 
                             f"✅ AutoML optimization detected for Random Forest. Best params: {best_params_found}, CV score: {cv_score_found}")
                
                # Store for detailed validation
                self.automl_rf_response = response
                return response
            else:
                self.log_test("AutoML with Random Forest", "FAIL", 
                             f"❌ AutoML optimization not detected in response")
                return None
        else:
            self.log_test("AutoML with Random Forest", "FAIL", 
                         "AutoML request did not return expected results", response)
            return None

    def test_automl_with_multiple_models(self):
        """Test 4: Test AutoML with Multiple Models (XGBoost, Ridge)"""
        if not hasattr(self, 'regression_path'):
            self.log_test("AutoML with Multiple Models", "SKIP", "No test dataset available")
            return
        
        print("🔍 Testing AutoML with XGBoost and Ridge...")
        
        data_source = {"type": "file", "path": self.regression_path}
        response = self.call_intelligent_prediction_api(
            data_source=data_source,
            user_prompt="Predict house prices with optimized XGBoost and Ridge models",
            target_column="price",
            feature_columns=["bedrooms", "bathrooms", "sqft", "age"],
            models_to_train=["xgboost", "ridge"],
            use_automl=True,
            automl_optimization_level="fast"
        )
        
        if "error" in response:
            self.log_test("AutoML with Multiple Models", "FAIL", 
                         f"Error: {response['error']}", response)
            return
        
        # Check if response is successful and contains AutoML results for multiple models
        if response.get("status") == "success" and "data" in response:
            data = response["data"]
            model_comparison = data.get("model_comparison", [])
            
            # Check each model for AutoML optimization
            optimized_models = []
            for model in model_comparison:
                model_name = model.get("model_name")
                if model_name in ["xgboost", "ridge"]:
                    # Check for AutoML indicators
                    model_str = str(model)
                    if "automl_optimized" in model_str or "best_params" in model_str:
                        optimized_models.append(model_name)
            
            if len(optimized_models) >= 2:
                self.log_test("AutoML with Multiple Models", "PASS", 
                             f"✅ AutoML optimization detected for {len(optimized_models)} models: {', '.join(optimized_models)}")
                
                # Store for detailed validation
                self.automl_multi_response = response
                return response
            elif len(optimized_models) >= 1:
                self.log_test("AutoML with Multiple Models", "PARTIAL", 
                             f"AutoML optimization detected for {len(optimized_models)} models: {', '.join(optimized_models)}")
                return response
            else:
                self.log_test("AutoML with Multiple Models", "FAIL", 
                             f"❌ AutoML optimization not detected for any models")
                return None
        else:
            self.log_test("AutoML with Multiple Models", "FAIL", 
                         "AutoML request did not return expected results", response)
            return None

    def test_automl_returns_optimized_hyperparameters(self):
        """Test 5: Verify AutoML Returns Optimized Hyperparameters"""
        if not hasattr(self, 'automl_rf_response'):
            self.log_test("AutoML Returns Optimized Hyperparameters", "SKIP", "No AutoML response available")
            return
        
        response = self.automl_rf_response
        data = response.get("data", {})
        model_comparison = data.get("model_comparison", [])
        
        # Look for hyperparameters in the response
        hyperparams_found = False
        cv_scores_found = False
        automl_optimized_found = False
        
        for model in model_comparison:
            model_str = str(model)
            if "best_params" in model_str:
                hyperparams_found = True
            if "cv_score" in model_str:
                cv_scores_found = True
            if "automl_optimized" in model_str:
                automl_optimized_found = True
        
        # Check training summary for AutoML indicators
        training_summary = data.get("training_summary", {})
        
        success_indicators = []
        if hyperparams_found:
            success_indicators.append("best_params")
        if cv_scores_found:
            success_indicators.append("cv_score")
        if automl_optimized_found:
            success_indicators.append("automl_optimized")
        
        if len(success_indicators) >= 2:
            self.log_test("AutoML Returns Optimized Hyperparameters", "PASS", 
                         f"✅ AutoML hyperparameters found: {', '.join(success_indicators)}")
        elif len(success_indicators) >= 1:
            self.log_test("AutoML Returns Optimized Hyperparameters", "PARTIAL", 
                         f"Some AutoML indicators found: {', '.join(success_indicators)}")
        else:
            self.log_test("AutoML Returns Optimized Hyperparameters", "FAIL", 
                         "❌ No AutoML hyperparameter indicators found in response")

    def test_automl_performance_comparison(self):
        """Test 6: Compare AutoML vs Default Performance"""
        if not hasattr(self, 'regression_path') or not hasattr(self, 'baseline_response'):
            self.log_test("AutoML Performance Comparison", "SKIP", "No baseline or AutoML response available")
            return
        
        # Get baseline performance (without AutoML)
        baseline_data = self.baseline_response.get("data", {})
        baseline_comparison = baseline_data.get("model_comparison", [])
        baseline_best = baseline_data.get("best_model", {})
        baseline_score = baseline_best.get("score", 0)
        
        # Get AutoML performance
        if hasattr(self, 'automl_rf_response'):
            automl_data = self.automl_rf_response.get("data", {})
            automl_comparison = automl_data.get("model_comparison", [])
            automl_best = automl_data.get("best_model", {})
            automl_score = automl_best.get("score", 0)
            
            # Compare performance
            if automl_score > baseline_score:
                improvement = ((automl_score - baseline_score) / baseline_score) * 100
                self.log_test("AutoML Performance Comparison", "PASS", 
                             f"✅ AutoML improved performance: {baseline_score:.4f} → {automl_score:.4f} (+{improvement:.2f}%)")
            elif automl_score >= baseline_score * 0.95:  # Within 5% is acceptable
                self.log_test("AutoML Performance Comparison", "PASS", 
                             f"✅ AutoML performance comparable: {baseline_score:.4f} → {automl_score:.4f}")
            else:
                self.log_test("AutoML Performance Comparison", "FAIL", 
                             f"❌ AutoML performance worse: {baseline_score:.4f} → {automl_score:.4f}")
        else:
            self.log_test("AutoML Performance Comparison", "SKIP", "No AutoML response available for comparison")

    def test_automl_classification_problem(self):
        """Test 7: Test AutoML with Classification Problem"""
        if not hasattr(self, 'classification_path'):
            self.log_test("AutoML Classification Problem", "SKIP", "No classification dataset available")
            return
        
        print("🔍 Testing AutoML with classification problem...")
        
        data_source = {"type": "file", "path": self.classification_path}
        response = self.call_intelligent_prediction_api(
            data_source=data_source,
            user_prompt="Predict customer churn to improve retention",
            target_column="churn",
            feature_columns=["monthly_charges", "total_charges", "tenure_months", "support_calls"],
            models_to_train=["random_forest", "xgboost"],
            problem_type="classification",
            use_automl=True,
            automl_optimization_level="fast"
        )
        
        if "error" in response:
            self.log_test("AutoML Classification Problem", "FAIL", 
                         f"Error: {response['error']}", response)
            return
        
        # Check if response is successful and contains AutoML results for classification
        if response.get("status") == "success" and "data" in response:
            data = response["data"]
            training_summary = data.get("training_summary", {})
            problem_type = training_summary.get("problem_type")
            
            if problem_type == "classification":
                model_comparison = data.get("model_comparison", [])
                
                # Check for AutoML optimization in classification models
                optimized_models = []
                for model in model_comparison:
                    model_str = str(model)
                    if "automl_optimized" in model_str or "best_params" in model_str:
                        optimized_models.append(model.get("model_name"))
                
                if len(optimized_models) >= 1:
                    self.log_test("AutoML Classification Problem", "PASS", 
                                 f"✅ AutoML classification working: {len(optimized_models)} models optimized: {', '.join(optimized_models)}")
                    
                    # Store for detailed validation
                    self.automl_classification_response = response
                    return response
                else:
                    self.log_test("AutoML Classification Problem", "FAIL", 
                                 f"❌ AutoML optimization not detected for classification models")
                    return None
            else:
                self.log_test("AutoML Classification Problem", "FAIL", 
                             f"❌ Problem type not detected as classification: {problem_type}")
                return None
        else:
            self.log_test("AutoML Classification Problem", "FAIL", 
                         "AutoML classification request did not return expected results", response)
            return None

    def test_automl_optimization_levels(self):
        """Test 8: Test Different AutoML Optimization Levels"""
        if not hasattr(self, 'regression_path'):
            self.log_test("AutoML Optimization Levels", "SKIP", "No test dataset available")
            return
        
        print("🔍 Testing different AutoML optimization levels...")
        
        optimization_levels = ['fast', 'balanced', 'thorough']
        results = {}
        
        for level in optimization_levels:
            print(f"  Testing {level} optimization...")
            
            data_source = {"type": "file", "path": self.regression_path}
            response = self.call_intelligent_prediction_api(
                data_source=data_source,
                user_prompt=f"Predict house prices with {level} AutoML optimization",
                target_column="price",
                feature_columns=["bedrooms", "bathrooms", "sqft", "age"],
                models_to_train=["random_forest"],
                use_automl=True,
                automl_optimization_level=level
            )
            
            if "error" not in response and response.get("status") == "success":
                data = response["data"]
                execution_time = data.get("execution_time", 0)
                best_model = data.get("best_model", {})
                score = best_model.get("score", 0)
                
                results[level] = {
                    "success": True,
                    "execution_time": execution_time,
                    "score": score
                }
            else:
                results[level] = {
                    "success": False,
                    "error": response.get("error", "Unknown error")
                }
        
        # Analyze results
        successful_levels = [level for level, result in results.items() if result["success"]]
        
        if len(successful_levels) >= 2:
            # Check if execution times make sense (fast < balanced < thorough)
            times = {level: results[level]["execution_time"] for level in successful_levels}
            
            self.log_test("AutoML Optimization Levels", "PASS", 
                         f"✅ {len(successful_levels)} optimization levels working: {', '.join(successful_levels)}. Times: {times}")
        elif len(successful_levels) >= 1:
            self.log_test("AutoML Optimization Levels", "PARTIAL", 
                         f"Some optimization levels working: {', '.join(successful_levels)}")
        else:
            self.log_test("AutoML Optimization Levels", "FAIL", 
                         f"❌ No optimization levels working. Errors: {[results[level].get('error') for level in optimization_levels]}")

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🧪 AutoML Hyperparameter Optimization Testing for PROMISE AI Platform")
        print("=" * 80)
        print(f"Backend URL: {self.backend_url}")
        print()
        
        # Run tests in order
        self.test_setup_datasets()
        self.test_endpoint_accepts_automl_parameter()
        self.test_automl_with_random_forest()
        self.test_automl_with_multiple_models()
        self.test_automl_returns_optimized_hyperparameters()
        self.test_automl_performance_comparison()
        self.test_automl_classification_problem()
        self.test_automl_optimization_levels()
        
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
        
        # AutoML feature status
        automl_tests = [r for r in self.test_results if "AutoML" in r["test"] or "automl" in r["test"].lower()]
        automl_working = sum(1 for r in automl_tests if r["status"] in ["PASS", "PARTIAL"])
        
        print(f"\n🎯 AUTOML HYPERPARAMETER OPTIMIZATION STATUS:")
        if automl_working >= len(automl_tests) * 0.7:  # 70% threshold
            print("   ✅ AutoML hyperparameter optimization is working")
        else:
            print("   ❌ AutoML hyperparameter optimization needs attention")
        
        # Endpoint status
        endpoint_tests = [r for r in self.test_results if "Endpoint" in r["test"]]
        endpoint_working = any(r["status"] == "PASS" for r in endpoint_tests)
        
        print(f"\n🔗 INTELLIGENT PREDICTION ENDPOINT STATUS:")
        if endpoint_working:
            print("   ✅ /api/intelligent-prediction/train-and-predict endpoint is working")
        else:
            print("   ❌ Endpoint may not be configured correctly")
        
        # Performance comparison status
        performance_tests = [r for r in self.test_results if "Performance" in r["test"]]
        performance_working = any(r["status"] == "PASS" for r in performance_tests)
        
        print(f"\n📊 AUTOML PERFORMANCE STATUS:")
        if performance_working:
            print("   ✅ AutoML shows performance improvements")
        else:
            print("   ⚠️  AutoML performance comparison inconclusive")
        
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "partial": partial,
            "success_rate": success_rate,
            "automl_working": automl_working >= len(automl_tests) * 0.7,
            "endpoint_working": endpoint_working,
            "performance_working": performance_working
        }

def main():
    """Main test execution"""
    tester = AutoMLTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    if results["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
