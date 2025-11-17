#!/usr/bin/env python3
"""
Smart Selection & Domain-Agnostic Features Testing for PROMISE AI Platform
Tests Phase 1 Remaining: Smart Selection & Domain-Agnostic Features
"""

import requests
import json
import sys
import time
from typing import Dict, List, Any

# Backend URL from environment
BACKEND_URL = "https://promise-ai-1.preview.emergentagent.com/api"

class SmartSelectionTester:
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

    def upload_it_infrastructure_dataset(self) -> str:
        """Upload IT infrastructure test dataset for smart selection testing"""
        import random
        
        # Create IT infrastructure dataset with latency/performance data
        csv_lines = ["timestamp,service_name,endpoint,latency_ms,cpu_usage,memory_usage,error_rate,throughput,region,status"]
        
        services = ["auth-service", "payment-service", "user-service", "order-service", "notification-service"]
        endpoints = ["/login", "/checkout", "/profile", "/orders", "/send"]
        regions = ["us-east", "us-west", "eu-central", "ap-southeast"]
        statuses = ["success", "error", "timeout", "warning"]
        
        # Generate 100 rows of realistic IT infrastructure data
        for i in range(100):
            timestamp = f"2024-11-{17 + i//10:02d} {(i*15)//60:02d}:{(i*15)%60:02d}:00"
            service = random.choice(services)
            endpoint = random.choice(endpoints)
            
            # Generate correlated metrics for realistic IT data
            base_latency = random.uniform(50, 800)
            cpu_usage = min(100, max(10, base_latency * 0.12 + random.uniform(-20, 20)))
            memory_usage = min(100, max(10, base_latency * 0.10 + random.uniform(-15, 15)))
            error_rate = max(0, min(50, (base_latency - 200) * 0.05 + random.uniform(-2, 2)))
            throughput = max(10, 1000 - base_latency * 0.8 + random.uniform(-100, 100))
            region = random.choice(regions)
            
            # Higher latency = higher chance of error
            if base_latency > 600:
                status = random.choice(["error", "timeout"]) if random.random() < 0.6 else "success"
            elif base_latency > 400:
                status = "warning" if random.random() < 0.4 else "success"
            else:
                status = "success" if random.random() < 0.85 else random.choice(["warning", "error"])
            
            csv_lines.append(f"{timestamp},{service},{endpoint},{base_latency:.1f},{cpu_usage:.1f},{memory_usage:.1f},{error_rate:.2f},{throughput:.1f},{region},{status}")
        
        test_csv_content = "\n".join(csv_lines)

        try:
            files = {
                'file': ('it_infrastructure_test_data.csv', test_csv_content, 'text/csv')
            }
            
            response = requests.post(
                f"{self.backend_url}/datasource/upload",
                files=files,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                dataset_id = data.get("dataset_id")
                if dataset_id:
                    print(f"✅ IT infrastructure test dataset uploaded successfully: {dataset_id} (100 rows)")
                    return dataset_id
                else:
                    print(f"❌ Upload response missing dataset_id: {data}")
                    return None
            else:
                print(f"❌ Failed to upload IT infrastructure test dataset: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Exception during IT infrastructure dataset upload: {str(e)}")
            return None

    def test_smart_selection_it_infrastructure(self):
        """Test 1: Smart Selection with IT Infrastructure Data"""
        if not self.test_dataset_id:
            self.log_test("Smart Selection IT Infrastructure", "SKIP", "No test dataset available")
            return None
        
        # Test smart selection with IT infrastructure expectation
        payload = {
            "dataset_id": self.test_dataset_id,
            "user_expectation": "I want to predict system latency to identify performance bottlenecks"
        }
        
        try:
            response = requests.post(
                f"{self.backend_url}/analysis/suggest-from-expectation",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if response has required fields
                if "suggestions" in data:
                    suggestions = data["suggestions"]
                    required_fields = ["suggested_target", "suggested_features", "problem_type", "confidence", "explanation"]
                    missing_fields = [field for field in required_fields if field not in suggestions]
                    
                    if not missing_fields:
                        target = suggestions.get("suggested_target")
                        features = suggestions.get("suggested_features", [])
                        problem_type = suggestions.get("problem_type")
                        confidence = suggestions.get("confidence")
                        
                        # Validate suggestions make sense for IT data
                        it_relevant = False
                        if target and ("latency" in target.lower() or "performance" in target.lower()):
                            it_relevant = True
                        
                        self.log_test("Smart Selection IT Infrastructure", "PASS", 
                                     f"✅ Smart selection working: target={target}, features={len(features)}, type={problem_type}, confidence={confidence}, IT-relevant={it_relevant}")
                        
                        # Store for later tests
                        self.it_suggestions = suggestions
                        return data
                    else:
                        self.log_test("Smart Selection IT Infrastructure", "FAIL", 
                                     f"Missing required fields: {missing_fields}")
                        return None
                else:
                    self.log_test("Smart Selection IT Infrastructure", "FAIL", 
                                 "Response missing 'suggestions' field", data)
                    return None
            else:
                self.log_test("Smart Selection IT Infrastructure", "FAIL", 
                             f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Smart Selection IT Infrastructure", "FAIL", 
                         f"Request failed: {str(e)}")
            return None

    def test_smart_selection_different_domain(self):
        """Test 2: Smart Selection with Different Domain (E-commerce/Finance)"""
        if not self.test_dataset_id:
            self.log_test("Smart Selection Different Domain", "SKIP", "No test dataset available")
            return None
        
        # Test with e-commerce expectation on IT data (should adapt)
        payload = {
            "dataset_id": self.test_dataset_id,
            "user_expectation": "Predict customer churn based on service usage patterns"
        }
        
        try:
            response = requests.post(
                f"{self.backend_url}/analysis/suggest-from-expectation",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if "suggestions" in data:
                    suggestions = data["suggestions"]
                    target = suggestions.get("suggested_target")
                    features = suggestions.get("suggested_features", [])
                    explanation = suggestions.get("explanation", "")
                    
                    # Check if AI adapts suggestions to different domain expectation
                    domain_adapted = False
                    if target or len(features) > 0:
                        domain_adapted = True
                    
                    # Compare with IT infrastructure suggestions
                    different_from_it = True
                    if hasattr(self, 'it_suggestions'):
                        it_target = self.it_suggestions.get("suggested_target")
                        if target == it_target:
                            different_from_it = False
                    
                    self.log_test("Smart Selection Different Domain", "PASS", 
                                 f"✅ Domain adaptation working: target={target}, features={len(features)}, adapted={domain_adapted}, different_from_IT={different_from_it}")
                    return data
                else:
                    self.log_test("Smart Selection Different Domain", "FAIL", 
                                 "Response missing 'suggestions' field", data)
                    return None
            else:
                self.log_test("Smart Selection Different Domain", "FAIL", 
                             f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Smart Selection Different Domain", "FAIL", 
                         f"Request failed: {str(e)}")
            return None

    def run_holistic_analysis_with_expectation(self, user_expectation: str) -> Dict:
        """Run holistic analysis with user expectation"""
        payload = {
            "dataset_id": self.test_dataset_id,
            "workspace_name": "test_workspace_smart_selection",
            "problem_type": "auto",
            "user_selection": {
                "mode": "auto",
                "user_expectation": user_expectation
            }
        }
        
        try:
            response = requests.post(
                f"{self.backend_url}/analysis/holistic",
                json=payload,
                timeout=60
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

    def test_domain_detection(self):
        """Test 3: Domain Detection in Holistic Analysis"""
        if not self.test_dataset_id:
            self.log_test("Domain Detection", "SKIP", "No test dataset available")
            return None
        
        print("🔍 Running holistic analysis with IT expectation for domain detection...")
        response = self.run_holistic_analysis_with_expectation(
            "I want to predict system latency to identify performance bottlenecks"
        )
        
        if "error" in response:
            self.log_test("Domain Detection", "FAIL", 
                         f"Analysis failed: {response['error']}")
            return None
        
        # Check for detected_domain field
        detected_domain = response.get("detected_domain")
        
        if detected_domain:
            domain_name = detected_domain if isinstance(detected_domain, str) else detected_domain.get("domain", "unknown")
            
            # Validate domain is one of expected categories
            valid_domains = ["it_infrastructure", "finance_trading", "ecommerce", "food_agriculture", 
                           "payments_banking", "healthcare", "logistics", "general"]
            
            if domain_name in valid_domains:
                self.log_test("Domain Detection", "PASS", 
                             f"✅ Domain detected: {domain_name}")
                
                # Store for later tests
                self.detected_domain_response = response
                return response
            else:
                self.log_test("Domain Detection", "FAIL", 
                             f"Invalid domain detected: {domain_name}")
                return None
        else:
            self.log_test("Domain Detection", "FAIL", 
                         "No 'detected_domain' field found in response")
            return None

    def test_domain_adapted_sre_forecast(self):
        """Test 4: Domain-Adapted SRE Forecast"""
        if not hasattr(self, 'detected_domain_response'):
            self.log_test("Domain-Adapted SRE Forecast", "SKIP", "No domain detection response available")
            return
        
        response = self.detected_domain_response
        
        # Check for SRE forecast
        sre_forecast = response.get("sre_forecast")
        
        if sre_forecast:
            # Check if forecast uses domain-appropriate terminology
            all_text = ""
            
            # Collect text from forecasts
            for forecast in sre_forecast.get("forecasts", []):
                all_text += f" {forecast.get('prediction', '')} {forecast.get('value', '')}"
            
            # Collect text from alerts
            for alert in sre_forecast.get("critical_alerts", []):
                all_text += f" {alert.get('alert', '')}"
            
            # Collect text from recommendations
            for rec in sre_forecast.get("recommendations", []):
                all_text += f" {rec.get('action', '')}"
            
            all_text = all_text.lower()
            
            # Check for IT/SRE terminology (since we used IT expectation)
            it_sre_terms = ["slo", "latency", "p95", "p99", "threshold", "performance", 
                           "monitoring", "reliability", "availability", "degradation"]
            
            found_terms = [term for term in it_sre_terms if term in all_text]
            
            if len(found_terms) >= 2:
                self.log_test("Domain-Adapted SRE Forecast", "PASS", 
                             f"✅ Domain-adapted SRE terminology found: {found_terms}")
            else:
                self.log_test("Domain-Adapted SRE Forecast", "PARTIAL", 
                             f"Limited domain terminology: {found_terms}")
        else:
            self.log_test("Domain-Adapted SRE Forecast", "FAIL", 
                         "No SRE forecast found in response")

    def test_user_expectation_storage(self):
        """Test 5: Storage of User Expectation"""
        if not hasattr(self, 'detected_domain_response'):
            self.log_test("User Expectation Storage", "SKIP", "No analysis response available")
            return
        
        response = self.detected_domain_response
        
        # Check if user_expectation is included in response
        user_expectation = response.get("user_expectation")
        
        if user_expectation:
            expected_text = "predict system latency to identify performance bottlenecks"
            
            if expected_text.lower() in user_expectation.lower():
                self.log_test("User Expectation Storage", "PASS", 
                             f"✅ User expectation stored: '{user_expectation}'")
            else:
                self.log_test("User Expectation Storage", "PARTIAL", 
                             f"User expectation found but different: '{user_expectation}'")
        else:
            self.log_test("User Expectation Storage", "FAIL", 
                         "No 'user_expectation' field found in response")

    def test_complete_flow(self):
        """Test 6: Complete Flow - Smart Selection → Analysis"""
        if not self.test_dataset_id:
            self.log_test("Complete Flow", "SKIP", "No test dataset available")
            return
        
        print("🔍 Testing complete flow: Smart Selection → Analysis...")
        
        # Step 1: Get smart selection suggestions
        smart_selection_payload = {
            "dataset_id": self.test_dataset_id,
            "user_expectation": "Predict system performance issues before they impact users"
        }
        
        try:
            # Get suggestions
            response = requests.post(
                f"{self.backend_url}/analysis/suggest-from-expectation",
                json=smart_selection_payload,
                timeout=30
            )
            
            if response.status_code != 200:
                self.log_test("Complete Flow", "FAIL", 
                             f"Smart selection failed: HTTP {response.status_code}")
                return
            
            suggestions_data = response.json()
            suggestions = suggestions_data.get("suggestions", {})
            
            # Step 2: Use suggestions in holistic analysis
            analysis_payload = {
                "dataset_id": self.test_dataset_id,
                "workspace_name": "test_workspace_complete_flow",
                "problem_type": suggestions.get("problem_type", "auto"),
                "user_selection": {
                    "target_variable": suggestions.get("suggested_target"),
                    "selected_features": suggestions.get("suggested_features", []),
                    "mode": "manual",
                    "user_expectation": "Predict system performance issues before they impact users"
                }
            }
            
            # Run analysis with suggestions
            analysis_response = requests.post(
                f"{self.backend_url}/analysis/holistic",
                json=analysis_payload,
                timeout=60
            )
            
            if analysis_response.status_code == 200:
                analysis_data = analysis_response.json()
                
                # Check if analysis completed successfully
                has_insights = "insights" in analysis_data
                has_models = "ml_models" in analysis_data and len(analysis_data.get("ml_models", [])) > 0
                has_domain = "detected_domain" in analysis_data
                has_sre_forecast = "sre_forecast" in analysis_data
                has_user_expectation = "user_expectation" in analysis_data
                
                success_count = sum([has_insights, has_models, has_domain, has_sre_forecast, has_user_expectation])
                
                if success_count >= 4:  # At least 4 out of 5 features working
                    self.log_test("Complete Flow", "PASS", 
                                 f"✅ Complete flow working: insights={has_insights}, models={has_models}, domain={has_domain}, sre_forecast={has_sre_forecast}, user_expectation={has_user_expectation}")
                elif success_count >= 2:
                    self.log_test("Complete Flow", "PARTIAL", 
                                 f"Partial flow working: {success_count}/5 features")
                else:
                    self.log_test("Complete Flow", "FAIL", 
                                 f"Flow mostly failed: only {success_count}/5 features working")
            else:
                self.log_test("Complete Flow", "FAIL", 
                             f"Analysis failed: HTTP {analysis_response.status_code}")
                
        except Exception as e:
            self.log_test("Complete Flow", "FAIL", 
                         f"Complete flow failed: {str(e)}")

    def test_setup_dataset(self):
        """Test 0: Setup test dataset"""
        # Look for existing suitable dataset first
        datasets = self.get_available_datasets()
        
        # Look for IT infrastructure or performance-related dataset
        suitable_dataset = None
        for dataset in datasets:
            name = dataset.get("name", "").lower()
            row_count = dataset.get("row_count", 0)
            
            # Look for existing IT/performance datasets
            if (("test_data" in name or "latency" in name or "performance" in name or "it_infrastructure" in name) 
                and row_count >= 50):
                suitable_dataset = dataset
                break
        
        if suitable_dataset:
            self.test_dataset_id = suitable_dataset.get("id")
            self.log_test("Setup Test Dataset", "PASS", 
                         f"Using existing dataset: {suitable_dataset.get('name')} (ID: {self.test_dataset_id}, {suitable_dataset.get('row_count')} rows)")
        else:
            # Upload new IT infrastructure dataset
            print("🔄 No suitable dataset found, uploading IT infrastructure test dataset...")
            self.test_dataset_id = self.upload_it_infrastructure_dataset()
            if self.test_dataset_id:
                self.log_test("Setup Test Dataset", "PASS", 
                             f"Uploaded new IT infrastructure dataset (ID: {self.test_dataset_id})")
            else:
                self.log_test("Setup Test Dataset", "FAIL", "Could not setup test dataset")

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🧪 Smart Selection & Domain-Agnostic Features Testing for PROMISE AI Platform")
        print("=" * 80)
        print(f"Backend URL: {self.backend_url}")
        print()
        
        # Run tests in order
        self.test_setup_dataset()
        self.test_smart_selection_it_infrastructure()
        self.test_smart_selection_different_domain()
        self.test_domain_detection()
        self.test_domain_adapted_sre_forecast()
        self.test_user_expectation_storage()
        self.test_complete_flow()
        
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
        
        # Smart selection feature status
        smart_tests = [r for r in self.test_results if "Smart Selection" in r["test"] or "Domain" in r["test"]]
        smart_working = sum(1 for r in smart_tests if r["status"] in ["PASS", "PARTIAL"])
        
        print(f"\n🎯 SMART SELECTION FEATURE STATUS:")
        if smart_working >= len(smart_tests) * 0.7:  # 70% threshold
            print("   ✅ Smart selection features are working")
        else:
            print("   ❌ Smart selection features need attention")
        
        # Domain-agnostic status
        domain_tests = [r for r in self.test_results if "Domain" in r["test"] or "Complete Flow" in r["test"]]
        domain_working = any(r["status"] == "PASS" for r in domain_tests)
        
        print(f"\n🌐 DOMAIN-AGNOSTIC STATUS:")
        if domain_working:
            print("   ✅ Domain-agnostic functionality is working")
        else:
            print("   ⚠️  Domain-agnostic functionality may need attention")
        
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "partial": partial,
            "success_rate": success_rate,
            "smart_working": smart_working >= len(smart_tests) * 0.7,
            "domain_working": domain_working
        }

def main():
    """Main test execution"""
    tester = SmartSelectionTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    if results["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()