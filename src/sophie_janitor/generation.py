from typing import List
#from langchain.schema import Document
from langchain_core.documents import Document
from langchain_ollama import ChatOllama


class Generator:
    """
    Handles LLM-based answer generation.
    """

    def __init__(
        self,
        model_name: str = "mistral:7b",
        temperature: float = 0.0,
    ):
        self.llm = ChatOllama(
            model=model_name,
            temperature=temperature,
            top_p=0.9,
            num_ctx=8192
        )

    def build_context(self, documents: List[Document]) -> str:
        """
        Build context string from retrieved documents.
        """
        context_blocks = []

        for i, doc in enumerate(documents, start=1):
            article_number = doc.metadata.get("article", "Inconnu")

            context_blocks.append(
                f"[SOURCE {i} — Article {article_number}]\n{doc.page_content}"
            )

        return "\n\n".join(context_blocks)

    def generate(self, question: str, documents: List[Document]) -> str:
        """
        Generate final answer using retrieved documents.
        """

        context = self.build_context(documents)

        # 3️⃣ Prompt final
        SYSTEM_PROMPT = """
Tu es un assistant juridique spécialisé en droit pénal français.

RÈGLES IMPÉRATIVES :
- Tu réponds UNIQUEMENT à partir du CONTEXTE fourni
- Tu cites explicitement les numéros d’articles utilisés
- Tu n’inventes jamais d’article
- Si la réponse n’est pas dans le contexte, tu dis : "Je ne sais pas"
- Tu écris en français juridique clair et structuré
"""

        prompt = f"""
{SYSTEM_PROMPT}

CONTEXTE JURIDIQUE :
{context}

QUESTION :
{question}

RÈGLES :
- Réponds uniquement à partir du contexte fourni
- Cite explicitement les articles utilisés (ex : article 122-5 du Code pénal)
- Si l'information n'est pas présente, dis "Je ne sais pas"
- Rédige en français juridique clair et structuré

RÉPONSE :
"""

        response = self.llm.invoke(prompt)
        return response.content