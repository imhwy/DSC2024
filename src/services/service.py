"""
This module provides services for handling LLM and embedding models using OpenAI's API
"""

import os
from dotenv import load_dotenv
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Settings

from src.repositories.weaviatedb import WeaviateDB
from src.engine.retriever_module import HybridRetriever
from src.engine.chat_module import ChatEngine
from src.services.retrieve_chat import RetrieveChat

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL')
OPENAI_EMBED_MODEL = os.getenv('OPENAI_EMBED_MODEL')
TEMPERATURE_MODEL = os.getenv('TEMPERATURE_MODEL')


class Service:
    """
    A service class that sets up and manages LLM and embedding models using OpenAI
    """

    def __init__(
        self,
        openai_api_key: str = OPENAI_API_KEY,
        openai_api_model: str = OPENAI_MODEL,
        openai_api_embed_model: str = OPENAI_EMBED_MODEL,
        temperature_model: str = TEMPERATURE_MODEL
    ):
        """
        Initializes the Service class with LLM and embedding models.
        """
        self._llm = OpenAI(
            api_key=openai_api_key,
            model=openai_api_model,
            temperature=temperature_model
        )
        self._embed_model = OpenAIEmbedding(
            api_key=openai_api_key,
            model=openai_api_embed_model
        )
        Settings.llm = self._llm
        Settings.embed_model = self._embed_model
        self._vector_database = WeaviateDB()
        self._retriever = HybridRetriever(
            index=self._vector_database.index
        )
        self._chat_engine = ChatEngine(
            language_model=self._llm
        )
        self._retrieve_chat_engine = RetrieveChat(
            retriever=self._retriever,
            chat=self._chat_engine
        )

    @property
    def vector_database(self) -> WeaviateDB:
        """
        Retrieves the vector database instance.

        Returns:
            WeaviateDB: The initialized vector database object.
        """
        return self._vector_database

    @property
    def llm(self) -> OpenAI:
        """
        Retrieves the LLM instance.

        Returns:
            OpenAI: The initialized LLM object.
        """
        return self._llm

    @property
    def embed_model(self) -> OpenAIEmbedding:
        """
        Retrieves the embedding model instance.

        Returns:
            OpenAIEmbedding: The initialized embedding model object.
        """
        return self._embed_model

    @property
    def retriever(self) -> HybridRetriever:
        """
        Retrieves the HybridRetriever instance.

        Returns:
            HybridRetriever: The initialized HybridRetriever object.
        """
        return self._retriever

    @property
    def chat_engine(self) -> ChatEngine:
        """
        Retrieves the ChatEngine instance.

        Returns:
            ChatEngine: The initialized ChatEngine object.
        """
        return self._chat_engine

    @property
    def retrieve_chat_engine(self) -> RetrieveChat:
        """
        Retrieves the RetrieveChat instance.

        Returns:
            RetrieveChat: The initialized RetrieveChat object.
        """
        return self._retrieve_chat_engine
