"""
this service provides retrieve and chat module for chatbot
"""

from typing import Tuple
from src.engines.chat_engine import ChatEngine
from src.engines.retriever_engine import HybridRetriever


class RetrieveChat:
    """
    RetrieveChat: A class designed to retrieve chat responses.
    """

    def __init__(
        self,
        retriever: HybridRetriever = None,
        chat: ChatEngine = None
    ):
        self._retriever = retriever
        self._chat = chat

    async def retrieve_chat(
        self,
        query: str
    ) -> Tuple[str, bool]:
        """
        Processes a user's query by retrieving relevant information and generating a chat response.

        Parameters:
            query(str): The user's input query.

        Returns:
            response (str): The chat response generated for the query.
            is_outdomain (bool): True if the query is outside the domain scope, otherwise False.
        """
        is_outdomain = False
        retrieved_nodes = await self._retriever.retrieve_nodes(query)
        response = await self._chat.generate_response(
            user_query=query,
            relevant_information=retrieved_nodes
        )
        if response in "Nội dung bạn đề cập không nằm trong phạm vi của nhà trường.":
            is_outdomain = True
        return response, is_outdomain
