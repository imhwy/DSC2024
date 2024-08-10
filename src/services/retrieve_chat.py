"""
this service provides retrieve and chat module for chatbot
"""

from typing import Tuple

from src.engines.chat_engine import ChatEngine
from src.engines.retriever_engine import HybridRetriever
from src.engines.preprocess_engine import PreprocessQuestion
from src.models.chat import Chat
from src.prompt.funny_chat_prompt import PROMPT_FUNNY_FLOW


class RetrieveChat:
    """
    RetrieveChat: A class designed to retrieve chat responses.
    """

    def __init__(
        self,
        retriever: HybridRetriever = None,
        chat: ChatEngine = None,
        preprocess: PreprocessQuestion = None
    ):
        self._retriever = retriever
        self._chat = chat
        self._preprocess = preprocess

    async def retrieve_chat(
        self,
        query: str
    ) -> Chat:
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
        return Chat(
            response=response,
            is_outdomain=is_outdomain,
            retrieved_nodes=retrieved_nodes
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
        if processed_query.is_prompt_injection:
            return Chat(
                response=PROMPT_FUNNY_FLOW,
                is_outdomain=True,
                retrieved_nodes=[]
            )
        if processed_query.is_outdomain:
            response = self._chat.funny_chat(
                query=processed_query.query
            )
            return Chat(
                response=response,
                is_outdomain=True,
                retrieved_nodes=[]
            )
        return await self.retrieve_chat(
            query=processed_query.query
        )
