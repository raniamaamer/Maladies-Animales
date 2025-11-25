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
# ============================================(-t)

os.makedirs('output', exist_ok=True)

# ============================================
# CONFIGURATION SELENIUM
# ============================================

def create_driver():
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
    js_sites = ['wahis.woah.org', 'app.', 'dashboard.', '#',
    'alyoum', 'aljazeera', 'akhbar', 'arab', 'saudi', 'gulf',
    'uae', 'kuwait', 'qatar', 'syria', 'iraq','elfagr', 
    '.sa', '.eg', '.qa', '.ae', '.ma', '.dz']
    needs_js = any(pattern in url for pattern in js_sites)
    
    if needs_js or use_selenium:
        return extract_with_selenium(url)
    else:
        return extract_with_requests(url)

def extract_with_requests(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        print(f"  📥 Téléchargement (requests)...")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        if soup.find('h1'):
            titre = soup.find('h1').get_text(strip=True)
        elif soup.find('title'):
            titre = soup.find('title').get_text(strip=True)
        else:
            titre = "Sans titre"
        
        for script in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            script.decompose()
        
        text = soup.get_text(separator=' ', strip=True)
        text = re.sub(r'\s+', ' ', text).strip()
        
        print(f"  ✅ Texte extrait : {len(text)} caractères")
        return titre, text, soup
        
    except Exception as e:
        print(f"  ❌ Erreur requests : {e}")
        return "", "", None

def extract_with_selenium(url):
    driver = None
    try:
        print(f"  🌐 Téléchargement (Selenium - JS)...")
        driver = create_driver()
        
        if not driver:
            print(f"  ⚠️ Selenium non disponible, tentative avec requests...")
            return extract_with_requests(url)
        
        driver.get(url)
        
        wait = WebDriverWait(driver, 20)
        
        # ===========================
        # CORRECTION ICI ✔✔✔
        # ===========================
        selectors_to_wait = [
            (By.TAG_NAME, 'h1'),
            (By.CLASS_NAME, 'article-body'),
            (By.CLASS_NAME, 'article-details'),
            (By.TAG_NAME, 'article'),
            (By.CLASS_NAME, 'content'),
            (By.ID, 'main'),
            (By.TAG_NAME, 'main')
        ]
        
        for by, selector in selectors_to_wait:
            try:
                wait.until(EC.presence_of_element_located((by, selector)))
                break
            except TimeoutException:
                continue
        
        time.sleep(3)
        
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        if soup.find('h1'):
            titre = soup.find('h1').get_text(strip=True)
        elif soup.find('title'):
            titre = soup.find('title').get_text(strip=True)
        else:
            titre = driver.title or "Sans titre"
        
        for script in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            script.decompose()

        # ===========================
        # CORRECTION EXTRACTION TEXTE ✔✔✔
        # ===========================
        main_blocks = soup.find_all(
            ['article', 'div'],
            class_=['article-body', 'article-details', 'content']
        )

        if main_blocks:
            text = " ".join(block.get_text(" ", strip=True) for block in main_blocks)
        else:
            text = soup.get_text(separator=" ", strip=True)

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
    arabic_chars = re.findall(r'[\u0600-\u06FF]', text)
    
    if len(arabic_chars) > 5:
        return 'arabe'
    
    text_lower = text.lower()
    french_words = [' le ', ' la ', ' les ', ' des ', ' une ', ' dans ', ' pour ']
    english_words = [' the ', ' and ', ' of ', ' in ', ' to ', ' with ']

    fr_count = sum(w in text_lower for w in french_words)
    en_count = sum(w in text_lower for w in english_words)

    if fr_count > en_count:
        return 'français'
    elif en_count > fr_count:
        return 'anglais'
    else:
        return 'autre'

def extract_date(text, soup):
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
    text_lower = text.lower()

    country_patterns = {
        "Tunisie": ["tunisie", "tunisia", "تونس"],
        "Algérie": ["algérie", "algeria", "الجزائر"],
        "Maroc": ["maroc", "morocco", "المغرب"],
        "Libye": ["libye", "libya", "ليبيا"],
        "Égypte": ["egypte", "egypt", "مصر"],
        "Arabie Saoudite": ["saudi", "arabie saoudite", "السعودية", "المملكة العربية السعودية"],
        "Qatar": ["qatar", "قطر"],
        "Émirats Arabes Unis": ["emirates", "uae", "الإمارات"],
        "Bahreïn": ["bahrain", "bahrein", "البحرين"],
        "Koweït": ["kuwait", "الكويت"],
        "Bulgarie": ["bulgaria", "بلغاريا"],
        "Jordanie": ["jordanie", "jordan", "الأردن"],
        "Liban": ["liban", "lebanon", "لبنان"],
        "Syrie": ["syrie", "syria", "سوريا"],
        "Turquie": ["turquie", "turkey", "تركيا"],
        "France": ["france"],
        "Italie": ["italie", "italy"],
        "Espagne": ["espagne", "spain"],
        "Allemagne": ["allemagne", "germany"],
        "Belgique": ["belgique", "belgium"],
        "Canada": ["canada"],
        "USA": ["usa", "united states", "états-unis"],
        "Royaume-Uni": ["uk", "united kingdom", "royaume-uni"],
        "Corée du Sud": ["korea", "south korea", "كوريا الجنوبية"],
    }

    city_patterns = {
        "Riyadh": ["riyadh", "الرياض"],
        "Jeddah": ["jeddah", "جدة"],
        "Sfax": ["sfax", "صفاقس"],
        "Tunis": ["tunis", "تونس"],
        "Kairouan": ["kairouan", "القيروان"],
        "Casablanca": ["casablanca", "الدار البيضاء"],
        "Rabat": ["rabat", "الرباط"],
        "Tripoli": ["tripoli", "طرابلس"],
        "Le Caire": ["cairo", "القاهرة", "caire"],
        "East Boston": ["east boston"],
        "Damiette": ["damietta", "دمياط"],
        "Sharqia": ["sharqia", "الشرقية"],
        "Zagazig": ["zagazig", "الزقازيق"],
        "Ismaïlia": ["ismailia", "الإسماعيلية"],
        "Port-Saïd": ["port said", "بورسعيد"],
        "Suez": ["suez", "السويس"],
        "Gizeh": ["giza", "الجيزة","محافظ الجيزة"],
        "Qalyubia": ["qalyubia", "القليوبية"],
        "Assouan": ["aswan", "أسوان"],
        "Louxor": ["luxor", "الأقصر"],
        "Sohag": ["sohag", "سوهاج"],
        "Assiout": ["asyut", "أسيوط"],
        "Minya": ["minya", "المنيا"],
        "Beheira": ["beheira", "البحيرة"],
        "Kafr el-Cheikh": ["kafr el-sheikh", "كفر الشيخ"],
        "Daqahliya": ["daqahliya", "الدقهلية"],
        "Alexandrie": ["alexandria", "الإسكندرية"],
        "Sinaï du Nord": ["north sinai", "شمال سيناء"],
        "Cheikh Zuweid": ["sheikh zuweid", "الشيخ زويد"],
        "Rafah": ["rafah", "رفح"],
    }

    for country, patterns in country_patterns.items():
        for p in patterns:
            if p.lower() in text_lower:
                return country

    for city, patterns in city_patterns.items():
        for p in patterns:
            if p.lower() in text_lower:
                return city

    return "Non spécifié"

def extract_disease(text, langue):
    text_lower = text.lower()
    diseases = {
        "Anthrax": ["anthrax", "الجمرة الخبيثة", "炭疽"],
        "Fièvre de la Vallée du Rift": ["rift valley fever", "rvf", "حمى وادي المتصدع", "حمى وادي الصدع"],
        "Fièvre Catarrhale / Bluetongue": ["bluetongue", "blue tongue", "fièvre catarrhale", "اللسان الأزرق"],
        "Brucellose (Brucella)": ["brucella", "brucellose", "brucellosis", "البروسيلا", "حمى مالطية"],
        "Grippe équine (Equine Influenza)": [
            "equine influenza", "grippe équine", "انفلونزا الخيول", "influenza equina"
        ],
        "SARS-CoV-2 / COVID-19": [
            "sars-cov-2", "covid-19", "covid19", "coronavirus", "فيروس كورونا", "كوفيد-19",
            "covid chez les animaux", "sars cov 2 chez les animaux"
        ],
        "Rage": ["rabies", "rage", "داء الكلب"],
        "Fièvre Aphteuse": ["foot and mouth disease", "fmd", "fièvre aphteuse", "الحمى القلاعية"],
        "Maladie de Newcastle": ["newcastle disease", "newcastle", "مرض نيوكاسل", "نيوكاسل"],
        "Maladie d'Aujeszky": ["aujeszky", "pseudorabies", "مرض أويزكي", "أويزكي"],
        "Heartwater": ["heartwater", "ehrlichia ruminantium", "إيرليشيا"],
        "EHD / Maladie hémorragique épizootique": [
            "epizootic hemorrhagic disease", "epizootic haemorrhagic disease",
            "maladie hémorragique épizootique", "maladie hemorragique epizootique",
            "hémorragique épizootique", "hemorragique epizootique",
            "hémorragique épidémique", "hemorragique epidemique",
            "maladie hémorragique épidémique",
            "مرض النزف الوبائي", "مرض نزيف وبائي", "المرض النزفي الوبائي"
        ],
        "Fièvre de West Nile": ["fièvre de west nile", "west nile fever", "حمى غرب النيل"],
        "Dermatose Nodulaire Contagieuse (LSD)": [
            "lumpy skin disease", "lsd", "الجلد العقدي",
            "dermatose nodulaire contagieuse (inf. par le virus de la)",
            "dermatose nodulaire contagieuse", "dermatose nodulaire"
        ],
        "Tuberculose": ["tuberculose", "tuberculosis", "السل"],
        "Trypanosomose (Surra)": ["trypanosoma evansi", "surra", "تريبانوسوما", "سورا"],
        "Tularemia": ["tularemia", "tularemie", "تالاريميا"],
        "Anaplasmose bovine": ["anaplasmosis", "anaplasmose", "أنابلازما"],
        "Babésiose": ["babesiosis", "babésiose", "بابيزيا"],
        "Nécrose hématopoïétique infectieuse": [
            "nécrose hématopoïétique infectieuse", "infectious hematopoietic necrosis",
            "مرض النخر الدموي المعدي"
        ],
        "Échinococcose / Hydatidose": ["echinococcus", "hydatidose", "echinococcosis", "إشينوكوكس"],
        "Peste des Petits Ruminants": ["peste des petits ruminants", "ppr", "طاعون المجترات الصغيرة"],
        "Peste Porcine Africaine": ["african swine fever", "asf", "الحمى الأفريقية للخنازير"],
        "Peste Porcine Classique": ["classical swine fever", "csf", "حمى الخنازير الكلاسيكية"],
        "Peste Équine": ["equine plague", "طاعون الخيل"],
        "Peste":["plague", "peste", "الطاعون"," مرض طاعون"],
        "Peste Aviaire (Influenza Aviaire)": [
            "avian influenza", "influenza aviaire", "bird flu", "انفلونزا الطيور", "إنفلونزا الطّيور"
        ],
        "Fièvre Hémorragique Crimée-Congo": [
            "crimean congo hemorrhagic fever", "cchf", "حمى القرم الكونغو النزفية"
        ],
        "Rinderpest": ["rinderpest", "peste bovine", "طاعون الأبقار"],
        "Paratuberculose": ["paratuberculosis", "paratuberculose", "باراتوبركولوز"],
        "Clavelée et variole caprine": [
            "clavelée", "clavele", "variole caprine", "variole ovine",
            "sheep pox", "goat pox", "sheeppox", "goatpox",
            "جدري الأغنام", "جدري الماعز", "الجدري"
        ],
        "Aethina tumida": [
            "aethina tumida", "petit coléoptère des ruches", "petit coléoptère de la ruche",
            "small hive beetle", "shb", "خنفساء الخلية الصغيرة"
        ]
    }
    
    for disease, keywords in diseases.items():
        for kw in keywords:
            if kw.lower() in text_lower:
                return disease
    
    return "Non identifiée"

def detect_source_type(url, text):
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
        
        if len(results) % 5 == 0:
            df_temp = pd.DataFrame(results)
            df_temp.to_csv('output/animal_diseases_dataset.csv', index=False, encoding='utf-8-sig')
            print(f"\n💾 Sauvegarde temporaire : {len(results)} entrées")
        
        time.sleep(1)
    
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
