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
from llama_index.core.schema import Document, TextNode
from llama_index.core.node_parser import SentenceSplitter
from llama_index.storage.docstore.mongodb import MongoDocumentStore

from src.utils.utility import convert_value

load_dotenv()

WEAVIATE_HOST = convert_value(os.getenv("WEAVIATE_HOST"))
WEAVIATE_PORT = convert_value(os.getenv("WEAVIATE_PORT"))
WEAVIATE_NAME = convert_value(os.getenv("WEAVIATE_NAME"))
MONGODB_URL = convert_value(os.getenv("MONGODB_URL"))
MONGODB_NAME = convert_value(os.getenv("MONGODB_NAME"))


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
        mongodb_url: str = MONGODB_URL,
        mongodb_name: str = MONGODB_NAME,
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
        self._mongodb_url = mongodb_url
        self._mongodb_name = mongodb_name
        self._client = weaviate.connect_to_local(
            host=self._host,
            port=self._port
        )
        self._vector_store = WeaviateVectorStore(
            weaviate_client=self._client,
            index_name=self._index_name
        )
        self._storage_context = StorageContext.from_defaults(
            docstore=MongoDocumentStore.from_uri(
                uri=self._mongodb_url,
                db_name=self._mongodb_name
            ),
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

        Args:
            None

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

    def document_configuration(
        self,
        file_name: str = None,
        public_id: str = None,
        documents: List[Document] = List[None]
    ) -> List[Document]:
        """
        Updates the metadata of a list of Document objects with a specified file name.

        Args:
            file_name (str, optional): The default file name to set in the metadata 
                                       if it is not already present.
            documents (List[Document], optional): A list of Document objects to be configured. 
                                                  Defaults to a list with a single Document 
                                                  containing empty text if not provided.

        Returns:
            List[Document]: The list of Document objects with updated metadata.
        """
        for document in documents:
            if not document.metadata.get("public_id"):
                document.metadata = {
                    "file_name": file_name,
                    "public_id": public_id
                }
                document.excluded_embed_metadata_keys = [
                    "file_name",
                    "public_id"
                ]
                document.excluded_llm_metadata_keys = [
                    "file_name",
                    "public_id"
                ]
        return documents

    def documents_to_nodes(
        self,
        documents: List[Document]
    ) -> List[TextNode]:
        """
        Converts a list of Document objects into a list of TextNode objects.

        Args:
            documents (List[Document]): A list of Document objects to be
                                        converted into TextNode objects.

        Returns:
            List[TextNode]: A list of TextNode objects derived from the given documents.
        """
        nodes = self.parser.get_nodes_from_documents(
            documents=documents
        )
        return nodes

    def insert_nodes(
        self,
        nodes: List[TextNode]
    ) -> str:
        """
        Adds a list of nodes into the vector store.

        Args:
            nodes (List[Node]): List of nodes to be added.

        Returns:
            None
        """
        if nodes:
            self._index.insert_nodes(nodes=nodes)

    def delete_nodes(
        self,
        ref_doc_id: str = None
    ) -> None:
        """
        Deletes a document from the vector store using the reference document ID.

        Returns:
            None

        Args:
            ref_doc_id (str, optional): The reference document ID of the document to be deleted.
        """
        if ref_doc_id:
            self._index.delete_ref_doc(
                ref_doc_id=ref_doc_id
            )

    def insert_docstore(
        self,
        nodes: List[TextNode]
    ) -> None:
        """
        Inserts a list of TextNode objects into the document store.

        Args:
        nodes (List[TextNode]): A list of TextNode objects to be inserted 
                                into the document store.

        Returns:
            None
        """
        if nodes:
            self._storage_context.docstore.add_documents(
                nodes
            )

    def delete_docstore(
        self,
        ref_doc_id: str = None
    ) -> None:
        """
        Deletes a document from the document store using its reference document ID.

        Args:
        ref_doc_id (str, optional): The reference document ID of the document to be deleted. 
                                    If None, no action is taken.

        Returns:
            None
        """
        if ref_doc_id:
            self._storage_context.docstore.delete_ref_doc(
                ref_doc_id=ref_doc_id
            )

    def add_knowledge(
        self,
        public_id: str = None,
        file_name: str = None,
        documents: List[Document] = List[None]
    ) -> None:
        """
        Adds a list of Document objects to the knowledge base.

        Args:
            file_name (str, optional): The name of the file associated with the documents.
            documents (List[Document], optional): A list of Document objects to be added. 
                                                  Defaults to an empty list if not provided.

        Returns:
            None
        """
        if documents:
            processed_documents = self.document_configuration(
                file_name=file_name,
                public_id=public_id,
                documents=documents
            )
            nodes = self.documents_to_nodes(
                documents=processed_documents
            )
            try:
                self.insert_nodes(
                    nodes=nodes
                )
                self.insert_docstore(
                    nodes=nodes
                )
            except ConnectionError as e:
                print(e)

    def delete_knowlegde(
        self,
        public_id: str = None
    ) -> None:
        """
        Deletes documents from the knowledge base by file name.

        Args:
            file_name (str, optional): The name of the file associated with the documents
                                       to be deleted. If None, no action is taken.
        """
        ref_doc_ids = []
        for _, node in self._storage_context.docstore.docs.items():
            if node.metadata.get("public_id") == public_id and node.ref_doc_id not in ref_doc_ids:
                self.delete_nodes(
                    ref_doc_id=node.ref_doc_id
                )
                print(
                    f"delete node with ref_doc_id {node.ref_doc_id} successfully ")
                self.delete_docstore(
                    ref_doc_id=node.ref_doc_id
                )
                print(
                    f"delete doc from docstore with ref_doc_id {node.ref_doc_id} successfully ")
                ref_doc_ids.append(node.ref_doc_id)

    def delete_collection(
        self,
        collection_name: str = None
    ) -> None:
        """
        Deletes a collection from the document storage by name.

        Args:
            collection_name (str, optional): The name of the collection to be deleted. 
                                             If None, no action is taken.

        Returns:
            None
        """
        self._client.collections.delete(
            name=collection_name
        )
