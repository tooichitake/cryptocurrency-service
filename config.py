"""
Configuration file for Streamlit app
Update the FastAPI URLs with your deployed endpoints
"""

# FastAPI endpoints for each student's model
FASTAPI_ENDPOINTS = {
    "bitcoin": {
        "url": "http://localhost:8000",  # Update with your deployed URL
        "student": "Student 1",
        "model": "Linear Regression"
    },
    "ethereum": {
        "url": "http://localhost:8001",  # Update with your deployed URL
        "student": "Student 2",
        "model": "XGBoost"  # Example
    },
    "xrp": {
        "url": "http://localhost:8002",  # Update with your deployed URL
        "student": "Student 3",
        "model": "LightGBM"  # Example
    },
    "solana": {
        "url": "http://localhost:8003",  # Update with your deployed URL
        "student": "Student 4",
        "model": "Random Forest"  # Example
    }
}

# API configuration
API_TIMEOUT = 15  # seconds
CACHE_TTL = 300  # 5 minutes in seconds

# Data fetch configuration
DEFAULT_DAYS = 365
MAX_DAYS = 730
