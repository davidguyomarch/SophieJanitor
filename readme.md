# SophieJanitor

Un assistant juridique, pour sortir les juges de la pananade !

## Téléchargement des codes 

Tu les trouveras par exemple ici : https://www.legifrance.gouv.fr/codes/texte_lc/LEGITEXT000006070719/

## Installation de python 

en version 3.13, car les versions supérieurs ne sont pas compatibles avec ollama

## Installation des dépendances

pip install langchain
pip install chromadb
pip install sentence-transformers
pip install unstructured pdfplumber python-docx
pip install fastapi uvicorn

langchain
langchain-community
chromadb
sentence-transformers
unstructured
pdfplumber
python-docx
fastapi
uvicorn
streamlit
requests

<code>
pip install -r requirements.txt
</code>

## Installation de ollama

ollama permet de faire tourner le Large Langage Model en local.

Installation 

<code>
$ brew install ollama
</code>

Test

<code>
$ ollama --version
</code>

Download model

<code>
ollama pull llm-model
# ollama pull mistral
# ollama pull deepseek-r1:7b
ollama pull deepseek-r1-distill-7b

</code>

lancement du modèle
<code>
$ ollama serve
</code>

Check du upbeat de ollama

<code>
curl http://localhost:11434
</code>

A ce moment , tu as un deepseek qui tourne sur ton PC. Tu peux commencer à jouer !

## Tester le modèle local

<code>
ollama run deepseek-r1
</code>

Puis poser une question dans le prompt : 
Analyse étape par étape les obligations essentielles
d’un contrat de prestation de services en droit français.

On peut vérifier, sur MAC que le GPU est bien utilsié :

<code>
log stream --predicate 'process == "ollama"' --info
</code>

OU 

<code>
ollama ps
</code>
