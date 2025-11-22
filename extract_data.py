import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

# ============================================
# VERSION AMÉLIORÉE - AVEC SELENIUM POUR JS
# ============================================

os.makedirs('output', exist_ok=True)

# ============================================
# CONFIGURATION SELENIUM
# ============================================

def create_driver():
    """Crée un driver Selenium headless"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"❌ Erreur création driver: {e}")
        print("💡 Installez ChromeDriver: pip install chromedriver-autoinstaller")
        return None

# ============================================
# FONCTIONS D'EXTRACTION AMÉLIORÉES
# ============================================

def extract_text_from_url(url, use_selenium=False):
    """Extrait le contenu textuel d'une URL avec option Selenium"""
    
    # Détection des sites nécessitant JavaScript
    js_sites = ['wahis.woah.org', 'app.', 'dashboard.', '#']
    needs_js = any(pattern in url for pattern in js_sites)
    
    if needs_js or use_selenium:
        return extract_with_selenium(url)
    else:
        return extract_with_requests(url)

def extract_with_requests(url):
    """Extraction classique avec requests + BeautifulSoup"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        print(f"  📥 Téléchargement (requests)...")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extraire le titre
        titre = ""
        if soup.find('h1'):
            titre = soup.find('h1').get_text(strip=True)
        elif soup.find('title'):
            titre = soup.find('title').get_text(strip=True)
        else:
            titre = "Sans titre"
        
        # Supprimer scripts et styles
        for script in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            script.decompose()
        
        # Extraire le texte principal
        text = soup.get_text(separator=' ', strip=True)
        text = re.sub(r'\s+', ' ', text).strip()
        
        print(f"  ✅ Texte extrait : {len(text)} caractères")
        return titre, text, soup
        
    except Exception as e:
        print(f"  ❌ Erreur requests : {e}")
        return "", "", None

def extract_with_selenium(url):
    """Extraction avec Selenium pour sites JavaScript"""
    driver = None
    try:
        print(f"  🌐 Téléchargement (Selenium - JS)...")
        driver = create_driver()
        
        if not driver:
            print(f"  ⚠️ Selenium non disponible, tentative avec requests...")
            return extract_with_requests(url)
        
        driver.get(url)
        
        # Attendre que le contenu se charge
        wait = WebDriverWait(driver, 20)
        
        # Attendre différents sélecteurs possibles
        selectors_to_wait = [
            (By.TAG_NAME, 'h1'),
            (By.TAG_NAME, 'article'),
            (By.CLASS_NAME, 'content'),
            (By.ID, 'main'),
            (By.TAG_NAME, 'main')
        ]
        
        content_loaded = False
        for by, selector in selectors_to_wait:
            try:
                wait.until(EC.presence_of_element_located((by, selector)))
                content_loaded = True
                break
            except TimeoutException:
                continue
        
        # Attendre un peu plus pour le JavaScript
        time.sleep(3)
        
        # Récupérer le HTML complet après rendu JavaScript
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extraire le titre
        titre = ""
        if soup.find('h1'):
            titre = soup.find('h1').get_text(strip=True)
        elif soup.find('title'):
            titre = soup.find('title').get_text(strip=True)
        else:
            titre = driver.title or "Sans titre"
        
        # Supprimer scripts et styles
        for script in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            script.decompose()
        
        # Extraire le texte principal
        text = soup.get_text(separator=' ', strip=True)
        text = re.sub(r'\s+', ' ', text).strip()
        
        print(f"  ✅ Texte extrait : {len(text)} caractères")
        
        return titre, text, soup
        
    except Exception as e:
        print(f"  ❌ Erreur Selenium : {e}")
        return "", "", None
    finally:
        if driver:
            driver.quit()

def detect_language(text):
    """Détecte la langue du texte"""
    arabic_chars = re.findall(r'[\u0600-\u06FF]', text)
    if len(arabic_chars) > 20:
        return 'arabe'
    
    text_lower = text.lower()
    french_words = ['le', 'la', 'les', 'de', 'des', 'et', 'dans', 'pour', 'est', 'une', 'sur']
    english_words = ['the', 'and', 'of', 'in', 'to', 'for', 'with', 'is', 'at', 'by', 'on']
    
    french_count = sum(1 for word in french_words if f' {word} ' in text_lower)
    english_count = sum(1 for word in english_words if f' {word} ' in text_lower)
    
    if french_count > english_count:
        return 'français'
    elif english_count > french_count:
        return 'anglais'
    else:
        return 'autre'

def extract_date(text, soup):
    """Tente d'extraire la date de publication"""
    date_patterns = [
        r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',
        r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',
        r'(\d{1,2})\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+(\d{4})',
        r'(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})',
    ]
    
    months_fr = {
        'janvier': '01', 'février': '02', 'mars': '03', 'avril': '04',
        'mai': '05', 'juin': '06', 'juillet': '07', 'août': '08',
        'septembre': '09', 'octobre': '10', 'novembre': '11', 'décembre': '12'
    }
    
    months_en = {
        'january': '01', 'february': '02', 'march': '03', 'april': '04',
        'may': '05', 'june': '06', 'july': '07', 'august': '08',
        'september': '09', 'october': '10', 'november': '11', 'december': '12'
    }
    
    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            groups = match.groups()
            if len(groups) == 3:
                if groups[1].lower() in months_fr:
                    return f"{groups[0].zfill(2)}-{months_fr[groups[1].lower()]}-{groups[2]}"
                elif groups[1].lower() in months_en:
                    return f"{groups[0].zfill(2)}-{months_en[groups[1].lower()]}-{groups[2]}"
                elif groups[0].isdigit() and groups[1].isdigit():
                    return f"{groups[0].zfill(2)}-{groups[1].zfill(2)}-{groups[2]}"
    
    return "01-01-2025"

