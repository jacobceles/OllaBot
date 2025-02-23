"""
Database LLM services for OllaBot.

This module provides functions to create database engines, generate SQL queries
from natural language questions, execute queries, and synthesize responses.
"""

import os
import re
import yaml
from typing import Any, Optional
from api.models.classes import CustomAccumulate
from llama_index.core import SQLDatabase, Settings
from llama_index.core.indices.struct_store.sql_query import SQLTableRetrieverQueryEngine
from llama_index.core.objects import SQLTableNodeMapping, ObjectIndex, SQLTableSchema
from llama_index.llms.ollama import Ollama  # type: ignore
from llama_index.embeddings.ollama import OllamaEmbedding  # type: ignore
from sqlalchemy import create_engine, text  # type: ignore
from sqlalchemy.engine import Engine  # type: ignore
from sqlalchemy.exc import SQLAlchemyError  # type: ignore
from utils.logging_config import logger


# Load configuration from YAML
with open("api/configs/config.yaml") as file:
    config = yaml.safe_load(file)
QUERY_MODEL_NAME: str = config["models"]["database_query"]["query_model"]
SUMMARY_MODEL_NAME: str = config["models"]["database_query"]["summary_model"]
EMBEDDING_MODEL: str = config["models"]["database_query"]["embedding_model"]


def load_table_config(db_type: str) -> list[dict[str, str]]:
    """
    Load table configurations from the table_config.yaml file.

    Args:
        db_type (str): The type of database (e.g., "postgres").

    Returns:
        list[dict[str, str]]: list of table configuration dictionaries.
    """
    try:
        with open("api/configs/table_config.yaml") as file:
            config_data: dict[str, dict[str, list[dict[str, str]]]] = yaml.safe_load(file)
        tables = config_data.get(db_type, {}).get("tables", [])
        logger.info("Loaded table configuration for db_type: %s", db_type)
        return tables
    except Exception as e:
        logger.exception("Error loading table configuration: %s", e)
        return []


def get_db_config(db_type: str) -> Optional[dict[str, Optional[str]]]:
    """
    Retrieve database connection details based on the database type.

    Args:
        db_type (str): The type of database.

    Returns:
        Optional[dict[str, Optional[str]]]: Database configuration dictionary or None if not found.
    """
    db_type = db_type.lower()
    if db_type == "postgres":
        config_data = {
            "user": os.getenv("POSTGRES_USER"),
            "password": os.getenv("POSTGRES_PASSWORD"),
            "host": os.getenv("POSTGRES_HOST"),
            "port": os.getenv("POSTGRES_PORT"),
            "db": os.getenv("POSTGRES_DB"),
            "schema": os.getenv("POSTGRES_SCHEMA"),
            "dialect": "postgresql",
        }
        logger.info("Retrieved Postgres configuration.")
        return config_data
    logger.error("Unsupported db_type: %s", db_type)
    return None


def create_db_engine(db_type: str) -> Optional[Engine]:
    """
    Create and return the SQLAlchemy engine for the given database type.

    Args:
        db_type (str): The type of database.

    Returns:
        Optional[Engine]: SQLAlchemy engine instance or None if configuration is missing.
    """
    config_data: Optional[dict[str, Optional[str]]] = get_db_config(db_type)
    if not config_data:
        logger.error("No configuration found for db_type: %s", db_type)
        return None
    try:
        engine: Engine = create_engine(
            f"{config_data['dialect']}://{config_data['user']}:{config_data['password']}@"
            f"{config_data['host']}:{config_data['port']}/{config_data['db']}",
            connect_args={"options": f"-c search_path={config_data['schema']}"},
        )
        logger.info("Created database engine for db_type: %s", db_type)
        return engine
    except Exception as e:
        logger.exception("Error creating database engine: %s", e)
        return None


