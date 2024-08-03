"""
"""

from typing import List

from src.data_loader.general_loader import GeneralLoader
from src.repositories.file_repository import FileRepository
from src.storage.weaviatedb import WeaviateDB


class FileManagement:
    """
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
        urls: List[str]
    ) -> List[str]:
        """
        Adds a file to the knowledge base.

        Args:
            urls (List[str]): A list of URLs to the files to be added.
        """
        for url in urls:
            if 'https://res.cloudinary.com/' in url:
                file_metadata = self._file_repository.file_info(url=url)
                print("pass 1")
                file_path = self._file_repository.file_transfer(
                    url=url,
                    file_info=file_metadata
                )
                print("pass 2")

                documents = self._general_loader.load_data(sources=[file_path])
                print("pass 3")
                print(documents)
                self._vector_database.add_knowledge(
                    file_name=file_metadata.file_name_with_extension,
                    documents=documents,
                )
                print("pass 4")

                self._file_repository.add_file(
                    url=url,
                    name=file_metadata.file_name_with_extension,
                    file_type=file_metadata.file_extension,
                    file_path=file_path,
                )
            else:
                documents = self._general_loader.load_data(sources=[url])
                print("pass 3")
                self._vector_database.add_knowledge(
                    file_name=url,
                    documents=documents,
                )
                print("pass 4")

                self._file_repository.add_file(
                    url=url,
                    name=url,
                    file_type="link",
                    file_path="link",
                )
        return urls

    def delete_file(
        self,
        file_name: str = None
    ) -> None:
        """
        """
        self._vector_database.delete_knowlegde(
            file_name=file_name
        )
        self._file_repository.delete_file(
            file_name=file_name
        )
