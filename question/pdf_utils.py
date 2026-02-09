"""
Utilitaires pour l'extraction du texte depuis des fichiers PDF.
"""

from pypdf import PdfReader
from io import BytesIO


def extract_text_from_pdf(file_content: bytes) -> str:
    """
    Extrait le texte d'un fichier PDF.

    Args:
        file_content: Contenu binaire du fichier PDF

    Returns:
        Texte extrait du PDF, ou chaîne vide en cas d'erreur
    """
    try:
        reader = PdfReader(BytesIO(file_content))
        text_parts = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text.strip())
        return "\n\n".join(text_parts) if text_parts else ""
    except Exception:
        return ""
