import os
from typing import Self, Optional, Callable
from warnings import warn
from collections import namedtuple
from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams, 
    Distance, 
    PointStruct
)

from natia.kb.document import Document
from ..base import BaseVectorDatabaseClient

# information of the collection
CollectionInfo = namedtuple(
    'CollectionInfo',
    (
        'name',
        'vec_dim',
        'metric'
    )
)
class Qdrant(BaseVectorDatabaseClient, QdrantClient):
    
    def __init__(self, *args, **kwargs):
        
        super().__init__(*args, **kwargs)
        
        # preserve super class's method create_collection
        self._create_collection = super().create_collection
        
        
        self._collection_name: Optional[str] = None

    @property
    def collection_name(self) -> Optional[str]:
        
        return self._collection_name
    
    @property
    def embed_func(self) -> Callable:
        
        return
    
    @classmethod
    def connect_to_host_port(cls, host: str, port: int) -> Self:
        """Connect to database via host and port.
        This requires that the docker image of Qdrant is running.

        Parameters
        ----------
            host (str): Host.
            port (int): Port.

        Returns
        -------
            Self: Client.
        """
     
        return cls(
            host=host,
            port=port
        )

    @classmethod
    def connect_to_dir(cls, dir: os.PathLike) -> Self:
        """Connect to local database specified by a directory path.
        In this case, the Qdrant database system is not used.
        Call this method only for testing APIs.

        Parameters
        ----------
            dir: Path to the directory for local storage.

        Returns
        -------
            Self: Client.
        """
        
        return cls(
            path=dir
        )
        
    def open_collection(self, collection_name: str) -> Self:
        
        assert collection_name in self.collections, \
            f"collection '{collection_name}' does not exists"
            
        self._collection_name = collection_name
        
        return self
    
    @property
    def collections(self) -> list[str]:
        """Names of existing collections in the database.
        """
        
        # get a list of cellection descriptions
        collections = self.get_collections().collections
        
        # extract collection names
        collection_names = list(map(
            lambda collection: collection.name,
            collections
        ))
        
        return collection_names
        
    def does_collection_exist(self, collection_name: str) -> bool:
        """Check whether the given collection exists in the database.

        Parameters
        ----------
            collection (str): Collection name.

        Returns
        -------
            bool: True if the collection exists.
        """
        
        return collection_name in self.collections
    
    def create_collection(
            self, 
            name: str, 
            vec_dim: int,
            embed_func: Callable,
            metric: Distance = Distance.COSINE,
            do_recreate: bool = False,
            do_warn: bool = False
        ) -> None:
        """Create a collection in Qdrant database.

        Parameters
        ----------
            name (str): Collection name.
            vec_dim (int): Dimension of the vector to store.
            metric (Distance, optional): Metric type, or in other words, 
            the distance function. 
            Defaults to Distance.COSINE.
            do_recreate (bool, optional): If set True, then the collection will be recreated/overwritten
            if it already exists in the database.
            Defaults to False.
            do_warn (bool, optional): If set True,
            then a warning message will be printed into terminal 
            if the collection already exists (and do_recreate is set False).
            Defaults to False.
        """
        
        # set the function to create a collection
        create_collection_func = QdrantClient.create_collection
        
        if self.does_collection_exist(name):
            
            # do nothing if the collection already exists
            if not do_recreate:
                
                # print warning message if required
                if do_warn:
                    warn(f"the collection '{name}' already exists")
                    
                return
            
            # need to create the collection, 
            # and hence change the creation function
            create_collection_func = QdrantClient.recreate_collection
        
        # use qdrant_client's API to create a collection
        create_collection_func(
            self,
            collection_name=name,
            vectors_config=VectorParams(
                size=vec_dim, 
                distance=metric
            ),
        )
        
    def get_collection_info(self, collection_name: str) -> CollectionInfo | None:
        """Get the information of the collection.

        Parameters
        ----------
            collection_name (str): Collection name.

        Returns
        -------
            CollectionInfo | None: A CollectionInfo instance, which contains attributes:
            - name: str
            - vec_dim: int,
            - metric: Distance
        """
        
        # return None if the collection does not exist
        if not self.does_collection_exist(collection_name):
            return None
        
        # get collection configuration
        collection_config = self.get_collection(collection_name).config
        
        # get vector parameters
        vector_params = collection_config.params.vectors
        
        # dimension of the vector
        vec_dim = vector_params.size
        
        # metric used in the collection
        metric = vector_params.distance
        
        return CollectionInfo(name=collection_name, vec_dim=vec_dim, metric=metric)
    
    def insert_document(self, document: Document) -> None:
        
        self.upsert(
            collection_name=self.collection_name,
            points=[
                PointStruct(
                    id=document.id.value,
                    vector=self.embed_func(document.text)
                )
            ]
        )
        return super().insert_document(document)
    