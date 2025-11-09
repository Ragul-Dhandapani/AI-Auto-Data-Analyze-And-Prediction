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

def test_root_cause_analysis():
    """Test 5: Root Cause Analysis - Identify the exact issue"""
    print("\n=== Test 5: Root Cause Analysis ===")
    print("Performing comprehensive analysis to identify the root cause...")
    
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
        
        print("\n   🔍 Analysis 1: Check workspace_name patterns in training_metadata")
        query1 = """
        SELECT DISTINCT workspace_name, COUNT(*) as count
        FROM training_metadata 
        GROUP BY workspace_name
        ORDER BY count DESC
        """
        
        cursor.execute(query1)
        workspace_patterns = cursor.fetchall()
        
        print(f"   Found {len(workspace_patterns)} unique workspace names:")
        for pattern in workspace_patterns:
            workspace_name = pattern[0] or 'NULL'
            count = pattern[1]
            print(f"      - '{workspace_name}': {count} models")
            
            if workspace_name and 'latency' in workspace_name.lower():
                print(f"        🎯 LATENCY WORKSPACE FOUND: '{workspace_name}'")
        
        print("\n   🔍 Analysis 2: Check dataset_id patterns")
        query2 = """
        SELECT tm.dataset_id, d.name as dataset_name, COUNT(tm.id) as training_count
        FROM training_metadata tm
        LEFT JOIN datasets d ON tm.dataset_id = d.id
        GROUP BY tm.dataset_id, d.name
        ORDER BY training_count DESC
        """
        
        cursor.execute(query2)
        dataset_patterns = cursor.fetchall()
        
        print(f"   Found {len(dataset_patterns)} datasets with training metadata:")
        for pattern in dataset_patterns:
            dataset_id = pattern[0] or 'NULL'
            dataset_name = pattern[1] or 'Unknown'
            count = pattern[2]
            print(f"      - Dataset: '{dataset_name}' (ID: {dataset_id[:8]}...): {count} models")
        
        print("\n   🔍 Analysis 3: Check workspace_states vs training_metadata alignment")
        query3 = """
        SELECT ws.state_name, ws.dataset_id, 
               COUNT(tm.id) as training_count,
               MAX(tm.created_at) as last_training
        FROM workspace_states ws
        LEFT JOIN training_metadata tm ON ws.dataset_id = tm.dataset_id 
                                       AND ws.state_name = tm.workspace_name
        GROUP BY ws.state_name, ws.dataset_id
        ORDER BY ws.state_name
        """
        
        cursor.execute(query3)
        alignment_data = cursor.fetchall()
        
        print(f"   Workspace alignment analysis:")
        latency_nov_alignment = None
        for row in alignment_data:
            state_name = row[0]
            dataset_id = row[1]
            training_count = row[2] or 0
            last_training = row[3]
            
            print(f"      - Workspace: '{state_name}' -> {training_count} training records")
            
            if 'latency_nov' in state_name.lower():
                latency_nov_alignment = {
                    'workspace_name': state_name,
                    'dataset_id': dataset_id,
                    'training_count': training_count,
                    'last_training': last_training
                }
                print(f"        🎯 LATENCY_NOV ALIGNMENT: {training_count} training records")
        
        cursor.close()
        connection.close()
        
        # Determine root cause
        if latency_nov_alignment:
            if latency_nov_alignment['training_count'] == 0:
                print("\n   🔍 ROOT CAUSE IDENTIFIED:")
                print("      ❌ Workspace 'latency_nov' exists but has NO training metadata")
                print("      ❌ This explains why Training Metadata page shows '0 models'")
                print("      🔧 SOLUTION: Check if training was actually completed and saved")
                return True, "workspace_exists_no_training"
            else:
                print("\n   ✅ Workspace 'latency_nov' has training metadata")
                print("      🔍 Issue might be in API query logic or frontend display")
                return True, "training_exists_api_issue"
        else:
            print("\n   🔍 ROOT CAUSE IDENTIFIED:")
            print("      ❌ Workspace 'latency_nov' not found in workspace_states")
            print("      ❌ Workspace was never saved or has different name")
            return True, "workspace_not_found"
        
    except Exception as e:
        print(f"❌ Root cause analysis failed: {str(e)}")
        return False, "analysis_failed"

