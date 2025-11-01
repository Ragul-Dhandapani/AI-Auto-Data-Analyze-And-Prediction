"""
Pydantic Models for Request/Response Validation
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid


class DataSourceConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_type: str  # 'file', 'oracle', 'postgresql', 'mysql', 'sqlserver', 'mongodb'
    name: str
    config: Dict[str, Any] = {}  # Connection details
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DataSourceTest(BaseModel):
    source_type: str
    config: Dict[str, Any]


class AnalysisRequest(BaseModel):
    dataset_id: str
    analysis_type: str = "holistic"  # 'profile', 'clean', 'predict', 'insights', 'holistic'
    options: Dict[str, Any] = {}


class HolisticRequest(BaseModel):
    dataset_id: str


class DatasetInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    source_type: str
    row_count: int
    column_count: int
    columns: List[str]
    data_preview: List[Dict[str, Any]]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ChatRequest(BaseModel):
    dataset_id: str
    message: str
    conversation_history: List[Dict[str, str]] = []


class SaveStateRequest(BaseModel):
    dataset_id: str
    state_name: str
    analysis_data: Dict[str, Any]
    chat_history: List[Dict[str, str]] = []


class LoadStateRequest(BaseModel):
    state_id: str
