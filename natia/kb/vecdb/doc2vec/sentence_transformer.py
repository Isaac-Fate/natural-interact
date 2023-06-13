from sentence_transformers import SentenceTransformer
from typing import Self, Optional, Iterable
from .base import BaseEmbeddingModel

class SentenceTransformerEmbeddingModel(BaseEmbeddingModel, SentenceTransformer):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._name = None
    
    @property
    def name(self) -> str:
        name = self._name
        assert isinstance(name, str)
        return name
    
    @property
    def vec_dim(self) -> int:
        vec_dim = self.get_sentence_embedding_dimension()
        assert isinstance(vec_dim, int)
        return vec_dim
    
    @classmethod
    def from_model_name(cls, model_name: str = 'all-mpnet-base-v2') -> Self:
        model = cls(model_name_or_path=model_name)
        model._name = model_name
        return model
    
    def embed_text(self, text: str) -> Optional[list[float]]:
        
        # compute embedding of the given document
        vec = self.encode(text)
        
        # convert to a list
        vec = vec.tolist()
        
        return vec
    
    def embed_texts(self, texts: Iterable[str]) -> list[list[float]]:
        
        # compute embeddings of all documents
        vecs = self.encode(texts)
        
        # covert to a list of vectors
        vecs = vecs.tolist()
        
        return vecs
