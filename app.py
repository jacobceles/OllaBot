"""
Main Streamlit application for OllaBot.

Features:
1. Ask me! - Converts natural language questions into SQL queries.
2. Analyze Logs - Provides log analysis and error summaries.
"""

import streamlit as st
from utils.logging_config import logger
from utils.helpers import get_execution_mode, make_api_request, initialize_session_state

# Determine execution mode (local vs. container)
IS_LOCAL, API_URL, ANALYSIS_TIMEOUT = get_execution_mode()

# Set the page title and layout
st.set_page_config(page_title="OllaBot", layout="wide")
st.title("OllaBot")

# Sidebar navigation
menu = st.sidebar.radio("Select Feature", ["Ask me!", "Analyze Logs"])

# Initialize session state variables
initialize_session_state(["query_submitted", "response_ready", "log_submitted", "log_response_ready"])

if menu == "Ask me!":
    st.sidebar.header("Database Configuration")
    db_type = st.sidebar.selectbox("Select Database Type", ["postgres"])

    query_disabled = st.session_state.query_submitted and not st.session_state.response_ready
    query = st.text_area("Enter your question:", disabled=query_disabled)

    if st.button("Ask me!", disabled=query_disabled):
        if query and db_type:
            st.session_state.query_submitted = True
            logger.info("Processing query: %s for db_type: %s", query, db_type)

            with st.spinner("Generating SQL query..."):
                response = make_api_request(f"{API_URL}/execute_query/", {"db_type": db_type, "question": query}, ANALYSIS_TIMEOUT)

                if "error" in response:
                    st.error(f"Error: {response['error']}")
                else:
                    st.session_state.response_ready = True
                    st.subheader("Executed SQL Query:")
                    st.code(response.get("sql_query", ""), language="sql")

                    st.subheader("Summary:")
                    st.write(response.get("response", ""))

                    logger.info("Query execution completed successfully.")

            # Reset session state
            st.session_state.query_submitted = False
            st.session_state.response_ready = False
        else:
            st.warning("Please enter a query before submitting.")

elif menu == "Analyze Logs":
    st.subheader("Log Analysis & Error Summarization")
    log_disabled = st.session_state.log_submitted and not st.session_state.log_response_ready
    log_input = st.text_area("Paste log data here:", disabled=log_disabled, height=200)

    if st.button("Analyze Logs", disabled=log_disabled):
        if log_input:
            st.session_state.log_submitted = True
            logger.info("Processing log analysis request.")

            with st.spinner("Analyzing logs..."):
                response = make_api_request(f"{API_URL}/analyze_logs/", {"logs": log_input}, ANALYSIS_TIMEOUT)

                if "error" in response:
                    st.error(f"Error: {response['error']}")
                else:
                    st.session_state.log_response_ready = True
                    st.subheader("Error Summary & Fix Suggestions:")
                    st.write(response.get("summary", ""))
                    logger.info("Log analysis completed successfully.")

            # Reset session state
            st.session_state.log_submitted = False
            st.session_state.log_response_ready = False
        else:
            st.warning("Please paste log data before analyzing.")
