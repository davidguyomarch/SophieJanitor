from typing import List, Tuple
import os

from langchain_core.documents import Document
#from langchain.schema import Document
from langchain_chroma import Chroma
#from langchain_community.embeddings import OllamaEmbeddings
from langchain_ollama import OllamaEmbeddings

class Retriever:
    """
    Handles document indexing and similarity search.
    """

    def __init__(self, persist_directory: str, embedding_model: str, collection_name: str):

        self.persist_directory = persist_directory
        self.collection_name = collection_name

        os.makedirs(self.persist_directory, exist_ok=True)

        self.embeddings = OllamaEmbeddings(model=embedding_model)

        try:
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings,
                collection_name=self.collection_name,
            )
        except Exception:
            # Si la base est cassée → on recrée proprement
            print("⚠️ Base corrompue ou incompatible. Recréation...")
            import shutil
            shutil.rmtree(self.persist_directory)
            os.makedirs(self.persist_directory)

            self.vectorstore = Chroma.from_documents(
                documents=[],
                embedding=self.embeddings,
                persist_directory=self.persist_directory,
                collection_name=self.collection_name,
            )

    # ------------------------
    # Indexing
    # ------------------------

    def add_documents(self, documents: List[Document]) -> None:
        if documents:
            self.vectorstore.add_documents(documents)

    # ------------------------
    # Retrieval
    # ------------------------

    def search(self, query: str, k: int = 5) -> List[Document]:
        return self.vectorstore.similarity_search(query, k=k)

    def search_with_score(
        self,
        query: str,
        k: int = 15
    ) -> List[Tuple[Document, float]]:
        return self.vectorstore.similarity_search_with_score(query, k=k)

    def search_with_threshold(
        self,
        query: str,
        threshold: float,
        k: int = 15,
        distance_mode: bool = True
    ) -> List[Document]:

        results = self.search_with_score(query, k=k)
        print(f"Nb résultats retournés : {len(results)} avant filtrage du score")

        filtered = []

        for doc, score in results:
            if distance_mode:
                if score <= threshold:
                    filtered.append(doc)
            else:
                if score >= threshold:
                    filtered.append(doc)

        return filtered
