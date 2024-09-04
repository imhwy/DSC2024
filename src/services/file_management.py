"""
This service represents the file management functionality of the application.
"""

from typing import List

from src.data_loader.general_loader import GeneralLoader
from src.repositories.file_repository import FileRepository
from src.storage.weaviatedb import WeaviateDB
from src.models.file import FileUpload


class FileManagement:
    """
    The FileManagement class provides functionalities to manage files
    """

    def __init__(
        self,
        file_repository: FileRepository = None,
        general_loader: GeneralLoader = None,
        vector_database: WeaviateDB = None
    ):
        self._file_repository = file_repository
        self._general_loader = general_loader
        self._vector_database = vector_database

    def add_file(
        self,
        data_list: List[FileUpload]
    ) -> None:
        """
        Adds files to the system by transferring them, loading their data,
        and storing them in a vector database.

        Args:
            data_list (List[FileUpload]): A list of FileUpload objects containing file metadata.

        Returns:
            None
        """
        for data in data_list:
            file_path = self._file_repository.file_transfer(
                data=data
            )
            documents = self._general_loader.load_data(sources=[file_path])
            try:
                self._vector_database.add_knowledge(
                    url=data.url,
                    file_type=data.file_type,
                    public_id=data.public_id,
                    file_name=data.file_name,
                    documents=documents,
                )
                self._file_repository.add_file(
                    public_id=data.public_id,
                    url=data.url,
                    file_name=data.file_name,
                    file_type=data.file_type,
                    file_path=file_path,
                )
            except ValueError as e:
                print(f"Failed to process file {data.file_name}: {str(e)}")

    def delete_file(
        self,
        public_id: str = None
    ) -> None:
        """
        Deletes a file and its associated knowledge from the vector database.

        Args:
            file_name (str): The name of the file to be deleted.

        Returns:
            None
        """
        self._file_repository.delete_specific_file(
            public_id=public_id
        )
        self._vector_database.delete_knowlegde(
            public_id=public_id
        )
