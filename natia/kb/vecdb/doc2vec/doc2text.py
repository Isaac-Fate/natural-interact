from sklearn.base import BaseEstimator, TransformerMixin
from typing import Self, Optional, Iterable
from ...document import Document, DocumentID

class Document2TextTransformer(BaseEstimator, TransformerMixin):
    
    def __init__(self) -> None:
        super().__init__()
        
        self._document_ids = None
    
    @property
    def document_ids(self) -> Optional[list[DocumentID]]:
        return self._document_ids
    
    def fit(self, document: Document) -> Self:
        return self 
    
    def transform(
            self, 
            document_or_documents: Document | Iterable[Document]
        ) -> Optional[str] | list[str]:
        """Transform each document its text content.

        Parameters
        ----------
            document_or_documents (Document | Iterable[Document]): A single document
            or multiple documents.

        Returns
        -------
            Optional[str] | list[str]: 
            - If a single document is passed in, 
            then a string of its text content will be returned.
            - If multiple documents are passed in, 
            then a list of text contents will be returned.
        """
        
        if isinstance(document_or_documents, Document):
            document = document_or_documents
            text = self.get_text(document)
            self._document_ids = None
            return text
        
        documents = document_or_documents
        texts: list[str] = []
        self._document_ids: list[DocumentID] = []
        for document in documents:
            text =  self.get_text(document)
            if text is not None:
                texts.append(text)
                self._document_ids.append(document.id)
        
        return texts

    def get_text(self, document: Document) -> Optional[str]:
        
        assert isinstance(document, Document)
        return document.get('text', None)
    