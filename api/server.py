"""
FastAPI server for OllaBot.

This server provides endpoints to:
- Execute SQL queries based on natural language questions.
- Analyze log data and provide error summaries and suggested fixes.
"""

from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from api.models.classes import LogRequest, QueryRequest
from api.services.database_llm import create_db_engine, create_query_engine, execute_query
from api.services.log_analysis_llm import summarize_errors
from utils.logging_config import logger

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Dictionary to store database engines to avoid redundant connections
db_engines: dict[str, Any] = {}


@app.post("/execute_query/", response_model=dict[str, str])
async def execute_sql_query(request: QueryRequest) -> dict[str, str]:
    """
    API endpoint to process user queries and return the SQL statement and response.

    Args:
        request (QueryRequest): Contains the database type and user query.

    Returns:
        dict[str, str]: A dictionary containing the generated SQL query and its response.

    Raises:
        HTTPException: If database connection fails or an error occurs during query execution.
    """
    logger.info("Received execute_query request with db_type: %s", request.db_type)
    db_type: str = request.db_type
    question: str = request.question

    # Create or reuse the database engine
    if db_type not in db_engines:
        engine = create_db_engine(db_type)
        if not engine:
            logger.error("Failed to connect to the database for db_type: %s", db_type)
            raise HTTPException(status_code=500, detail="Failed to connect to the database")
        db_engines[db_type] = engine
        logger.info("Created new database engine for db_type: %s", db_type)
    else:
        engine = db_engines[db_type]
        logger.info("Using cached database engine for db_type: %s", db_type)

    # Create query engine and response synthesizer
    query_engine, synthesizer = create_query_engine(engine, db_type)

    try:
        # Execute query and return both SQL and its natural language summary
        response_text, sql_query = execute_query(engine, query_engine, synthesizer, question)
        logger.info("Executed query successfully for question: %s", question)
        return {"sql_query": sql_query, "response": response_text}
    except Exception as e:
        logger.exception("Error executing SQL query for question: %s", question)
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/analyze_logs/", response_model=dict[str, str])
async def analyze_logs(request: LogRequest) -> dict[str, str]:
    """
    API endpoint to analyze Spark logs, extract errors, and summarize them.

    Args:
        request (LogRequest): Request body containing the log data.

    Returns:
        dict[str, str]: JSON containing the error summary and possible fixes.

    Raises:
        HTTPException: If an error occurs during log analysis.
    """
    logger.info("Received log analysis request.")
    try:
        summary: str = summarize_errors(request.logs)
        logger.info("Log analysis completed successfully.")
        return {"summary": summary}
    except Exception as e:
        logger.exception("Error analyzing logs.")
        raise HTTPException(status_code=500, detail=str(e)) from e
