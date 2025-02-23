"""
Pydantic models and custom classes for OllaBot.

This module includes:
- QueryRequest: Model for SQL query requests.
- LogRequest: Model for log analysis requests.
- CustomAccumulate: Modified response synthesizer for concatenating outputs.
"""

from pydantic import BaseModel
from llama_index.core.response_synthesizers import Accumulate


class QueryRequest(BaseModel):
    """
    Pydantic model to validate incoming request data for SQL queries.

    Attributes:
        db_type (str): The type of database (e.g., "postgres").
        question (str): The user's natural language question.
    """
    db_type: str
    question: str


class LogRequest(BaseModel):
    """
    Pydantic model for log analysis request body.

    Attributes:
        logs (str): The error logs to analyze.
    """
    logs: str


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
