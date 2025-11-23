#!/usr/bin/env python3
"""
Detailed Phase 3 Testing - Business Recommendations and Explainability
"""

import requests
import json
import sys
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://model-genius.preview.emergentagent.com/api"

def test_business_recommendations_detailed():
    """Test business recommendations generation in detail"""
    print("\n=== Detailed Test: Business Recommendations ===")
    
    dataset_id = "f3ee15b1-2c23-4538-b2d2-9839aea11a4e"  # application_latency_16.csv
    
    payload = {
        "dataset_id": dataset_id,
        "user_selection": {
            "target_variable": "latency_ms",
            "selected_features": ["cpu_utilization", "memory_usage_mb"],
            "mode": "manual"
        }
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/analysis/holistic",
            json=payload,
            timeout=60
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check AI insights (should work with rule-based fallback)
            ai_insights = data.get('ai_insights', [])
            print(f"AI Insights count: {len(ai_insights)}")
            
            if ai_insights:
                print("✅ AI Insights generated (rule-based fallback working)")
                for i, insight in enumerate(ai_insights[:3], 1):
                    print(f"   {i}. {insight.get('title', 'N/A')}: {insight.get('type', 'N/A')}")
            else:
                print("❌ No AI insights generated")
            
            # Check business recommendations
            business_recs = data.get('business_recommendations', [])
            print(f"Business Recommendations count: {len(business_recs)}")
            
            if business_recs:
                print("✅ Business recommendations generated")
                for i, rec in enumerate(business_recs[:3], 1):
                    print(f"   {i}. {rec.get('title', 'N/A')}: Priority {rec.get('priority', 'N/A')}")
            else:
                print("⚠️ No business recommendations - checking if fallback is working")
                
                # Check if we have models trained (needed for recommendations)
                models = data.get('models', [])
                print(f"   Models trained: {len(models)}")
                
                if models:
                    best_model = max(models, key=lambda m: m.get('r2_score', 0))
                    r2_score = best_model.get('r2_score', 0)
                    print(f"   Best model R²: {r2_score:.3f}")
                    
                    if r2_score > 0.5:
                        print("   ❌ Good model available but no recommendations generated")
                        return False
                    else:
                        print("   ℹ️ Model performance too low for meaningful recommendations")
                        return True
                else:
                    print("   ❌ No models trained - cannot generate recommendations")
                    return False
            
            # Check explainability
            explainability = data.get('explainability', {})
            print(f"Explainability available: {bool(explainability)}")
            
            if explainability:
                print("✅ Model explainability data present")
                print(f"   Model: {explainability.get('model_name', 'N/A')}")
                print(f"   Available: {explainability.get('available', False)}")
            else:
                print("ℹ️ No explainability data (may be due to model performance)")
            
            return True
        else:
            print(f"❌ Test Failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test Exception: {str(e)}")
        return False

def test_model_performance_for_explainability():
    """Test if models are performing well enough for explainability"""
    print("\n=== Test: Model Performance for Explainability ===")
    
    dataset_id = "f3ee15b1-2c23-4538-b2d2-9839aea11a4e"
    
    payload = {
        "dataset_id": dataset_id,
        "user_selection": {
            "target_variable": "latency_ms",
            "selected_features": ["cpu_utilization", "memory_usage_mb", "payload_size_kb"],
            "mode": "manual"
        }
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/analysis/holistic",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            
            print(f"Total models trained: {len(models)}")
            
            if models:
                # Analyze model performance
                for i, model in enumerate(models, 1):
                    model_name = model.get('model_name', f'Model {i}')
                    r2_score = model.get('r2_score', 0)
                    rmse = model.get('rmse', 0)
                    
                    print(f"   {i}. {model_name}: R²={r2_score:.3f}, RMSE={rmse:.3f}")
                
                # Find best model
                best_model = max(models, key=lambda m: m.get('r2_score', 0))
                best_r2 = best_model.get('r2_score', 0)
                
                print(f"\nBest model R²: {best_r2:.3f}")
                
                if best_r2 > 0.5:
                    print("✅ Model performance sufficient for explainability (R² > 0.5)")
                    
                    # Check if explainability was generated
                    explainability = data.get('explainability', {})
                    if explainability:
                        print("✅ Explainability data generated for good model")
                        return True
                    else:
                        print("❌ Good model but no explainability data generated")
                        return False
                else:
                    print(f"ℹ️ Model performance too low for explainability (R² = {best_r2:.3f} ≤ 0.5)")
                    return True  # This is expected behavior
            else:
                print("❌ No models trained")
                return False
        else:
            print(f"❌ Request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_phase3_with_different_datasets():
    """Test Phase 3 features with different dataset sizes"""
    print("\n=== Test: Phase 3 with Different Dataset Scenarios ===")
    
    # Test with the available dataset
    dataset_id = "f3ee15b1-2c23-4538-b2d2-9839aea11a4e"
    
    # Test auto mode (no user selection)
    payload_auto = {
        "dataset_id": dataset_id
    }
    
    try:
        print("\n--- Testing Auto Mode ---")
        response = requests.post(
            f"{BACKEND_URL}/analysis/holistic",
            json=payload_auto,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            
            ai_insights = data.get('ai_insights', [])
            business_recs = data.get('business_recommendations', [])
            explainability = data.get('explainability', {})
            phase3_enabled = data.get('phase_3_enabled', False)
            
            print(f"   Phase 3 enabled: {phase3_enabled}")
            print(f"   AI insights: {len(ai_insights)}")
            print(f"   Business recommendations: {len(business_recs)}")
            print(f"   Explainability: {bool(explainability)}")
            
            if phase3_enabled and len(ai_insights) > 0:
                print("✅ Phase 3 working in auto mode")
                return True
            else:
                print("❌ Phase 3 not working properly in auto mode")
                return False
        else:
            print(f"❌ Auto mode test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Auto mode test exception: {str(e)}")
        return False

def main():
    """Run detailed Phase 3 tests"""
    print("🔬 Starting DETAILED PHASE 3 TESTING")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now().isoformat()}")
    
    results = {
        'business_recommendations': False,
        'model_performance': False,
        'different_scenarios': False
    }
    
    results['business_recommendations'] = test_business_recommendations_detailed()
    results['model_performance'] = test_model_performance_for_explainability()
    results['different_scenarios'] = test_phase3_with_different_datasets()
    
    # Summary
    print("\n" + "="*60)
    print("📊 DETAILED PHASE 3 TEST SUMMARY")
    print("="*60)
    
    passed_tests = sum(1 for result in results.values() if result)
    total_tests = len(results)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)