from typing import (
    Any, 
    Self,
    Optional,
    Iterable
)
from itertools import filterfalse
from natia.kb.document import DocumentID
import pymongo
from pymongo.database import Database
from pymongo.collection import Collection
from .base import BaseDocumentDatabaseClient
from ..document import Document, DocumentID

class MongoDBClient(BaseDocumentDatabaseClient, pymongo.MongoClient):
    
    def __init__(self, *args, **kwargs) -> None:
        
        super().__init__(*args, **kwargs)
        
        self._database: Optional[Database] = None
        self._collection: Optional[Collection] = None
    
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
        
    def insert_documents(self, documents: Iterable[Document]) -> list[DocumentID]:
        
        # filter out those documents that have IDs
        # since they are already in the collection
        documents = self.filter_out_documents_with_ids(documents)
        
        # stop here if there is no document to insert
        if len(documents) == 0:
            return []
        
        # get insertion result from MongoDB
        insertion_result = self._collection.insert_many(documents)
        
        # convert to document IDs
        inserted_ids = list(map(
            DocumentID,
            insertion_result.inserted_ids
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
    
    def update_documents(
            self, 
            documents: Iterable[Document],
            do_insert: bool = True
        ) -> list[DocumentID]:
        
        document_ids: list[DocumentID] = []
        
        for document in documents:
            
            # the document is not in the collection yet
            if document.id is None:
                if do_insert:
                    document_id = self.insert_document(document)
                    if document_id is not None:
                        document_ids.append(document_id)
                else:
                    continue
            
            # update the document
            self._collection.update_one(
                filter={
                    '_id': document.id.to_objectid()
                },
                update={
                    '$set': document
                }
            )
            
            document_ids.append(document.id)
        
        return document_ids
    
    def delete_documents(
            self, 
            documents: Iterable[Document]
        ) -> list[DocumentID]:
        
        # extract docuemnt IDs
        document_ids = list(map(
            lambda document: document.id, 
            documents
        ))
        
        # get deleted document IDs
        deleted_document_ids = self.delete_documents_by_ids(document_ids)
        
        return deleted_document_ids
        
    def delete_documents_by_ids(
            self, 
            ids: Iterable[DocumentID]
        ) -> list[DocumentID]:
        
        # get nonempty IDs
        ids = self.filter_out_empty_document_ids(ids)
        
        # convert each ID to ObjectId instance
        document_ids_as_objectids = list(map(
            lambda id: id.to_objectid(),
            ids
        ))
        
        # delete documents
        self._collection.delete_many({
            '_id': {
                '$in': document_ids_as_objectids
            }
        })
        
        return ids
    
    def drop_collection(self, collection_name: str) -> None:
        
        if self._database is None:
            raise RuntimeError('no database is opened')
        
        self._database.drop_collection(collection_name)
      
        
    
