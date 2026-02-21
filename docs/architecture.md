# Architecture de SophieJanitor

## Vue d'ensemble

SophieJanitor est un assistant juridique basé sur une architecture RAG (Retrieval-Augmented Generation) spécialisé dans le droit pénal français. Le système permet d'interroger le Code pénal en langage naturel et de recevoir des réponses précises avec citations des articles pertinents.

## Architecture globale

```
┌─────────────────────────────────────────────────────────────┐
│                      SophieJanitor                          │
│                    (Orchestrateur RAG)                      │
└────────────┬────────────────────────────────┬───────────────┘
             │                                │
             ▼                                ▼
    ┌────────────────┐              ┌─────────────────┐
    │   Retriever    │              │    Generator    │
    │  (Recherche)   │              │  (Génération)   │
    └────────┬───────┘              └────────┬────────┘
             │                               │
             ▼                               ▼
    ┌────────────────┐              ┌─────────────────┐
    │ ChromaDB       │              │  Ollama LLM     │
    │ (VectorStore)  │              │  (Mistral 7B)   │
    └────────────────┘              └─────────────────┘
```

## Composants principaux

### 1. SophieJanitor (Orchestrateur)

**Fichier:** `src/sophie_janitor/sophie_janitor.py`

**Responsabilité:** Point d'entrée principal qui coordonne le pipeline RAG complet.

**Configuration:**
- Modèle d'embeddings: `bge-m3` (via Ollama)
- Modèle LLM: `mistral:7b` (via Ollama)
- VectorStore: ChromaDB persistant dans `./chroma_code_penal`

**Méthode principale:**
```python
def ask(question: str, threshold: float, k: int, distance_mode: bool) -> Dict[str, Any]
```

**Workflow:**
1. Reçoit une question juridique
2. Délègue la recherche au `Retriever` avec filtrage par seuil de similarité
3. Transmet les documents pertinents au `Generator`
4. Retourne la réponse avec les articles cités

**Sortie:**
```python
{
    "answer": str,           # Réponse générée par le LLM
    "articles_cites": list,  # Liste des articles du Code pénal utilisés
    "nb_sources": int        # Nombre de documents récupérés
}
```

### 2. Retriever (Recherche sémantique)

**Fichier:** `src/sophie_janitor/retrieval.py`

**Responsabilité:** Gestion de l'indexation et de la recherche par similarité vectorielle.

**Fonctionnalités:**

#### Initialisation
- Charge ou crée un VectorStore ChromaDB persistant
- Gère la récupération automatique en cas de base corrompue
- Configure les embeddings via Ollama

#### Méthodes de recherche

**`search(query, k)`**
- Recherche simple par similarité
- Retourne les k documents les plus proches

**`search_with_score(query, k)`**
- Recherche avec scores de similarité
- Retourne des tuples `(Document, score)`

**`search_with_threshold(query, threshold, k, distance_mode)`**
- Recherche avec filtrage par seuil
- `distance_mode=True`: filtre par distance (score ≤ threshold)
- `distance_mode=False`: filtre par similarité (score ≥ threshold)
- Permet d'éliminer les résultats peu pertinents

#### Indexation

**`add_documents(documents)`**
- Ajoute des documents au VectorStore existant
- Utilisé pour enrichir la base de connaissances

### 3. Generator (Génération de réponses)

**Fichier:** `src/sophie_janitor/generation.py`

**Responsabilité:** Génération de réponses juridiques à partir des documents récupérés.

**Configuration LLM:**
- Modèle: `mistral:7b`
- Temperature: `0.0` (réponses déterministes)
- Top-p: `0.9`
- Context window: `8192` tokens

**Workflow:**

1. **Construction du contexte** (`build_context`)
   - Agrège les documents récupérés
   - Formate avec numéros d'articles et sources
   - Structure: `[SOURCE n — Article XXX] contenu`

2. **Génération de la réponse** (`generate`)
   - Construit un prompt structuré avec:
     - System prompt (règles impératives)
     - Contexte juridique (articles pertinents)
     - Question de l'utilisateur
     - Instructions de formatage
   - Invoque le LLM via ChatOllama
   - Retourne la réponse textuelle

