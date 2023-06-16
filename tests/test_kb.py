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
        print('Insertion result:')
        pprint(result)
        print()
        
        result = knowledge_base_client.insert_documents(
            documents=[
                Document(user='Isaac', age=23, text='Hello, MongoDB!'),
                Document(user='John', age=50, text='I will serve. I will be of service')
            ]
        )
        print('Insertion result:')
        pprint(result)
        print()
        
        result = knowledge_base_client.insert_documents(
            documents=[
                Document(user='Isaac', text='Hello, Natia!'),
                Document(user='Albert', age=89, text='I taught mathematics.'),
                Document(user='Tom', text='I invented the language TOML.'),
                Document(user='Jex', gpa=3.1, text='I am a front-end engineer?'),  
            ],
            with_embedding=True
        )
        print('Insertion result:')
        pprint(result)
        print()
        
        # delete documents
        documents_to_delete = knowledge_base_client.find_documents({
            'text': {
                '$regex': 'Hello'
            }
        })
        print('Documents to delete:')
        pprint(documents_to_delete)
        result = knowledge_base_client.delete_documents(documents_to_delete)
        print('Deletion result:')
        pprint(result)
        print()
        
        # retrieve similar documents
        documents = knowledge_base_client.retrieve_similar_documents(
            query='algebra',
            n_similar_documents=2
        )
        print('Similar documents:')
        pprint(documents)
        print()
        
        # udpate documents
        documents[0]['value'] = 100
        update_result = knowledge_base_client.update_documents(documents)
        print('Update result:')
        pprint(update_result)
        pprint(knowledge_base_client._doc_db_client.find_documents_by_ids(update_result['doc_db']))
        print()
        
        updated_document_ids = knowledge_base_client.update_document_embeddings(documents)
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
    