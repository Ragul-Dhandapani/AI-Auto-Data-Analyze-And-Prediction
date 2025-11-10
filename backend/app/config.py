"""
Configuration and Environment Settings
"""
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent.parent
print("ROOT_DIR from config.py which loads the .env file:",ROOT_DIR)
load_dotenv(ROOT_DIR / '.env')

# MongoDB Configuration
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'autopredict_db')

# API Configuration
API_PREFIX = "/api"
CORS_ORIGINS = ["*"]  # Configure based on environment

# File Upload Configuration
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
GRIDFS_THRESHOLD = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = ['.csv', '.xlsx', '.xls']

# ML Configuration
TRAIN_TEST_SPLIT_RATIO = 0.2
RANDOM_STATE = 42

# LLM Configuration
LLM_PROVIDER = os.environ.get('LLM_PROVIDER', 'emergent')
LLM_MODEL = os.environ.get('LLM_MODEL', 'gpt-4')

# Logging Configuration
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
