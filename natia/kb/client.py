from .document import Document, DocumentID
from .docdb.base import BaseDocumentDatabaseClient
from .vecdb.base import BaseVectorDatabaseClient

class KnowledgeBaseClient:
    
    def __init__(
            self,
            doc_db_client: BaseDocumentDatabaseClient,
            vec_db_client: BaseVectorDatabaseClient
        ) -> None:
        
        self._doc_db_client = doc_db_client
        self._vec_db_client = vec_db_client
    
    def insert_document(
            self, 
            document: Document,
            with_embedding: bool = False
        ):
        
        # insert into document database
        self._doc_db_client.insert_document(document)
        
        # store the vector embedding of the document if required
        if with_embedding:
            self._vec_db_client.insert_document(document)
            