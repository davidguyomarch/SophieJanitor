import re
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document


class CodePenalIngestor:
    """
    Parse un PDF du Code pénal, découpe par article (Article XXX-XX),
    et retourne une liste de Documents LangChain structurés avec metadata.
    """

    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path

    def parse(self) -> List[Document]:
        """
        Parse le PDF et retourne une liste de Documents LangChain.
        """
        # 1️⃣ Charger le PDF
        loader = PyPDFLoader(self.pdf_path)
        pages = loader.load()

        # 2️⃣ Reconstituer le texte complet
        full_text = "\n".join(page.page_content for page in pages)

        # 3️⃣ Nettoyage léger du texte (important pour PDF)
        full_text = full_text.replace("\r", "\n")
        full_text = re.sub(r"\n+", "\n", full_text)

        # 4️⃣ Regex robuste pour détecter les articles
        article_pattern = re.compile(
            r"(Article\s+[A-Z]?\d+(?:-\d+)*)",
            re.IGNORECASE
        )

        # 5️⃣ Split en gardant les titres
        splits = article_pattern.split(full_text)

        article_documents = []

        # Structure obtenue :
        # ["", "Article 111-1", "contenu...", "Article 111-2", "contenu...", ...]

        for i in range(1, len(splits), 2):
            title = splits[i].strip()
            content = splits[i + 1].strip()

            # Extraire numéro article
            match = re.search(r"[A-Z]?\d+(?:-\d+)*", title)
            if not match:
                continue

            article_number = match.group()

            # Nettoyage léger du contenu
            content = re.sub(r"\s+", " ", content)

            # Création du Document
            doc = Document(
                page_content=content,
                metadata={
                    "article": article_number,
                    "code": "Code pénal",
                    "type": "article"
                }
            )

            article_documents.append(doc)
        return article_documents
