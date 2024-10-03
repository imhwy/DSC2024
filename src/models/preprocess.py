"""
this model provides a data model for representing a processed data entry
"""

from pydantic import BaseModel


class ProcessedData(BaseModel):
    """
    Represents the processed data of a user's query.

    Attributes:
        query (str): The processed query text.
        language (bool): A flag indicating whether the language is detected
        is_prompt_injection (bool): A flag indicating if the query contains a prompt injection.
        is_outdomain (bool): A flag indicating if the query is outside the expected domain.
    """
    query: str
    language: bool
    is_prompt_injection: bool
    is_outdomain: bool
    is_short_chat: bool
    is_only_icon: bool


class ShortChat(BaseModel):
    """
    """
    query: str
    clean_query: str
    is_short_chat: bool
    short_chat_response: str


class UnsupportedLanguage(BaseModel):
    """
    """
    language: bool
    response: str


class PromptInjection(BaseModel):
    """
    """
    is_prompt_injection: bool
    response: str
