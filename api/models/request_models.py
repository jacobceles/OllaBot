"""
Pydantic models for validating request payloads.
"""

from pydantic import BaseModel

class QueryRequest(BaseModel):
    """
    Model for SQL query requests.
    
    Attributes:
        db_type (str): The type of database (e.g., "postgres").
        question (str): The user's natural language question.
    """
    db_type: str
    question: str


class LogRequest(BaseModel):
    """
    Model for log analysis requests.
    
    Attributes:
        logs (str): The error logs to analyze.
    """
    logs: str