def main():
    """Run Training Metadata Investigation"""
    print("🚀 PROMISE AI TRAINING METADATA INVESTIGATION")
    print("🎯 Focus: Workspace 'latency_nov' showing '0 models' issue")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now().isoformat()}")
    print("="*70)
    
    # Track test results
    results = {
        'direct_db_query': False,
        'workspace_states': False,
        'training_metadata_api': False,
        'dataset_correlation': False,
        'root_cause_analysis': False
    }
    
    findings = {}
    
    # Test 1: Direct Database Query
    print("\n🔍 PRIORITY: HIGH - Direct Database Investigation")
    db_success, latency_nov_in_training = test_direct_database_query()
    results['direct_db_query'] = db_success
    findings['latency_nov_in_training'] = latency_nov_in_training
    
    # Test 2: Workspace States Query
    print("\n🔍 PRIORITY: HIGH - Workspace States Verification")
    ws_success, workspace_dataset_id = test_workspace_states_query()
    results['workspace_states'] = ws_success
    findings['workspace_dataset_id'] = workspace_dataset_id
    
    # Test 3: Training Metadata API
    print("\n🔍 PRIORITY: CRITICAL - API Endpoint Testing")
    api_success, latency_nov_in_api = test_training_metadata_endpoint()
    results['training_metadata_api'] = api_success
    findings['latency_nov_in_api'] = latency_nov_in_api
    
    # Test 4: Dataset-Workspace Correlation
    if workspace_dataset_id:
        print("\n🔍 PRIORITY: HIGH - Dataset Correlation Analysis")
        corr_success, has_training_data = test_dataset_workspace_correlation(workspace_dataset_id)
        results['dataset_correlation'] = corr_success
        findings['has_training_data'] = has_training_data
    else:
        print("\n⚠️  Skipping dataset correlation - no workspace dataset ID found")
        results['dataset_correlation'] = True  # Don't fail for missing prerequisite
        findings['has_training_data'] = False
    
    # Test 5: Root Cause Analysis
    print("\n🔍 PRIORITY: CRITICAL - Root Cause Identification")
    rca_success, root_cause = test_root_cause_analysis()
    results['root_cause_analysis'] = rca_success
    findings['root_cause'] = root_cause
    
    # Summary
    print("\n" + "="*70)
    print("📊 TRAINING METADATA INVESTIGATION SUMMARY")
    print("="*70)
    
    passed_tests = sum(1 for result in results.values() if result)
    total_tests = len(results)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests completed successfully")
    
    # Key Findings
    print("\n🔍 KEY FINDINGS:")
    print(f"   📋 Workspace 'latency_nov' in training_metadata table: {'✅ YES' if findings.get('latency_nov_in_training') else '❌ NO'}")
    print(f"   📋 Workspace 'latency_nov' in workspace_states table: {'✅ YES' if findings.get('workspace_dataset_id') else '❌ NO'}")
    print(f"   📋 Workspace 'latency_nov' in API response: {'✅ YES' if findings.get('latency_nov_in_api') else '❌ NO'}")
    print(f"   📋 Training data exists for workspace dataset: {'✅ YES' if findings.get('has_training_data') else '❌ NO'}")
    
    # Root Cause Determination
    root_cause = findings.get('root_cause', 'unknown')
    print(f"\n🎯 ROOT CAUSE: {root_cause}")
    
    if root_cause == "workspace_exists_no_training":
        print("   🔧 SOLUTION: Workspace exists but no training metadata was saved")
        print("      - Check if training process completed successfully")
        print("      - Verify training metadata is being saved to database")
        print("      - Check for errors during model training")
    elif root_cause == "training_exists_api_issue":
        print("   🔧 SOLUTION: Training data exists but API not returning it")
        print("      - Check API query logic in /api/training/metadata/by-workspace")
        print("      - Verify workspace name matching logic")
        print("      - Check JOIN conditions between tables")
    elif root_cause == "workspace_not_found":
        print("   🔧 SOLUTION: Workspace 'latency_nov' was never saved")
        print("      - Check workspace save functionality")
        print("      - Verify workspace name is being saved correctly")
        print("      - Check for case sensitivity issues")
    else:
        print("   🔧 SOLUTION: Further investigation needed")
        print("      - Check backend logs for training errors")
        print("      - Verify database schema and constraints")
        print("      - Test training process end-to-end")
    
    # Final Status
    if findings.get('latency_nov_in_api'):
        print("\n📋 STATUS: ✅ ISSUE RESOLVED - Workspace found in API")
        return True
    else:
        print("\n📋 STATUS: ❌ ISSUE CONFIRMED - Root cause identified")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
