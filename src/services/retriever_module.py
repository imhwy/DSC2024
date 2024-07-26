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

load_dotenv()

VECTOR_STORE_QUERY_MODE = os.getenv('VECTOR_STORE_QUERY_MODE')
SIMILARITY_TOP_K = os.getenv('SIMILARITY_TOP_K')
ALPHA = os.getenv('ALPHA')
MAX_TOKENS = os.getenv('MAX_TOKENS')


class HybridRetriever:
    """
    HybridRetriever class for retrieving documents using both vector search 
    and BM25 retrieval methods.
    """

    def __init__(
        self,
        query_mode: str = VECTOR_STORE_QUERY_MODE,
        top_k: int = SIMILARITY_TOP_K,
        alpha: float = ALPHA,
        index: VectorStoreIndex = None
    ):
        """
        Initializes the HybridRetriever with the given configuration parameters.
        """
        self._query_mode = query_mode
        self._top_k = top_k
        self._alpha = alpha
        self._index = index
        self._encoding = tiktoken.get_encoding("cl100k_base")

    def get_retriever(self) -> BaseRetriever:
        """
        Constructs a BaseRetriever object from the stored vector index.

        Returns:
            BaseRetriever: A retriever object configured with the
            current query mode, top-k, and alpha values.

        Raises:
            ValueError: If the index attribute is None, indicating no index has been set.
        """
        if self._index is None:
            raise ValueError(
                "Index must be initialized before creating a retriever.")

        retriever = self._index.as_retriever(
            vector_store_query_mode=self._query_mode,
            similarity_top_k=int(self._top_k),
            alpha=float(self._alpha)
        )
        return retriever

    def combine_retrieved_nodes(
        self,
        retrieved_nodes: List[TextNode],
        max_tokens: int = MAX_TOKENS
    ) -> List[str]:
        """
        Combines multiple retrieved TextNode objects into a list of strings.

        Args:
            retrieved_nodes (List[TextNode]): The list of TextNode objects to be combined.
            max_tokens (int, optional): The maximum number of tokens to
            include in each combined string. Defaults to MAX_TOKENS.

        Returns:
            List[str]: The list of combined strings.
        """
        combined_strings = []
        current_tokens = []
        current_string = ""
        for retrieved_node in retrieved_nodes:
            tokens = self._encoding.encode(retrieved_node.text)
            if len(current_tokens) + len(tokens) > int(max_tokens):
                combined_strings.append(current_string.strip())
                current_tokens = []
                current_string = ""
            current_tokens.extend(tokens)
            current_string += retrieved_node.text + " "
        if current_string:
            combined_strings.append(current_string.strip())
        return combined_strings

    def retrieve_nodes(
        self,
        query: str
    ) -> List[TextNode]:
        """
        Retrieves nodes from the vector store based on the given query.

        Args:
            query (str): The query to be used for retrieving nodes.

        Returns:
            List[TextNode]: A list of TextNode objects retrieved from the vector store.
        """
        retriever = self.get_retriever()
        retrieved_nodes = retriever.retrieve(query)
        combined_retrieved_nodes = self.combine_retrieved_nodes(
            retrieved_nodes=retrieved_nodes,
        )
        return combined_retrieved_nodes
