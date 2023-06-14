from abc import ABC, abstractmethod
from typing import Optional, Iterable
from itertools import filterfalse
from ..document import Document, DocumentID

class BaseVectorDatabaseClient(ABC):
    
    @property
    @abstractmethod
    def collection_name(self) -> str:
        pass
    
    @staticmethod
    def filter_out_documents_without_ids(documents: Iterable[Document]) -> list[Document]:
        
        return list(filterfalse(
            lambda document: document.id is None,
            documents
        ))
        
    
    @abstractmethod
    def upsert_document(self, document: Document) -> Optional[DocumentID]:
        pass
    
    def upsert_documents(self, documents: Iterable[Document]) -> list[DocumentID]:
        
        document_ids = []
        for document in documents:
            document_id = self.upsert_document(document)
            if document_id is not None:
                document_ids.append(document_id)
        
        return document_ids
    
    @abstractmethod
    def delete_document_by_id(self, id: DocumentID) -> None:
        """Delete the vector embedding of the document specified by its ID.

        Paramerters
        -----------
            id (DocumentID): ID of the document to delete.
        """
        
        pass
    
    def delete_documents_by_ids(self, ids: Iterable[DocumentID]) -> None:
        """Delete all vector embeddings of the documents specified by their IDs.

        Paramerters
        -----------
            ids (Iterable[DocumentID]): IDs of the documents to delete.
        """
        
        for id in ids:
            self.delete_document_by_id(id)
        
    @abstractmethod
    def retrieve_similar_document_ids(
            self, 
            query: str, 
            n_similar_documents: int
        ) -> list[DocumentID]:
        pass
    
    @abstractmethod
    def drop_collection(self, collection_name: str) -> None:
        pass
        
        