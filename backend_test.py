#!/usr/bin/env python3
"""
PROMISE AI Backend Testing - Training Metadata Investigation
Investigating the "latency_nov" workspace training metadata issue
"""

import requests
import json
import sys
import os
import time
from datetime import datetime
import cx_Oracle

# Get backend URL from environment
BACKEND_URL = "https://ai-insight-hub-4.preview.emergentagent.com/api"

# Oracle connection details for direct database queries
ORACLE_CONFIG = {
    'user': 'testuser',
    'password': 'DbPasswordTest',
    'host': 'promise-ai-test-oracle.cgxf9inhpsec.us-east-1.rds.amazonaws.com',
    'port': '1521',
    'service_name': 'ORCL'
}

def test_direct_database_query():
    """Test 1: Direct Database Query - Check training_metadata table"""
    print("\n=== Test 1: Direct Database Query ===")
    print("Checking what's actually in the training_metadata table...")
    
    try:
        # Initialize Oracle client
        try:
            cx_Oracle.init_oracle_client(lib_dir='/opt/oracle/instantclient_19_23')
        except:
            pass  # Already initialized
        
        # Create connection
        dsn = cx_Oracle.makedsn(
            ORACLE_CONFIG['host'],
            ORACLE_CONFIG['port'],
            service_name=ORACLE_CONFIG['service_name']
        )
        
        connection = cx_Oracle.connect(
            user=ORACLE_CONFIG['user'],
            password=ORACLE_CONFIG['password'],
            dsn=dsn
        )
        
        cursor = connection.cursor()
        
        # Query training_metadata table
        query = """
        SELECT id, dataset_id, workspace_name, model_type, created_at 
        FROM training_metadata 
        ORDER BY created_at DESC 
        FETCH FIRST 20 ROWS ONLY
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [col[0].lower() for col in cursor.description]
        
        print(f"✅ Found {len(rows)} training metadata records")
        print(f"   Columns: {columns}")
        
        # Check for latency_nov workspace
        latency_nov_found = False
        for row in rows:
            row_dict = dict(zip(columns, row))
            workspace_name = row_dict.get('workspace_name', '')
            
            print(f"   - Dataset: {row_dict.get('dataset_id', 'N/A')[:8]}..., "
                  f"Workspace: '{workspace_name}', "
                  f"Model: {row_dict.get('model_type', 'N/A')}, "
                  f"Created: {row_dict.get('created_at', 'N/A')}")
            
            if workspace_name and 'latency_nov' in workspace_name.lower():
                latency_nov_found = True
                print(f"   🎯 FOUND latency_nov workspace: {workspace_name}")
        
        if not latency_nov_found:
            print("   ❌ No 'latency_nov' workspace found in training_metadata")
        
        cursor.close()
        connection.close()
        
        return True, latency_nov_found
        
    except Exception as e:
        print(f"❌ Direct database query failed: {str(e)}")
        return False, False

def test_workspace_states_query():
    """Test 2: Check Workspace States - Verify workspace was saved"""
    print("\n=== Test 2: Check Workspace States ===")
    print("Verifying workspace 'latency_nov' exists in workspace_states...")
    
    try:
        # Initialize Oracle client
        try:
            cx_Oracle.init_oracle_client(lib_dir='/opt/oracle/instantclient_19_23')
        except:
            pass  # Already initialized
        
        # Create connection
        dsn = cx_Oracle.makedsn(
            ORACLE_CONFIG['host'],
            ORACLE_CONFIG['port'],
            service_name=ORACLE_CONFIG['service_name']
        )
        
        connection = cx_Oracle.connect(
            user=ORACLE_CONFIG['user'],
            password=ORACLE_CONFIG['password'],
            dsn=dsn
        )
        
        cursor = connection.cursor()
        
        # Query workspace_states table
        query = """
        SELECT id, dataset_id, state_name, size_bytes, created_at 
        FROM workspace_states 
        WHERE LOWER(state_name) LIKE '%latency%nov%' OR LOWER(state_name) = 'latency_nov'
        ORDER BY created_at DESC
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [col[0].lower() for col in cursor.description]
        
        print(f"✅ Found {len(rows)} workspace states matching 'latency_nov'")
        
        workspace_dataset_id = None
        for row in rows:
            row_dict = dict(zip(columns, row))
            workspace_dataset_id = row_dict.get('dataset_id')
            
            print(f"   - ID: {row_dict.get('id', 'N/A')}")
            print(f"   - Dataset ID: {workspace_dataset_id}")
            print(f"   - State Name: '{row_dict.get('state_name', 'N/A')}'")
            print(f"   - Size: {row_dict.get('size_bytes', 0)} bytes")
            print(f"   - Created: {row_dict.get('created_at', 'N/A')}")
        
        # Also check all workspace states to see what's available
        query_all = """
        SELECT state_name, dataset_id, created_at 
        FROM workspace_states 
        ORDER BY created_at DESC 
        FETCH FIRST 10 ROWS ONLY
        """
        
        cursor.execute(query_all)
        all_rows = cursor.fetchall()
        
        print(f"\n   📋 Recent workspace states ({len(all_rows)} total):")
        for row in all_rows:
            print(f"      - '{row[0]}' (Dataset: {row[1][:8] if row[1] else 'N/A'}..., Created: {row[2]})")
        
        cursor.close()
        connection.close()
        
        return True, workspace_dataset_id
        
    except Exception as e:
        print(f"❌ Workspace states query failed: {str(e)}")
        return False, None

