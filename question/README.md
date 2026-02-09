# Générateur de questions à partir de PDF

Application Streamlit qui génère des questions (QCM, texte à trous, réponses courtes) à partir de documents PDF, en utilisant l'API OpenRouter avec des modèles gratuits.

## Fonctionnalités

- **Upload PDF** : extraction automatique du texte
- **3 types de questions** :
  - QCM (choix multiple) avec options et bonne réponse
  - Texte à trous (fill in the blanks)
  - Réponse courte

## Prérequis

- Python 3.10+
- Clé API OpenRouter (gratuite sur [openrouter.ai/keys](https://openrouter.ai/keys))

## Installation

```bash
# Créer et activer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env et ajouter OPENROUTER_API_KEY
```

## Configuration

Créer un fichier `.env` à la racine :

```env
OPENROUTER_API_KEY=sk-or-v1-votre-cle-ici
OPENROUTER_MODEL=meta-llama/llama-3.2-3b-instruct:free
```

Modèles gratuits recommandés :

- `meta-llama/llama-3.2-3b-instruct:free`
- `google/gemma-2-9b-it:free`
- `openrouter/free` (sélection automatique)

## Lancement

```bash
streamlit run app.py
```

## Docker (optionnel)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV OPENROUTER_API_KEY=""
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
docker build -t question-generator .
docker run -p 8501:8501 -e OPENROUTER_API_KEY=sk-or-v1-xxx question-generator
```

## Structure du projet

```
question/
├── app.py              # Application Streamlit principale
├── config.py           # Configuration centralisée
├── pdf_utils.py        # Extraction de texte PDF
├── question_generator.py  # Génération via OpenRouter
├── requirements.txt
├── .env.example
└── README.md
```
