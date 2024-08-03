"""
This module provides services for handling LLM and embedding models using OpenAI's API
"""

import os
from dotenv import load_dotenv
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Settings

from src.storage.weaviatedb import WeaviateDB
from src.engines.retriever_engine import HybridRetriever
from src.engines.chat_engine import ChatEngine
from src.services.retrieve_chat import RetrieveChat
from src.utils.utility import convert_value
from src.repositories.chat_repository import ChatRepository
from src.repositories.file_repository import FileRepository
from src.data_loader.general_loader import GeneralLoader
from src.services.file_management import FileManagement

load_dotenv()

OPENAI_API_KEY = convert_value(os.getenv('OPENAI_API_KEY'))
OPENAI_MODEL = convert_value(os.getenv('OPENAI_MODEL'))
OPENAI_EMBED_MODEL = convert_value(os.getenv('OPENAI_EMBED_MODEL'))
TEMPERATURE_MODEL = convert_value(os.getenv('TEMPERATURE_MODEL'))


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
        self._chat_repository = ChatRepository()
        self._file_repository = FileRepository()
        self._general_loader = GeneralLoader()
        self._file_management = FileManagement(
            file_repository=self._file_repository,
            general_loader=self._general_loader,
            vector_database=self._vector_database
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

    @property
    def chat_repository(self) -> ChatRepository:
        """
        Retrieves the ChatRepository instance.

        Returns:
            ChatRepository: The initialized ChatRepository object.
        """
        return self._chat_repository

    @property
    def file_repository(self) -> FileRepository:
        """
        Retrieves the FileRepository instance.

        Returns:
            FileRepository: The initialized FileRepository object.
        """
        return self._file_repository

    @property
    def general_loader(self) -> GeneralLoader:
        """
        """
        return self._general_loader
    
    @property
    def file_management(self) -> FileManagement:
        """
        """
        return self._file_management
