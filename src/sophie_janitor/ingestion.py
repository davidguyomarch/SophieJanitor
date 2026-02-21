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

    def parse(self):
        """
        Parse le Code Pénal en format PDF et retourne une liste de Documents LangChain
        en découpant par article
        et en conservant la hiérarchie (Livre, Titre, Chapitre, Section)
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

        documents = []

        # ----------------------------
        # 1. Contexte hiérarchique courant
        # ----------------------------
        current_livre = None
        current_titre = None
        current_chapitre = None
        current_section = None

        # ----------------------------
        # 2. Split par lignes
        # ----------------------------
        lines = full_text.split("\n")

        # Buffer pour construire un article
        current_article_number = None
        current_article_lines = []

        for line in lines:
            line = line.strip()

            if not line:
                continue

            # ----------------------------
            # 3. Détection hiérarchie
            # ----------------------------

            if line.startswith("Livre"):
                current_livre = line
                current_titre = None
                current_chapitre = None
                current_section = None
                continue

            if line.startswith("Titre"):
                current_titre = line
                current_chapitre = None
                current_section = None
                continue

            if line.startswith("Chapitre"):
                current_chapitre = line
                current_section = None
                continue

            if line.startswith("Section"):
                current_section = line
                continue

            # ----------------------------
            # 4. Détection article
            # ----------------------------

            article_match = re.match(r"Article\s+([0-9\-\.]+)", line)

            if article_match:

                # Si on était déjà en train de construire un article,
                # on le finalise avant de passer au suivant
                if current_article_number:

                    full_text = self._build_article_text(
                        current_livre,
                        current_titre,
                        current_chapitre,
                        current_section,
                        current_article_number,
                        current_article_lines
                    )

                    documents.append(
                        Document(
                            page_content=full_text,
                            metadata={
                                "code": "Code pénal",
                                "livre": current_livre,
                                "titre": current_titre,
                                "chapitre": current_chapitre,
                                "section": current_section,
                                "article": current_article_number
                            }
                        )
                    )

                # Nouveau article
                current_article_number = article_match.group(1)
                current_article_lines = []

                continue

            # ----------------------------
            # 5. Contenu de l’article
            # ----------------------------

            if current_article_number:
                current_article_lines.append(line)

        # ----------------------------
        # 6. Ajouter le dernier article
        # ----------------------------

        if current_article_number:

            full_text = self._build_article_text(
                current_livre,
                current_titre,
                current_chapitre,
                current_section,
                current_article_number,
                current_article_lines
            )

            documents.append(
                Document(
                    page_content=full_text,
                    metadata={
                        "code": "Code pénal",
                        "livre": current_livre,
                        "titre": current_titre,
                        "chapitre": current_chapitre,
                        "section": current_section,
                        "article": current_article_number
                    }
                )
            )

        return documents


    def _build_article_text(
        self,
        livre,
        titre,
        chapitre,
        section,
        article_number,
        article_lines
    ):
        """
        Construit le texte enrichi de l'article
        en injectant la hiérarchie dans le contenu
        """

        header_parts = []

        if livre:
            header_parts.append(livre)
        if titre:
            header_parts.append(titre)
        if chapitre:
            header_parts.append(chapitre)
        if section:
            header_parts.append(section)

        header_text = "\n".join(header_parts)

        article_body = "\n".join(article_lines)

        full_text = f"""
{header_text}

Article {article_number}

{article_body}
""".strip()

        return full_text
