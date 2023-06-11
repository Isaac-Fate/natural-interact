from typing import Any, Self, Optional
from .id import DocumentID

class Document:
    
    def __init__(self, text: str, meta: Optional[Any] = None) -> None:
        
        self._id = None
        self._text = text
        self._meta = meta
    
    def __str__(self) -> str:
        return f'Document(id: {self.id}, text: {self.text}, meta: {self.meta})'
    
    def __repr__(self) -> str:
        return str(self)
    
    @property
    def id(self) -> Optional[DocumentID]:
        
        return self._id
    
    @id.setter
    def id(self, new_id: DocumentID) -> None:
        
        assert isinstance(new_id, DocumentID)
        self._id = new_id
    
    @property
    def text(self) -> str:
        
        return self._text
    
    @property
    def meta(self) -> Optional[Any]:
        
        return self._meta
    
    @classmethod
    def from_dict(
            cls, 
            document: dict,
            key_of_text: str = 'text',
            use_meta: bool = True
        ) -> Self:
        
        # get the text value from the dict
        text = document.get(key_of_text, None)
        
        assert text is not None, \
            f"the value of '{key_of_text}' cannot be None"
        
        # make a copy and remove the text
        document = document.copy()
        document.pop(key_of_text)
        
        # get meta data
        
        # directly use the value of the 'meta' key of the dict
        if use_meta:
            
            # the the value of meta
            meta = document.get('meta', None)
            
            # create the document if meta is not None
            if meta is not None:
                return cls(text=text, meta=meta)
        
        # the meta data of the document is 
        # all the rest objects contained in the dict 
        meta = document
        
        # set the meta None if its value is an empty dict
        if len(meta) == 0:
            meta = None
        
        return cls(text=text, meta=meta)
            
    def to_dict(self, with_id: bool = False) -> dict:
        
        document_dict = dict(
            text=self.text,
            meta=self.meta
        )
        
        if with_id:
            document_dict['id'] = self.id.value
            
        return document_dict
    
    