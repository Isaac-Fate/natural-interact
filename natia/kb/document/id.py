from bson import ObjectId
from typing import Type

class DocumentID:
    
    def __init__(self, value: int | ObjectId) -> None:
        
        self._value = value
        self._type = type(value)
        
    def __str__(self) -> str:
        return f'{self.value}'
    
    @property
    def value(self) -> int | object:
        return self._value
    
    @property
    def type(self) -> Type:
        return self._type