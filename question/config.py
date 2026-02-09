"""
Configuration centralisée pour l'application de génération de questions.
Utilise des variables d'environnement - jamais de valeurs en dur.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

# OpenRouter
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = os.getenv(
    "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"
)

# Modèle gratuit OpenRouter (meta-llama ou openrouter/free)
DEFAULT_MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "meta-llama/llama-3.2-3b-instruct:free"
)

# Paramètres de génération
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4096"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))


def validate_config() -> tuple[bool, str]:
    """
    Valide la configuration requise.
    Returns:
        (is_valid, error_message)
    """
    if not OPENROUTER_API_KEY:
        return False, (
            "OPENROUTER_API_KEY manquant. "
            "Obtenez une clé sur https://openrouter.ai/keys et ajoutez-la à .env"
        )
    return True, ""
