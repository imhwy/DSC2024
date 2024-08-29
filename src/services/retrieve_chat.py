"""
this service provides retrieve and chat module for chatbot
"""

import json
from typing import List
from llama_index.core.schema import TextNode

from src.engines.chat_engine import ChatEngine
from src.engines.retriever_engine import HybridRetriever
from src.engines.semantic_engine import SemanticSearch
from src.engines.preprocess_engine import PreprocessQuestion
from src.models.chat import Chat
from src.prompt.postprocessing_prompt import FAIL_CASES, RESPONSE_FAIL_CASE
from src.utils.utility import format_document


class RetrieveChat:
    """
    RetrieveChat: A class designed to retrieve chat responses.
    """

    def __init__(
        self,
        retriever: HybridRetriever = None,
        chat: ChatEngine = None,
        preprocess: PreprocessQuestion = None,
        semantic: SemanticSearch = None
    ):
        self._retriever = retriever
        self._chat = chat
        self._preprocess = preprocess
        self._semantic = semantic

    async def retrieve_chat(
        self,
        query: str
    ) -> Chat:
        """
        Processes a user"s query by retrieving relevant information and generating a chat response.

        Parameters:
            query(str): The user"s input query.

        Returns:
            response (str): The chat response generated for the query.
            is_outdomain (bool): True if the query is outside the domain scope, otherwise False.
        """
        combined_retrieved_nodes, retrieved_nodes = await self._retriever.retrieve_nodes(query)
        response = await self._chat.generate_response(
            user_query=query,
            relevant_information=combined_retrieved_nodes
        )
        if response in FAIL_CASES:
            return Chat(
                response=RESPONSE_FAIL_CASE,
                is_outdomain=False,
                retrieved_nodes=[]
            )
        list_nodes = []
        for retrieved_node in retrieved_nodes:
            list_nodes.append(retrieved_node.text)
        return Chat(
            response=response,
            is_outdomain=False,
            retrieved_nodes=list_nodes
        )

    async def preprocess_query(
        self,
        query: str
    ) -> Chat:
        """
        Preprocesses the user's query and generates an appropriate response.

        Args:
            query (str): The input query from the user.

        Returns:
            Chat: A Chat object containing the response, a flag indicating if the response
                is out of domain, and a list of retrieved nodes.
        """
        processed_query = await self._preprocess.preprocess_text(
            text_input=query
        )
        print(processed_query)
        if processed_query.is_short_chat:
            return Chat(
                response=processed_query.query,
                is_outdomain=True,
                retrieved_nodes=[]
            )
        if processed_query.language is False:
            return Chat(
                response=processed_query.query,
                is_outdomain=True,
                retrieved_nodes=[]
            )
        if processed_query.is_prompt_injection:
            return Chat(
                response=processed_query.query,
                is_outdomain=True,
                retrieved_nodes=[]
            )
        if processed_query.is_outdomain:
            answer = await self._semantic.get_relevant_answer(
                query=processed_query.query
            )
            if answer:
                return Chat(
                    response=answer,
                    is_outdomain=True,
                    retrieved_nodes=[]
                )
            result = await self._chat.funny_chat(
                query=processed_query.query
            )
            return Chat(
                response=result,
                is_outdomain=True,
                retrieved_nodes=[]
            )
        return await self.retrieve_chat(
            query=processed_query.query
        )
