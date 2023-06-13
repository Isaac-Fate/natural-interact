from abc import ABC, abstractmethod
from typing import Iterable
from ...document import Document

class BaseEmbeddingModel(ABC):
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Model name.
        """
        pass

    @property
    @abstractmethod
    def vec_dim(self) -> int:
        """Dimension of the embedding vector space.
        """
        pass

    @abstractmethod
    def embed_text(self, text: str) -> list[float]:
        pass

    @abstractmethod
    def embed_texts(self, texts: Iterable[Document]) -> list[list[float]]:
        pass
    
    

    