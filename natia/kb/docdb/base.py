from abc import ABC, abstractmethod
from typing import Optional, Iterable
from itertools import filterfalse
from ..document import Document, DocumentID

class BaseDocumentDatabaseClient(ABC):
    
    @property
    @abstractmethod
    def collection_name(self) -> str:
        pass
    
    @staticmethod
    def filter_out_documents_with_ids(
            documents: Iterable[Document]
        ) -> list[Document]:
        
        documents = list(filter(
            lambda document: document.id is None,
            documents
        ))
        
        return documents
    
    @staticmethod
    def filter_out_documents_without_ids(
            documents: Iterable[Document]
        ) -> list[Document]:
        
        documents = list(filterfalse(
            lambda document: document.id is None,
            documents
        ))
        
        return documents
    
    @staticmethod
    def filter_out_empty_document_ids(
            ids: Iterable[DocumentID]
        ) -> list[DocumentID]:
        
        ids = list(filterfalse(
            lambda id: id is None,
            ids
        ))
        
        return ids
    
    @abstractmethod
    def insert_documents(self, documents: Iterable[Document]) -> list[DocumentID]:
        pass
    
    def insert_document(self, document: Document) -> Optional[DocumentID]:
        
        document_ids = self.insert_documents([document])
        if len(document_ids) > 0:
            return document_ids[0]
        else:
            return None
    
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
    def update_documents(
            self, 
            documents: Iterable[Document],
            do_insert: bool = True
        ) -> list[DocumentID]:
        pass

    @abstractmethod
    def delete_documents(
            self, 
            documents: Iterable[Document]
        ) -> list[DocumentID]:
        pass
    
    def delete_document(
            self, 
            document: Document
        ) -> Optional[DocumentID]:
        
        deleted_document_ids = self.delete_documents([document])
        
        if len(deleted_document_ids) > 0:
            return deleted_document_ids[0]
        else:
            return None
    
    @abstractmethod
    def drop_collection(self, collection_name: str) -> None:
        pass
