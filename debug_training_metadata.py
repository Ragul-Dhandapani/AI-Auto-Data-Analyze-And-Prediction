#!/usr/bin/env python3
"""
Debug Training Metadata API Issue
Investigating why API returns 0 models when database has training records
"""

import requests
import json
import cx_Oracle
from datetime import datetime

# Configuration
BACKEND_URL = "https://model-genius.preview.emergentagent.com/api"
ORACLE_CONFIG = {
    'user': 'testuser',
    'password': 'DbPasswordTest',
    'host': 'promise-ai-test-oracle.cgxf9inhpsec.us-east-1.rds.amazonaws.com',
    'port': '1521',
    'service_name': 'ORCL'
}

def debug_specific_workspace():
    """Debug specific workspace 'latency_nov3' that shows 0 models in API"""
    print("🔍 DEBUGGING SPECIFIC WORKSPACE: latency_nov3")
    print("="*60)
    
    try:
        # Initialize Oracle client
        try:
            cx_Oracle.init_oracle_client(lib_dir='/opt/oracle/instantclient_19_23')
        except:
            pass
        
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
        
        # Step 1: Find the workspace_state for latency_nov3
        print("\n1. Finding workspace_state for 'latency_nov3':")
        ws_query = """
        SELECT id, dataset_id, state_name, created_at
        FROM workspace_states 
        WHERE state_name = 'latency_nov3'
        """
        cursor.execute(ws_query)
        ws_rows = cursor.fetchall()
        
        if not ws_rows:
            print("   ❌ No workspace_state found for 'latency_nov3'")
            return
        
        ws_row = ws_rows[0]
        ws_id, dataset_id, state_name, created_at = ws_row
        print(f"   ✅ Found workspace: ID={ws_id}")
        print(f"      Dataset ID: {dataset_id}")
        print(f"      State Name: {state_name}")
        print(f"      Created: {created_at}")
        
        # Step 2: Check training_metadata for this exact dataset_id and workspace_name
        print(f"\n2. Checking training_metadata for dataset_id='{dataset_id}' AND workspace_name='{state_name}':")
        training_query = """
        SELECT id, dataset_id, workspace_name, model_type, created_at
        FROM training_metadata
        WHERE dataset_id = :dataset_id
        AND workspace_name = :workspace_name
        ORDER BY created_at DESC
        """
        cursor.execute(training_query, {'dataset_id': dataset_id, 'workspace_name': state_name})
        training_rows = cursor.fetchall()
        
        print(f"   Found {len(training_rows)} training records with EXACT match")
        for row in training_rows:
            print(f"      - Model: {row[3]}, Created: {row[4]}")
        
        # Step 3: Check training_metadata for this dataset_id with ANY workspace_name
        print(f"\n3. Checking ALL training_metadata for dataset_id='{dataset_id}':")
        all_training_query = """
        SELECT id, dataset_id, workspace_name, model_type, created_at
        FROM training_metadata
        WHERE dataset_id = :dataset_id
        ORDER BY created_at DESC
        """
        cursor.execute(all_training_query, {'dataset_id': dataset_id})
        all_training_rows = cursor.fetchall()
        
        print(f"   Found {len(all_training_rows)} training records for this dataset:")
        workspace_counts = {}
        for row in all_training_rows:
            ws_name = row[2] or 'NULL'
            workspace_counts[ws_name] = workspace_counts.get(ws_name, 0) + 1
            print(f"      - Workspace: '{ws_name}', Model: {row[3]}, Created: {row[4]}")
        
        print(f"\n   Workspace distribution:")
        for ws_name, count in workspace_counts.items():
            print(f"      - '{ws_name}': {count} models")
        
        # Step 4: Test the exact API query that should return this data
        print(f"\n4. Testing API endpoint for this specific workspace:")
        try:
            response = requests.get(f"{BACKEND_URL}/training/metadata/by-workspace", timeout=30)
            if response.status_code == 200:
                data = response.json()
                datasets = data.get("datasets", [])
                
                # Find our specific dataset
                target_dataset = None
                for dataset in datasets:
                    if dataset.get('dataset_id') == dataset_id:
                        target_dataset = dataset
                        break
                
                if target_dataset:
                    print(f"   ✅ Found dataset in API response:")
                    print(f"      Dataset Name: {target_dataset.get('dataset_name')}")
                    print(f"      Dataset ID: {target_dataset.get('dataset_id')}")
                    print(f"      Total Workspaces: {target_dataset.get('total_workspaces', 0)}")
                    
                    workspaces = target_dataset.get('workspaces', [])
                    for workspace in workspaces:
                        ws_name = workspace.get('workspace_name')
                        total_models = workspace.get('total_models', 0)
                        training_runs = workspace.get('training_runs', [])
                        
                        print(f"      - Workspace: '{ws_name}' ({total_models} models)")
                        if ws_name == 'latency_nov3':
                            print(f"        🎯 TARGET WORKSPACE FOUND!")
                            print(f"        Training runs returned: {len(training_runs)}")
                            for run in training_runs[:3]:
                                print(f"           - {run.get('model_type', 'N/A')}")
                else:
                    print(f"   ❌ Dataset {dataset_id} NOT found in API response")
            else:
                print(f"   ❌ API request failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ API request exception: {str(e)}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Debug failed: {str(e)}")

