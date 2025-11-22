#!/usr/bin/env python3
"""
SRE Forecasting & Historical Trends Feature Fix Testing
Tests the specific fix where backend was passing 'models' key but Azure OpenAI expected 'ml_models' key
"""

import requests
import json
import sys
import time
from typing import Dict, List, Any

# Backend URL from environment
BACKEND_URL = "https://oracle-ml-hub.preview.emergentagent.com/api"

class SREForecastFixTester:
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

    def find_suitable_dataset(self) -> str:
        """Find existing dataset suitable for SRE forecasting testing"""
        datasets = self.get_available_datasets()
        
        # Look for the specific SRE test dataset first
        for dataset in datasets:
            name = dataset.get("name", "").lower()
            dataset_id = dataset.get("id")
            row_count = dataset.get("row_count", 0)
            
            if dataset_id == "5621a093-501c-45c6-b7d3-ea5f0ea33e43" or ("sre_test_latency_data" in name):
                print(f"✅ Found SRE test dataset: {dataset.get('name')} (ID: {dataset_id}, {row_count} rows)")
                return dataset_id
        
        # Look for any other suitable dataset
        for dataset in datasets:
            name = dataset.get("name", "").lower()
            row_count = dataset.get("row_count", 0)
            
            if ("sre" in name or "latency" in name) and row_count >= 50:
                dataset_id = dataset.get("id")
                print(f"✅ Found suitable existing dataset: {dataset.get('name')} (ID: {dataset_id}, {row_count} rows)")
                return dataset_id
        
        # If no suitable dataset found, return None
        print("❌ No suitable existing dataset found for SRE forecasting testing")
        return None

    def run_holistic_analysis_with_expectation(self, dataset_id: str, user_expectation: str) -> Dict:
        """Run holistic analysis with user expectation to trigger SRE forecast generation"""
        payload = {
            "dataset_id": dataset_id,
            "workspace_name": "sre_forecast_fix_test",
            "problem_type": "auto",
            "user_selection": {
                "user_expectation": user_expectation
            }
        }
        
        try:
            print(f"🔄 Running holistic analysis with expectation: '{user_expectation}'")
            response = requests.post(
                f"{self.backend_url}/analysis/holistic",
                json=payload,
                timeout=120  # Extended timeout for full analysis
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
        dataset_id = self.find_suitable_dataset()
        
        if dataset_id:
            self.test_dataset_id = dataset_id
            self.log_test(
                "Setup Test Dataset",
                "PASS",
                f"Using existing dataset: {dataset_id}"
            )
        else:
            self.log_test(
                "Setup Test Dataset",
                "FAIL",
                "No suitable dataset found for SRE forecasting testing"
            )

    def test_sre_forecast_generation(self):
        """Test 2: SRE Forecast Generation with Historical Trends"""
        if not self.test_dataset_id:
            self.log_test(
                "SRE Forecast Generation",
                "SKIP",
                "No dataset available"
            )
            return

        # Run analysis with user expectation to trigger SRE forecast
        user_expectation = "Predict system latency to prevent performance degradation and identify SLO violations"
        
        result = self.run_holistic_analysis_with_expectation(
            self.test_dataset_id,
            user_expectation
        )
        
        if result.get("error"):
            self.log_test(
                "SRE Forecast Generation",
                "FAIL",
                f"Analysis failed: {result.get('error')} - {result.get('details')}",
                result
            )
            return

        # Check if both historical_trends and sre_forecast are present
        has_historical_trends = "historical_trends" in result
        has_sre_forecast = "sre_forecast" in result
        
        if has_historical_trends and has_sre_forecast:
            self.log_test(
                "SRE Forecast Generation",
                "PASS",
                f"✅ Both historical_trends and sre_forecast present in response"
            )
        elif has_historical_trends and not has_sre_forecast:
            self.log_test(
                "SRE Forecast Generation",
                "FAIL",
                "❌ historical_trends present but sre_forecast missing - Fix not working",
                {"has_historical_trends": has_historical_trends, "has_sre_forecast": has_sre_forecast}
            )
        elif not has_historical_trends and has_sre_forecast:
            self.log_test(
                "SRE Forecast Generation",
                "PARTIAL",
                "🟡 sre_forecast present but historical_trends missing",
                {"has_historical_trends": has_historical_trends, "has_sre_forecast": has_sre_forecast}
            )
        else:
            self.log_test(
                "SRE Forecast Generation",
                "FAIL",
                "❌ Both historical_trends and sre_forecast missing",
                {"has_historical_trends": has_historical_trends, "has_sre_forecast": has_sre_forecast}
            )

        # Store result for detailed validation
        self.analysis_result = result

    def test_sre_forecast_structure(self):
        """Test 3: SRE Forecast Structure Validation"""
        if not hasattr(self, 'analysis_result'):
            self.log_test(
                "SRE Forecast Structure",
                "SKIP",
                "No analysis result available"
            )
            return

        sre_forecast = self.analysis_result.get("sre_forecast")
        if not sre_forecast:
            self.log_test(
                "SRE Forecast Structure",
                "FAIL",
                "sre_forecast not present in response"
            )
            return

        # Check required fields
        required_fields = ["forecasts", "critical_alerts", "feature_influence"]
        optional_fields = ["good_news"]
        
        missing_required = []
        present_fields = []
        
        for field in required_fields:
            if field in sre_forecast:
                present_fields.append(field)
            else:
                missing_required.append(field)
        
        # Check optional fields
        for field in optional_fields:
            if field in sre_forecast:
                present_fields.append(f"{field} (optional)")

        if not missing_required:
            # Check if forecasts array is not empty
            forecasts = sre_forecast.get("forecasts", [])
            critical_alerts = sre_forecast.get("critical_alerts", [])
            
            if len(forecasts) > 0 and len(critical_alerts) >= 0:  # alerts can be empty
                self.log_test(
                    "SRE Forecast Structure",
                    "PASS",
                    f"✅ All required fields present: {present_fields}. Forecasts: {len(forecasts)}, Alerts: {len(critical_alerts)}"
                )
            else:
                self.log_test(
                    "SRE Forecast Structure",
                    "FAIL",
                    f"❌ Required fields present but forecasts array is empty: {len(forecasts)} forecasts"
                )
        else:
            self.log_test(
                "SRE Forecast Structure",
                "FAIL",
                f"❌ Missing required fields: {missing_required}. Present: {present_fields}"
            )

    def test_backend_logs_verification(self):
        """Test 4: Backend Logs Verification"""
        # This test checks if we can verify the fix through response indicators
        if not hasattr(self, 'analysis_result'):
            self.log_test(
                "Backend Logs Verification",
                "SKIP",
                "No analysis result available"
            )
            return

        result = self.analysis_result
        
        # Check for success indicators in the response
        has_sre_forecast = "sre_forecast" in result
        has_detected_domain = "detected_domain" in result
        
        if has_sre_forecast:
            sre_forecast = result["sre_forecast"]
            forecasts_count = len(sre_forecast.get("forecasts", []))
            alerts_count = len(sre_forecast.get("critical_alerts", []))
            
            if forecasts_count > 0:
                self.log_test(
                    "Backend Logs Verification",
                    "PASS",
                    f"✅ SRE forecast generated successfully: {forecasts_count} forecasts, {alerts_count} alerts. Domain: {result.get('detected_domain', 'unknown')}"
                )
            else:
                self.log_test(
                    "Backend Logs Verification",
                    "FAIL",
                    "❌ SRE forecast present but no forecasts generated - indicates Azure OpenAI integration issue"
                )
        else:
            self.log_test(
                "Backend Logs Verification",
                "FAIL",
                "❌ No SRE forecast in response - indicates the fix may not be working"
            )

    def test_historical_trends_presence(self):
        """Test 5: Historical Trends Presence"""
        if not hasattr(self, 'analysis_result'):
            self.log_test(
                "Historical Trends Presence",
                "SKIP",
                "No analysis result available"
            )
            return

        historical_trends = self.analysis_result.get("historical_trends")
        
        if historical_trends:
            # Check if historical trends has meaningful content
            if isinstance(historical_trends, dict) and len(historical_trends) > 0:
                self.log_test(
                    "Historical Trends Presence",
                    "PASS",
                    f"✅ Historical trends present with {len(historical_trends)} sections"
                )
            elif isinstance(historical_trends, list) and len(historical_trends) > 0:
                self.log_test(
                    "Historical Trends Presence",
                    "PASS",
                    f"✅ Historical trends present with {len(historical_trends)} items"
                )
            else:
                self.log_test(
                    "Historical Trends Presence",
                    "PARTIAL",
                    "🟡 Historical trends present but appears empty"
                )
        else:
            self.log_test(
                "Historical Trends Presence",
                "FAIL",
                "❌ Historical trends missing from response"
            )

    def test_fix_validation(self):
        """Test 6: Overall Fix Validation"""
        if not hasattr(self, 'analysis_result'):
            self.log_test(
                "Fix Validation",
                "SKIP",
                "No analysis result available"
            )
            return

        result = self.analysis_result
        
        # The fix should ensure both sections are present
        has_historical_trends = "historical_trends" in result
        has_sre_forecast = "sre_forecast" in result
        
        if has_historical_trends and has_sre_forecast:
            # Check if sre_forecast has content (indicating Azure OpenAI integration works)
            sre_forecast = result["sre_forecast"]
            forecasts = sre_forecast.get("forecasts", [])
            
            if len(forecasts) > 0:
                self.log_test(
                    "Fix Validation",
                    "PASS",
                    f"✅ FIX SUCCESSFUL: Both historical_trends and sre_forecast present with {len(forecasts)} forecasts"
                )
            else:
                self.log_test(
                    "Fix Validation",
                    "PARTIAL",
                    "🟡 Both sections present but sre_forecast has no forecasts - may indicate partial fix"
                )
        else:
            missing_sections = []
            if not has_historical_trends:
                missing_sections.append("historical_trends")
            if not has_sre_forecast:
                missing_sections.append("sre_forecast")
            
            self.log_test(
                "Fix Validation",
                "FAIL",
                f"❌ FIX NOT WORKING: Missing sections: {missing_sections}"
            )

    def run_all_tests(self):
        """Run all SRE forecast fix tests"""
        print("🧪 SRE Forecasting & Historical Trends Feature Fix Testing")
        print("=" * 60)
        print(f"Backend URL: {self.backend_url}")
        print(f"Test Focus: Verify 'models' -> 'ml_models' key fix for Azure OpenAI")
        print()

        # Run tests in sequence
        self.test_setup_dataset()
        self.test_sre_forecast_generation()
        self.test_sre_forecast_structure()
        self.test_backend_logs_verification()
        self.test_historical_trends_presence()
        self.test_fix_validation()

        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for r in self.test_results if r["status"] == "PASS")
        failed = sum(1 for r in self.test_results if r["status"] == "FAIL")
        partial = sum(1 for r in self.test_results if r["status"] == "PARTIAL")
        skipped = sum(1 for r in self.test_results if r["status"] == "SKIP")
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"🟡 Partial: {partial}")
        print(f"⏭️ Skipped: {skipped}")
        
        if failed == 0 and partial == 0:
            print(f"\n🎉 ALL TESTS PASSED! SRE Forecasting fix is working correctly.")
        elif failed == 0:
            print(f"\n🟡 MOSTLY WORKING with {partial} partial results. Fix appears to be working.")
        else:
            print(f"\n❌ {failed} TESTS FAILED. SRE Forecasting fix needs attention.")
        
        return self.test_results

if __name__ == "__main__":
    tester = SREForecastFixTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    failed_count = sum(1 for r in results if r["status"] == "FAIL")
    sys.exit(0 if failed_count == 0 else 1)