from typing import (
    Any, 
    Self,
    Optional,
    Iterable
)
import pymongo
from .base import BaseDocumentDatabaseClient
from ..document import Document, DocumentID

class MongoDBClient(BaseDocumentDatabaseClient, pymongo.MongoClient):
    
    def __init__(self, *args, **kwargs) -> None:
        
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
    
    def open_database(
            self,
            database_name: str
        ) -> Self:
        
        self._database = self.get_database(database_name)
        
        return self
    
    def open_collection(
            self,
            collection_name: str
        ) -> Self:
        
        if self._database is None:
            raise RuntimeError('no database is opened')
        
        self._collection = self._database.get_collection(collection_name)
        
        return self
    
    def insert_document(self, document: Document) -> DocumentID:
        inserted_result = self._collection.insert_one(document)
        inserted_id = DocumentID(inserted_result.inserted_id)
        return inserted_id
        
    def insert_documents(self, documents: Iterable[Document]) -> list[DocumentID]:
        
        # stop here if there is no document to insert
        if len(documents) == 0:
            return []
        
        inserted_result = self._collection.insert_many(documents)
        inserted_ids = list(map(
            DocumentID,
            inserted_result.inserted_ids
        ))
        return inserted_ids
        
    def find_document(self, filter: Optional[Any] = None) -> Optional[Document]:
        
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
    
    def find_documents(self, filter: Optional[Any] = None) -> list[Document]:
        
        # find documents in the collection
        fetched_documents = self._collection.find(filter)
        
        # a list of Document instances to return
        documents = []
        
        for document in fetched_documents:
            
            document_id = DocumentID(document.pop('_id'))
        
            # convert to document instance
            document: Document = Document.from_dict(document)
        
            # set document ID
            document.id = document_id
            
            documents.append(document)
        
        return documents
    
    def find_document_by_id(self, id: DocumentID) -> Optional[Document]:
        return self.find_document(id.to_objectid())
    
    def find_documents_by_ids(self, ids: Iterable[DocumentID]) -> list[Document]:
        
        # use find_many method provided by MongoDB 
        # may not be helpful since the number of documents to find 
        # is not large,
        # and most importantly, 
        # the returned documents must be in the same order
        # as the input IDs
        
        documents: list[Document] = []
        for document_id in ids:
            document = self.find_document_by_id(document_id)
            if document is not None:
                documents.append(document)
        
        return documents
    
    def drop_collection(self, collection_name: str) -> None:
        
        if self._database is None:
            raise RuntimeError('no database is opened')
        
        self._database.drop_collection(collection_name)
      
        
    