def extract_location(text):
    """Extrait les lieux mentionnés"""
    countries = [
        'France', 'Tunisie', 'Algérie', 'Maroc', 'Belgique', 'Suisse', 
        'Canada', 'Espagne', 'Italie', 'Allemagne', 'UK', 'USA',
        'Égypte', 'Turquie', 'Liban', 'Syrie', 'Jordanie', 'Libye',
        'Corée', 'Korea', 'République de Corée'
    ]
    
    for country in countries:
        if country.lower() in text.lower():
            return country
    
    return "Non spécifié"

def extract_disease(text, langue):
    """Extrait le nom de la maladie"""
    diseases = {
        'Grippe Aviaire': ['grippe aviaire', 'influenza aviaire', 'bird flu', 'avian influenza', 'h5n1', 'h5n8'],
        'Peste Porcine Africaine': ['peste porcine', 'african swine fever', 'asf'],
        'Fièvre Aphteuse': ['fièvre aphteuse', 'foot and mouth', 'fmd'],
        'Fièvre Catarrhale': ['bluetongue', 'fièvre catarrhale', 'blue tongue'],
        'Rage': ['rage', 'rabies'],
        'Brucellose': ['brucellose', 'brucellosis'],
        'Dermatose Nodulaire': ['lumpy skin', 'dermatose nodulaire', 'lsd', 'dermatose nodulaire contagieuse'],
        'Maladie de Newcastle': ['newcastle', 'pseudo-peste'],
        'Tuberculose Bovine': ['tuberculose bovine', 'bovine tuberculosis'],
        'Salmonellose': ['salmonelle', 'salmonella'],
    }
    
    text_lower = text.lower()
    
    for disease, keywords in diseases.items():
        for keyword in keywords:
            if keyword in text_lower:
                return disease
    
    return "Non identifiée"

def detect_source_type(url, text):
    """Détecte le type de source"""
    official_domains = ['gouv', 'gov', 'who', 'woah', 'oie', 'fao', 'europa.eu', 'cdc']
    media_keywords = ['journal', 'news', 'presse', 'radio', 'tv', 'média', 'media']
    social_domains = ['facebook', 'twitter', 'instagram', 'linkedin']
    
    url_lower = url.lower()
    text_lower = text.lower()
    
    for domain in official_domains:
        if domain in url_lower:
            return "site officiel"
    
    for domain in social_domains:
        if domain in url_lower:
            return "réseaux sociaux"
    
    for keyword in media_keywords:
        if keyword in text_lower[:500]:
            return "médias"
    
    return "médias"

def create_summary(text, word_count):
    """Crée un résumé du texte"""
    words = text.split()
    
    if len(words) <= word_count:
        return text
    
    summary_words = words[:word_count]
    summary = ' '.join(summary_words)
    
    last_period = summary.rfind('.')
    if last_period > 0:
        summary = summary[:last_period + 1]
    
    return summary

def extract_named_entities(text):
    """Extrait les entités nommées"""
    entities = []
    
    orgs = ['OMS', 'WHO', 'FAO', 'OIE', 'WOAH', 'ministère', 'Ministry', 'APQA']
    for org in orgs:
        if org.lower() in text.lower():
            entities.append(org)
    
    animals = ['bovins', 'volailles', 'porcs', 'poulets', 'cattle', 'poultry', 'pigs', 'chickens']
    for animal in animals:
        if animal.lower() in text.lower():
            entities.append(animal)
    
    return list(set(entities))

# ============================================
# TRAITEMENT PRINCIPAL
# ============================================

