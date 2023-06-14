from typing import Optional, Iterable
from itertools import filterfalse
from .document import Document, DocumentID
from .docdb.base import BaseDocumentDatabaseClient
from .vecdb.base import BaseVectorDatabaseClient

class KnowledgeBaseClient:
    
    def __init__(
            self,
            doc_db_client: BaseDocumentDatabaseClient,
            vec_db_client: BaseVectorDatabaseClient
        ) -> None:
        
        self._doc_db_client = doc_db_client
        self._vec_db_client = vec_db_client
    
    @property
    def doc_db_client(self) -> BaseDocumentDatabaseClient:
        return self._doc_db_client
    
    @property
    def vec_db_client(self) -> BaseVectorDatabaseClient:
        return self._vec_db_client
    
    @property
    def doc_db_collection_name(self) -> str:
        return self._doc_db_client.collection_name
    
    @property
    def vec_db_collection_name(self) -> str:
        return self._vec_db_client.collection_name
    
    def find_document(self, *args, **kwargs) -> Optional[Document]:
        
        return self._doc_db_client.find_document(*args, **kwargs)
    
    def find_documents(self, *args, **kwargs) -> list[Document]:
        
        return self._doc_db_client.find_documents(*args, **kwargs)
    
    def insert_document(
            self, 
            document: Document,
            with_embedding: bool = False
        ):
        
        # do nothing if the document has an ID,
        # which means it already exits in the document database
        if document.id is not None:
            return
        
        # insert into document database
        # and then get the inserted ID
        document_id = self._doc_db_client.insert_document(document)
        
        # store the vector embedding of the document if required
        if with_embedding:
            
            # set the ID
            document.id = document_id
            
            # insert into vector database
            self._vec_db_client.upsert_document(document)
    
    def update_document_embeddings(self, documents: Iterable[Document]) -> list[DocumentID]:
        
        document_ids = self._vec_db_client.upsert_documents(documents)
        
        return document_ids
    
    def insert_documents(
            self, 
            documents: Iterable[Document],
            with_embedding: bool = False
        ) -> dict[str, list[DocumentID]]:
        
        # filter out those documents that already have IDs
        documents = list(filter(
            lambda document: document.id is None,
            documents
        ))
        
        # insert multiple documents into document database
        # and get the inserted IDs
        inserted_document_ids_in_doc_db = self._doc_db_client.insert_documents(documents)
        
        # set IDs
        for i, _ in enumerate(documents):
            documents[i].id = inserted_document_ids_in_doc_db[i]
        
        # store all vector embeddings of the document if required
        if with_embedding:
            inserted_document_ids_in_vec_db = self._vec_db_client.upsert_documents(documents)
            return {
                'doc_db': inserted_document_ids_in_doc_db,
                'vec_db': inserted_document_ids_in_vec_db
            }
        
        return {
            'doc_db': inserted_document_ids_in_doc_db,
            'vec_db': []
        }

    def retrieve_similar_documents(
            self, 
            query: str,
            n_similar_documents: int
        ) -> list[Document]:
        
        # retrieve similar document IDs from vector database
        similar_document_ids = self._vec_db_client.retrieve_similar_document_ids(
            query,
            n_similar_documents
        )
        
        # find the actual documents in the document database
        similar_documents = self._doc_db_client.find_documents_by_ids(similar_document_ids)
        
        return similar_documents
    