def create_query_engine(engine: Engine, db_type: str) -> tuple[SQLTableRetrieverQueryEngine, CustomAccumulate]:
    """
    Set up the SQL query engine and response synthesizer.

    Args:
        engine (Engine): SQLAlchemy engine instance.
        db_type (str): The type of database.

    Returns:
        tuple[SQLTableRetrieverQueryEngine, CustomAccumulate]: Query engine and synthesizer.
    """
    sql_database = SQLDatabase(engine)

    # Setup for SQL generation
    sql_llm = Ollama(model=QUERY_MODEL_NAME, request_timeout=60.0)
    Settings.embed_model = OllamaEmbedding(model_name=EMBEDDING_MODEL)

    # Setup for summary generation
    summary_llm = Ollama(model=SUMMARY_MODEL_NAME, request_timeout=60.0)
    accumulate_synthesizer = CustomAccumulate(llm=summary_llm)

    # Load table schema from configuration
    tables = load_table_config(db_type)
    table_schemas = [
        SQLTableSchema(table_name=t["table_name"], context_str=t["context"]) for t in tables
    ]

    # Create table mappings and object index
    table_node_mapping = SQLTableNodeMapping(sql_database)
    obj_index = ObjectIndex.from_objects(table_schemas, table_node_mapping)

    # Create SQL query engine
    query_engine = SQLTableRetrieverQueryEngine(
        sql_database=sql_database,
        table_retriever=obj_index.as_retriever(similarity_top_k=1),
        rows_retrievers=None,
        llm=sql_llm,
        synthesize_response=False,
        sql_only=True
    )
    logger.info("Created query engine for db_type: %s", db_type)
    return query_engine, accumulate_synthesizer


def validate_sql_query(sql_query: str) -> bool:
    """
    Validate the SQL query to prevent SQL injection.

    This is a basic implementation; consider using more robust solutions.

    Args:
        sql_query (str): The SQL query to validate.

    Returns:
        bool: True if the SQL query is safe, False otherwise.
    """
    prohibited_patterns = [
        r"xp_",  # Disallow SQL Server extended procedures
        r"drop\s+table",  # Disallow DROP TABLE statements
    ]
    for pattern in prohibited_patterns:
        if re.search(pattern, sql_query, re.IGNORECASE):
            logger.warning("SQL query validation failed for pattern: %s", pattern)
            return False
    return True


def clean_sql_query(sql_query: str) -> str:
    """
    Extract and return only the SQL query from a given text.

    Args:
        sql_query (str): The input text containing an SQL query and possibly extra text.

    Returns:
        str: The cleaned SQL query.
    """
    match = re.search(r"^(.*?;)", sql_query, re.DOTALL)
    cleaned_query = match.group(1).strip() if match else sql_query.strip()
    logger.info("Cleaned SQL query: %s", cleaned_query)
    return cleaned_query


def execute_custom_query(engine: Engine, sql_query: str) -> Any:
    """
    Execute the SQL query using SQLAlchemy and return the results.

    Args:
        engine (Engine): SQLAlchemy engine instance.
        sql_query (str): The SQL query to execute.

    Returns:
        Any: Query results or None if execution fails.
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text(sql_query))
            results = result.fetchall()
            logger.info("Executed SQL query successfully.")
            return results
    except SQLAlchemyError as e:
        logger.exception("SQL execution error: %s", e)
        return None


def execute_query(engine: Engine, query_engine: SQLTableRetrieverQueryEngine, 
                  synthesizer: CustomAccumulate, query: str) -> tuple[str, str]:
    """
    Generate SQL from a natural language query, validate, execute, and summarize the results.

    Args:
        engine (Engine): SQLAlchemy engine instance.
        query_engine (SQLTableRetrieverQueryEngine): Query engine for SQL generation.
        synthesizer (CustomAccumulate): Response synthesizer for generating summaries.
        query (str): The user's natural language query.

    Returns:
        tuple[str, str]: A tuple containing the summary response and the generated SQL query.
    """
    # Generate SQL query from natural language input
    sql_response = query_engine.query(query)
    generated_sql_query: str = ""
    if hasattr(sql_response, "metadata") and sql_response.metadata:
        generated_sql_query = sql_response.metadata.get("sql_query", "")

    if not generated_sql_query:
        logger.error("No SQL query generated for query: %s", query)
        return "No SQL query generated.", ""

    # Validate the generated SQL query
    if not validate_sql_query(generated_sql_query):
        logger.error("Generated SQL query is unsafe: %s", generated_sql_query)
        return "Generated SQL query is potentially unsafe and was not executed.", generated_sql_query

    # Clean the generated SQL query
    generated_sql_query = clean_sql_query(generated_sql_query)
    
    # Execute the validated SQL query
    query_results = execute_custom_query(engine, generated_sql_query)
    if query_results is None:
        logger.error("Error executing SQL query: %s", generated_sql_query)
        return "Error executing SQL query.", generated_sql_query

    # Generate a natural language summary of the query results
    formatted_results = [str(row) for row in query_results]
    summary_response = synthesizer.get_response(query_str=query, text_chunks=[str(formatted_results)])
    logger.info("Generated summary response for query: %s", query)
    return str(summary_response).strip(), generated_sql_query
