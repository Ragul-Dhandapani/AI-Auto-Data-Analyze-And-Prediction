#!/usr/bin/env python3
"""
Training Metadata Investigation - Latency_2_Oracle Workspace
Investigating why the saved workspace "Latency_2_Oracle" is not appearing in Training Metadata page
"""

import requests
import json
import sys
import os
import time
from datetime import datetime
import pymongo
from pymongo import MongoClient

# Get backend URL from environment
BACKEND_URL = "https://predict-analyze.preview.emergentagent.com/api"

def test_api_health():
    """Test if the API is running"""
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=10)
        print(f"✅ API Health Check: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Version: {data.get('version', 'Unknown')}")
            print(f"   Status: {data.get('status', 'Unknown')}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ API Health Check Failed: {str(e)}")
        return False

def test_training_metadata_api():
    """Test 1: Check Training Metadata API"""
    print("\n=== Test 1: Training Metadata API ===")
    
    try:
        response = requests.get(f"{BACKEND_URL}/training/metadata", timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Training metadata endpoint accessible")
            
            # Verify response structure
            if "metadata" not in data:
                print("❌ Response missing 'metadata' key")
                return False, None
            
            metadata = data.get("metadata", [])
            print(f"   Found {len(metadata)} datasets with training metadata")
            
            # Look for Latency_2_Oracle workspace
            latency_oracle_found = False
            for dataset_meta in metadata:
                dataset_name = dataset_meta.get("dataset_name", "")
                workspaces = dataset_meta.get("workspaces", [])
                
                print(f"   Dataset: {dataset_name} - {len(workspaces)} workspaces")
                
                for workspace in workspaces:
                    workspace_name = workspace.get("workspace_name", "")
                    print(f"     - Workspace: {workspace_name}")
                    
                    if "Latency" in workspace_name and "Oracle" in workspace_name:
                        latency_oracle_found = True
                        print(f"     ✅ FOUND: {workspace_name}")
                        print(f"        Saved at: {workspace.get('saved_at')}")
                        print(f"        Workspace ID: {workspace.get('workspace_id')}")
            
            if latency_oracle_found:
                print("✅ Latency_2_Oracle workspace found in training metadata")
            else:
                print("❌ Latency_2_Oracle workspace NOT found in training metadata")
            
            return True, metadata
        else:
            print(f"❌ Training metadata endpoint failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Error: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Training metadata exception: {str(e)}")
        return False, None

def test_datasets_api():
    """Test 2: Check Datasets API"""
    print("\n=== Test 2: Datasets API ===")
    
    try:
        response = requests.get(f"{BACKEND_URL}/datasets", timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Datasets endpoint accessible")
            
            datasets = data.get("datasets", [])
            print(f"   Found {len(datasets)} datasets")
            
            # Look for datasets with training_count > 0
            trained_datasets = []
            for dataset in datasets:
                dataset_name = dataset.get("name", "")
                training_count = dataset.get("training_count", 0)
                dataset_id = dataset.get("id", "")
                
                print(f"   Dataset: {dataset_name} (ID: {dataset_id}) - Training count: {training_count}")
                
                if training_count > 0:
                    trained_datasets.append({
                        "name": dataset_name,
                        "id": dataset_id,
                        "training_count": training_count
                    })
            
            print(f"   Datasets with training > 0: {len(trained_datasets)}")
            return True, datasets
        else:
            print(f"❌ Datasets endpoint failed: {response.status_code}")
            return False, None
            
    except Exception as e:
        print(f"❌ Datasets exception: {str(e)}")
        return False, None

def check_mongodb_directly():
    """Test 3: Check MongoDB directly for saved_states"""
    print("\n=== Test 3: MongoDB Direct Check ===")
    
    try:
        # Connect to MongoDB directly
        client = MongoClient("mongodb://localhost:27017")
        db = client["test_database"]
        
        # Check saved_states collection
        saved_states = db.saved_states
        
        # Count total saved states
        total_states = saved_states.count_documents({})
        print(f"   Total saved states in MongoDB: {total_states}")
        
        # Look for Latency workspaces
        latency_query = {"state_name": {"$regex": "Latency", "$options": "i"}}
        latency_states = list(saved_states.find(latency_query))
        
        print(f"   Workspaces with 'Latency' in name: {len(latency_states)}")
        
        # Look specifically for Latency_2_Oracle
        oracle_query = {"state_name": {"$regex": "Latency.*Oracle", "$options": "i"}}
        oracle_states = list(saved_states.find(oracle_query))
        
        print(f"   Workspaces with 'Latency' and 'Oracle': {len(oracle_states)}")
        
        # Show all saved states for debugging
        all_states = list(saved_states.find({}, {"state_name": 1, "dataset_id": 1, "created_at": 1, "_id": 0}).limit(20))
        print(f"   Recent saved states (showing up to 20):")
        
        for state in all_states:
            state_name = state.get("state_name", "Unnamed")
            dataset_id = state.get("dataset_id", "Unknown")
            created_at = state.get("created_at", "Unknown")
            print(f"     - {state_name} (Dataset: {dataset_id}, Created: {created_at})")
        
        # Check if Latency_2_Oracle exists
        latency_oracle_exact = saved_states.find_one({"state_name": "Latency_2_Oracle"})
        if latency_oracle_exact:
            print("✅ FOUND: Latency_2_Oracle workspace exists in MongoDB")
            print(f"   Dataset ID: {latency_oracle_exact.get('dataset_id')}")
            print(f"   Created at: {latency_oracle_exact.get('created_at')}")
            print(f"   Workspace ID: {latency_oracle_exact.get('id')}")
            return True, latency_oracle_exact
        else:
            print("❌ Latency_2_Oracle workspace NOT found in MongoDB")
            return False, None
        
    except Exception as e:
        print(f"❌ MongoDB direct check exception: {str(e)}")
        return False, None

def check_datasets_collection():
    """Test 4: Check datasets collection in MongoDB"""
    print("\n=== Test 4: MongoDB Datasets Collection ===")
    
    try:
        client = MongoClient("mongodb://localhost:27017")
        db = client["test_database"]
        
        datasets = db.datasets
        total_datasets = datasets.count_documents({})
        print(f"   Total datasets in MongoDB: {total_datasets}")
        
        # Get all datasets
        all_datasets = list(datasets.find({}, {"name": 1, "id": 1, "training_count": 1, "_id": 0}))
        
        print("   Datasets in MongoDB:")
        for dataset in all_datasets:
            name = dataset.get("name", "Unnamed")
            dataset_id = dataset.get("id", "Unknown")
            training_count = dataset.get("training_count", 0)
            print(f"     - {name} (ID: {dataset_id}, Training count: {training_count})")
        
        return True, all_datasets
        
    except Exception as e:
        print(f"❌ MongoDB datasets check exception: {str(e)}")
        return False, None

def check_backend_logs():
    """Test 5: Check backend logs for training metadata errors"""
    print("\n=== Test 5: Backend Logs Check ===")
    
    try:
        # Check supervisor backend logs
        import subprocess
        
        # Get recent backend logs
        result = subprocess.run(
            ["tail", "-n", "50", "/var/log/supervisor/backend.err.log"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            logs = result.stdout
            print("   Recent backend error logs:")
            
            # Look for training metadata related errors
            lines = logs.split('\n')
            training_errors = []
            
            for line in lines:
                if any(keyword in line.lower() for keyword in ['training', 'metadata', 'saved_states', 'workspace']):
                    training_errors.append(line)
            
            if training_errors:
                print("   Training/metadata related log entries:")
                for error in training_errors[-10:]:  # Show last 10
                    print(f"     {error}")
            else:
                print("   No training/metadata related errors found in recent logs")
            
            return True, training_errors
        else:
            print(f"   Could not read backend logs: {result.stderr}")
            return False, None
            
    except Exception as e:
        print(f"❌ Backend logs check exception: {str(e)}")
        return False, None

def debug_training_metadata_logic():
    """Test 6: Debug the training metadata logic"""
    print("\n=== Test 6: Debug Training Metadata Logic ===")
    
    try:
        client = MongoClient("mongodb://localhost:27017")
        db = client["test_database"]
        
        # Get all datasets and their saved states
        datasets = list(db.datasets.find({}, {"_id": 0}))
        saved_states = list(db.saved_states.find({}, {"_id": 0}))
        
        print(f"   Processing {len(datasets)} datasets and {len(saved_states)} saved states")
        
        # Simulate the training metadata logic
        metadata = []
        
        for dataset in datasets:
            dataset_id = dataset.get("id")
            dataset_name = dataset.get("name")
            
            # Get workspaces for this dataset
            dataset_states = [s for s in saved_states if s.get("dataset_id") == dataset_id]
            
            print(f"   Dataset '{dataset_name}' (ID: {dataset_id}): {len(dataset_states)} workspaces")
            
            for state in dataset_states:
                workspace_name = state.get("state_name", "Unnamed")
                created_at = state.get("created_at", "Unknown")
                print(f"     - Workspace: {workspace_name} (Created: {created_at})")
            
            if dataset_states:
                # Calculate training metadata
                training_count = len(dataset_states)
                
                # Get last trained from most recent workspace
                sorted_by_date = sorted(dataset_states, key=lambda x: x.get("created_at", ""), reverse=True)
                last_trained = sorted_by_date[0].get("created_at") if sorted_by_date else None
                
                metadata.append({
                    "dataset_id": dataset_id,
                    "dataset_name": dataset_name,
                    "training_count": training_count,
                    "last_trained": last_trained,
                    "workspaces": [
                        {
                            "workspace_name": state.get("state_name"),
                            "saved_at": state.get("created_at"),
                            "workspace_id": state.get("id")
                        }
                        for state in sorted_by_date
                    ]
                })
        
        print(f"\n   Generated metadata for {len(metadata)} datasets")
        
        # Look for Latency_2_Oracle in generated metadata
        latency_oracle_found = False
        for dataset_meta in metadata:
            for workspace in dataset_meta.get("workspaces", []):
                workspace_name = workspace.get("workspace_name", "")
                if "Latency_2_Oracle" in workspace_name:
                    latency_oracle_found = True
                    print(f"   ✅ Latency_2_Oracle found in generated metadata")
                    print(f"      Dataset: {dataset_meta.get('dataset_name')}")
                    print(f"      Saved at: {workspace.get('saved_at')}")
                    break
        
        if not latency_oracle_found:
            print("   ❌ Latency_2_Oracle NOT found in generated metadata")
        
        return True, metadata
        
    except Exception as e:
        print(f"❌ Debug training metadata logic exception: {str(e)}")
        return False, None

def main():
    """Run Training Metadata Investigation"""
    print("🔍 TRAINING METADATA INVESTIGATION - Latency_2_Oracle Workspace")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Investigation Time: {datetime.now().isoformat()}")
    print("="*80)
    
    # Track test results
    results = {
        'api_health': False,
        'training_metadata_api': False,
        'datasets_api': False,
        'mongodb_direct_check': False,
        'datasets_collection': False,
        'backend_logs': False,
        'debug_logic': False
    }
    
    findings = {}
    
    # Test 0: API Health Check
    results['api_health'] = test_api_health()
    
    if not results['api_health']:
        print("\n❌ API is not accessible. Stopping investigation.")
        return False
    
    # Test 1: Training Metadata API
    api_success, metadata = test_training_metadata_api()
    results['training_metadata_api'] = api_success
    findings['metadata'] = metadata
    
    # Test 2: Datasets API
    datasets_success, datasets = test_datasets_api()
    results['datasets_api'] = datasets_success
    findings['datasets'] = datasets
    
    # Test 3: MongoDB Direct Check
    mongo_success, latency_oracle_workspace = check_mongodb_directly()
    results['mongodb_direct_check'] = mongo_success
    findings['latency_oracle_workspace'] = latency_oracle_workspace
    
    # Test 4: Datasets Collection
    datasets_mongo_success, datasets_mongo = check_datasets_collection()
    results['datasets_collection'] = datasets_mongo_success
    findings['datasets_mongo'] = datasets_mongo
    
    # Test 5: Backend Logs
    logs_success, training_errors = check_backend_logs()
    results['backend_logs'] = logs_success
    findings['training_errors'] = training_errors
    
    # Test 6: Debug Logic
    debug_success, debug_metadata = debug_training_metadata_logic()
    results['debug_logic'] = debug_success
    findings['debug_metadata'] = debug_metadata
    
    # Summary
    print("\n" + "="*80)
    print("📊 INVESTIGATION SUMMARY")
    print("="*80)
    
    passed_tests = sum(1 for result in results.values() if result)
    total_tests = len(results)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests completed successfully")
    
    # Key Findings
    print("\n🔍 KEY FINDINGS:")
    
    # 1. Number of datasets
    datasets_count = len(findings.get('datasets', [])) if findings.get('datasets') else 0
    print(f"   📊 Total datasets found: {datasets_count}")
    
    # 2. Number of saved workspaces
    if findings.get('latency_oracle_workspace'):
        print(f"   ✅ Latency_2_Oracle workspace EXISTS in MongoDB")
        workspace = findings['latency_oracle_workspace']
        print(f"      Dataset ID: {workspace.get('dataset_id')}")
        print(f"      Created at: {workspace.get('created_at')}")
    else:
        print(f"   ❌ Latency_2_Oracle workspace NOT found in MongoDB")
    
    # 3. Training metadata response
    metadata_count = len(findings.get('metadata', [])) if findings.get('metadata') else 0
    print(f"   📊 Training metadata returned {metadata_count} datasets")
    
    # 4. Whether Latency_2_Oracle appears in API
    latency_in_api = False
    if findings.get('metadata'):
        for dataset_meta in findings['metadata']:
            for workspace in dataset_meta.get('workspaces', []):
                if 'Latency_2_Oracle' in workspace.get('workspace_name', ''):
                    latency_in_api = True
                    break
    
    if latency_in_api:
        print(f"   ✅ Latency_2_Oracle appears in training metadata API")
    else:
        print(f"   ❌ Latency_2_Oracle does NOT appear in training metadata API")
    
    # 5. Root cause analysis
    print(f"\n🔧 ROOT CAUSE ANALYSIS:")
    
    if findings.get('latency_oracle_workspace') and not latency_in_api:
        print(f"   🚨 ISSUE IDENTIFIED: Workspace exists in MongoDB but not in API response")
        print(f"   📋 Possible causes:")
        print(f"      - Dataset-workspace association issue")
        print(f"      - Date parsing problems in training metadata logic")
        print(f"      - Database query filtering issue")
        
        workspace = findings['latency_oracle_workspace']
        dataset_id = workspace.get('dataset_id')
        
        # Check if dataset exists
        dataset_exists = False
        if findings.get('datasets'):
            for dataset in findings['datasets']:
                if dataset.get('id') == dataset_id:
                    dataset_exists = True
                    print(f"      ✅ Associated dataset exists: {dataset.get('name')}")
                    break
        
        if not dataset_exists:
            print(f"      ❌ Associated dataset (ID: {dataset_id}) NOT found")
            print(f"      🔧 SOLUTION: Dataset may have been deleted or ID mismatch")
    
    elif not findings.get('latency_oracle_workspace'):
        print(f"   🚨 ISSUE: Workspace was never saved or was deleted")
        print(f"   🔧 SOLUTION: User needs to re-run analysis and save workspace")
    
    elif latency_in_api:
        print(f"   ✅ NO ISSUE: Workspace exists and appears in training metadata")
    
    # 6. Backend logs analysis
    if findings.get('training_errors'):
        print(f"   📋 Backend logs show {len(findings['training_errors'])} training-related entries")
    else:
        print(f"   📋 No training-related errors in backend logs")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)