"""
This module defines the HybridRetriever class for retrieving documents
using a hybrid approach combining vector search and traditional retrieval methods.
"""

import os
from typing import List
from dotenv import load_dotenv
import tiktoken
from llama_index.core import VectorStoreIndex
from llama_index.core.retrievers import BaseRetriever
from llama_index.core.schema import TextNode

from src.utils.utility import convert_value

load_dotenv()

MAX_TOKENS = convert_value(os.getenv('MAX_TOKENS'))


class HybridRetriever:
    """
    HybridRetriever class for retrieving documents using both vector search 
    and BM25 retrieval methods.
    """

    def __init__(
        self,
        index: VectorStoreIndex = None,
        retriever: BaseRetriever = None
    ):
        """
        Initializes the HybridRetriever with the given configuration parameters.
        """
        self._index = index
        self._encoding = tiktoken.get_encoding("cl100k_base")
        self._retriever = retriever

    async def combine_retrieved_nodes(
        self,
        retrieved_nodes: List[TextNode],
        max_tokens: int = MAX_TOKENS
    ) -> str:
        """
        Combines multiple retrieved TextNode objects into a single string.
        Args:
            retrieved_nodes (List[TextNode]): The list of TextNode objects to be combined.
            max_tokens (int, optional): The maximum number of tokens.
        Returns:
            str: The combined string of text nodes up to the token limit.
        """
        combined_strings = ""
        current_tokens = 0
        for retrieved_node in retrieved_nodes:
            text = retrieved_node.text
            metadata = str(retrieved_node.id_)
            sub_combine = text + "\nmetadata:\n" + "id: " + metadata
            tokens = len(self._encoding.encode(sub_combine))
            if tokens + current_tokens > max_tokens:
                break
            combined_strings = combined_strings + "\n" + "=" * 20 + "\n" + sub_combine
            current_tokens += tokens
        return combined_strings

    async def retrieve_nodes(
        self,
        query: str
    ) -> List[TextNode]:
        """
        Retrieves nodes based on a given query.

        Args:
            query (str): The search query to retrieve TextNode objects.

        Returns:
            Tuple[str, List[TextNode]]: A tuple containing the combined text
                                         and the list of original TextNode objects.
        """
        retrieved_nodes = await self._retriever.aretrieve(query)
        combined_retrieved_nodes = await self.combine_retrieved_nodes(
            retrieved_nodes=retrieved_nodes,
        )
        return combined_retrieved_nodes, retrieved_nodes
