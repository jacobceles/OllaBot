"""
Centralized configuration management for OllaBot.

This module loads configurations from YAML files and provides helper functions
to access different settings dynamically.
"""

import os
import yaml
from utils.logging_config import logger
from utils.constants import LOCAL_OLLAMA_URL, CONTAINER_OLLAMA_URL


# Load configuration from YAML files
def load_yaml_config(file_path: str) -> dict:
    """Load a YAML configuration file and return its contents."""
    try:
        with open(file_path) as file:
            return yaml.safe_load(file)
    except Exception as e:
        logger.error("Failed to load config file %s: %s", file_path, e)
        return {}

# Load main and table configurations
CONFIG = load_yaml_config("api/configs/config.yaml")
TABLE_CONFIG = load_yaml_config("api/configs/table_config.yaml")


# Load database settings dynamically
def get_db_config(db_type: str) -> dict:
    """Retrieve database connection details from environment variables."""
    db_type = db_type.lower()
    if db_type == "postgres":
        return {
            "user": os.getenv("POSTGRES_USER"),
            "password": os.getenv("POSTGRES_PASSWORD"),
            "host": os.getenv("POSTGRES_HOST"),
            "port": os.getenv("POSTGRES_PORT"),
            "db": os.getenv("POSTGRES_DB"),
            "schema": os.getenv("POSTGRES_SCHEMA"),
            "dialect": "postgresql",
        }
    logger.error("Unsupported db_type: %s", db_type)
    return {}


# Get base URL for Ollama service
def get_ollama_base_url(is_local: bool) -> str:
    """
    Determines the correct base URL for the Ollama service.

    Args:
        is_local (bool): Whether the application is running in local mode.

    Returns:
        str: The correct base URL.
    """
    return LOCAL_OLLAMA_URL if is_local else CONTAINER_OLLAMA_URL