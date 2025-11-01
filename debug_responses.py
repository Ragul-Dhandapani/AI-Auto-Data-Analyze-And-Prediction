#!/usr/bin/env python3
"""
Debug script to check actual API responses
"""

import requests
import json
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

print(f"Debugging API responses at: {API_BASE}")

# Get a dataset ID first
datasets_response = requests.get(f"{API_BASE}/datasets")
if datasets_response.status_code == 200:
    datasets = datasets_response.json()['datasets']
    if datasets:
        dataset_id = datasets[0]['id']
        print(f"Using dataset ID: {dataset_id}")
        
        # Test 1: AI Insights Generation
        print("\n=== DEBUG: AI Insights Generation ===")
        response = requests.post(f"{API_BASE}/analysis/run", json={
            "dataset_id": dataset_id,
            "analysis_type": "insights"
        })
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Response keys: {list(result.keys())}")
            print(f"Full response: {json.dumps(result, indent=2)}")
        else:
            print(f"Error: {response.text}")
        
        # Test 3: Training Metadata
        print("\n=== DEBUG: Training Metadata ===")
        response = requests.get(f"{API_BASE}/training-metadata")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Response keys: {list(result.keys())}")
            print(f"Full response: {json.dumps(result, indent=2)}")
        else:
            print(f"Error: {response.text}")
        
        # Test 4: ML Models Structure
        print("\n=== DEBUG: ML Models Structure ===")
        response = requests.post(f"{API_BASE}/analysis/holistic", json={
            "dataset_id": dataset_id
        })
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Response keys: {list(result.keys())}")
            if 'ml_models' in result:
                print(f"ML Models type: {type(result['ml_models'])}")
                print(f"ML Models content: {json.dumps(result['ml_models'], indent=2)}")
        else:
            print(f"Error: {response.text}")