**Règles du système:**
- Réponses basées UNIQUEMENT sur le contexte fourni
- Citations explicites des articles utilisés
- Pas d'invention d'articles
- Réponse "Je ne sais pas" si information absente
- Style juridique français clair et structuré

### 4. CodePenalIngestor (Parsing PDF)

**Fichier:** `src/sophie_janitor/ingestion.py`

**Responsabilité:** Extraction et structuration du Code pénal depuis un PDF.

**Fonctionnalités:**

#### Parsing hiérarchique
- Détecte la structure: Livre → Titre → Chapitre → Section → Article
- Maintient le contexte hiérarchique pendant le parsing
- Enrichit chaque article avec sa position dans la hiérarchie

#### Extraction d'articles
- Regex robuste: `Article\s+[A-Z]?\d+(?:-\d+)*`
- Gère les numéros complexes (ex: `122-5`, `A123-4`)
- Découpe le texte en articles individuels

#### Enrichissement du contenu
- Injecte la hiérarchie dans le `page_content` de chaque document
- Préserve le contexte juridique pour améliorer la recherche sémantique

**Métadonnées générées:**
```python
{
    "code": "Code pénal",
    "livre": str,      # Ex: "Livre I : Dispositions générales"
    "titre": str,      # Ex: "Titre II : De la responsabilité pénale"
    "chapitre": str,   # Ex: "Chapitre II : Des causes d'irresponsabilité"
    "section": str,    # Ex: "Section 1 : De la contrainte"
    "article": str     # Ex: "122-5"
}
```

**Sortie:**
- Liste de `Document` LangChain prêts pour l'indexation

### 5. Indexer (Construction du VectorStore)

**Fichier:** `src/sophie_janitor/indexing.py`

**Responsabilité:** Création initiale du VectorStore à partir de documents parsés.

**Utilisation:**
```python
indexer = Indexer(
    embeddings=OllamaEmbeddings(model="bge-m3"),
    persist_directory="./chroma_code_penal",
    collection_name="code_penal"
)
vectorstore = indexer.build(documents)
```

**Note:** Utilisé principalement lors de l'initialisation. Pour ajouter des documents à un store existant, utiliser `Retriever.add_documents()`.

## Flux de données

### Pipeline de question-réponse

```
1. Question utilisateur
   │
   ▼
2. SophieJanitor.ask()
   │
   ├─► Retriever.search_with_threshold()
   │   │
   │   ├─► Embedding de la question (bge-m3)
   │   │
   │   ├─► Recherche vectorielle dans ChromaDB
   │   │
   │   └─► Filtrage par seuil de similarité
   │
   ├─► Documents pertinents récupérés
   │
   ├─► Generator.generate()
   │   │
   │   ├─► Construction du contexte
   │   │
   │   ├─► Création du prompt structuré
   │   │
   │   └─► Invocation LLM (Mistral 7B)
   │
   └─► Réponse + articles cités
```

### Pipeline d'indexation (one-time)

```
1. PDF du Code pénal
   │
   ▼
2. CodePenalIngestor.parse()
   │
   ├─► Chargement PDF (PyPDFLoader)
   │
   ├─► Nettoyage du texte
   │
   ├─► Détection hiérarchie (Livre/Titre/Chapitre/Section)
   │
   ├─► Extraction articles (regex)
   │
   └─► Documents LangChain avec métadonnées
       │
       ▼
3. Indexer.build()
   │
   ├─► Génération embeddings (bge-m3)
   │
   └─► Stockage dans ChromaDB
```

## Technologies utilisées

### Stack principal
- **LangChain**: Framework RAG et orchestration
- **ChromaDB**: Base de données vectorielle persistante
- **Ollama**: Exécution locale des modèles (embeddings + LLM)

### Modèles
- **Embeddings**: `bge-m3` (multilingue, optimisé pour le français)
- **LLM**: `mistral:7b` (génération de texte, français natif)

