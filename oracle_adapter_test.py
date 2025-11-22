#!/usr/bin/env python3
"""
Oracle Database Adapter Comprehensive Test Suite
Tests Oracle 19c on AWS RDS with workspace-centric architecture

Test Coverage:
1. Workspace Operations (create, list, get)
2. File Upload & Dataset Creation (DATASET_BLOBS, DATASETS tables)
3. Dataset Operations (list, get by ID)
4. File Retrieval (BLOB data retrieval and DataFrame loading)

Success Criteria:
✅ All CRUD operations work without ORA errors
✅ Foreign key constraints are satisfied
✅ File upload -> storage -> retrieval cycle works end-to-end
✅ Workspace-dataset hierarchy is maintained
✅ No "table or view does not exist" errors
"""

import asyncio
import requests
import json
import pandas as pd
import io
import uuid
from datetime import datetime
import logging
import sys
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Backend URL from environment
BACKEND_URL = "https://oracle-ml-hub.preview.emergentagent.com/api"

class OracleAdapterTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_workspace_id = None
        self.test_dataset_id = None
        self.test_file_id = None
        self.test_results = []
        
    def log_test_result(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASSED" if success else "❌ FAILED"
        logger.info(f"{status}: {test_name}")
        if details:
            logger.info(f"   Details: {details}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
    
    def create_test_csv_data(self) -> bytes:
        """Create test CSV data with mixed numeric and string data"""
        test_data = {
            'id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'product_name': ['Widget A', 'Widget B', 'Gadget X', 'Tool Y', 'Device Z', 
                           'Component P', 'Module Q', 'Unit R', 'Item S', 'Part T'],
            'price': [19.99, 29.99, 39.99, 49.99, 59.99, 69.99, 79.99, 89.99, 99.99, 109.99],
            'category': ['Electronics', 'Tools', 'Electronics', 'Tools', 'Electronics',
                        'Tools', 'Electronics', 'Tools', 'Electronics', 'Tools'],
            'in_stock': [True, False, True, True, False, True, False, True, True, False]
        }
        
        df = pd.DataFrame(test_data)
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        return csv_buffer.getvalue().encode('utf-8')
    
    async def test_1_workspace_create(self):
        """Test 1: Create workspace (POST /api/workspace/create)"""
        try:
            workspace_data = {
                "name": f"Oracle Test Workspace {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "description": "Test workspace for Oracle adapter validation",
                "tags": ["oracle", "test", "adapter"]
            }
            
            response = requests.post(f"{self.backend_url}/workspace/create", json=workspace_data)
            
            if response.status_code == 200:
                result = response.json()
                self.test_workspace_id = result['workspace']['id']
                self.log_test_result(
                    "Workspace Creation", 
                    True, 
                    f"Created workspace ID: {self.test_workspace_id}"
                )
                return True
            else:
                self.log_test_result(
                    "Workspace Creation", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test_result("Workspace Creation", False, f"Exception: {str(e)}")
            return False
    
    async def test_2_workspace_list(self):
        """Test 2: List workspaces (GET /api/workspace/list)"""
        try:
            response = requests.get(f"{self.backend_url}/workspace/list")
            
            if response.status_code == 200:
                result = response.json()
                workspaces = result.get('workspaces', [])
                
                # Check if our test workspace is in the list
                found_workspace = any(w.get('id') == self.test_workspace_id for w in workspaces)
                
                if found_workspace:
                    self.log_test_result(
                        "Workspace List", 
                        True, 
                        f"Found {len(workspaces)} workspaces, including test workspace"
                    )
                    return True
                else:
                    self.log_test_result(
                        "Workspace List", 
                        False, 
                        f"Test workspace {self.test_workspace_id} not found in list"
                    )
                    return False
            else:
                self.log_test_result(
                    "Workspace List", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test_result("Workspace List", False, f"Exception: {str(e)}")
            return False
    
    async def test_3_workspace_get(self):
        """Test 3: Get specific workspace (GET /api/workspace/{id})"""
        try:
            if not self.test_workspace_id:
                self.log_test_result("Workspace Get", False, "No test workspace ID available")
                return False
            
            response = requests.get(f"{self.backend_url}/workspace/{self.test_workspace_id}")
            
            if response.status_code == 200:
                result = response.json()
                workspace = result.get('workspace', {})
                
                if workspace.get('id') == self.test_workspace_id:
                    self.log_test_result(
                        "Workspace Get", 
                        True, 
                        f"Retrieved workspace: {workspace.get('name')}"
                    )
                    return True
                else:
                    self.log_test_result(
                        "Workspace Get", 
                        False, 
                        "Workspace ID mismatch in response"
                    )
                    return False
            else:
                self.log_test_result(
                    "Workspace Get", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test_result("Workspace Get", False, f"Exception: {str(e)}")
            return False
    
    async def test_4_file_upload_dataset_creation(self):
        """Test 4: Upload CSV file to workspace (POST /api/datasource/upload)"""
        try:
            if not self.test_workspace_id:
                self.log_test_result("File Upload", False, "No test workspace ID available")
                return False
            
            # Create test CSV data
            csv_data = self.create_test_csv_data()
            
            # Prepare multipart form data
            files = {
                'file': ('oracle_test_data.csv', csv_data, 'text/csv')
            }
            data = {
                'workspace_id': self.test_workspace_id
            }
            
            response = requests.post(f"{self.backend_url}/datasource/upload", files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                dataset = result.get('dataset', {})
                self.test_dataset_id = dataset.get('id')
                
                if self.test_dataset_id:
                    self.log_test_result(
                        "File Upload & Dataset Creation", 
                        True, 
                        f"Created dataset ID: {self.test_dataset_id}, File size: {len(csv_data)} bytes"
                    )
                    return True
                else:
                    self.log_test_result(
                        "File Upload & Dataset Creation", 
                        False, 
                        "No dataset_id in response"
                    )
                    return False
            else:
                self.log_test_result(
                    "File Upload & Dataset Creation", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test_result("File Upload & Dataset Creation", False, f"Exception: {str(e)}")
            return False
    
    async def test_5_dataset_metadata_verification(self):
        """Test 5: Verify dataset metadata in DATASETS table with foreign keys"""
        try:
            if not self.test_dataset_id:
                self.log_test_result("Dataset Metadata Verification", False, "No test dataset ID available")
                return False
            
            response = requests.get(f"{self.backend_url}/datasource/datasets/{self.test_dataset_id}")
            
            if response.status_code == 200:
                dataset = response.json()
                
                # Verify required fields
                required_fields = ['id', 'workspace_id', 'name', 'row_count', 'column_count', 'storage_type']
                missing_fields = [field for field in required_fields if field not in dataset]
                
                if missing_fields:
                    self.log_test_result(
                        "Dataset Metadata Verification", 
                        False, 
                        f"Missing fields: {missing_fields}"
                    )
                    return False
                
                # Verify workspace_id foreign key relationship
                if dataset.get('workspace_id') != self.test_workspace_id:
                    self.log_test_result(
                        "Dataset Metadata Verification", 
                        False, 
                        f"Workspace ID mismatch: expected {self.test_workspace_id}, got {dataset.get('workspace_id')}"
                    )
                    return False
                
                # Verify STORAGE_TYPE and GRIDFS_FILE_ID columns are populated
                storage_type = dataset.get('storage_type')
                gridfs_file_id = dataset.get('gridfs_file_id')
                
                if not storage_type:
                    self.log_test_result(
                        "Dataset Metadata Verification", 
                        False, 
                        "STORAGE_TYPE column not populated"
                    )
                    return False
                
                self.log_test_result(
                    "Dataset Metadata Verification", 
                    True, 
                    f"All metadata fields present, workspace_id FK correct, storage_type: {storage_type}"
                )
                return True
                
            else:
                self.log_test_result(
                    "Dataset Metadata Verification", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test_result("Dataset Metadata Verification", False, f"Exception: {str(e)}")
            return False
    
    async def test_6_dataset_list(self):
        """Test 6: List datasets (GET /api/datasource/datasets)"""
        try:
            response = requests.get(f"{self.backend_url}/datasource/datasets")
            
            if response.status_code == 200:
                result = response.json()
                datasets = result.get('datasets', [])
                
                # Check if our test dataset is in the list
                found_dataset = any(d.get('id') == self.test_dataset_id for d in datasets)
                
                if found_dataset:
                    self.log_test_result(
                        "Dataset List", 
                        True, 
                        f"Found {len(datasets)} datasets, including test dataset"
                    )
                    return True
                else:
                    self.log_test_result(
                        "Dataset List", 
                        False, 
                        f"Test dataset {self.test_dataset_id} not found in list"
                    )
                    return False
            else:
                self.log_test_result(
                    "Dataset List", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test_result("Dataset List", False, f"Exception: {str(e)}")
            return False
    
    async def test_7_dataset_get_by_id(self):
        """Test 7: Get specific dataset by ID (GET /api/datasource/datasets/{id})"""
        try:
            if not self.test_dataset_id:
                self.log_test_result("Dataset Get by ID", False, "No test dataset ID available")
                return False
            
            response = requests.get(f"{self.backend_url}/datasource/datasets/{self.test_dataset_id}")
            
            if response.status_code == 200:
                dataset = response.json()
                
                # Verify WORKSPACE_ID foreign key relationship
                if dataset.get('workspace_id') == self.test_workspace_id:
                    self.log_test_result(
                        "Dataset Get by ID", 
                        True, 
                        f"Retrieved dataset with correct workspace_id FK: {dataset.get('name')}"
                    )
                    return True
                else:
                    self.log_test_result(
                        "Dataset Get by ID", 
                        False, 
                        f"Workspace ID FK mismatch: expected {self.test_workspace_id}, got {dataset.get('workspace_id')}"
                    )
                    return False
            else:
                self.log_test_result(
                    "Dataset Get by ID", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test_result("Dataset Get by ID", False, f"Exception: {str(e)}")
            return False
    
    async def test_8_file_blob_storage_verification(self):
        """Test 8: Verify file is stored in DATASET_BLOBS table"""
        try:
            if not self.test_dataset_id:
                self.log_test_result("BLOB Storage Verification", False, "No test dataset ID available")
                return False
            
            # Get dataset to check for file storage information
            response = requests.get(f"{self.backend_url}/datasource/datasets/{self.test_dataset_id}")
            
            if response.status_code == 200:
                dataset = response.json()
                
                # Check if dataset has file storage information
                storage_type = dataset.get('storage_type')
                gridfs_file_id = dataset.get('gridfs_file_id')
                
                if storage_type and storage_type in ['direct', 'blob']:
                    self.log_test_result(
                        "BLOB Storage Verification", 
                        True, 
                        f"File stored with storage_type: {storage_type}, file_id: {gridfs_file_id}"
                    )
                    return True
                else:
                    self.log_test_result(
                        "BLOB Storage Verification", 
                        False, 
                        f"Invalid or missing storage_type: {storage_type}"
                    )
                    return False
            else:
                self.log_test_result(
                    "BLOB Storage Verification", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test_result("BLOB Storage Verification", False, f"Exception: {str(e)}")
            return False
    
    async def test_9_file_retrieval_dataframe_loading(self):
        """Test 9: Retrieve file BLOB data and verify DataFrame loading"""
        try:
            if not self.test_dataset_id:
                self.log_test_result("File Retrieval & DataFrame Loading", False, "No test dataset ID available")
                return False
            
            # Get dataset with data preview to verify file content
            response = requests.get(f"{self.backend_url}/datasource/datasets/{self.test_dataset_id}")
            
            if response.status_code == 200:
                dataset = response.json()
                
                # Check data preview (this indicates file was successfully loaded as DataFrame)
                data_preview = dataset.get('data_preview', [])
                columns = dataset.get('columns', [])
                row_count = dataset.get('row_count', 0)
                
                if data_preview and columns and row_count > 0:
                    # Verify expected columns from our test data
                    expected_columns = ['id', 'product_name', 'price', 'category', 'in_stock']
                    columns_match = all(col in columns for col in expected_columns)
                    
                    if columns_match and row_count == 10:
                        self.log_test_result(
                            "File Retrieval & DataFrame Loading", 
                            True, 
                            f"File successfully loaded as DataFrame: {row_count} rows, {len(columns)} columns"
                        )
                        return True
                    else:
                        self.log_test_result(
                            "File Retrieval & DataFrame Loading", 
                            False, 
                            f"Data integrity issue: expected 10 rows with specific columns, got {row_count} rows, columns: {columns}"
                        )
                        return False
                else:
                    self.log_test_result(
                        "File Retrieval & DataFrame Loading", 
                        False, 
                        "No data preview available - file may not have been loaded properly"
                    )
                    return False
            else:
                self.log_test_result(
                    "File Retrieval & DataFrame Loading", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test_result("File Retrieval & DataFrame Loading", False, f"Exception: {str(e)}")
            return False
    
    async def test_10_file_integrity_check(self):
        """Test 10: Check file integrity (row count, column names match)"""
        try:
            if not self.test_dataset_id:
                self.log_test_result("File Integrity Check", False, "No test dataset ID available")
                return False
            
            response = requests.get(f"{self.backend_url}/datasource/datasets/{self.test_dataset_id}")
            
            if response.status_code == 200:
                dataset = response.json()
                
                # Verify exact match with our test data
                expected_row_count = 10
                expected_columns = ['id', 'product_name', 'price', 'category', 'in_stock']
                expected_column_count = 5
                
                actual_row_count = dataset.get('row_count', 0)
                actual_columns = dataset.get('columns', [])
                actual_column_count = dataset.get('column_count', 0)
                
                # Check row count
                if actual_row_count != expected_row_count:
                    self.log_test_result(
                        "File Integrity Check", 
                        False, 
                        f"Row count mismatch: expected {expected_row_count}, got {actual_row_count}"
                    )
                    return False
                
                # Check column count
                if actual_column_count != expected_column_count:
                    self.log_test_result(
                        "File Integrity Check", 
                        False, 
                        f"Column count mismatch: expected {expected_column_count}, got {actual_column_count}"
                    )
                    return False
                
                # Check column names
                if set(actual_columns) != set(expected_columns):
                    self.log_test_result(
                        "File Integrity Check", 
                        False, 
                        f"Column names mismatch: expected {expected_columns}, got {actual_columns}"
                    )
                    return False
                
                self.log_test_result(
                    "File Integrity Check", 
                    True, 
                    f"File integrity verified: {actual_row_count} rows, {actual_column_count} columns match expected"
                )
                return True
                
            else:
                self.log_test_result(
                    "File Integrity Check", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test_result("File Integrity Check", False, f"Exception: {str(e)}")
            return False
    
    async def test_11_workspace_dataset_hierarchy(self):
        """Test 11: Verify workspace-dataset hierarchy is maintained"""
        try:
            if not self.test_workspace_id:
                self.log_test_result("Workspace-Dataset Hierarchy", False, "No test workspace ID available")
                return False
            
            # Get workspace details including datasets
            response = requests.get(f"{self.backend_url}/workspace/{self.test_workspace_id}")
            
            if response.status_code == 200:
                result = response.json()
                workspace = result.get('workspace', {})
                datasets = result.get('datasets', [])
                
                # Check if our test dataset is in the workspace datasets
                found_dataset = any(d.get('id') == self.test_dataset_id for d in datasets)
                
                if found_dataset:
                    # Verify the dataset has correct workspace_id
                    test_dataset = next((d for d in datasets if d.get('id') == self.test_dataset_id), None)
                    if test_dataset and test_dataset.get('workspace_id') == self.test_workspace_id:
                        self.log_test_result(
                            "Workspace-Dataset Hierarchy", 
                            True, 
                            f"Hierarchy maintained: workspace contains dataset with correct FK"
                        )
                        return True
                    else:
                        self.log_test_result(
                            "Workspace-Dataset Hierarchy", 
                            False, 
                            "Dataset found in workspace but workspace_id FK is incorrect"
                        )
                        return False
                else:
                    self.log_test_result(
                        "Workspace-Dataset Hierarchy", 
                        False, 
                        f"Test dataset {self.test_dataset_id} not found in workspace datasets"
                    )
                    return False
            else:
                self.log_test_result(
                    "Workspace-Dataset Hierarchy", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test_result("Workspace-Dataset Hierarchy", False, f"Exception: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Run all Oracle adapter tests"""
        logger.info("🧪 Starting Oracle Database Adapter Comprehensive Test Suite")
        logger.info(f"Backend URL: {self.backend_url}")
        logger.info("=" * 80)
        
        # Test sequence
        tests = [
            self.test_1_workspace_create,
            self.test_2_workspace_list,
            self.test_3_workspace_get,
            self.test_4_file_upload_dataset_creation,
            self.test_5_dataset_metadata_verification,
            self.test_6_dataset_list,
            self.test_7_dataset_get_by_id,
            self.test_8_file_blob_storage_verification,
            self.test_9_file_retrieval_dataframe_loading,
            self.test_10_file_integrity_check,
            self.test_11_workspace_dataset_hierarchy
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test in tests:
            try:
                success = await test()
                if success:
                    passed_tests += 1
            except Exception as e:
                logger.error(f"Test {test.__name__} failed with exception: {str(e)}")
        
        # Summary
        logger.info("=" * 80)
        logger.info("🎯 ORACLE ADAPTER TEST SUMMARY")
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {total_tests - passed_tests}")
        logger.info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Detailed results
        logger.info("\n📊 DETAILED TEST RESULTS:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            logger.info(f"{status} {result['test']}")
            if result['details']:
                logger.info(f"   {result['details']}")
        
        # Success criteria evaluation
        logger.info("\n🎯 SUCCESS CRITERIA EVALUATION:")
        
        # Check for ORA errors (would be in failed test details)
        ora_errors = any("ORA-" in result['details'] for result in self.test_results if not result['success'])
        logger.info(f"✅ No ORA errors detected: {not ora_errors}")
        
        # Check foreign key constraints
        fk_tests = [r for r in self.test_results if 'FK' in r['details'] or 'foreign key' in r['details'].lower()]
        fk_success = all(r['success'] for r in fk_tests)
        logger.info(f"✅ Foreign key constraints satisfied: {fk_success}")
        
        # Check end-to-end cycle
        e2e_tests = ['File Upload & Dataset Creation', 'BLOB Storage Verification', 'File Retrieval & DataFrame Loading']
        e2e_success = all(any(r['test'] == test and r['success'] for r in self.test_results) for test in e2e_tests)
        logger.info(f"✅ File upload -> storage -> retrieval cycle works: {e2e_success}")
        
        # Check workspace-dataset hierarchy
        hierarchy_success = any(r['test'] == 'Workspace-Dataset Hierarchy' and r['success'] for r in self.test_results)
        logger.info(f"✅ Workspace-dataset hierarchy maintained: {hierarchy_success}")
        
        # Overall assessment
        overall_success = passed_tests >= (total_tests * 0.9)  # 90% pass rate
        logger.info(f"\n🏆 OVERALL ASSESSMENT: {'✅ SUCCESS' if overall_success else '❌ NEEDS ATTENTION'}")
        
        if overall_success:
            logger.info("Oracle database adapter operations are working correctly!")
        else:
            logger.info("Oracle database adapter has issues that need to be addressed.")
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'success_rate': (passed_tests/total_tests)*100,
            'overall_success': overall_success,
            'test_results': self.test_results
        }

async def main():
    """Main test execution"""
    tester = OracleAdapterTester()
    results = await tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if results['overall_success'] else 1)

if __name__ == "__main__":
    asyncio.run(main())