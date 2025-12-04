import re
from langdetect import detect, LangDetectException
from bs4 import BeautifulSoup
from datetime import datetime
import logging

def clean_text(html_content: str) -> str:
    """Nettoie le contenu HTML"""
    soup = BeautifulSoup(html_content, "lxml")
    for script in soup(["script", "style"]):
        script.decompose()
    text = soup.get_text(separator=' ')
    
    # Normaliser espaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Supprimer caractères corrompus
    text = re.sub(r'[^\w\s\d.,!?;:()\[\]{}«»""\'\-—–/@#$%&*+=<>|\\\/\u0600-\u06FF\u0750-\u077F\u0590-\u05FF\u0400-\u04FF\u00C0-\u017F]', ' ', text, flags=re.UNICODE)
    
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def detect_language(text: str) -> str:
    """Détecte la langue avec priorité scripts non-latins"""
    if not text or len(text.strip()) < 10:
        return "unknown"
    
    try:
        # Détection par script
        if re.search(r'[\u0600-\u06FF]', text):
            return "ar"
        if re.search(r'[\u0400-\u04FF]', text):
            return "ru"
        if re.search(r'[\u0590-\u05FF]', text):
            return "he"
        if re.search(r'[\u4E00-\u9FFF]', text):
            return "zh"
        
        # Détection standard
        sample = text[:1500]
        lang = detect(sample)
        return lang
    except:
        return "unknown"

def get_domain_type(url: str) -> str:
    """Détermine le type de source"""
    if not url:
        return "médias"
    
    url_lower = url.lower()
    
    # Sites officiels
    if any(site in url_lower for site in ['wahis', 'woah', 'who.int', 'fao.org', 'oie.int']):
        return "site officiel"
    
    # Sites gouvernementaux
    if any(ext in url_lower for ext in ['.gov', '.gouv', '.gob']):
        return "site officiel"
    
    return "médias"

def extract_date_from_content(content: str, url: str = None) -> str:
    """
    Extrait la date de publication du contenu HTML ou texte.
    Retourne la date au format JJ/MM/AAAA ou "inconnue".
    """
    if not content:
        return "inconnue"
    
    # Patterns de dates à rechercher (ordre de priorité)
    date_patterns = [
        # Format ISO : 2023-10-19, 2023/10/19
        r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})',
        # Format français : 19/10/2023, 19-10-2023
        r'(\d{1,2})[-/](\d{1,2})[-/](\d{4})',
        # Format avec mois texte : 19 octobre 2023, Oct 19, 2023, October 19, 2023
        r'(\d{1,2})\s+(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre|january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[,\s]+(\d{4})',
        # Format américain : Oct 19, 2023
        r'(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+(\d{1,2}),?\s+(\d{4})',
    ]
    
    months_map = {
        'janvier': '01', 'january': '01', 'jan': '01',
        'février': '02', 'february': '02', 'feb': '02',
        'mars': '03', 'march': '03', 'mar': '03',
        'avril': '04', 'april': '04', 'apr': '04',
        'mai': '05', 'may': '05',
        'juin': '06', 'june': '06', 'jun': '06',
        'juillet': '07', 'july': '07', 'jul': '07',
        'août': '08', 'august': '08', 'aug': '08',
        'septembre': '09', 'september': '09', 'sep': '09',
        'octobre': '10', 'october': '10', 'oct': '10',
        'novembre': '11', 'november': '11', 'nov': '11',
        'décembre': '12', 'december': '12', 'dec': '12'
    }
    
    # Chercher dans les 2000 premiers caractères (généralement l'en-tête)
    search_content = content[:2000].lower()
    
    for pattern in date_patterns:
        matches = re.finditer(pattern, search_content, re.IGNORECASE)
        for match in matches:
            try:
                groups = match.groups()
                
                # Format ISO ou français
                if len(groups) == 3:
                    if int(groups[0]) > 31:  # Format AAAA-MM-JJ
                        year, month, day = groups
                    else:  # Format JJ-MM-AAAA
                        day, month, year = groups
                    
                    day = day.zfill(2)
                    month = month.zfill(2)
                    
                    # Validation
                    if 1 <= int(day) <= 31 and 1 <= int(month) <= 12 and 2000 <= int(year) <= 2025:
                        return f"{day}/{month}/{year}"
                
                # Format avec mois texte
                elif len(groups) == 2:
                    day_or_month = groups[0]
                    year = groups[1]
                    
                    # Chercher le nom du mois dans le match complet
                    month_text = match.group(0)
                    for month_name, month_num in months_map.items():
                        if month_name in month_text:
                            day = day_or_month.zfill(2)
                            
                            if 1 <= int(day) <= 31 and 2000 <= int(year) <= 2025:
                                return f"{day}/{month_num}/{year}"
                            break
            
            except (ValueError, IndexError) as e:
                logging.debug(f"Erreur parsing date: {e}")
                continue
    
    # Si aucune date trouvée dans le contenu, essayer l'URL
    if url:
        url_match = re.search(r'/(\d{4})/(\d{1,2})/(\d{1,2})/', url)
        if url_match:
            year, month, day = url_match.groups()
            day = day.zfill(2)
            month = month.zfill(2)
            if 2000 <= int(year) <= 2025:
                return f"{day}/{month}/{year}"
    
    return "inconnue"

def normalize_field(text: str) -> str:
    """Normalise un champ texte"""
    if not text:
        return ""
    
    text = re.sub(r'\s+', ' ', str(text)).strip()
    
    # Corrections encodage
    replacements = {
        'Ã©': 'é', 'Ã¨': 'è', 'Ã ': 'à', 'Ã´': 'ô',
        'Ã®': 'î', 'Ã§': 'ç', 'Ã«': 'ë', 'Ã¯': 'ï',
        'Ã¹': 'ù', 'Ã»': 'û',
    }
    
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    
    return text

def validate_extracted_data(data: dict) -> dict:
    """Valide les données extraites"""
    validated = {}
    
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
        value = normalize_field(value)
        
        if not value or len(value) < 3:
            value = default_value
        
        validated[key] = value
    
    return validated