def test_api_query_directly():
    """Test the exact query that the API uses"""
    print("\n🔍 TESTING API QUERY LOGIC DIRECTLY")
    print("="*60)
    
    try:
        # Initialize Oracle client
        try:
            cx_Oracle.init_oracle_client(lib_dir='/opt/oracle/instantclient_19_23')
        except:
            pass
        
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
        
        # Simulate the exact API logic
        print("\n1. Getting all datasets (like API does):")
        datasets_query = "SELECT id, name FROM datasets ORDER BY created_at DESC"
        cursor.execute(datasets_query)
        dataset_rows = cursor.fetchall()
        
        print(f"   Found {len(dataset_rows)} datasets")
        
        for ds_row in dataset_rows[:3]:  # Test first 3 datasets
            ds_id, ds_name = ds_row
            print(f"\n   📊 Processing Dataset: {ds_name} (ID: {ds_id[:8]}...)")
            
            # Get workspace states for this dataset (like API does)
            ws_query = """
            SELECT state_name, created_at, size_bytes
            FROM workspace_states
            WHERE dataset_id = :dataset_id
            ORDER BY created_at DESC
            """
            cursor.execute(ws_query, {'dataset_id': ds_id})
            ws_rows = cursor.fetchall()
            
            print(f"      Found {len(ws_rows)} workspace states")
            
            for ws_row in ws_rows:
                ws_name, ws_created, ws_size = ws_row
                print(f"      - Workspace: '{ws_name}'")
                
                # Get training runs for this workspace (EXACT API QUERY)
                training_query = """
                SELECT *
                FROM training_metadata
                WHERE dataset_id = :dataset_id
                AND workspace_name = :workspace_name
                ORDER BY created_at DESC
                """
                cursor.execute(training_query, {'dataset_id': ds_id, 'workspace_name': ws_name})
                training_runs = cursor.fetchall()
                
                print(f"         Training runs found: {len(training_runs)}")
                
                if 'latency_nov' in ws_name.lower():
                    print(f"         🎯 LATENCY WORKSPACE: {len(training_runs)} models")
                    if len(training_runs) == 0:
                        print(f"         ❌ ISSUE: No training runs found for '{ws_name}'")
                        
                        # Debug: Check if there are training runs with different workspace_name
                        debug_query = """
                        SELECT workspace_name, COUNT(*) as count
                        FROM training_metadata
                        WHERE dataset_id = :dataset_id
                        GROUP BY workspace_name
                        """
                        cursor.execute(debug_query, {'dataset_id': ds_id})
                        debug_rows = cursor.fetchall()
                        
                        print(f"         🔍 All workspace names for this dataset:")
                        for debug_row in debug_rows:
                            print(f"            - '{debug_row[0]}': {debug_row[1]} models")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ API query test failed: {str(e)}")

def main():
    print("🚀 TRAINING METADATA API DEBUG")
    print(f"Time: {datetime.now().isoformat()}")
    print("="*60)
    
    # Debug specific workspace
    debug_specific_workspace()
    
    # Test API query logic
    test_api_query_directly()
    
    print("\n" + "="*60)
    print("🎯 DEBUG COMPLETE")

if __name__ == "__main__":
    main()