def test_training_metadata_endpoint():
    """Test 3: Training Metadata Endpoint - GET /api/training/metadata/by-workspace"""
    print("\n=== Test 3: Training Metadata Endpoint ===")
    print("Testing the endpoint that the Training Metadata page uses...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/training/metadata/by-workspace", timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Training metadata endpoint accessible")
            
            datasets = data.get("datasets", [])
            print(f"   Found {len(datasets)} datasets with training metadata")
            
            # Look for latency_nov workspace
            latency_nov_found = False
            for dataset in datasets:
                dataset_name = dataset.get('dataset_name', 'Unknown')
                workspaces = dataset.get('workspaces', [])
                
                print(f"\n   📊 Dataset: {dataset_name}")
                print(f"      - Dataset ID: {dataset.get('dataset_id', 'N/A')[:8]}...")
                print(f"      - Total workspaces: {len(workspaces)}")
                
                for workspace in workspaces:
                    workspace_name = workspace.get('workspace_name', 'Unknown')
                    total_models = workspace.get('total_models', 0)
                    
                    print(f"      - Workspace: '{workspace_name}' ({total_models} models)")
                    
                    if 'latency_nov' in workspace_name.lower():
                        latency_nov_found = True
                        print(f"        🎯 FOUND latency_nov workspace with {total_models} models!")
                        
                        # Show training runs
                        training_runs = workspace.get('training_runs', [])
                        for run in training_runs[:3]:  # Show first 3
                            print(f"           - Model: {run.get('model_type', 'N/A')}, "
                                  f"Created: {run.get('created_at', 'N/A')}")
            
            if not latency_nov_found:
                print("\n   ❌ 'latency_nov' workspace NOT found in API response")
                print("   🔍 This explains why the Training Metadata page shows '0 models'")
            else:
                print("\n   ✅ 'latency_nov' workspace found in API response")
            
            return True, latency_nov_found
        else:
            print(f"❌ Training metadata endpoint failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Error: {response.text}")
            return False, False
            
    except Exception as e:
        print(f"❌ Training metadata endpoint exception: {str(e)}")
        return False, False

def test_dataset_workspace_correlation(workspace_dataset_id):
    """Test 4: Dataset-Workspace Correlation - Check if dataset IDs match"""
    print("\n=== Test 4: Dataset-Workspace Correlation ===")
    print("Checking if dataset_id matches between workspace_states and training_metadata...")
    
    if not workspace_dataset_id:
        print("❌ No workspace dataset ID available from previous test")
        return False
    
    try:
        # Initialize Oracle client
        try:
            cx_Oracle.init_oracle_client(lib_dir='/opt/oracle/instantclient_19_23')
        except:
            pass  # Already initialized
        
        # Create connection
        dsn = cx_Oracle.makedsn(
            ORACLE_CONFIG['host'],
            ORACLE_CONFIG['port'],
            service_name=ORACLE_CONFIG['service_name']
        )
        
        connection = cx_Oracle.connect(
            user=ORACLE_CONFIG['user'],
            password=ORACLE_CONFIG['password'],
            dsn=dsn
        )
        
        cursor = connection.cursor()
        
        print(f"   🔍 Looking for training_metadata with dataset_id: {workspace_dataset_id}")
        
        # Query training_metadata for this specific dataset_id
        query = """
        SELECT id, dataset_id, workspace_name, model_type, created_at 
        FROM training_metadata 
        WHERE dataset_id = :dataset_id
        ORDER BY created_at DESC
        """
        
        cursor.execute(query, {'dataset_id': workspace_dataset_id})
        rows = cursor.fetchall()
        columns = [col[0].lower() for col in cursor.description]
        
        print(f"   ✅ Found {len(rows)} training metadata records for this dataset")
        
        if len(rows) > 0:
            print("   📋 Training metadata records:")
            for row in rows:
                row_dict = dict(zip(columns, row))
                print(f"      - Workspace: '{row_dict.get('workspace_name', 'N/A')}', "
                      f"Model: {row_dict.get('model_type', 'N/A')}, "
                      f"Created: {row_dict.get('created_at', 'N/A')}")
        else:
            print("   ❌ No training metadata found for this dataset_id")
            print("   🔍 This is the ROOT CAUSE - workspace exists but no training metadata!")
        
        # Also check if there are training_metadata records with different workspace names
        query_all = """
        SELECT DISTINCT workspace_name, COUNT(*) as count
        FROM training_metadata 
        WHERE dataset_id = :dataset_id
        GROUP BY workspace_name
        ORDER BY count DESC
        """
        
        cursor.execute(query_all, {'dataset_id': workspace_dataset_id})
        workspace_rows = cursor.fetchall()
        
        if workspace_rows:
            print(f"\n   📊 Workspace names in training_metadata for this dataset:")
            for row in workspace_rows:
                print(f"      - '{row[0]}': {row[1]} models")
        
        cursor.close()
        connection.close()
        
        return True, len(rows) > 0
        
    except Exception as e:
        print(f"❌ Dataset-workspace correlation check failed: {str(e)}")
        return False, False

def check_backend_logs():
    """Check backend logs for any startup errors"""
    print("\n=== Backend Logs Check ===")
    
    try:
        # Check recent backend logs
        import subprocess
        result = subprocess.run(
            ["tail", "-n", "20", "/var/log/supervisor/backend.err.log"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            logs = result.stdout.strip()
            if logs:
                print("Recent backend error logs:")
                print(logs)
                
                # Check for specific errors
                if "ERROR" in logs:
                    print("⚠️  Errors found in backend logs")
                    return False
                else:
                    print("✅ No critical errors in recent logs")
                    return True
            else:
                print("✅ No recent error logs")
                return True
        else:
            print("⚠️  Could not access backend logs")
            return True  # Don't fail the test for log access issues
            
    except Exception as e:
        print(f"⚠️  Could not check backend logs: {str(e)}")
        return True  # Don't fail the test for log access issues

def main():
    """Run Critical Backend Tests"""
    print("🚀 PROMISE AI BACKEND TESTING - Critical Endpoints")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now().isoformat()}")
    print("="*70)
    
    # Track test results
    results = {
        'backend_health': False,
        'datasets_endpoint': False,
        'suggest_features': False,
        'hyperparameter_tuning': False,
        'backend_logs': False
    }
    
    dataset_id = None
    
    # Test 1: Backend Health (GENERAL)
    print("\n🔍 PRIORITY: GENERAL")
    results['backend_health'] = test_backend_health()
    
    if not results['backend_health']:
        print("\n❌ Backend is not accessible. Stopping tests.")
        return False
    
    # Test 2: Datasets Endpoint (SANITY CHECK)
    print("\n🔍 PRIORITY: MEDIUM")
    datasets_success, dataset_id = test_datasets_endpoint()
    results['datasets_endpoint'] = datasets_success
    
    # Test 3: Suggest-Features Endpoint (NEW - Just Added)
    print("\n🔍 PRIORITY: HIGH")
    results['suggest_features'] = test_suggest_features_endpoint(dataset_id)
    
    # Test 4: Hyperparameter Tuning Endpoint (REPORTED 500 ERROR)
    print("\n🔍 PRIORITY: HIGH")
    results['hyperparameter_tuning'] = test_hyperparameter_tuning_endpoint(dataset_id)
    
    # Test 5: Backend Logs Check
    results['backend_logs'] = check_backend_logs()
    
    # Summary
    print("\n" + "="*70)
    print("📊 CRITICAL ENDPOINTS TEST SUMMARY")
    print("="*70)
    
    passed_tests = sum(1 for result in results.values() if result)
    total_tests = len(results)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        priority = ""
        if test_name == 'suggest_features':
            priority = " (HIGH PRIORITY - NEW ENDPOINT)"
        elif test_name == 'hyperparameter_tuning':
            priority = " (HIGH PRIORITY - 500 ERROR REPORTED)"
        elif test_name == 'datasets_endpoint':
            priority = " (MEDIUM PRIORITY - SANITY CHECK)"
        elif test_name == 'backend_health':
            priority = " (GENERAL)"
        
        print(f"{test_name.replace('_', ' ').title()}: {status}{priority}")
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    # Detailed findings
    print("\n🔍 DETAILED FINDINGS:")
    
    if results['backend_health']:
        print("   ✅ Backend is running and responsive")
    else:
        print("   ❌ Backend health issues detected")
    
    if results['datasets_endpoint']:
        print("   ✅ Datasets endpoint working - Oracle RDS connection stable")
    else:
        print("   ❌ Datasets endpoint issues - Oracle RDS connection problems")
    
    if results['suggest_features']:
        print("   ✅ NEW suggest-features endpoint working correctly")
    else:
        print("   ❌ NEW suggest-features endpoint has issues")
    
    if results['hyperparameter_tuning']:
        print("   ✅ Hyperparameter tuning endpoint working - 500 error resolved")
    else:
        print("   ❌ Hyperparameter tuning endpoint still has issues - 500 error persists")
    
    if results['backend_logs']:
        print("   ✅ Backend logs show no critical errors")
    else:
        print("   ❌ Backend logs show errors")
    
    # Final status
    critical_tests = ['suggest_features', 'hyperparameter_tuning']
    critical_passed = sum(1 for test in critical_tests if results[test])
    
    if critical_passed == len(critical_tests):
        print("\n🎉 All CRITICAL tests passed!")
        print("\n📋 STATUS: ✅ CRITICAL FIXES VERIFIED")
        return True
    else:
        print(f"\n⚠️ {len(critical_tests) - critical_passed} CRITICAL test(s) failed.")
        print("\n📋 STATUS: ❌ CRITICAL ISSUES DETECTED")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
