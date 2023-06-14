import unittest
from pprint import pprint
from natia.kb import KnowledgeBaseClient
from natia.kb.document import Document, DocumentID
from natia.kb.docdb import MongoDBClient
from natia.kb.vecdb import QdrantClient
from natia.kb.vecdb.doc2vec import (
    Document2TextTransformer,
    SentenceTransformerEmbeddingModel
)

class KnowledgeBaseTester(unittest.TestCase):
    
    def test_basics(self):
        
        print()
        
        # set up document database
        doc_db_client = MongoDBClient.connect_to_host_port(
            host='localhost',
            port=27017
        ).open_database(
            database_name='test-document-database'
        ).open_collection(
            collection_name='test-document-collection'
        )
        
        # set up vector database
        
        document2text_transformer = Document2TextTransformer()
        
        embedding_model = SentenceTransformerEmbeddingModel.from_model_name('all-MiniLM-L6-v2')
        
        vec_db_client = QdrantClient.connect_to_host_port(
            host='localhost',
            port=6333
        ).open_collection(
            collection_name='test-vector-database-collection',
            document2text_transformer=document2text_transformer,
            embedding_model=embedding_model
        )
        
        # set up knowledge base
        knowledge_base_client = KnowledgeBaseClient(
            doc_db_client=doc_db_client,
            vec_db_client=vec_db_client
        )
        
        result = knowledge_base_client.insert_documents(
            documents=[],
            with_embedding=True
        )
        pprint(result)
        
        result = knowledge_base_client.insert_documents(
            documents=[
                Document(user='Isaac', text='Hello, Natia!'),
                Document(user='Albert', age=89, text='I tought mathematics.')
            ]
        )
        pprint(result)
        
        result = knowledge_base_client.insert_documents(
            documents=[
                Document(user='Isaac', text='Hello, Natia!'),
                Document(user='Albert', age=89, text='I taught mathematics.'),
                Document(user='Tom', text='I invented the language TOML.'),
                Document(user='Jex', gpa=3.1, text='I am a front-end engineer?'),  
            ],
            with_embedding=True
        )
        pprint(result)
        
        documents = knowledge_base_client.retrieve_similar_documents(
            query='algebra',
            n_similar_documents=2
        )
        pprint(documents)
        
        updated_document_ids =knowledge_base_client.update_document_embeddings(documents)
        pprint(updated_document_ids)
        
        # clean up
        
        doc_db_client.drop_collection(
            collection_name='test-document-collection'
        )
        
        vec_db_client.drop_collection(
            collection_name='test-vector-database-collection'
        )
        
        

if __name__ == '__main__':
    unittest.main()