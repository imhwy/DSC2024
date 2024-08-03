"""
This module provides a wrapper class Weaviate database
for managing a vector store using Weaviate and LlamaIndex.
"""

import os
from typing import List
from dotenv import load_dotenv
import weaviate
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.weaviate import WeaviateVectorStore
from llama_index.core.schema import Document, Node
from llama_index.core.node_parser import SentenceSplitter

from src.utils.utility import convert_value

load_dotenv()

WEAVIATE_HOST = convert_value(os.getenv('WEAVIATE_HOST'))
WEAVIATE_PORT = convert_value(os.getenv('WEAVIATE_PORT'))
WEAVIATE_NAME = convert_value(os.getenv('WEAVIATE_NAME'))


class WeaviateDB:
    """
    WeaviateDB is a wrapper class for managing a Weaviate-based vector store.

    Attributes:
        embed_model (GeminiEmbedding): The embedding model used for document embedding.
        documents (List[Document]): A list of documents to be added to the vector store.
        client (weaviate.Client): The client instance to interact with the Weaviate server.
        vector_store (WeaviateVectorStore): The vector store for managing document vectors.
        storage_context (StorageContext): The context for storing and retrieving vector data.
        index (VectorStoreIndex): The index of documents in the vector store.
    """

    def __init__(
        self,
        host: str = WEAVIATE_HOST,
        port: str = WEAVIATE_PORT,
        index_name: str = WEAVIATE_NAME,
        documents: List[Document] = None
    ):
        """
        Initializes the WeaviateDB class with the specified host, port
        and index name for the Weaviate instance,
        and optionally a list of documents.
        """
        self._host = host
        self._port = port
        self._index_name = index_name
        self._documents = documents

        self._client = weaviate.connect_to_local(
            host=self._host,
            port=self._port
        )
        self._vector_store = WeaviateVectorStore(
            weaviate_client=self._client,
            index_name=self._index_name
        )
        self._storage_context = StorageContext.from_defaults(
            vector_store=self._vector_store
        )
        self.parser = SentenceSplitter()
        if self._documents:
            self._index = VectorStoreIndex.from_documents(
                documents=self._documents,
                storage_context=self._storage_context
            )
        else:
            self._index = VectorStoreIndex.from_vector_store(
                vector_store=self._vector_store
            )

    @property
    def index(self) -> VectorStoreIndex:
        """
        Returns the VectorStoreIndex object that is used for
        querying and retrieving documents from the Weaviate database.

        Returns:
            VectorStoreIndex: The VectorStoreIndex object
        """
        return self._index

    @property
    def client(self) -> weaviate:
        """
        Provides access to the Weaviate client instance.
        """
        return self._client

    def documents_to_nodes(
        self,
        documents: List[Document]
    ) -> List[Node]:
        """
        """
        nodes = self.parser.get_nodes_from_documents(
            documents=documents
        )
        return nodes

    async def add_nodes(
        self,
        nodes: List[Node]
    ) -> str:
        """
        Adds a list of nodes into the vector store.

        Args:
            nodes (List[Node]): List of nodes to be added.

        Returns:
            str: A success message if nodes were added, 
            otherwise a message indicating no nodes were added.
        """
        if nodes:
            self._index.insert_nodes(nodes=nodes)
            return "Adding nodes into vector store successfully!"
        return "No nodes to add!"

    def delete_from_vector_store(
        self,
        ref_doc_id: str = None
    ) -> str:
        """
        Deletes a document from the vector store using the reference document ID.

        Args:
            ref_doc_id (str, optional): The reference document ID of the document to be deleted.

        Returns:
            str: A success message if a document was deleted,
            otherwise a message indicating no nodes were deleted.
        """
        if ref_doc_id:
            self._index.delete_ref_doc(
                ref_doc_id=ref_doc_id
            )
            return "Deleting nodes from vector store successfully!"
        return "No nodes to delete!"
