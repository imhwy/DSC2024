"""
This module provides services for handling LLM and embedding models using OpenAI's API
"""

import os
import joblib
from dotenv import load_dotenv

import torch
from transformers import pipeline

import google.generativeai as genai
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
from src.repositories.suggestion_repository import SuggestionRepository
from src.prompt.preprocessing_prompt import SAFETY_SETTINGS

from src.engines.preprocess_engine import PreprocessQuestion

load_dotenv()

OPENAI_API_KEY = convert_value(os.getenv('OPENAI_API_KEY'))
OPENAI_MODEL = convert_value(os.getenv('OPENAI_MODEL'))
OPENAI_EMBED_MODEL = convert_value(os.getenv('OPENAI_EMBED_MODEL'))
TEMPERATURE_MODEL = convert_value(os.getenv('TEMPERATURE_MODEL'))
GEMINI_API_KEY = convert_value(os.getenv('GEMINI_API_KEY'))
GEMINI_LLM_MODEL = convert_value(os.getenv('GEMINI_LLM_MODEL'))
TEMPERATURE = convert_value(os.getenv('TEMPERATURE'))
TOP_P = convert_value(os.getenv('TOP_P'))
TOP_K = convert_value(os.getenv('TOP_K'))
MAX_OUTPUT_TOKENS = convert_value(os.getenv('MAX_OUTPUT_TOKENS'))
DOMAIN_CLF_MODEL = convert_value(os.getenv('DOMAIN_CLF_MODEL'))
DOMAIN_CLF_VECTORIZER = convert_value(os.getenv('DOMAIN_CLF_VECTORIZER'))
PROMPT_INJECTION_CLF_MODEL = convert_value(os.getenv('PROMPT_INJECTION_CLF_MODEL'))
PROMPT_INJECTION_CLF_VECTORIZER = convert_value(os.getenv('PROMPT_INJECTION_CLF_VECTORIZER'))
LANG_DETECTOR = convert_value(os.getenv('LANG_DETECTOR'))
VECTOR_STORE_QUERY_MODE = convert_value(os.getenv('VECTOR_STORE_QUERY_MODE'))
SIMILARITY_TOP_K = convert_value(os.getenv('SIMILARITY_TOP_K'))
ALPHA = convert_value(os.getenv('ALPHA'))


class Service:
    """
    A service class that sets up and manages LLM and embedding models using OpenAI
    """

    def __init__(self):
        """
        Initializes the Service class with LLM and embedding models.
        """
        genai.configure(
            api_key=GEMINI_API_KEY
        )
        self._domain_clf_model = joblib.load(
            filename=DOMAIN_CLF_MODEL
        )
        self._domain_clf_vectorizer = joblib.load(
            filename=DOMAIN_CLF_VECTORIZER
        )
        self._prompt_injection_clf_model = joblib.load(
            filename=PROMPT_INJECTION_CLF_MODEL
        )
        self._prompt_injection_clf_vectorizer = joblib.load(
            filename=PROMPT_INJECTION_CLF_VECTORIZER
        )
        self._lang_detector = pipeline(
            'text-classification', 
            model=LANG_DETECTOR, 
            device='cuda' if torch.cuda.is_available() else 'cpu'
        )
        self._generation_config = {
            "temperature": TEMPERATURE,
            "top_p": TOP_P,
            "top_k": TOP_K,
            "max_output_tokens": MAX_OUTPUT_TOKENS,
        }
        self._llm = OpenAI(
            api_key=OPENAI_API_KEY,
            model=OPENAI_MODEL,
            temperature=TEMPERATURE_MODEL
        )
        self._embed_model = OpenAIEmbedding(
            api_key=OPENAI_API_KEY,
            model=OPENAI_EMBED_MODEL
        )
        self._gemini = genai.GenerativeModel(
            model_name=GEMINI_LLM_MODEL,
            generation_config=self._generation_config,
            safety_settings=SAFETY_SETTINGS
        )
        Settings.llms = self._llm
        Settings.embed_model = self._embed_model
        self._vector_database = WeaviateDB()
        self._hybrid_retriever = self._vector_database.index.as_retriever(
            vector_store_query_mode=VECTOR_STORE_QUERY_MODE,
            similarity_top_k=SIMILARITY_TOP_K,
            alpha=ALPHA
        )
        self._retriever = HybridRetriever(
            index=self._vector_database.index,
            retriever=self._hybrid_retriever,
        )
        self._chat_engine = ChatEngine(
            language_model=self._llm
        )
        self._preprocess_engine = PreprocessQuestion(
            gemini=self._gemini,
            domain_clf_model=self._clf_model,
            domain_clf_vectorizer=self._clf_vectorizer,
            lang_detect_model=None,
            lang_detect_vectorizer=None
        )
        self._retrieve_chat_engine = RetrieveChat(
            retriever=self._retriever,
            chat=self._chat_engine,
            preprocess=self._preprocess_engine
        )
        self._chat_repository = ChatRepository()
        self._file_repository = FileRepository()
        self._general_loader = GeneralLoader()
        self._file_management = FileManagement(
            file_repository=self._file_repository,
            general_loader=self._general_loader,
            vector_database=self._vector_database
        )
        self._suggestion_repository = SuggestionRepository()

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
        Provides access to the GeneralLoader instance.
        """
        return self._general_loader

    @property
    def file_management(self) -> FileManagement:
        """
        Provides access to the FileManagement instance.
        """
        return self._file_management

    @property
    def suggestion_repository(self) -> SuggestionRepository:
        """
        Provides access to the SuggestionRepository instance.
        """
        return self._suggestion_repository

    @property
    def get_preprocess_engine(self) -> PreprocessQuestion:
        """
        Provides access to the PreprocessQuestion instance.
        """
        return self._preprocess_engine
