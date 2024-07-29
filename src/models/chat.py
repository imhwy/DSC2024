"""
This module defines a data model for handling chat domain data using Pydantic.
"""

from pydantic import BaseModel


class ChatDomain(BaseModel):
    """
    A Pydantic model representing a chat domain entry.

    Attributes:
        Id (str): A unique identifier for the chat entry.
        query (str): The user's query or question.
        answer (str): The response generated for the query.
        time (str): The timestamp of when the query was processed.
        is_outdomain (bool): A flag indicating whether the query is outside 
                             the expected domain of questions.
    """
    Id: str
    query: str
    answer: str
    time: str
    is_outdomain: bool