def main():
    print("=" * 70)
    print("🦠 EXTRACTION DES NEWS SUR LES MALADIES ANIMALES")
    print("🚀 VERSION AMÉLIORÉE - AVEC SUPPORT JAVASCRIPT (SELENIUM)")
    print("=" * 70)
    
    print("\n📂 Chargement des URLs...")
    df_urls = pd.read_csv('urls.csv')
    print(f"✅ {len(df_urls)} URLs chargées")
    
    # Test Selenium au démarrage
    print("\n🧪 Test de Selenium...")
    test_driver = create_driver()
    if test_driver:
        print("✅ Selenium opérationnel")
        test_driver.quit()
    else:
        print("⚠️ Selenium non disponible - utilisation de requests uniquement")
    
    results = []
    
    for idx, row in df_urls.head(50).iterrows():
        code = row['code']
        url = row['url']
        
        print(f"\n{'='*70}")
        print(f"📄 [{idx+1}/50] Traitement de {code}")
        print(f"{'='*70}")
        print(f"🔗 {url}")
        
        titre, text, soup = extract_text_from_url(url)
        
        if not text or len(text) < 100:
            print(f"  ⚠️ Contenu insuffisant ({len(text)} caractères), passage au suivant")
            
            # Sauvegarder quand même avec un marqueur
            results.append({
                'code': code,
                'url': url,
                'titre': 'ERREUR: Contenu insuffisant',
                'contenu': text,
                'langue': 'N/A',
                'nb_caracteres': len(text),
                'nb_mots': 0,
                'date_publication': 'N/A',
                'lieu': 'N/A',
                'maladie': 'N/A',
                'source_type': 'N/A',
                'resume_50': '',
                'resume_100': '',
                'resume_150': '',
                'entites_nommees': ''
            })
            continue
        
        langue = detect_language(text)
        print(f"  🌍 Langue : {langue}")
        
        nb_mots = len(text.split())
        nb_caracteres = len(text)
        print(f"  📊 {nb_mots} mots, {nb_caracteres} caractères")
        
        date_pub = extract_date(text, soup)
        print(f"  📅 Date : {date_pub}")
        
        lieu = extract_location(text)
        print(f"  📍 Lieu : {lieu}")
        
        maladie = extract_disease(text, langue)
        print(f"  🦠 Maladie : {maladie}")
        
        source_type = detect_source_type(url, text)
        print(f"  📰 Source : {source_type}")
        
        resume_50 = create_summary(text, 50)
        resume_100 = create_summary(text, 100)
        resume_150 = create_summary(text, 150)
        
        entites = extract_named_entities(text)
        
        result = {
            'code': code,
            'url': url,
            'titre': titre,
            'contenu': text,
            'langue': langue,
            'nb_caracteres': nb_caracteres,
            'nb_mots': nb_mots,
            'date_publication': date_pub,
            'lieu': lieu,
            'maladie': maladie,
            'source_type': source_type,
            'resume_50': resume_50,
            'resume_100': resume_100,
            'resume_150': resume_150,
            'entites_nommees': ';'.join(entites)
        }
        
        results.append(result)
        print(f"  ✅ Données enregistrées")
        
        # Sauvegarde temporaire
        if len(results) % 5 == 0:
            df_temp = pd.DataFrame(results)
            df_temp.to_csv('output/animal_diseases_dataset.csv', index=False, encoding='utf-8-sig')
            print(f"\n💾 Sauvegarde temporaire : {len(results)} entrées")
        
        time.sleep(1)  # Pause entre requêtes
    
    print("\n" + "=" * 70)
    print("💾 SAUVEGARDE DU DATASET FINAL")
    print("=" * 70)
    
    df_final = pd.DataFrame(results)
    output_file = 'output/animal_diseases_dataset.csv'
    df_final.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"\n✅ Dataset sauvegardé : {output_file}")
    print(f"📊 Total d'entrées : {len(df_final)}")
    
    print("\n" + "=" * 70)
    print("📈 STATISTIQUES DU DATASET")
    print("=" * 70)
    
    # Filtrer les erreurs pour les stats
    df_valid = df_final[df_final['langue'] != 'N/A']
    
    print(f"\n✅ Entrées valides : {len(df_valid)} / {len(df_final)}")
    print(f"❌ Entrées en erreur : {len(df_final) - len(df_valid)}")
    
    if len(df_valid) > 0:
        print(f"\n🌍 Répartition par langue :")
        print(df_valid['langue'].value_counts())
        
        print(f"\n📰 Répartition par type de source :")
        print(df_valid['source_type'].value_counts())
        
        print(f"\n🦠 Top 10 des maladies :")
        print(df_valid['maladie'].value_counts().head(10))
        
        print(f"\n📍 Top 10 des lieux :")
        print(df_valid['lieu'].value_counts().head(10))
        
        print(f"\n📝 Statistiques sur les mots :")
        print(f"  Moyenne : {df_valid['nb_mots'].mean():.0f}")
        print(f"  Médiane : {df_valid['nb_mots'].median():.0f}")
        print(f"  Min     : {df_valid['nb_mots'].min()}")
        print(f"  Max     : {df_valid['nb_mots'].max()}")
    
    print("\n" + "=" * 70)
    print("✨ TRAITEMENT TERMINÉ AVEC SUCCÈS !")
    print("=" * 70)

if __name__ == "__main__":
    main()