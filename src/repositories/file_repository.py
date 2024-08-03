"""
This module provides a `FileRepository` class to manage file records in a data storage system.
"""

import os
import requests
from urllib.parse import urlparse
from dotenv import load_dotenv
from typing import List

from src.storage.file_crud import CRUDFileCollection
from src.models.file import (File,
                             FileMetadata)
from src.utils.utility import (create_new_id,
                               get_datetime,
                               convert_value)

load_dotenv()

TIME_OUT = convert_value(os.getenv('TIME_OUT'))
DIRECTORY = convert_value(os.getenv('DIRECTORY'))


class FileRepository:
    """
    A repository class for managing file records in a data storage system.
    """

    def __init__(
        self,
        time_out: int = TIME_OUT,
        directory: str = DIRECTORY
    ):
        """
        Initializes the FileRepository instance.
        """
        self.time_out = time_out
        self.directory = directory
        self.collection = CRUDFileCollection()
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

    def add_one_record(
        self,
        file: File = None
    ) -> None:
        """
        Insert a single file record into the collection.

        Args:
            file (File): A `File` instance containing the data to be inserted.
        """
        self.collection.insert_one_doc(file.__dict__)

    def add_file(
        self,
        url: str = None,
        name: str = None,
        file_type: str = None,
        file_path: str = None
    ) -> None:
        """
        Create and add a new file record to the collection.

        Args:
            url (str, optional): The URL associated with the file.
            name (str, optional): The name of the file.
            file_type (str, optional): The type or format of the file (e.g., 'pdf', 'txt').
        """
        file_id = create_new_id(prefix="file")
        timestamp = get_datetime()
        file_instance = File(
            Id=file_id,
            url=url,
            file_name=name,
            file_type=file_type,
            file_path=file_path,
            time=timestamp
        )
        self.add_one_record(
            file=file_instance
        )

    def file_info(
        self,
        url: str = None
    ) -> FileMetadata:
        """
        """
        parsed_url = urlparse(url)
        file_name_with_extension = os.path.basename(
            parsed_url.path
        )
        file_name, file_extension = os.path.splitext(
            file_name_with_extension
        )
        return FileMetadata(
            file_name_with_extension=file_name_with_extension,
            file_name=file_name,
            file_extension=file_extension
        )

    def file_transfer(
        self,
        url: str = None,
        file_info: FileMetadata = None
    ) -> str:
        """
        """
        os.makedirs(
            self.directory,
            exist_ok=True
        )
        file_path = os.path.join(
            self.directory,
            file_info.file_name_with_extension
        )
        response = requests.get(
            url,
            timeout=self.time_out
        )
        response.raise_for_status()
        with open(file_path, "wb") as file:
            file.write(response.content)
        return file_path

    def delete_file(
        self,
        file_name: str = None
    ):
        try:
            result = self.collection.delete_one_doc({'file_name': file_name})
            if result.deleted_count > 0:
                print(
                    f"Document with file_name = {file_name} deleted successfully.")
            else:
                print(f"No document with file_name = {file_name} found.")
            return result
        except Exception as e:
            print(f"Error deleting document with file_name = {file_name}: {e}")
            raise

    def get_file(
        self,
        file_name: str = None
    ) -> List:
        documents = list(self.collection.find_one_doc(
            {'file_name': file_name}))
        for document in documents:
            document["id_"] = str(document["id_"])
        return documents
