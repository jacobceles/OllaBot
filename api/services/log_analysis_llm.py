"""
Log Analysis LLM services for OllaBot.

This module provides functions to extract error messages from log data and generate summaries
with potential fixes.
"""

import re

import yaml
from llama_index.core import Document, Settings, SummaryIndex
from llama_index.core.node_parser.text.token import TokenTextSplitter
from llama_index.embeddings.ollama import OllamaEmbedding  # type: ignore
from llama_index.llms.ollama import Ollama  # type: ignore

from utils.logging_config import logger

# Load configuration from YAML
with open("api/configs/config.yaml") as file:
    config = yaml.safe_load(file)
SUMMARY_MODEL_NAME: str = config["models"]["summarize_errors"]["summary_model"]
EMBEDDING_MODEL: str = config["models"]["summarize_errors"]["embedding_model"]


def extract_errors(logs: str) -> str:
    """
    Extract error messages from the logs.

    Args:
        logs (str): The Spark log data as a string.

    Returns:
        str: Extracted error logs or a message indicating no critical errors were found.
    """
    match = re.search(r"- ERROR - (.*)", logs, re.DOTALL)
    extracted: str = match.group(1).strip() if match else "No critical errors found."
    logger.info("Extracted errors from logs.")
    return extracted


def summarize_errors(logs: str) -> str:
    """
    Process the extracted error logs, split them into chunks, and generate a summary with potential fixes.

    Args:
        logs (str): The raw log data.

    Returns:
        str: Summary of errors and potential fixes.
    """
    error_logs: str = extract_errors(logs)
    if error_logs == "No critical errors found.":
        logger.info("No critical errors found in logs.")
        return error_logs

    # Configure LLM and embeddings
    llm = Ollama(model=SUMMARY_MODEL_NAME)
    Settings.embed_model = OllamaEmbedding(model_name=EMBEDDING_MODEL)

    # Split text into manageable chunks
    text_splitter = TokenTextSplitter(chunk_size=100, chunk_overlap=20)
    chunks: list[str] = text_splitter.split_text(error_logs)

    # Create Document objects from the chunks
    documents = [Document(text=chunk) for chunk in chunks]
    logger.info("Created %d document chunks for log analysis.", len(documents))

    # Build a summary index from the documents
    summary_index = SummaryIndex.from_documents(documents)

    # Define query prompt for summarization
    query_prompt: str = "Provide a concise summary of the following error logs and propose potential fixes for the observed issues:"

    # Query the index to generate a summary
    result = summary_index.as_query_engine(llm=llm).query(query_prompt)
    logger.info("Generated log summary.")
    return str(result)
