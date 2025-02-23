"""
Main Streamlit application for OllaBot.

This app provides two functionalities:
1. Ask me! - Allows users to ask questions in natural language which are converted into SQL queries.
2. Analyze Logs - Allows users to analyze log data and receive error summaries and fix suggestions.
"""

import requests
import streamlit as st
from utils.logging_config import logger


# Set the page title and layout
st.set_page_config(page_title="OllaBot", layout="wide")

# App title
st.title("OllaBot")

# Sidebar navigation for selecting feature
menu: str = st.sidebar.radio("Select Feature", ["Ask me!", "Analyze Logs"])

# API Base URL
API_URL: str = "http://127.0.0.1:8000"

# Initialize session state variables
if "query_submitted" not in st.session_state:
    st.session_state.query_submitted = False
if "response_ready" not in st.session_state:
    st.session_state.response_ready = False
if "log_submitted" not in st.session_state:
    st.session_state.log_submitted = False
if "log_response_ready" not in st.session_state:
    st.session_state.log_response_ready = False

### Option 1: Ask me!
if menu == "Ask me!":
    st.sidebar.header("Database Configuration")
    db_type: str = st.sidebar.selectbox("Select Database Type", ["postgres"])

    query_disabled: bool = st.session_state.query_submitted and not st.session_state.response_ready
    query: str = st.text_area("Enter your question:", disabled=query_disabled)

    submit_button: bool = st.button("Ask me!", disabled=query_disabled)

    if submit_button:
        if query and db_type:
            st.session_state.query_submitted = True  # Disable input during processing
            logger.info("User submitted query: %s for db_type: %s", query, db_type)
            try:
                with st.spinner("Generating SQL query..."):
                    response = requests.post(
                        f"{API_URL}/execute_query/",
                        json={"db_type": db_type, "question": query},
                        timeout=120
                    )
                    response.raise_for_status()  # Raise error for bad HTTP responses
                    data = response.json()
                    st.session_state.response_ready = True  # Mark response as ready

                    st.subheader("Executed SQL Query:")
                    st.code(data.get("sql_query", ""), language="sql")

                    st.subheader("Summary:")
                    st.write(data.get("response", ""))

                    logger.info("Successfully generated SQL query and response.")
            except requests.exceptions.RequestException as e:
                logger.error("Error during API request: %s", e)
                st.error(f"Error: {e}")
            finally:
                # Reset session state after processing
                st.session_state.query_submitted = False
                st.session_state.response_ready = False
        else:
            st.warning("Please enter a query before submitting.")

### Option 2: Analyze Logs
elif menu == "Analyze Logs":
    st.subheader("Log Analysis & Error Summarization")

    log_disabled: bool = st.session_state.log_submitted and not st.session_state.log_response_ready
    log_input: str = st.text_area("Paste log data here:", disabled=log_disabled, height=200)

    analyze_button: bool = st.button("Analyze Logs", disabled=log_disabled)

    if analyze_button:
        if log_input:
            st.session_state.log_submitted = True  # Disable input during processing
            logger.info("User submitted logs for analysis.")
            try:
                with st.spinner("Analyzing logs..."):
                    response = requests.post(
                        f"{API_URL}/analyze_logs/",
                        json={"logs": log_input},
                        timeout=120
                    )
                    response.raise_for_status()
                    data = response.json()
                    st.session_state.log_response_ready = True  # Mark response as ready

                    st.subheader("Error Summary & Fix Suggestions:")
                    st.write(data.get("summary", ""))

                    logger.info("Successfully analyzed logs.")
            except requests.exceptions.RequestException as e:
                logger.error("Error during log analysis request: %s", e)
                st.error(f"Error: {e}")
            finally:
                # Reset session state after processing
                st.session_state.log_submitted = False
                st.session_state.log_response_ready = False
        else:
            st.warning("Please paste log data before analyzing.")
