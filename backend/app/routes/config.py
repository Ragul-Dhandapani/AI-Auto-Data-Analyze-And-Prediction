"""
Database Configuration Routes
Temporary endpoints for switching databases via UI
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
import os
import logging

router = APIRouter(prefix="/config", tags=["Configuration"])
logger = logging.getLogger(__name__)

# Standardized .env path
ROOT_DIR = Path(__file__).parent.parent.parent
ENV_PATH = ROOT_DIR / '.env'

class DatabaseSwitchRequest(BaseModel):
    db_type: str  # 'mongodb' or 'oracle'

@router.get("/current-database")
async def get_current_database():
    """Get currently active database type - reads from .env file"""
    try:
        # Read directly from .env file to get current setting
        db_type = 'mongodb'  # default
        
        with open(ENV_PATH, 'r') as f:
            for line in f:
                if line.startswith('DB_TYPE='):
                    db_type = line.split('=')[1].strip().strip('"')
                    break
        
        return {
            "current_database": db_type,
            "available_databases": ["mongodb", "oracle"],
            "note": "Switching requires backend restart"
        }
    except Exception as e:
        logger.error(f"Failed to read DB_TYPE: {str(e)}")
        # Fallback to environment variable
        db_type = os.getenv('DB_TYPE', 'mongodb')
        return {
            "current_database": db_type,
            "available_databases": ["mongodb", "oracle"],
            "note": "Switching requires backend restart"
        }

@router.post("/switch-database")
async def switch_database(request: DatabaseSwitchRequest):
    """
    Switch database type (TEMPORARY ENDPOINT - FOR TESTING)
    This endpoint will be removed in production
    """
    try:
        db_type = request.db_type.lower()
        
        if db_type not in ['mongodb', 'oracle']:
            raise HTTPException(400, "Invalid database type. Must be 'mongodb' or 'oracle'")
        
        # Read current .env file
        with open(ENV_PATH, 'r') as f:
            lines = f.readlines()
        
        # Update DB_TYPE line
        updated_lines = []
        found = False
        for line in lines:
            if line.startswith('DB_TYPE='):
                updated_lines.append(f'DB_TYPE="{db_type}"\n')
                found = True
            else:
                updated_lines.append(line)
        
        # If DB_TYPE not found, add it at the beginning
        if not found:
            updated_lines.insert(0, f'DB_TYPE="{db_type}"\n')
        
        # Write back to .env
        with open(env_path, 'w') as f:
            f.writelines(updated_lines)
        
        logger.info(f"✅ Database type switched to: {db_type}")
        
        # Trigger background restart using system command
        import subprocess
        subprocess.Popen(
            ['bash', '-c', 'sleep 1 && sudo supervisorctl restart backend'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        
        return {
            "success": True,
            "message": f"Database switched to {db_type}. Backend is restarting...",
            "new_database": db_type,
            "note": "Backend will restart in 1 second. Page may become unresponsive briefly."
        }
        
    except Exception as e:
        logger.error(f"Failed to switch database: {str(e)}")
        raise HTTPException(500, f"Failed to switch database: {str(e)}")

@router.post("/restart-backend")
async def restart_backend():
    """
    Restart backend to apply database changes
    (TEMPORARY ENDPOINT - FOR TESTING)
    """
    try:
        import subprocess
        
        # Restart backend via supervisorctl
        result = subprocess.run(
            ['sudo', 'supervisorctl', 'restart', 'backend'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            return {
                "success": True,
                "message": "Backend restarting...",
                "output": result.stdout,
                "note": "Please wait 5-10 seconds for backend to be ready"
            }
        else:
            raise HTTPException(500, f"Restart failed: {result.stderr}")
    
    except subprocess.TimeoutExpired:
        return {
            "success": True,
            "message": "Restart command issued (timeout reached)",
            "note": "Backend is restarting, please wait 10 seconds"
        }
    except Exception as e:
        logger.error(f"Failed to restart backend: {str(e)}")
        raise HTTPException(500, f"Failed to restart: {str(e)}")
