"""
This repository class for managing result documents in the question answering system.
"""

from src.storage.chat_crud import CRUDChatCollection
from src.models.chat import ChatDomain
from src.utils.utility import (create_new_id,
                               get_datetime)


class ChatRepository():
    """
    A repository class for managing result documents in the question answering system.
    """

    def __init__(self):
        """
        Initializes the collection attribute with a CRUDResultCollection instance 
        and loads all data into the data attribute.
        """
        self.collection = CRUDChatCollection()
        self.data = self.load_all_data()

    def load_all_data(self):
        """
        Load all documents from the collection.

        Returns:
            list: A list of documents with '_id' field as a string.
        """
        self.data = list(self.collection.find_all_doc())
        for doc in self.data:
            doc['_id'] = str(doc['_id'])
        return self.data

    async def add_one_record(self, chat: ChatDomain):
        """
        Add a new chat domain document to the collection.

        Args:
            chat (ChatDomain): The chat document to be added.
        """
        self.collection.insert_one_doc(chat.__dict__)

    async def add_chat_domains(
        self,
        query: str,
        answer: str,
        is_out_of_domain: bool = False
    ):
        """
        Add a new chat domain document to the collection.

        Args:
            query (str): The user's query.
            answer (str): The chatbot's answer to the query.
            inference_time (float): The time it took to generate the answer.
            is_out_of_domain (bool, optional): Flag indicating if the query 
                                               is out of domain. Defaults to False.
        """
        chat_domain_id = create_new_id(prefix="chatdomain")
        timestamp = get_datetime()
        chat_instance = ChatDomain(
            Id=chat_domain_id,
            query=query,
            answer=answer,
            time=timestamp,
            is_outdomain=is_out_of_domain
        )
        await self.add_one_record(chat=chat_instance)
