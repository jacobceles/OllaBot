"""
Database LLM services for OllaBot.

Handles:
- Creating database engines.
- Generating SQL queries from natural language.
- Validating and executing SQL queries.
- Synthesizing natural language responses for query results.
"""

import re
from typing import Optional
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from llama_index.core import SQLDatabase, Settings
from llama_index.core.response_synthesizers import Accumulate
from llama_index.core.indices.struct_store.sql_query import SQLTableRetrieverQueryEngine
from llama_index.core.objects import ObjectIndex, SQLTableNodeMapping, SQLTableSchema
from llama_index.embeddings.ollama import OllamaEmbedding # type: ignore
from llama_index.llms.ollama import Ollama # type: ignore

from utils.logging_config import logger
from utils.config import CONFIG, TABLE_CONFIG, get_ollama_base_url


class CustomAccumulate(Accumulate):
    """
    A modified response synthesizer that concatenates outputs without adding labels.

    Methods:
        _format_response(outputs, separator): Joins response outputs.
    """

    def _format_response(self, outputs: list[str], separator: str) -> str:
        """
        Joins response outputs into a single string using the provided separator.

        Args:
            outputs (list[str]): List of response strings.
            separator (str): Separator for concatenation.

        Returns:
            str: Concatenated response string.
        """
        return separator.join(outputs)


def create_db_engine(db_type: str) -> Optional[Engine]:
    """
    Creates a database engine using SQLAlchemy.

    Args:
        db_type (str): Type of database (e.g., "postgres").

    Returns:
        Optional[Engine]: SQLAlchemy engine if successful, None otherwise.
    """
    db_config = CONFIG.get(db_type, {})
    if not db_config:
        logger.error("No database configuration found for %s", db_type)
        return None

    try:
        engine = create_engine(
            f"{db_config['dialect']}://{db_config['user']}:{db_config['password']}@"
            f"{db_config['host']}:{db_config['port']}/{db_config['db']}",
            connect_args={"options": f"-c search_path={db_config['schema']}"},
        )
        logger.info("Database engine created for %s", db_type)
        return engine
    except Exception as e:
        logger.exception("Failed to create database engine: %s", e)
        return None


def create_query_engine(engine: Engine, db_type: str, is_local: bool) -> tuple[SQLTableRetrieverQueryEngine, CustomAccumulate]:
    """
    Creates an SQL query engine and response synthesizer.

    Args:
        engine (Engine): SQLAlchemy engine instance.
        db_type (str): Database type.
        is_local (bool): Whether running in local mode.

    Returns:
        Tuple[SQLTableRetrieverQueryEngine, CustomAccumulate]: Query engine and response synthesizer.
    """
    QUERY_MODEL_NAME = CONFIG["models"]["database_query"]["query_model"]
    SUMMARY_MODEL_NAME = CONFIG["models"]["database_query"]["summary_model"]
    EMBEDDING_MODEL = CONFIG["models"]["database_query"]["embedding_model"]

    sql_database = SQLDatabase(engine)
    
    # Configure LLM models
    base_url = get_ollama_base_url(is_local)
    sql_llm = Ollama(model=QUERY_MODEL_NAME, request_timeout=600.0, base_url=base_url)
    Settings.embed_model = OllamaEmbedding(model_name=EMBEDDING_MODEL, request_timeout=600.0, base_url=base_url)
    summary_llm = Ollama(model=SUMMARY_MODEL_NAME, request_timeout=600.0, base_url=base_url)

    accumulate_synthesizer = CustomAccumulate(llm=summary_llm)

    # Load table configurations
    tables = TABLE_CONFIG.get(db_type, {}).get("tables", [])
    table_schemas = [SQLTableSchema(table_name=t["table_name"], context_str=t["context"]) for t in tables]

    table_node_mapping = SQLTableNodeMapping(sql_database)
    obj_index = ObjectIndex.from_objects(table_schemas, table_node_mapping)

    query_engine = SQLTableRetrieverQueryEngine(
        sql_database=sql_database,
        table_retriever=obj_index.as_retriever(similarity_top_k=1),
        rows_retrievers=None,
        llm=sql_llm,
        synthesize_response=False,
        sql_only=True
    )

    logger.info("Created SQL query engine for %s", db_type)
    return query_engine, accumulate_synthesizer


def validate_sql_query(sql_query: str) -> bool:
    """
    Validates an SQL query to prevent SQL injection.

    Args:
        sql_query (str): The SQL query.

    Returns:
        bool: True if the query is safe, False otherwise.
    """
    if re.search(r"xp_|drop\s+table", sql_query, re.IGNORECASE):
        logger.warning("SQL query validation failed: %s", sql_query)
        return False
    return True


def clean_sql_query(sql_query: str) -> str:
    """
    Extracts the actual SQL query from a response, removing any extra text.

    Args:
        sql_query (str): The raw SQL response.

    Returns:
        str: Cleaned SQL query.
    """
    match = re.search(r"^(.*?;)", sql_query, re.DOTALL)
    cleaned_query = match.group(1).strip() if match else sql_query.strip()
    logger.info("Cleaned SQL query: %s", cleaned_query)
    return cleaned_query


def execute_query(engine: Engine, query_engine: SQLTableRetrieverQueryEngine, synthesizer: CustomAccumulate, query: str) -> tuple[str, str]:
    """
    Generates, validates, executes an SQL query, and returns a summary.

    Args:
        engine (Engine): SQLAlchemy engine.
        query_engine (SQLTableRetrieverQueryEngine): Query engine.
        synthesizer (CustomAccumulate): Response synthesizer.
        query (str): User's natural language query.

    Returns:
        Tuple[str, str]: (Generated SQL query, Summary response)
    """
    sql_response = query_engine.query(query)
    if hasattr(sql_response, "metadata") and sql_response.metadata:
        generated_sql_query = sql_response.metadata.get("sql_query", "") if hasattr(sql_response, "metadata") else ""

    if not generated_sql_query:
        logger.error("No SQL query generated for: %s", query)
        return "", "No SQL query generated."

    generated_sql_query = clean_sql_query(generated_sql_query)

    if not validate_sql_query(generated_sql_query):
        logger.error("Unsafe SQL query: %s", generated_sql_query)
        return generated_sql_query, "Generated SQL query is potentially unsafe."

    try:
        with engine.connect() as connection:
            result = connection.execute(text(generated_sql_query))
            rows = result.fetchall()
            summary_response = synthesizer.get_response(query_str=query, text_chunks=[str(rows)])
            return generated_sql_query, str(summary_response).strip()
    except SQLAlchemyError as e:
        logger.error("SQL execution failed: %s", e)
        return generated_sql_query, "SQL execution failed."
