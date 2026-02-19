# indexing.py

from langchain_chroma import Chroma

class Indexer:

    def __init__(self, embeddings, persist_directory, collection_name):
        self.embeddings = embeddings
        self.persist_directory = persist_directory
        self.collection_name = collection_name

    def build(self, documents):
        return Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_directory,
            collection_name=self.collection_name,
        )
