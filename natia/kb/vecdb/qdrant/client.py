import os
from uuid import UUID
from typing import Self, Optional, Iterable
from warnings import warn
from collections import namedtuple
import qdrant_client
from qdrant_client.models import (
    VectorParams, 
    Distance, 
    PointStruct,
    Batch,
    PointIdsList
)

from ...document import Document, DocumentID
from ..base import BaseVectorDatabaseClient
from ..doc2vec.doc2text import Document2TextTransformer
from ..doc2vec.base import BaseEmbeddingModel

# information of the collection
CollectionInfo = namedtuple(
    'CollectionInfo',
    (
        'name',
        'vec_dim',
        'metric'
    )
)

class QdrantClient(BaseVectorDatabaseClient, qdrant_client.QdrantClient):
    
    def __init__(self, *args, **kwargs):
        
        super().__init__(*args, **kwargs)
        
        # preserve super class's method create_collection
        self._create_collection = super().create_collection
        
        
        self._collection_name: Optional[str] = None

    @property
    def collection_name(self) -> Optional[str]:
        
        return self._collection_name
    
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
        
    def open_collection(
            self, 
            collection_name: str,
            document2text_transformer: Document2TextTransformer,
            embedding_model: BaseEmbeddingModel,
            do_create: bool = True,
            metric: Distance = Distance.COSINE
        ) -> Self:
        
        # handle the situation where the collection does not exist
        if not self.does_collection_exist(collection_name):
            
            # create a collection if it does not exist
            if do_create:
            
                self.create_collection(
                    collection_name=collection_name,
                    embedding_model=embedding_model,
                    metric=metric,
                    do_recreate=False,
                    do_warn=False
                )
            
            else:
                raise RuntimeError(f"collection '{collection_name}' does not exists")
        
        # set collection name
        self._collection_name = collection_name
        
        # set a transformer that transform a document to text
        # and the embedding model
        self._document2text_transformer = document2text_transformer
        self._embedding_model = embedding_model
        
        return self

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
            collection_name: str,
            embedding_model: BaseEmbeddingModel,
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
        create_collection_func = qdrant_client.QdrantClient.create_collection
        
        if self.does_collection_exist(collection_name):
            
            # do nothing if the collection already exists
            if not do_recreate:
                
                # print warning message if required
                if do_warn:
                    warn(f"the collection '{collection_name}' already exists")
                    
                return
            
            # need to create the collection, 
            # and hence change the creation function
            create_collection_func = qdrant_client.QdrantClient.recreate_collection
        
        # use qdrant_client's API to create a collection
        create_collection_func(
            self,
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=embedding_model.vec_dim, 
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
    
    def upsert_document(self, document: Document) -> Optional[DocumentID]:
        
        if document.id is None:
            return None
        
        # get text content
        text = self._document2text_transformer.transform(document)
        
        # do nothing if the text cannot be extracted from the document
        if text is None:
            return None
        
        # insert into vector database
        self.upsert(
            collection_name=self.collection_name,
            points=[
                PointStruct(
                    id=str(document.id.to_uuid()),
                    vector=self._embedding_model.embed_text(text)
                )
            ]
        )
        
        return document.id
    
    def upsert_documents(
            self, 
            documents: Iterable[Document]
        ) -> list[DocumentID]:
        
        # filter out those documents without IDs
        documents = self.filter_out_documents_without_ids(documents)
        
        # get text contents
        texts = self._document2text_transformer.transform(documents)
        
        # IDs of the documents that have text contents
        document_ids = self._document2text_transformer.document_ids
        
        # stop here if there is no document to insert
        if len(document_ids) == 0:
            return []
        
        # convert to strings
        document_ids_as_strs = list(map(
            lambda document_id: str(document_id.to_uuid()), 
            document_ids
        ))
        
        # vector embeddings of text contents
        vectors = self._embedding_model.embed_texts(texts)
        
        # bulk insert into vector database
        self.upsert(
            collection_name=self.collection_name,
            points=Batch(
                ids=document_ids_as_strs,
                vectors=vectors
            )
        )
        
        return document_ids
        
    def delete_document_by_id(self, id: DocumentID) -> None:
        
        self.delete(
            collection_name=self.collection_name,
            points_selector=PointIdsList(
                points=[str(id.to_uuid())]
            )
        )
    
    def delete_documents_by_ids(self, ids: Iterable[DocumentID]) -> list[DocumentID]:
        
        # do nothing
        if len(ids) == 0:
            return []
        
        # convert IDs to a list of UUID strings
        document_ids = list(map(
            lambda document_id: str(document_id.to_uuid()),
            ids
        ))
        
        # find actual records to delete
        records = self.retrieve(
            collection_name=self.collection_name,
            ids=document_ids
        )
        
        # delete from database
        self.delete(
            collection_name=self.collection_name,
            points_selector=PointIdsList(
                points=document_ids
            )
        )
        
       # extract IDs
        deleted_document_ids = list(map(
            lambda record: DocumentID(UUID(record.id)),
            records
        ))
        
        return deleted_document_ids

    def retrieve_similar_document_ids(
            self, 
            query: str,
            n_similar_documents: int
        ) -> list[DocumentID]:
        
        # get the embedding vector of the query
        query_vector = self._embedding_model.embed_text(query)
        
        # get points with scores
        scored_points = self.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=n_similar_documents,
            with_payload=False,
            with_vectors=False
        )
        
        # extract document IDs
        document_ids = list(map(
            lambda point: DocumentID(UUID(point.id)),
            scored_points
        ))
        
        return document_ids
        
    def drop_collection(self, collection_name: str) -> None:
        
        self.delete_collection(
            collection_name=collection_name
        )
    