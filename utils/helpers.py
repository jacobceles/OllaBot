"""
Helper utility functions to streamline repetitive operations in OllaBot.
"""

import requests
import argparse
import streamlit as st
from utils.logging_config import logger
from utils.constants import LOCAL_API_URL, CONTAINER_API_URL, LOCAL_TIMEOUT, CONTAINER_TIMEOUT

def get_execution_mode() -> tuple[bool, str, int]:
    """
    Determines if the application is running locally or in a container.

    Returns:
        tuple: (is_local, API_URL, ANALYSIS_TIMEOUT)
    """
    parser = argparse.ArgumentParser(description="Run Streamlit app.")
    parser.add_argument("--local", action="store_true", help="Run in local mode")
    args, _ = parser.parse_known_args()

    if args.local:
        logger.info("Running in local mode...")
        return True, LOCAL_API_URL, LOCAL_TIMEOUT
    return False, CONTAINER_API_URL, CONTAINER_TIMEOUT


def make_api_request(endpoint: str, payload: dict, timeout: int) -> dict:
    """
    Makes a POST request to the API and handles errors gracefully.

    Args:
        endpoint (str): The API endpoint.
        payload (dict): The JSON payload to send.
        timeout (int): Timeout duration for the request.

    Returns:
        dict: JSON response or an error message.
    """
    try:
        response = requests.post(endpoint, json=payload, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error("API request failed: %s", e)
        return {"error": str(e)}


def initialize_session_state(keys: list[str]) -> None:
    """
    Initializes session state variables if they are not already set.

    Args:
        keys (list[str]): List of session state keys to initialize.
    """
    for key in keys:
        if key not in st.session_state:
            st.session_state[key] = False
