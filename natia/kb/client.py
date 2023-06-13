from typing import Iterable
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
    def doc_db_collection_name(self) -> str:
        return self._doc_db_client.collection_name
    
    @property
    def vec_db_collection_name(self) -> str:
        return self._vec_db_client.collection_name
    
    def insert_document(
            self, 
            document: Document,
            with_embedding: bool = False
        ):
        
        # insert into document database
        # and then get the inserted ID
        document_id = self._doc_db_client.insert_document(document)
        
        # store the vector embedding of the document if required
        if with_embedding:
            
            # set the ID
            document.id = document_id
            
            # insert into vector database
            self._vec_db_client.insert_document(document)
            
    def insert_documents(
            self, 
            documents: Iterable[Document],
            with_embedding: bool = False
        ):
        
        # insert multiple documents into document database
        # and get the inserted IDs
        document_ids = self._doc_db_client.insert_documents(documents)
        
        # set IDs
        for i, _ in enumerate(documents):
            documents[i].id = document_ids[i]
        
        # store all vector embeddings of the document if required
        if with_embedding:
            self._vec_db_client.insert_documents(documents)

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
    