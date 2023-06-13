from abc import ABC, abstractmethod
from typing import Iterable
from ..document import Document, DocumentID

class BaseVectorDatabaseClient(ABC):
    
    @property
    @abstractmethod
    def collection_name(self) -> str:
        pass
    
    @abstractmethod
    def insert_document(self, document: Document) -> None:
        pass
    
    @abstractmethod
    def insert_documents(self, documents: Iterable[Document]) -> None:
        pass
    
    @abstractmethod
    def retrieve_similar_document_ids(
            self, 
            query: str, 
            n_similar_documents: int
        ) -> list[DocumentID]:
        pass
        
        