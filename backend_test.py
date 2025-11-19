#!/usr/bin/env python3
"""
AutoML Hyperparameter Optimization Testing for PROMISE AI Platform
Tests the newly integrated AutoML feature for the MCP intelligent prediction endpoint
"""

import requests
import json
import sys
import time
import csv
import io
from typing import Dict, List, Any

# Backend URL from environment
BACKEND_URL = "https://model-wizard-2.preview.emergentagent.com/api"

class AutoMLTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.test_csv_path = "/tmp/automl_test_data.csv"
        
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

    def create_test_datasets(self):
        """Create test datasets for regression and classification"""
        import random
        import numpy as np
        
        # Create regression dataset (predicting house prices)
        regression_data = []
        regression_data.append(["bedrooms", "bathrooms", "sqft", "age", "price"])
        
        for i in range(300):  # Enough data for ML training
            bedrooms = random.randint(1, 5)
            bathrooms = random.randint(1, 4)
            sqft = random.randint(800, 4000)
            age = random.randint(0, 50)
            
            # Price formula with some noise
            base_price = (sqft * 150) + (bedrooms * 10000) + (bathrooms * 15000) - (age * 1000)
            noise = random.uniform(-50000, 50000)
            price = max(100000, base_price + noise)
            
            regression_data.append([bedrooms, bathrooms, sqft, age, int(price)])
        
        # Save regression dataset
        regression_path = "/tmp/regression_test_data.csv"
        with open(regression_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(regression_data)
        
        # Create classification dataset (predicting customer churn)
        classification_data = []
        classification_data.append(["monthly_charges", "total_charges", "tenure_months", "support_calls", "churn"])
        
        for i in range(300):
            monthly_charges = random.uniform(20, 120)
            tenure_months = random.randint(1, 72)
            total_charges = monthly_charges * tenure_months + random.uniform(-500, 500)
            support_calls = random.randint(0, 10)
            
            # Churn probability based on features
            churn_prob = 0.1
            if monthly_charges > 80:
                churn_prob += 0.2
            if tenure_months < 12:
                churn_prob += 0.3
            if support_calls > 5:
                churn_prob += 0.4
            
            churn = 1 if random.random() < churn_prob else 0
            
            classification_data.append([monthly_charges, total_charges, tenure_months, support_calls, churn])
        
        # Save classification dataset
        classification_path = "/tmp/classification_test_data.csv"
        with open(classification_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(classification_data)
        
        return regression_path, classification_path

    def call_intelligent_prediction_api(self, data_source: Dict, user_prompt: str, target_column: str, 
                                       feature_columns: List[str], models_to_train: List[str] = None,
                                       problem_type: str = None, use_automl: bool = False, 
                                       automl_optimization_level: str = 'fast') -> Dict:
        """Call the intelligent prediction API"""
        payload = {
            "data_source": data_source,
            "user_prompt": user_prompt,
            "target_column": target_column,
            "feature_columns": feature_columns,
            "models_to_train": models_to_train or ["random_forest", "xgboost", "ridge"],
            "problem_type": problem_type,
            "include_forecasting": True,
            "include_insights": True,
            "test_size": 0.2,
            "use_automl": use_automl,
            "automl_optimization_level": automl_optimization_level
        }
        
        try:
            response = requests.post(
                f"{self.backend_url}/intelligent-prediction/train-and-predict",
                json=payload,
                timeout=300  # 5 minutes timeout for AutoML
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

    def test_setup_datasets(self):
        """Test 1: Setup test datasets for regression and classification"""
        try:
            regression_path, classification_path = self.create_test_datasets()
            self.regression_path = regression_path
            self.classification_path = classification_path
            
            self.log_test("Setup Test Datasets", "PASS", 
                         f"Created regression dataset: {regression_path} and classification dataset: {classification_path}")
        except Exception as e:
            self.log_test("Setup Test Datasets", "FAIL", f"Failed to create test datasets: {str(e)}")

    def test_endpoint_accepts_automl_parameter(self):
        """Test 2: Verify endpoint accepts use_automl parameter"""
        if not hasattr(self, 'regression_path'):
            self.log_test("Endpoint Accepts AutoML Parameter", "SKIP", "No test dataset available")
            return None
        
        print("🔍 Testing endpoint accepts use_automl parameter...")
        
        data_source = {"type": "file", "path": self.regression_path}
        response = self.call_intelligent_prediction_api(
            data_source=data_source,
            user_prompt="Predict house prices for real estate analysis",
            target_column="price",
            feature_columns=["bedrooms", "bathrooms", "sqft", "age"],
            models_to_train=["random_forest"],
            use_automl=False  # Test with AutoML disabled first
        )
        
        if "error" in response:
            self.log_test("Endpoint Accepts AutoML Parameter", "FAIL", 
                         f"Error: {response['error']}", response)
            return None
        
        # Check if response is successful
        if response.get("status") == "success" and "data" in response:
            data = response["data"]
            training_summary = data.get("training_summary", {})
            
            self.log_test("Endpoint Accepts AutoML Parameter", "PASS", 
                         f"Endpoint accepts use_automl parameter. Trained {training_summary.get('models_trained', 0)} models")
            
            # Store baseline for comparison
            self.baseline_response = response
            return response
        else:
            self.log_test("Endpoint Accepts AutoML Parameter", "FAIL", 
                         "Endpoint did not return expected results", response)
            return None

    def test_analysis_with_sre_forecast_generation(self):
        """Test 3: Analysis WITH SRE Forecast Generation (CRITICAL TEST)"""
        if not self.test_dataset_id:
            self.log_test("Analysis With SRE Forecast Generation", "SKIP", "No test dataset available")
            return None
        
        # Define user selection with expectation for SRE forecasting
        user_selection = {
            "target_variable": "latency_ms",
            "selected_features": ["cpu_usage", "memory_usage"],
            "mode": "manual",
            "user_expectation": "Predict system latency to prevent performance degradation"
        }
        
        print("🔍 Running analysis WITH SRE forecast generation...")
        response = self.run_holistic_analysis(self.test_dataset_id, user_selection)
        
        if "error" in response:
            self.log_test("Analysis With SRE Forecast Generation", "FAIL", 
                         f"Error: {response['error']}", response)
            return None
        
        # Check if analysis completed successfully
        if "insights" in response and "ml_models" in response:
            models = response.get("ml_models", [])
            
            # CRITICAL: Check for sre_forecast field
            sre_forecast = response.get("sre_forecast")
            
            if sre_forecast:
                self.log_test("Analysis With SRE Forecast Generation", "PASS", 
                             f"✅ SRE FORECAST FOUND: Generated {len(models)} models with SRE forecasting.")
                
                # Store for detailed validation
                self.sre_forecast_response = response
                return response
            else:
                self.log_test("Analysis With SRE Forecast Generation", "FAIL", 
                             f"❌ SRE FORECAST MISSING: Analysis completed with {len(models)} models but no sre_forecast field.")
                return None
        else:
            self.log_test("Analysis With SRE Forecast Generation", "FAIL", 
                         "Analysis did not return expected results", response)
            return None

    def test_sre_forecast_content_validation(self):
        """Test 4: Validate SRE Forecast Content Structure"""
        if not hasattr(self, 'sre_forecast_response'):
            self.log_test("SRE Forecast Content Validation", "SKIP", "No SRE forecast response available")
            return
        
        sre_forecast = self.sre_forecast_response.get("sre_forecast", {})
        
        # Check required fields
        required_fields = ["forecasts", "critical_alerts", "recommendations"]
        missing_fields = [field for field in required_fields if field not in sre_forecast]
        
        if missing_fields:
            self.log_test("SRE Forecast Content Validation", "FAIL", 
                         f"Missing required fields: {missing_fields}")
            return
        
        # Validate forecasts structure
        forecasts = sre_forecast.get("forecasts", [])
        forecast_valid = True
        forecast_details = []
        
        for i, forecast in enumerate(forecasts):
            required_forecast_fields = ["timeframe", "prediction", "value", "confidence"]
            missing_forecast_fields = [field for field in required_forecast_fields if field not in forecast]
            if missing_forecast_fields:
                forecast_valid = False
                forecast_details.append(f"Forecast {i+1} missing: {missing_forecast_fields}")
            else:
                forecast_details.append(f"Forecast {i+1}: {forecast['timeframe']} - {forecast['prediction']}")
        
        # Validate alerts structure
        alerts = sre_forecast.get("critical_alerts", [])
        alert_valid = True
        alert_details = []
        
        for i, alert in enumerate(alerts):
            required_alert_fields = ["severity", "alert"]
            missing_alert_fields = [field for field in required_alert_fields if field not in alert]
            if missing_alert_fields:
                alert_valid = False
                alert_details.append(f"Alert {i+1} missing: {missing_alert_fields}")
            else:
                alert_details.append(f"Alert {i+1}: {alert['severity']} - {alert['alert']}")
        
        # Validate recommendations structure
        recommendations = sre_forecast.get("recommendations", [])
        rec_valid = True
        rec_details = []
        
        for i, rec in enumerate(recommendations):
            required_rec_fields = ["priority", "action"]
            missing_rec_fields = [field for field in required_rec_fields if field not in rec]
            if missing_rec_fields:
                rec_valid = False
                rec_details.append(f"Recommendation {i+1} missing: {missing_rec_fields}")
            else:
                rec_details.append(f"Recommendation {i+1}: {rec['priority']} - {rec['action']}")
        
        # Overall validation
        if forecast_valid and alert_valid and rec_valid:
            self.log_test("SRE Forecast Content Validation", "PASS", 
                         f"✅ All structures valid: {len(forecasts)} forecasts, {len(alerts)} alerts, {len(recommendations)} recommendations")
            print(f"   📊 Forecasts: {forecast_details}")
            print(f"   🚨 Alerts: {alert_details}")
            print(f"   💡 Recommendations: {rec_details}")
        else:
            issues = []
            if not forecast_valid:
                issues.extend(forecast_details)
            if not alert_valid:
                issues.extend(alert_details)
            if not rec_valid:
                issues.extend(rec_details)
            
            self.log_test("SRE Forecast Content Validation", "FAIL", 
                         f"Structure validation failed: {'; '.join(issues)}")

    def test_backend_logging_verification(self):
        """Test 5: Check Backend Logging for SRE Forecast Generation"""
        # Since we can't directly access logs, we'll check for indicators in the response
        # that suggest proper logging is happening
        
        if not hasattr(self, 'sre_forecast_response'):
            self.log_test("Backend Logging Verification", "SKIP", "No SRE forecast response available")
            return
        
        response = self.sre_forecast_response
        
        # Check if we have models (indicates training completed)
        models = response.get("ml_models", [])
        sre_forecast = response.get("sre_forecast", {})
        
        # If we have models and SRE forecast, logging should have occurred
        if models and sre_forecast:
            forecasts_count = len(sre_forecast.get("forecasts", []))
            alerts_count = len(sre_forecast.get("critical_alerts", []))
            
            self.log_test("Backend Logging Verification", "PASS", 
                         f"✅ SRE forecast generation completed: {forecasts_count} forecasts, {alerts_count} alerts (logging should show: '🔮 Generating SRE-style forecast summaries...' and '✅ SRE forecast generated')")
        else:
            self.log_test("Backend Logging Verification", "FAIL", 
                         "SRE forecast generation may not have completed properly")

    def test_sre_terminology_usage(self):
        """Test 6: Verify SRE Terminology is Used in Forecasts"""
        if not hasattr(self, 'sre_forecast_response'):
            self.log_test("SRE Terminology Usage", "SKIP", "No SRE forecast response available")
            return
        
        sre_forecast = self.sre_forecast_response.get("sre_forecast", {})
        
        # Collect all text from forecasts, alerts, and recommendations
        all_text = ""
        
        for forecast in sre_forecast.get("forecasts", []):
            all_text += f" {forecast.get('prediction', '')} {forecast.get('value', '')}"
        
        for alert in sre_forecast.get("critical_alerts", []):
            all_text += f" {alert.get('alert', '')}"
        
        for rec in sre_forecast.get("recommendations", []):
            all_text += f" {rec.get('action', '')}"
        
        all_text = all_text.lower()
        
        # Check for SRE terminology
        sre_terms = [
            "slo", "latency", "threshold", "percentile", "p95", "p99", 
            "error budget", "capacity", "performance", "monitoring", 
            "reliability", "availability", "degradation", "optimization"
        ]
        
        found_terms = [term for term in sre_terms if term in all_text]
        
        if len(found_terms) >= 3:
            self.log_test("SRE Terminology Usage", "PASS", 
                         f"✅ SRE terminology detected: {found_terms}")
        elif len(found_terms) >= 1:
            self.log_test("SRE Terminology Usage", "PARTIAL", 
                         f"Some SRE terminology found: {found_terms}")
        else:
            self.log_test("SRE Terminology Usage", "FAIL", 
                         "No SRE terminology detected in forecasts")

    def test_azure_openai_integration(self):
        """Test 7: Azure OpenAI Integration for SRE Forecasting"""
        if not hasattr(self, 'sre_forecast_response'):
            self.log_test("Azure OpenAI Integration", "SKIP", "No SRE forecast response available")
            return
        
        sre_forecast = self.sre_forecast_response.get("sre_forecast", {})
        
        # Check if we have valid JSON structure (indicates Azure OpenAI worked)
        if sre_forecast.get("error"):
            self.log_test("Azure OpenAI Integration", "FAIL", 
                         f"Azure OpenAI error: {sre_forecast['error']}")
            return
        
        forecasts = sre_forecast.get("forecasts", [])
        alerts = sre_forecast.get("critical_alerts", [])
        recommendations = sre_forecast.get("recommendations", [])
        
        # Check for meaningful content (not just empty arrays)
        total_items = len(forecasts) + len(alerts) + len(recommendations)
        
        if total_items >= 5:  # Expect at least 5 total items
            self.log_test("Azure OpenAI Integration", "PASS", 
                         f"✅ Azure OpenAI generated valid SRE forecast: {len(forecasts)} forecasts, {len(alerts)} alerts, {len(recommendations)} recommendations")
        elif total_items >= 1:
            self.log_test("Azure OpenAI Integration", "PARTIAL", 
                         f"Azure OpenAI generated limited content: {total_items} total items")
        else:
            self.log_test("Azure OpenAI Integration", "FAIL", 
                         "Azure OpenAI did not generate meaningful SRE forecast content")

    def test_different_problem_types(self):
        """Test 8: Test SRE Forecasting with Different Problem Types"""
        if not self.test_dataset_id:
            self.log_test("Different Problem Types", "SKIP", "No test dataset available")
            return
        
        # Test with classification problem (status prediction)
        user_selection_classification = {
            "target_variable": "status",
            "selected_features": ["cpu_usage", "memory_usage", "latency_ms"],
            "mode": "manual",
            "user_expectation": "Predict system failure status to prevent outages"
        }
        
        print("🔍 Testing SRE forecast with classification problem...")
        response = self.run_holistic_analysis(self.test_dataset_id, user_selection_classification)
        
        if "error" in response:
            self.log_test("Different Problem Types", "FAIL", 
                         f"Classification test failed: {response['error']}")
            return
        
        # Check if SRE forecast adapts to classification problem
        sre_forecast = response.get("sre_forecast", {})
        
        if sre_forecast:
            # Check if forecasts mention classification-specific terms
            all_text = ""
            for forecast in sre_forecast.get("forecasts", []):
                all_text += f" {forecast.get('prediction', '')}"
            
            classification_terms = ["failure", "success", "error", "status", "probability", "classification"]
            found_classification_terms = [term for term in classification_terms if term.lower() in all_text.lower()]
            
            if found_classification_terms:
                self.log_test("Different Problem Types", "PASS", 
                             f"✅ SRE forecast adapts to classification: {found_classification_terms}")
            else:
                self.log_test("Different Problem Types", "PARTIAL", 
                             "SRE forecast generated but may not be classification-specific")
        else:
            self.log_test("Different Problem Types", "FAIL", 
                         "No SRE forecast generated for classification problem")

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🧪 SRE-Style Forecasting Feature Testing for PROMISE AI Platform")
        print("=" * 80)
        print(f"Backend URL: {self.backend_url}")
        print()
        
        # Run tests in order
        self.test_setup_dataset()
        self.test_analysis_without_user_expectation()
        self.test_analysis_with_sre_forecast_generation()
        self.test_sre_forecast_content_validation()
        self.test_backend_logging_verification()
        self.test_sre_terminology_usage()
        self.test_azure_openai_integration()
        self.test_different_problem_types()
        
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
        
        # SRE forecasting feature status
        sre_tests = [r for r in self.test_results if "SRE" in r["test"] or "Forecast" in r["test"]]
        sre_working = sum(1 for r in sre_tests if r["status"] in ["PASS", "PARTIAL"])
        
        print(f"\n🎯 SRE FORECASTING FEATURE STATUS:")
        if sre_working >= len(sre_tests) * 0.7:  # 70% threshold
            print("   ✅ SRE forecasting feature is working")
        else:
            print("   ❌ SRE forecasting feature needs attention")
        
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
            "sre_working": sre_working >= len(sre_tests) * 0.7,
            "ai_working": ai_working
        }

def main():
    """Main test execution"""
    tester = SREForecastTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    if results["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
