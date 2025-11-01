"""
Server Entry Point
Imports from modular app structure
"""
from app.main import app

# This maintains backward compatibility with:
# python server.py
# uvicorn server:app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )
