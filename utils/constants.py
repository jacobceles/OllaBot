"""
Defines global constants used across the application.
"""

# API URL defaults for local and container environments
LOCAL_API_URL = "http://127.0.0.1:8000"
CONTAINER_API_URL = "http://fastapi:8000"

# API URL defaults for local and container environments
LOCAL_OLLAMA_URL = "http://localhost:11434"
CONTAINER_OLLAMA_URL = "http://ollama-service:11434"

# API request timeout settings
LOCAL_TIMEOUT = 120
CONTAINER_TIMEOUT = 600

