#!/usr/bin/env python3
"""
Script de ré-indexation du Code pénal

Ce script supprime le vectorstore existant et le recrée à partir du PDF du Code pénal.
Utilise les classes existantes du projet pour garantir la cohérence.

Usage:
    python scripts/reindex_code_penal.py [--pdf-path PATH] [--persist-dir PATH]

Arguments:
    --pdf-path: Chemin vers le PDF du Code pénal (défaut: data/LEGITEXT000006070719.pdf)
    --persist-dir: Répertoire du vectorstore (défaut: ./chroma_code_penal)
    --embedding-model: Modèle d'embeddings Ollama (défaut: bge-m3)
    --collection-name: Nom de la collection ChromaDB (défaut: code_penal)
"""

import argparse
import os
import shutil
import sys
from pathlib import Path

# Ajouter le répertoire src au path pour les imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from sophie_janitor.ingestion import CodePenalIngestor
from sophie_janitor.indexing import Indexer
from langchain_ollama import OllamaEmbeddings


def delete_vectorstore(persist_directory: str) -> None:
    """
    Supprime le vectorstore existant.
    
    Args:
        persist_directory: Chemin du répertoire à supprimer
    """
    if os.path.exists(persist_directory):
        print(f"🗑️  Suppression du vectorstore existant: {persist_directory}")
        shutil.rmtree(persist_directory)
        print("✅ Vectorstore supprimé")
    else:
        print(f"ℹ️  Aucun vectorstore à supprimer dans {persist_directory}")


def reindex_code_penal(
    pdf_path: str,
    persist_directory: str,
    embedding_model: str,
    collection_name: str
) -> None:
    """
    Pipeline complet de ré-indexation.
    
    Args:
        pdf_path: Chemin vers le PDF du Code pénal
        persist_directory: Répertoire de persistance ChromaDB
        embedding_model: Nom du modèle d'embeddings Ollama
        collection_name: Nom de la collection ChromaDB
    """
    
    # Vérifier que le PDF existe
    if not os.path.exists(pdf_path):
        print(f"❌ Erreur: Le fichier PDF n'existe pas: {pdf_path}")
        sys.exit(1)
    
    print(f"📄 Fichier PDF: {pdf_path}")
    print(f"📦 Modèle d'embeddings: {embedding_model}")
    print(f"💾 Répertoire de persistance: {persist_directory}")
    print(f"🏷️  Collection: {collection_name}")
    print()
    
    # Étape 1: Suppression du vectorstore existant
    delete_vectorstore(persist_directory)
    print()
    
    # Étape 2: Parsing du PDF
    print("📖 Parsing du Code pénal...")
    ingestor = CodePenalIngestor(pdf_path)
    documents = ingestor.parse()
    print(f"✅ {len(documents)} articles extraits")
    print()
    
    # Étape 3: Création des embeddings
    print("🔢 Initialisation du modèle d'embeddings...")
    embeddings = OllamaEmbeddings(model=embedding_model)
    print("✅ Modèle d'embeddings chargé")
    print()
    
    # Étape 4: Indexation
    print("🔨 Indexation des documents dans ChromaDB...")
    print("⏳ Cette étape peut prendre plusieurs minutes...")
    indexer = Indexer(
        embeddings=embeddings,
        persist_directory=persist_directory,
        collection_name=collection_name
    )
    vectorstore = indexer.build(documents)
    print("✅ Indexation terminée")
    print()
    
    # Étape 5: Vérification
    print("🔍 Vérification du vectorstore...")
    collection = vectorstore._collection
    count = collection.count()
    print(f"✅ Nombre de documents indexés: {count}")
    print()
    
    print("🎉 Ré-indexation terminée avec succès!")
    print()
    print("Vous pouvez maintenant utiliser SophieJanitor:")
    print("  from sophie_janitor import SophieJanitor")
    print("  sj = SophieJanitor()")
    print('  result = sj.ask("Quelles sont les conditions de la légitime défense ?")')


def main():
    parser = argparse.ArgumentParser(
        description="Ré-indexation du Code pénal dans ChromaDB",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  # Utilisation par défaut
  python scripts/reindex_code_penal.py
  
  # Avec un PDF personnalisé
  python scripts/reindex_code_penal.py --pdf-path data/nouveau_code_penal.pdf
  
  # Avec un modèle d'embeddings différent
  python scripts/reindex_code_penal.py --embedding-model nomic-embed-text
        """
    )
    
    parser.add_argument(
        "--pdf-path",
        type=str,
        default="data/LEGITEXT000006070719.pdf",
        help="Chemin vers le PDF du Code pénal (défaut: data/LEGITEXT000006070719.pdf)"
    )
    
    parser.add_argument(
        "--persist-dir",
        type=str,
        default="./chroma_code_penal",
        help="Répertoire du vectorstore (défaut: ./chroma_code_penal)"
    )
    
    parser.add_argument(
        "--embedding-model",
        type=str,
        default="bge-m3",
        help="Modèle d'embeddings Ollama (défaut: bge-m3)"
    )
    
    parser.add_argument(
        "--collection-name",
        type=str,
        default="code_penal",
        help="Nom de la collection ChromaDB (défaut: code_penal)"
    )
    
    args = parser.parse_args()
    
    try:
        reindex_code_penal(
            pdf_path=args.pdf_path,
            persist_directory=args.persist_dir,
            embedding_model=args.embedding_model,
            collection_name=args.collection_name
        )
    except KeyboardInterrupt:
        print("\n⚠️  Indexation interrompue par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur lors de l'indexation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
