from typing import Any, Self, Optional
from .id import DocumentID

class Document(dict):
    
    KEY_OF_TEXT = 'text'
    
    def __init__(self, *args, **kwargs) -> None:
        
        super().__init__(*args, **kwargs)
        
        self._id = None
        self._text = None
    
    @property
    def id(self) -> Optional[DocumentID]:
        return self._id
    
    @id.setter
    def id(self, new_id: DocumentID) -> None:
        
        assert isinstance(new_id, DocumentID)
        self._id = new_id
    
    @property
    def text(self) -> Optional[str]:
        
        return self.get_text()
    
    @classmethod
    def from_dict(cls, document: dict) -> Self:
        document = cls(document)
        return document
    
    def get_text(self) -> Optional[str]:
        return self.get(self.KEY_OF_TEXT, None)
            
    def to_dict(self, with_id: bool = False) -> dict:
        
        document_dict = self.copy()
        
        if with_id:
            if self.id is None:
                document_dict['id'] = None
            else:
                document_dict['id'] = self.id.value
            
        return document_dict
    
    