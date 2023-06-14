from abc import ABC, abstractmethod
from typing import Optional, Iterable
from ..document import Document, DocumentID

class BaseDocumentDatabaseClient(ABC):
    
    @property
    @abstractmethod
    def collection_name(self) -> str:
        pass
    
    @abstractmethod
    def insert_document(self, document: Document) -> DocumentID:
        pass
    
    @abstractmethod
    def insert_documents(self, documents: Iterable[Document]) -> list[DocumentID]:
        pass
    
    @abstractmethod
    def find_document(self, *args, **kwargs) -> Optional[Document]:
        """Find one document in the database satisfying some requirements.

        Returns
        -------
            Optional[Document]: None if no ducument is found.
        """
        pass
    
    @abstractmethod
    def find_documents(self, *args, **kwargs) -> list[Document]:
        """Find all documents in the databae satisfying some requirements.

        Returns
        -------
            list[Document]: An empty list if no ducument is found.
        """
        pass
    
    @abstractmethod
    def find_document_by_id(self, id: DocumentID) -> Optional[Document]:
        """Find one document in the databae by its ID.

        Parameters
        ----------
            id (DocumentID): Document ID.

        Returns
        -------
            Optional[Document]: None if no ducument is found.
        """
        pass
    
    def find_documents_by_ids(self, ids: Iterable[DocumentID]) -> list[Document]:
        """Find one document in the databae by its ID.

        Parameters
        ----------
            ids (Iterable[DocumentID]): Document IDs.
            If a list of IDs is passed in,
            then the documents to find will be returned in the same order.

        Returns
        -------
            list[Document]: An empty list if no ducument is found.
        """
        
        documents = []
        for id in ids:
            document = self.find_document_by_id(id)
            documents.append(document)
        
        return documents
    
    @abstractmethod
    def drop_collection(self, collection_name: str) -> None:
        pass
