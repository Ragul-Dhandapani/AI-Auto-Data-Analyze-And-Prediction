"""
Comprehensive Backend Test Suite for PROMISE AI
Tests all critical backend functionality
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi.testclient import TestClient
import pandas as pd
from io import BytesIO
import json

# Import after path adjustment
os.chdir('/app/backend')
from server import app

client = TestClient(app)


class TestDataSourceEndpoints:
    """Test database connection endpoints"""
    
    def test_parse_postgresql_connection_string(self):
        """Test PostgreSQL connection string parsing"""
        response = client.post(
            "/api/datasource/parse-connection-string",
            data={
                "source_type": "postgresql",
                "connection_string": "postgresql://user:pass@localhost:5432/testdb"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["config"]["host"] == "localhost"
        assert data["config"]["port"] == 5432
        assert data["config"]["database"] == "testdb"
    
    def test_parse_mysql_connection_string(self):
        """Test MySQL connection string parsing"""
        response = client.post(
            "/api/datasource/parse-connection-string",
            data={
                "source_type": "mysql",
                "connection_string": "mysql://user:pass@localhost:3306/testdb"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["config"]["port"] == 3306
    
    def test_parse_oracle_connection_string(self):
        """Test Oracle connection string parsing"""
        response = client.post(
            "/api/datasource/parse-connection-string",
            data={
                "source_type": "oracle",
                "connection_string": "oracle://user:pass@localhost:1521/ORCL"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["config"]["service_name"] == "ORCL"
    
    def test_test_connection_invalid_credentials(self):
        """Test connection with invalid credentials"""
        response = client.post(
            "/api/datasource/test-connection",
            json={
                "source_type": "postgresql",
                "config": {
                    "host": "localhost",
                    "port": 5432,
                    "database": "testdb",
                    "username": "invalid",
                    "password": "invalid"
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "message" in data


class TestFileUpload:
    """Test file upload functionality"""
    
    def test_upload_csv_file(self):
        """Test CSV file upload"""
        # Create sample CSV
        csv_content = "name,age,salary\nJohn,30,50000\nJane,25,45000\nBob,35,60000"
        
        files = {"file": ("test.csv", BytesIO(csv_content.encode()), "text/csv")}
        response = client.post("/api/datasource/upload-file", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["row_count"] == 3
        assert data["column_count"] == 3
        assert "name" in data["columns"]
        assert "age" in data["columns"]
        assert "salary" in data["columns"]
    
    def test_upload_invalid_file_type(self):
        """Test upload with invalid file type"""
        files = {"file": ("test.txt", BytesIO(b"invalid content"), "text/plain")}
        response = client.post("/api/datasource/upload-file", files=files)
        
        assert response.status_code == 500  # Should fail
    
    def test_upload_duplicate_filename(self):
        """Test duplicate filename handling"""
        csv_content = "col1,col2\n1,2\n3,4"
        
        # Upload first file
        files1 = {"file": ("duplicate.csv", BytesIO(csv_content.encode()), "text/csv")}
        response1 = client.post("/api/datasource/upload-file", files=files1)
        assert response1.status_code == 200
        name1 = response1.json()["name"]
        
        # Upload second file with same name
        files2 = {"file": ("duplicate.csv", BytesIO(csv_content.encode()), "text/csv")}
        response2 = client.post("/api/datasource/upload-file", files=files2)
        assert response2.status_code == 200
        name2 = response2.json()["name"]
        
        # Names should be different
        assert name1 != name2
        assert "duplicate_1.csv" in name2 or "duplicate" in name2


class TestAnalysisEndpoints:
    """Test data analysis endpoints"""
    
    @pytest.fixture
    def uploaded_dataset(self):
        """Fixture to upload a test dataset"""
        csv_content = "age,salary,experience\n25,50000,2\n30,60000,5\n35,70000,8\n40,80000,12\n45,90000,15"
        files = {"file": ("test_analysis.csv", BytesIO(csv_content.encode()), "text/csv")}
        response = client.post("/api/datasource/upload-file", files=files)
        return response.json()["id"]
    
    def test_holistic_analysis(self, uploaded_dataset):
        """Test holistic analysis endpoint"""
        response = client.post(
            "/api/analysis/holistic",
            json={"dataset_id": uploaded_dataset}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "profile" in data
        assert "models" in data
        assert "auto_charts" in data
        assert "correlations" in data
        
        # Check profiling
        assert data["profile"]["row_count"] == 5
        assert data["profile"]["column_count"] == 3
        
        # Check models trained
        assert len(data["models"]) > 0
        for model in data["models"]:
            assert "model_name" in model
            assert "r2_score" in model
            assert "rmse" in model
        
        # Check charts generated
        assert len(data["auto_charts"]) > 0
        
    def test_analysis_nonexistent_dataset(self):
        """Test analysis with non-existent dataset"""
        response = client.post(
            "/api/analysis/holistic",
            json={"dataset_id": "nonexistent-id"}
        )
        
        assert response.status_code == 404


class TestChatEndpoints:
    """Test chat functionality"""
    
    @pytest.fixture
    def uploaded_dataset(self):
        """Fixture to upload a test dataset"""
        csv_content = "product,quantity,price\nLaptop,5,1200\nMouse,25,25\nKeyboard,15,75"
        files = {"file": ("test_chat.csv", BytesIO(csv_content.encode()), "text/csv")}
        response = client.post("/api/datasource/upload-file", files=files)
        return response.json()["id"]
    
    def test_chat_pie_chart_request(self, uploaded_dataset):
        """Test chat pie chart generation"""
        response = client.post(
            "/api/analysis/chat-action",
            json={
                "dataset_id": uploaded_dataset,
                "message": "show me a pie chart of products",
                "conversation_history": []
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["action"] in ["add_chart", "message"]
        if data["action"] == "add_chart":
            assert data["chart_data"]["type"] == "pie"
            assert "plotly_data" in data["chart_data"]
    
    def test_chat_correlation_request(self, uploaded_dataset):
        """Test chat correlation analysis"""
        response = client.post(
            "/api/analysis/chat-action",
            json={
                "dataset_id": uploaded_dataset,
                "message": "show correlation analysis",
                "conversation_history": []
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        if data["action"] == "add_chart":
            assert data["chart_data"]["type"] == "correlation"
            assert "correlations" in data["chart_data"]


class TestStateManagement:
    """Test workspace save/load functionality"""
    
    @pytest.fixture
    def uploaded_dataset(self):
        """Fixture to upload a test dataset"""
        csv_content = "col1,col2\n1,2\n3,4"
        files = {"file": ("test_state.csv", BytesIO(csv_content.encode()), "text/csv")}
        response = client.post("/api/datasource/upload-file", files=files)
        return response.json()["id"]
    
    def test_save_analysis_state(self, uploaded_dataset):
        """Test saving analysis state"""
        response = client.post(
            "/api/analysis/save-state",
            json={
                "dataset_id": uploaded_dataset,
                "state_name": "Test Workspace",
                "analysis_data": {"models": [], "charts": []},
                "chat_history": []
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "state_id" in data
        assert "message" in data
        
        return data["state_id"]
    
    def test_load_analysis_state(self, uploaded_dataset):
        """Test loading analysis state"""
        # First save a state
        save_response = client.post(
            "/api/analysis/save-state",
            json={
                "dataset_id": uploaded_dataset,
                "state_name": "Load Test",
                "analysis_data": {"test": "data"},
                "chat_history": [{"role": "user", "content": "test"}]
            }
        )
        state_id = save_response.json()["state_id"]
        
        # Now load it
        load_response = client.get(f"/api/analysis/load-state/{state_id}")
        
        assert load_response.status_code == 200
        data = load_response.json()
        assert data["state_name"] == "Load Test"
        assert data["analysis_data"]["test"] == "data"
        assert len(data["chat_history"]) == 1
    
    def test_get_saved_states_for_dataset(self, uploaded_dataset):
        """Test retrieving all saved states for a dataset"""
        # Save multiple states
        for i in range(3):
            client.post(
                "/api/analysis/save-state",
                json={
                    "dataset_id": uploaded_dataset,
                    "state_name": f"Workspace {i+1}",
                    "analysis_data": {},
                    "chat_history": []
                }
            )
        
        # Get all states
        response = client.get(f"/api/analysis/saved-states/{uploaded_dataset}")
        
        assert response.status_code == 200
        data = response.json()
        assert "states" in data
        assert len(data["states"]) >= 3


class TestTrainingMetadata:
    """Test training metadata endpoints"""
    
    def test_get_training_metadata(self):
        """Test retrieving training metadata"""
        response = client.get("/api/training-metadata")
        
        assert response.status_code == 200
        data = response.json()
        assert "metadata" in data
        assert isinstance(data["metadata"], list)


class TestDataValidation:
    """Test data validation and error handling"""
    
    def test_analysis_with_missing_required_fields(self):
        """Test analysis endpoint with missing fields"""
        response = client.post(
            "/api/analysis/holistic",
            json={}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_chat_with_invalid_dataset_id(self):
        """Test chat with invalid dataset ID"""
        response = client.post(
            "/api/analysis/chat-action",
            json={
                "dataset_id": "invalid-id",
                "message": "test",
                "conversation_history": []
            }
        )
        
        assert response.status_code in [404, 500]


class TestDataProcessing:
    """Test data processing utilities"""
    
    def test_large_dataset_handling(self):
        """Test handling of larger datasets"""
        # Create a larger CSV (1000 rows)
        rows = [f"{i},{i*10},{i*100}" for i in range(1000)]
        csv_content = "id,value1,value2\n" + "\n".join(rows)
        
        files = {"file": ("large.csv", BytesIO(csv_content.encode()), "text/csv")}
        response = client.post("/api/datasource/upload-file", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["row_count"] == 1000
    
    def test_dataset_with_missing_values(self):
        """Test handling of missing values"""
        csv_content = "col1,col2,col3\n1,2,3\n4,,6\n,8,9"
        
        files = {"file": ("missing.csv", BytesIO(csv_content.encode()), "text/csv")}
        response = client.post("/api/datasource/upload-file", files=files)
        
        assert response.status_code == 200
        
        # Test analysis with missing values
        dataset_id = response.json()["id"]
        analysis_response = client.post(
            "/api/analysis/holistic",
            json={"dataset_id": dataset_id}
        )
        
        assert analysis_response.status_code == 200


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
