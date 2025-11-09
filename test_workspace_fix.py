#!/usr/bin/env python3
"""
Test script to verify the workspace loading fix
This script will test the training metadata association after the fix
"""

import requests
import json
import time
from datetime import datetime

# Backend URL
BACKEND_URL = "https://data-prophet-4.preview.emergentagent.com/api"

def test_training_with_workspace():
    """Test training with explicit workspace name"""
    print("🧪 Testing Training with Explicit Workspace Name")
    print("="*60)
    
    try:
        # Get datasets first
        datasets_response = requests.get(f"{BACKEND_URL}/datasets", timeout=10)
        if datasets_response.status_code != 200:
            print("❌ Failed to get datasets")
            return False
        
        datasets = datasets_response.json().get("datasets", [])
        if not datasets:
            print("❌ No datasets available")
            return False
        
        # Use the first dataset
        dataset = datasets[0]
        dataset_id = dataset.get("id")
        dataset_name = dataset.get("name", "Unknown")
        
        print(f"📊 Using dataset: {dataset_name} (ID: {dataset_id[:8]}...)")
        
        # Test training with explicit workspace name
        test_workspace_name = "test_workspace_fix"
        
        payload = {
            "dataset_id": dataset_id,
            "workspace_name": test_workspace_name,  # Explicit workspace name
            "problem_type": "auto",
            "selected_models": ["linear_regression"]  # Just one model for quick test
        }
        
        print(f"🚀 Starting training with workspace: '{test_workspace_name}'")
        print("   This should create training metadata with the correct workspace name...")
        
        start_time = time.time()
        response = requests.post(f"{BACKEND_URL}/analysis/holistic", json=payload, timeout=120)
        end_time = time.time()
        
        print(f"⏱️  Training completed in {end_time - start_time:.1f} seconds")
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            models_trained = len(data.get("ml_models", []))
            print(f"✅ Training successful - {models_trained} models trained")
            
            # Wait a moment for database to update
            time.sleep(2)
            
            # Check if training metadata was saved with correct workspace name
            print(f"\n🔍 Checking training metadata for workspace '{test_workspace_name}'...")
            
            metadata_response = requests.get(f"{BACKEND_URL}/training/metadata/by-workspace", timeout=10)
            if metadata_response.status_code == 200:
                metadata = metadata_response.json()
                datasets_with_metadata = metadata.get("datasets", [])
                
                found_workspace = False
                for ds in datasets_with_metadata:
                    if ds.get("dataset_id") == dataset_id:
                        workspaces = ds.get("workspaces", [])
                        for ws in workspaces:
                            if ws.get("workspace_name") == test_workspace_name:
                                model_count = ws.get("total_models", 0)
                                print(f"✅ Found workspace '{test_workspace_name}' with {model_count} models!")
                                found_workspace = True
                                break
                        break
                
                if found_workspace:
                    print("🎉 SUCCESS: Training metadata correctly associated with workspace!")
                    return True
                else:
                    print(f"❌ FAILED: Workspace '{test_workspace_name}' not found in training metadata")
                    return False
            else:
                print("❌ Failed to fetch training metadata")
                return False
        else:
            print(f"❌ Training failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test exception: {str(e)}")
        return False

def main():
    """Run workspace fix verification test"""
    print("🚀 WORKSPACE FIX VERIFICATION TEST")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now().isoformat()}")
    print("="*60)
    
    success = test_training_with_workspace()
    
    print("\n" + "="*60)
    if success:
        print("📋 STATUS: ✅ WORKSPACE FIX VERIFIED")
        print("   Training metadata is correctly associated with workspace names")
    else:
        print("📋 STATUS: ❌ WORKSPACE FIX NEEDS INVESTIGATION")
        print("   Training metadata association may still have issues")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)