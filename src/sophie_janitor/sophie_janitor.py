from typing import Dict, Any

from .retrieval import Retriever
from .generation import Generator


class SophieJanitor:
    """
    Full RAG pipeline orchestrator.
    """

    def __init__(self):
        self.retriever = Retriever(
            persist_directory="./chroma_code_penal",
#            embedding_model="nomic-embed-text",
            embedding_model = "bge-m3",
            collection_name="code_penal",
        )

        self.generator = Generator(
            model_name="mistral:7b",
            temperature=0.0,
        )

    def ask(
        self,
        question: str,
        threshold: float = 0.5,
        k: int = 10,
        distance_mode: bool = True
    ) -> Dict[str, Any]:

        documents = self.retriever.search_with_threshold(
            query=question,
            threshold=threshold,
            k=k,
            distance_mode=distance_mode
        )
        print(f"nb articles:{len(documents)}")

        answer = self.generator.generate(question, documents)

        cited_articles = list(
            {doc.metadata.get("article", "Inconnu") for doc in documents}
        )

        return {
            "answer": answer,
            "articles_cites": cited_articles,
            "nb_sources": len(documents)
        }
