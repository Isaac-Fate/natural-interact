from abc import (
    ABC, 
    abstractmethod
)
from ..document import Document

class BaseDocumentDatabaseClient(ABC):
    
    @abstractmethod
    def insert_document(self, document: Document) -> None:
        pass
    
    