from bson import ObjectId
from uuid import UUID
from typing import Type

class DocumentID:
    
    def __init__(self, value: ObjectId | UUID) -> None:
        
        self._value = value
        self._type = type(value)
        
    def __str__(self) -> str:
        return f'type: {self.type}, value: {self.value}'
    
    def __repr__(self) -> str:
        return str(self)
    
    @property
    def value(self) -> ObjectId | UUID:
        return self._value
    
    @property
    def type(self) -> Type:
        return self._type
    
    def to_objectid(self) -> ObjectId:
        
        if self.type is ObjectId:
            return self.value
        
        assert self.type is UUID
        return self.uuid_to_objectid(self.value)
    
    def to_uuid(self) -> UUID:
        
        if self.type is UUID:
            return self.value
        
        assert self.type is ObjectId
        return self.objectid_to_uuid(self.value)
    
    @staticmethod
    def objectid_to_uuid(objectid: ObjectId) -> UUID:
    
        objectid_12bytes = objectid.binary
        zero_4bytes = bytes(4)
        
        # 16 bytes required by UUID
        uuid_bytes = zero_4bytes + objectid_12bytes
        
        # create a UUID instance
        uuid = UUID(bytes=uuid_bytes)
        
        return uuid

    @staticmethod
    def uuid_to_objectid(uuid: UUID) -> ObjectId:
        
        # 16 bytes UUID
        uuid_bytes = uuid.bytes
        
        # remove the first 4 bytes
        objectid_12bytes = uuid_bytes.removeprefix(bytes(4))
        
        # create an ObjectId instance
        objectid = ObjectId(objectid_12bytes)
        
        return objectid
    