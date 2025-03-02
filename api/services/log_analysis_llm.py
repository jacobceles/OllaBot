"""
Log Analysis LLM services for OllaBot.

Handles:
- Extracting error messages from logs.
- Summarizing errors and suggesting fixes using an LLM.
"""

import re
from transformers import AutoTokenizer # type: ignore
from llama_index.core.node_parser.text.token import TokenTextSplitter
from llama_index.core import Settings, Document, SummaryIndex
from llama_index.embeddings.ollama import OllamaEmbedding # type: ignore
from llama_index.llms.ollama import Ollama # type: ignore
from llama_index.core.callbacks import CallbackManager, TokenCountingHandler
from utils.logging_config import logger
from utils.config import CONFIG, get_ollama_base_url


def extract_errors(logs: str) -> str:
    """
    Extracts error messages from logs.

    Args:
        logs (str): Log data.

    Returns:
        str: Extracted error messages or 'No critical errors found.'
    """
    match = re.search(r"- ERROR - (.*)", logs, re.DOTALL)
    return match.group(1).strip() if match else "No critical errors found."


def summarize_errors(logs: str, is_local: bool) -> str:
    """
    Summarizes errors and suggests fixes.

    Args:
        logs (str): Raw log data.

    Returns:
        str: Summary of errors and fixes.
    """
    errors = extract_errors(logs)
    if errors == "No critical errors found.":
        return errors

    base_url = get_ollama_base_url(is_local)
    llm_model = CONFIG["models"]["summarize_errors"]["summary_model"]
    embedding_model = CONFIG["models"]["database_query"]["embedding_model"]
    llm = Ollama(model=llm_model, base_url=base_url)
    Settings.embed_model = OllamaEmbedding(model_name=embedding_model, request_timeout=120.0)

    tokenizer = AutoTokenizer.from_pretrained("api/services/llama_3.2_tokenizer/")
    token_counter = TokenCountingHandler(tokenizer.encode)
    Settings.callback_manager = CallbackManager([token_counter])

    text_splitter = TokenTextSplitter(chunk_size=100, chunk_overlap=20)
    documents = [Document(text=chunk) for chunk in text_splitter.split_text(errors)]

    summary_index = SummaryIndex.from_documents(documents)
    summary = summary_index.as_query_engine(llm=llm).query("Summarize the errors and suggest fixes.")

    logger.info("LLM Token Usage: %s", token_counter.total_llm_token_count)
    
    return str(summary)