### Dépendances clés
- `langchain-core`: Types et abstractions de base
- `langchain-community`: Loaders (PyPDFLoader)
- `langchain-chroma`: Intégration ChromaDB
- `langchain-ollama`: Intégration Ollama (embeddings + chat)

## Choix d'architecture

### Pourquoi RAG ?
- **Précision**: Réponses basées sur le texte officiel du Code pénal
- **Traçabilité**: Citations des articles sources
- **Actualisation**: Facile de mettre à jour la base juridique
- **Pas d'hallucinations**: Le LLM ne peut répondre qu'avec le contexte fourni

### Pourquoi Ollama local ?
- **Confidentialité**: Données juridiques sensibles restent locales
- **Coût**: Pas de frais d'API
- **Latence**: Pas de dépendance réseau
- **Contrôle**: Choix des modèles et paramètres

### Pourquoi ChromaDB ?
- **Persistance**: Base vectorielle sauvegardée sur disque
- **Performance**: Recherche vectorielle optimisée
- **Simplicité**: API intuitive, pas de serveur externe
- **Métadonnées**: Support natif pour filtrage et enrichissement

### Filtrage par seuil
- **Qualité**: Élimine les résultats peu pertinents
- **Flexibilité**: Paramètre `threshold` ajustable selon le cas d'usage
- **Modes**: Distance ou similarité selon le backend d'embeddings

## Points d'extension

### Ajout de nouveaux codes juridiques
1. Créer un nouvel ingestor (ex: `CodeCivilIngestor`)
2. Parser le PDF avec la structure spécifique
3. Indexer dans une nouvelle collection ChromaDB
4. Modifier `SophieJanitor` pour interroger plusieurs collections

### Support multi-modèles
- Abstraire la configuration des modèles
- Permettre le choix dynamique (Mistral, Llama, etc.)
- Comparer les performances selon le cas d'usage

### Amélioration du ranking
- Implémenter un re-ranking avec un modèle cross-encoder
- Ajouter des filtres par métadonnées (livre, chapitre)
- Combiner recherche vectorielle + recherche par mots-clés (hybrid search)

### Interface utilisateur
- API REST (FastAPI)
- Interface web (Streamlit, Gradio)
- CLI enrichie avec historique

## Limitations actuelles

### Performance
- Temps de réponse dépend de la puissance locale (GPU recommandé)
- Pas de cache des embeddings de questions

### Qualité
- Dépend de la qualité du parsing PDF (peut manquer des nuances)
- Pas de gestion des articles abrogés ou modifiés
- Pas de contexte conversationnel (chaque question est indépendante)

### Scalabilité
- Une seule collection (Code pénal uniquement)
- Pas de gestion de versions du code
- Pas de support multi-utilisateurs

## Maintenance

### Mise à jour du Code pénal
1. Télécharger le nouveau PDF depuis Légifrance
2. Supprimer l'ancien VectorStore: `rm -rf ./chroma_code_penal`
3. Ré-exécuter le pipeline d'indexation:
   ```bash
   python scripts/reindex_code_penal.py
   ```
   
   Options disponibles:
   ```bash
   # Avec un PDF personnalisé
   python scripts/reindex_code_penal.py --pdf-path data/nouveau_code_penal.pdf
   
   # Avec un modèle d'embeddings différent
   python scripts/reindex_code_penal.py --embedding-model nomic-embed-text
   
   # Avec un répertoire de persistance personnalisé
   python scripts/reindex_code_penal.py --persist-dir ./mon_vectorstore
   ```
   
   Le script effectue automatiquement:
   - Suppression du vectorstore existant
   - Parsing du PDF avec `CodePenalIngestor`
   - Génération des embeddings
   - Indexation dans ChromaDB
   - Vérification du nombre de documents indexés

4. Tester avec des questions de validation

### Changement de modèle
- Modifier les paramètres dans `SophieJanitor.__init__()`
- Attention: changer le modèle d'embeddings nécessite de ré-indexer

### Monitoring
- Logs de debug disponibles via `print()` (à améliorer avec logging)
- Métriques: nombre de sources, scores de similarité
