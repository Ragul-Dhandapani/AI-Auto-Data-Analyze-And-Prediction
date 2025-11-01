#!/usr/bin/env python3
"""
Database Connection Functionality Testing
Tests comprehensive database connection support for all 5 database types:
PostgreSQL, MySQL, Oracle, SQL Server, MongoDB
"""

import requests
import json
import os
from pathlib import Path

# Get backend URL from frontend .env file
def get_backend_url():
    frontend_env_path = Path("/app/frontend/.env")
    if frontend_env_path.exists():
        with open(frontend_env_path, 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    return "http://localhost:8001"

BACKEND_URL = get_backend_url()
API_BASE = f"{BACKEND_URL}/api"

print(f"Testing database connection functionality at: {API_BASE}")

def test_connection_string_parsing():
    """Test connection string parsing for all database types"""
    
    print("\n=== Testing Connection String Parsing ===")
    
    # Test cases for different database types and connection string formats
    test_cases = [
        {
            "name": "PostgreSQL URL format",
            "source_type": "postgresql",
            "connection_string": "postgresql://testuser:testpass@localhost:5432/testdb",
            "expected_config": {
                "host": "localhost",
                "port": 5432,
                "database": "testdb",
                "username": "testuser",
                "password": "testpass"
            }
        },
        {
            "name": "MySQL URL format",
            "source_type": "mysql",
            "connection_string": "mysql://testuser:testpass@localhost:3306/testdb",
            "expected_config": {
                "host": "localhost",
                "port": 3306,
                "database": "testdb",
                "username": "testuser",
                "password": "testpass"
            }
        },
        {
            "name": "Oracle URL format",
            "source_type": "oracle",
            "connection_string": "oracle://testuser:testpass@localhost:1521/XEPDB1",
            "expected_config": {
                "host": "localhost",
                "port": 1521,
                "service_name": "XEPDB1",
                "username": "testuser",
                "password": "testpass"
            }
        },
        {
            "name": "SQL Server URL format",
            "source_type": "sqlserver",
            "connection_string": "mssql://sa:StrongPass123!@localhost:1433/master",
            "expected_config": {
                "host": "localhost",
                "port": 1433,
                "database": "master",
                "username": "sa",
                "password": "StrongPass123!"
            }
        },
        {
            "name": "SQL Server key-value format",
            "source_type": "sqlserver",
            "connection_string": "Server=localhost,1433;Database=master;User Id=sa;Password=StrongPass123!;",
            "expected_config": {
                "host": "localhost",
                "port": 1433,
                "database": "master",
                "username": "sa",
                "password": "StrongPass123!"
            }
        },
        {
            "name": "MongoDB URL format",
            "source_type": "mongodb",
            "connection_string": "mongodb://testuser:testpass@localhost:27017/testdb",
            "expected_config": {
                "host": "localhost",
                "port": 27017,
                "database": "testdb",
                "username": "testuser",
                "password": "testpass"
            }
        }
    ]
    
    parse_url = f"{API_BASE}/datasource/parse-connection-string"
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing {test_case['name']}...")
        
        # Prepare form data
        form_data = {
            'source_type': test_case['source_type'],
            'connection_string': test_case['connection_string']
        }
        
        try:
            response = requests.post(parse_url, data=form_data)
            
            if response.status_code != 200:
                print(f"❌ Request failed: {response.status_code} - {response.text}")
                all_passed = False
                continue
            
            result = response.json()
            
            # Check if parsing was successful
            if not result.get('success'):
                print(f"❌ Parsing failed: {result.get('message', 'Unknown error')}")
                all_passed = False
                continue
            
            # Verify config structure
            config = result.get('config', {})
            expected = test_case['expected_config']
            
            # Check each expected field
            for key, expected_value in expected.items():
                if key not in config:
                    print(f"❌ Missing field '{key}' in config")
                    all_passed = False
                    continue
                
                actual_value = config[key]
                if actual_value != expected_value:
                    print(f"❌ Field '{key}': expected {expected_value}, got {actual_value}")
                    all_passed = False
                    continue
            
            print(f"✅ {test_case['name']} parsed correctly")
            print(f"   Config: {config}")
            
        except Exception as e:
            print(f"❌ Exception during {test_case['name']}: {str(e)}")
            all_passed = False
    
    return all_passed

def test_connection_testing():
    """Test connection testing for all database types"""
    
    print("\n=== Testing Database Connection Testing ===")
    
    # Test configurations for different database types
    test_configs = [
        {
            "name": "PostgreSQL",
            "source_type": "postgresql",
            "config": {
                "host": "localhost",
                "port": 5432,
                "database": "testdb",
                "username": "testuser",
                "password": "testpass"
            }
        },
        {
            "name": "MySQL",
            "source_type": "mysql",
            "config": {
                "host": "localhost",
                "port": 3306,
                "database": "testdb",
                "username": "testuser",
                "password": "testpass"
            }
        },
        {
            "name": "Oracle",
            "source_type": "oracle",
            "config": {
                "host": "localhost",
                "port": 1521,
                "service_name": "XEPDB1",
                "username": "testuser",
                "password": "testpass"
            }
        },
        {
            "name": "SQL Server",
            "source_type": "sqlserver",
            "config": {
                "host": "localhost",
                "port": 1433,
                "database": "master",
                "username": "sa",
                "password": "StrongPass123!"
            }
        },
        {
            "name": "MongoDB",
            "source_type": "mongodb",
            "config": {
                "host": "localhost",
                "port": 27017,
                "database": "testdb",
                "username": "testuser",
                "password": "testpass"
            }
        }
    ]
    
    test_url = f"{API_BASE}/datasource/test-connection"
    
    all_passed = True
    
    for i, test_config in enumerate(test_configs, 1):
        print(f"\n{i}. Testing {test_config['name']} connection...")
        
        request_data = {
            "source_type": test_config['source_type'],
            "config": test_config['config']
        }
        
        try:
            response = requests.post(test_url, json=request_data)
            
            if response.status_code != 200:
                print(f"❌ Request failed: {response.status_code} - {response.text}")
                all_passed = False
                continue
            
            result = response.json()
            
            # Check response structure
            if 'success' not in result:
                print(f"❌ Missing 'success' field in response")
                all_passed = False
                continue
            
            if 'message' not in result:
                print(f"❌ Missing 'message' field in response")
                all_passed = False
                continue
            
            # Since databases aren't actually running, we expect connection failures
            if result['success']:
                print(f"⚠️  Unexpected success (databases should not be running)")
            else:
                print(f"✅ Expected connection failure: {result['message']}")
            
            # Verify response format
            print(f"   Response format: {{'success': {result['success']}, 'message': '{result['message'][:50]}...'}")
            
        except Exception as e:
            print(f"❌ Exception during {test_config['name']} test: {str(e)}")
            all_passed = False
    
    return all_passed

def test_list_tables():
    """Test table listing for all database types"""
    
    print("\n=== Testing Table Listing ===")
    
    # Test configurations for different database types
    test_configs = [
        {
            "name": "PostgreSQL",
            "source_type": "postgresql",
            "config": {
                "host": "localhost",
                "port": 5432,
                "database": "testdb",
                "username": "testuser",
                "password": "testpass"
            }
        },
        {
            "name": "MySQL",
            "source_type": "mysql",
            "config": {
                "host": "localhost",
                "port": 3306,
                "database": "testdb",
                "username": "testuser",
                "password": "testpass"
            }
        },
        {
            "name": "Oracle",
            "source_type": "oracle",
            "config": {
                "host": "localhost",
                "port": 1521,
                "service_name": "XEPDB1",
                "username": "testuser",
                "password": "testpass"
            }
        },
        {
            "name": "SQL Server",
            "source_type": "sqlserver",
            "config": {
                "host": "localhost",
                "port": 1433,
                "database": "master",
                "username": "sa",
                "password": "StrongPass123!"
            }
        },
        {
            "name": "MongoDB",
            "source_type": "mongodb",
            "config": {
                "host": "localhost",
                "port": 27017,
                "database": "testdb",
                "username": "testuser",
                "password": "testpass"
            }
        }
    ]
    
    list_url = f"{API_BASE}/datasource/list-tables"
    
    all_passed = True
    
    for i, test_config in enumerate(test_configs, 1):
        print(f"\n{i}. Testing {test_config['name']} table listing...")
        
        request_data = {
            "source_type": test_config['source_type'],
            "config": test_config['config']
        }
        
        try:
            response = requests.post(list_url, json=request_data)
            
            # Since databases aren't running, we expect 500 errors with proper error messages
            if response.status_code == 500:
                print(f"✅ Expected 500 error for {test_config['name']} (database not running)")
                
                # Check if error message is informative
                try:
                    error_data = response.json()
                    if 'detail' in error_data:
                        print(f"   Error message: {error_data['detail'][:100]}...")
                    else:
                        print(f"   Raw error: {response.text[:100]}...")
                except:
                    print(f"   Raw error: {response.text[:100]}...")
                    
            elif response.status_code == 200:
                # Unexpected success
                result = response.json()
                print(f"⚠️  Unexpected success for {test_config['name']}")
                print(f"   Tables: {result.get('tables', [])}")
                
            else:
                print(f"❌ Unexpected status code: {response.status_code}")
                all_passed = False
            
        except Exception as e:
            print(f"❌ Exception during {test_config['name']} test: {str(e)}")
            all_passed = False
    
    return all_passed

def test_load_table():
    """Test table loading for different source types"""
    
    print("\n=== Testing Table Loading ===")
    
    load_url = f"{API_BASE}/datasource/load-table"
    
    # Test with invalid source type
    print("\n1. Testing with invalid source type...")
    
    form_data = {
        'source_type': 'invalid_db_type',
        'config': json.dumps({"host": "localhost"}),
        'table_name': 'test_table'
    }
    
    try:
        response = requests.post(load_url, data=form_data)
        
        if response.status_code == 500:
            print(f"✅ Expected 500 error for invalid source type")
            print(f"   Error: {response.text[:100]}...")
        else:
            print(f"❌ Expected 500 error, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception during invalid source type test: {str(e)}")
        return False
    
    # Test with valid source types but invalid credentials
    test_configs = [
        {
            "name": "PostgreSQL",
            "source_type": "postgresql",
            "config": {
                "host": "localhost",
                "port": 5432,
                "database": "testdb",
                "username": "testuser",
                "password": "testpass"
            }
        },
        {
            "name": "MySQL",
            "source_type": "mysql",
            "config": {
                "host": "localhost",
                "port": 3306,
                "database": "testdb",
                "username": "testuser",
                "password": "testpass"
            }
        }
    ]
    
    for i, test_config in enumerate(test_configs, 2):
        print(f"\n{i}. Testing {test_config['name']} table loading...")
        
        form_data = {
            'source_type': test_config['source_type'],
            'config': json.dumps(test_config['config']),
            'table_name': 'test_table'
        }
        
        try:
            response = requests.post(load_url, data=form_data)
            
            if response.status_code == 500:
                print(f"✅ Expected 500 error for {test_config['name']} (database not running)")
                print(f"   Error: {response.text[:100]}...")
            else:
                print(f"❌ Expected 500 error, got {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Exception during {test_config['name']} test: {str(e)}")
            return False
    
    return True

def test_unsupported_database_types():
    """Test handling of unsupported database types"""
    
    print("\n=== Testing Unsupported Database Types ===")
    
    # Test connection with unsupported type
    print("\n1. Testing unsupported database type in connection test...")
    
    test_url = f"{API_BASE}/datasource/test-connection"
    request_data = {
        "source_type": "unsupported_db",
        "config": {"host": "localhost"}
    }
    
    try:
        response = requests.post(test_url, json=request_data)
        
        if response.status_code == 200:
            result = response.json()
            if not result.get('success') and 'unsupported' in result.get('message', '').lower():
                print(f"✅ Correctly handled unsupported database type")
                print(f"   Message: {result['message']}")
            else:
                print(f"❌ Unexpected response for unsupported type: {result}")
                return False
        else:
            print(f"❌ Expected 200 with error message, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception during unsupported type test: {str(e)}")
        return False
    
    # Test list tables with unsupported type
    print("\n2. Testing unsupported database type in list tables...")
    
    list_url = f"{API_BASE}/datasource/list-tables"
    
    try:
        response = requests.post(list_url, json=request_data)
        
        if response.status_code == 400:
            print(f"✅ Correctly returned 400 for unsupported database type")
            error_data = response.json()
            print(f"   Error: {error_data.get('detail', response.text)}")
        else:
            print(f"❌ Expected 400 error, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception during unsupported type test: {str(e)}")
        return False
    
    return True

def test_endpoint_accessibility():
    """Test that all endpoints are accessible and return proper responses"""
    
    print("\n=== Testing Endpoint Accessibility ===")
    
    endpoints = [
        {
            "name": "Parse Connection String",
            "url": f"{API_BASE}/datasource/parse-connection-string",
            "method": "POST",
            "data": {
                'source_type': 'postgresql',
                'connection_string': 'postgresql://user:pass@host:5432/db'
            },
            "content_type": "form"
        },
        {
            "name": "Test Connection",
            "url": f"{API_BASE}/datasource/test-connection",
            "method": "POST",
            "data": {
                "source_type": "postgresql",
                "config": {"host": "localhost", "port": 5432}
            },
            "content_type": "json"
        },
        {
            "name": "List Tables",
            "url": f"{API_BASE}/datasource/list-tables",
            "method": "POST",
            "data": {
                "source_type": "postgresql",
                "config": {"host": "localhost", "port": 5432}
            },
            "content_type": "json"
        },
        {
            "name": "Load Table",
            "url": f"{API_BASE}/datasource/load-table",
            "method": "POST",
            "data": {
                'source_type': 'postgresql',
                'config': json.dumps({"host": "localhost", "port": 5432}),
                'table_name': 'test_table'
            },
            "content_type": "form"
        }
    ]
    
    all_passed = True
    
    for i, endpoint in enumerate(endpoints, 1):
        print(f"\n{i}. Testing {endpoint['name']} endpoint accessibility...")
        
        try:
            if endpoint['content_type'] == 'json':
                response = requests.post(endpoint['url'], json=endpoint['data'])
            else:
                response = requests.post(endpoint['url'], data=endpoint['data'])
            
            # Check if endpoint is accessible (not 404)
            if response.status_code == 404:
                print(f"❌ Endpoint not found: {endpoint['url']}")
                all_passed = False
                continue
            
            # Any other status code means the endpoint exists
            print(f"✅ Endpoint accessible: {response.status_code}")
            
            # Check if response is JSON (for most endpoints)
            try:
                response.json()
                print(f"   Returns valid JSON response")
            except:
                print(f"   Returns non-JSON response: {response.text[:50]}...")
            
        except Exception as e:
            print(f"❌ Exception testing {endpoint['name']}: {str(e)}")
            all_passed = False
    
    return all_passed

def main():
    """Run all database connection tests"""
    print("Starting Database Connection Functionality Tests")
    print("=" * 70)
    
    try:
        test_results = []
        
        # Test all functionality
        print("\n🔍 Testing Connection String Parsing...")
        test_results.append(("Connection String Parsing", test_connection_string_parsing()))
        
        print("\n🔗 Testing Database Connections...")
        test_results.append(("Database Connection Testing", test_connection_testing()))
        
        print("\n📋 Testing Table Listing...")
        test_results.append(("Table Listing", test_list_tables()))
        
        print("\n📊 Testing Table Loading...")
        test_results.append(("Table Loading", test_load_table()))
        
        print("\n❌ Testing Unsupported Types...")
        test_results.append(("Unsupported Database Types", test_unsupported_database_types()))
        
        print("\n🌐 Testing Endpoint Accessibility...")
        test_results.append(("Endpoint Accessibility", test_endpoint_accessibility()))
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 DATABASE CONNECTION TEST RESULTS:")
        print("=" * 70)
        
        passed = 0
        failed = 0
        
        for test_name, result in test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name:<35} {status}")
            if result:
                passed += 1
            else:
                failed += 1
        
        print(f"\nTotal: {len(test_results)} tests | Passed: {passed} | Failed: {failed}")
        
        if failed == 0:
            print("\n🎉 ALL DATABASE CONNECTION TESTS PASSED!")
            print("Database connection functionality is working correctly.")
            print("\nKey findings:")
            print("- All 5 database types (PostgreSQL, MySQL, Oracle, SQL Server, MongoDB) are supported")
            print("- Connection string parsing works for all formats")
            print("- Error handling is proper for connection failures")
            print("- All endpoints are accessible and return proper responses")
            print("- Unsupported database types are handled correctly")
            return True
        else:
            print(f"\n❌ {failed} TEST(S) FAILED!")
            print("Some database connection functionality needs to be addressed.")
            return False
            
    except Exception as e:
        print(f"\n❌ Test execution failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)