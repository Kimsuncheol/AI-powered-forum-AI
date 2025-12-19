"""
AI-Powered Forum API - Entry Point

Run with: uvicorn main:app --reload
Or: python main.py
"""

import uvicorn

# Import app from the app package
from app.main import app  # noqa: F401

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
