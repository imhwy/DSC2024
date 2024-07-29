"""
mongodb function
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient

from src.services.logger import DSCLogger
from src.utils.utility import convert_value

load_dotenv()

MONGODB_URL = convert_value(os.environ.get('MONGODB_URL'))
MONGODB_NAME = convert_value(os.environ.get('MONGODB_NAME'))
if MONGODB_URL is None:
    MONGODB_URL = convert_value(os.environ.get('MONGODB_URL'))
LOG_LEVEL = convert_value(os.environ.get('LOG_LEVEL'))
WRITE_LOG_TO_FILE = convert_value(os.environ.get('WRITE_LOG_TO_FILE'))
FILE_NAME = convert_value(os.environ.get('FILE_NAME'))

log = DSCLogger(
    file_name=FILE_NAME,
    write_to_file=WRITE_LOG_TO_FILE,
    mode=LOG_LEVEL
)


class MongoDBConnection():
    """
    Connect to the MongoDB, change the connection string per your MongoDB environment
    Connection String
    mongodb://username:password@host[:port]/defaultauthdb?<options>
    """
    url = MONGODB_URL
    col = MONGODB_NAME

    def __init__(self):
        self.client = MongoClient(self.url)
        self.db = self.client[MONGODB_NAME]
        print("DEBUG DEBUG")
        try:
            # check connection is available
            self.client.admin.command('ismaster')
            log.info(f"CONNECT TO DB {self.db} SUCCESSFULLY")

        except ValueError as e:
            log.error(f"CONNECT TO DB {self.db} FAIL, ERROR: {e}")


class CRUDDocuments():
    """
    author: Ngo Phuc Danh
    """
    connection = MongoDBConnection()

    def __init__(self):
        self.collection = None

    def insert_one_doc(self, obj):
        """
        Insert a single document.
        Example:
            Input: x= {'x': 1}
                result = db.test.insert_one_doc(x)
            Output: result.inserted_id
                ObjectId('54f112defba522406c9cc208')
        Parameters:
            obj: The document to insert. Must be a mutable mapping type. 
                If the document does not have an _id field one will be added automatically.
            Returns:
                An instance of InsertOneResult.
        """
        return self.collection.insert_one(document=obj)

    def find_all_doc(self):
        """
        Retrieve all documents from the collection.

        This method queries the database collection and returns all documents contained within it.

        Returns:
            pymongo.cursor.Cursor: A cursor to iterate over all documents in the collection.
        """
        return self.collection.find({})
