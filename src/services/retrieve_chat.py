"""
this service provides retrieve and chat module for chatbot
"""

import json
from typing import List
from llama_index.core.schema import TextNode

from src.engines.chat_engine import ChatEngine
from src.engines.retriever_engine import HybridRetriever
from src.engines.preprocess_engine import PreprocessQuestion
from src.models.chat import Chat
from src.prompt.preprocessing_prompt import PROMPT_INJECTION_ANNOUCEMENT
from src.prompt.postprocessing_prompt import (FAIL_CASE,
                                              RESPONSE_FAIL_CASE)
from src.utils.utility import format_document


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

    async def post_processing(
        self,
        result: str,
        retrieved_nodes: List["TextNode"]
    ) -> str:
        """
        Processes the result by extracting metadata and formatting it.
        """
        cleaned_json = result.strip("```json\n").strip()

        try:
            data = json.loads(cleaned_json)
            if data.get("response") in FAIL_CASE:
                return RESPONSE_FAIL_CASE
            metadata_dict = {
                meta["id"]: meta for meta in data.get("metadata", [])
            }
            titles, sessions, pages, data_types, links = [], [], [], [], []
            for node in retrieved_nodes:
                if node.id_ in metadata_dict:
                    meta = metadata_dict[node.id_]
                    titles.append(node.metadata.get("file_name", ""))
                    sessions.append(meta.get("session", ""))
                    pages.append(node.metadata.get("page", ""))
                    data_types.append(node.metadata.get("file_type", ""))
                    links.append(node.metadata.get("link", ""))
            processed_result = format_document(
                result=data.get("response"),
                titles=titles,
                sessions=sessions,
                pages=pages,
                data_types=data_types,
                links=links
            )
            return processed_result

        except json.JSONDecodeError as e:
            print("Invalid JSON:", e)
            return RESPONSE_FAIL_CASE

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
        is_outdomain = False
        combined_retrieved_nodes, retrieved_nodes = await self._retriever.retrieve_nodes(query)
        response = await self._chat.generate_response(
            user_query=query,
            relevant_information=combined_retrieved_nodes
        )
        processed_response = await self.post_processing(
            result=response,
            retrieved_nodes=retrieved_nodes
        )
        if processed_response in FAIL_CASE:
            is_outdomain = True
            
        list_nodes = []
        for retrieved_node in retrieved_nodes:
            list_nodes.append(retrieved_node.text)
        return Chat(
            response=processed_response,
            is_outdomain=is_outdomain,
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
        if processed_query.is_prompt_injection:
            return Chat(
                response=PROMPT_INJECTION_ANNOUCEMENT,
                is_outdomain=True,
                retrieved_nodes=[]
            )
        if processed_query.is_outdomain:
            response = await self._chat.funny_chat(
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
