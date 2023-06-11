from typing import (
    Any, 
    Self,
    Optional
)
import pymongo
from bson import ObjectId
from .base import BaseDocumentDatabaseClient
from ..document import Document, DocumentID

class MongoDBClient(BaseDocumentDatabaseClient, pymongo.MongoClient):
    
    def __init__(self, *args, **kwargs) -> None:
        
        # initialize super class
        super().__init__(*args, **kwargs)
        
        self._database = None
        self._collection = None
    
    @property
    def collection_name(self) -> str:
        return self._collection.name
    
    @classmethod
    def connect_to_host_port(cls, host: str, port: int) -> Self:
        """Connect to MongoDB host on a given port.

        Parameters
        ----------
            host (str): Host.
            port (int): Port.

        Returns
        -------
            Self: MongoDB client.
        """
        
        client = cls(
            host=host,
            port=port
        )
        
        return client
    
    def open_database_collection(
            self,
            database_name: str,
            collection_name: str
        ) -> Self:
        
        self._database = self.get_database(database_name)
        self._collection = self._database.get_collection(collection_name)
        
        return self
    
    def insert_document(self, document: Document):
        
        self._collection.insert_one(document.to_dict())
        
    def find_one(self, filter: Optional[Any] = None) -> Optional[Document]:
        
        # find document in the collection
        document: Optional[dict] = self._collection.find_one(filter)
        
        # no document is found
        if document is None:
            return None
        
        assert isinstance(document, dict)
        
        document_id = DocumentID(document.pop('_id'))
        
        # convert to document instance
        document: Document = Document.from_dict(document)
        
        # set document ID
        document.id = document_id
        
        return document
    
    def find_one_by_id(self, id: DocumentID) -> Optional[Document]:
        
        assert isinstance(id.value, ObjectId), \
            'the value of the document ID must be an instance of ObjectId'
            
        return self.find_one(id.value)
