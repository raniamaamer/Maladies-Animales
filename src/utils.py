import re
from langdetect import detect, LangDetectException
from bs4 import BeautifulSoup

def clean_text(html_content: str) -> str:
    """Nettoie le contenu HTML et corrige les problèmes d'encodage"""
    soup = BeautifulSoup(html_content, "lxml")
    for script in soup(["script", "style"]):
        script.decompose()
    text = soup.get_text(separator=' ')
    
    # Normaliser les espaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Correction des problèmes d'encodage courants
    # Remplacer les caractères corrompus par des espaces
    text = re.sub(r'[^\w\s\d.,!?;:()\[\]{}«»""\'\-—–/@#$%&*+=<>|\\\/\u0600-\u06FF\u0750-\u077F\u0590-\u05FF\u0400-\u04FF\u00C0-\u017F]', ' ', text, flags=re.UNICODE)
    
    # Re-normaliser après nettoyage
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def detect_language(text: str) -> str:
    """Détecte la langue du texte avec gestion d'erreur robuste"""
    if not text or len(text.strip()) < 10:
        return "unknown"
    
    try:
        # Utiliser un échantillon de texte pour la détection
        sample = text[:1000]
        lang = detect(sample)
        return lang
    except LangDetectException as e:
        # Log pour debugging mais pas d'erreur fatale
        return "unknown"
    except Exception as e:
        return "unknown"

def get_domain_type(url: str) -> str:
    """Heuristique simple pour deviner le type de source"""
    if not url:
        return "médias"
    
    url_lower = url.lower()
    
    # Sites officiels d'organisations internationales
    if any(site in url_lower for site in ['wahis', 'woah', 'who.int', 'fao.org', 'oie.int']):
        return "site officiel"
    
    # Sites gouvernementaux
    if any(ext in url_lower for ext in ['.gov', '.gouv', '.gob']):
        return "site officiel"
    
    # Par défaut : média
    return "médias"

def normalize_field(text: str) -> str:
    """Normalise un champ texte (supprime espaces superflus, etc.)"""
    if not text:
        return ""
    
    # Supprimer espaces multiples
    text = re.sub(r'\s+', ' ', str(text)).strip()
    
    # Corriger les caractères corrompus courants
    replacements = {
        'Ã©': 'é',
        'Ã¨': 'è',
        'Ã ': 'à',
        'Ã´': 'ô',
        'Ã®': 'î',
        'Ã§': 'ç',
        'Ã«': 'ë',
        'Ã¯': 'ï',
        'Ã¹': 'ù',
        'Ã»': 'û',
    }
    
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    
    return text

def validate_extracted_data(data: dict) -> dict:
    """Valide et normalise les données extraites"""
    validated = {}
    
    # Champs obligatoires avec valeurs par défaut
    defaults = {
        "date_publication": "inconnue",
        "lieu": "inconnu",
        "maladie": "inconnue",
        "animal": "inconnu",
        "resume_50_mots": "Résumé indisponible.",
        "resume_100_mots": "Résumé indisponible.",
        "resume_150_mots": "Résumé indisponible."
    }
    
    for key, default_value in defaults.items():
        value = data.get(key, default_value)
        
        # Normaliser le texte
        value = normalize_field(value)
        
        # Si vide ou trop court, utiliser la valeur par défaut
        if not value or len(value) < 3:
            value = default_value
        
        validated[key] = value
    
    return validated