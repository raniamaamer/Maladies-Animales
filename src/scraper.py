import os
import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import requests

# ⚠️ ATTENTION SÉCURITÉ : NE JAMAIS EXPOSER UNE CLÉ API DANS LE CODE !
# Utiliser une variable d'environnement à la place
SCRAPINGBEE_API_KEY = os.getenv("SCRAPINGBEE_API_KEY", "Z6EZC64J4I2EA4WW5Z1X1UA8BKQVFRQ06F4HW26Y2SADBEBMEG691D484AY7MVTGHI9S5TZ8D8UK4TFT")

def setup_driver():
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--lang=fr")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def _detecter_pays_europeens(texte):
    """Détecte les pays européens mentionnés dans le texte"""
    pays_europe = {
        # Pays en anglais
        "Albania": "Albanie", "Andorra": "Andorre", "Austria": "Autriche", 
        "Belarus": "Biélorussie", "Belgium": "Belgique", "Bosnia": "Bosnie-Herzégovine",
        "Bulgaria": "Bulgarie", "Croatia": "Croatie", "Cyprus": "Chypre",
        "Czech": "République tchèque", "Czechia": "République tchèque",
        "Denmark": "Danemark", "Estonia": "Estonie", "Finland": "Finlande",
        "France": "France", "Germany": "Allemagne", "Greece": "Grèce",
        "Hungary": "Hongrie", "Iceland": "Islande", "Ireland": "Irlande",
        "Italy": "Italie", "Kosovo": "Kosovo", "Latvia": "Lettonie",
        "Liechtenstein": "Liechtenstein", "Lithuania": "Lituanie",
        "Luxembourg": "Luxembourg", "Malta": "Malte", "Moldova": "Moldavie",
        "Monaco": "Monaco", "Montenegro": "Monténégro", "Netherlands": "Pays-Bas",
        "North Macedonia": "Macédoine du Nord", "Norway": "Norvège",
        "Poland": "Pologne", "Portugal": "Portugal", "Romania": "Roumanie",
        "Russia": "Russie", "San Marino": "Saint-Marin", "Serbia": "Serbie",
        "Slovakia": "Slovaquie", "Slovenia": "Slovénie", "Spain": "Espagne",
        "Sweden": "Suède", "Switzerland": "Suisse", "Ukraine": "Ukraine",
        "United Kingdom": "Royaume-Uni", "Vatican": "Vatican",
        
        # Pays en français
        "Albanie": "Albanie", "Andorre": "Andorre", "Autriche": "Autriche",
        "Biélorussie": "Biélorussie", "Belgique": "Belgique", 
        "Bosnie-Herzégovine": "Bosnie-Herzégovine", "Bulgarie": "Bulgarie",
        "Croatie": "Croatie", "Chypre": "Chypre", "République tchèque": "République tchèque",
        "Danemark": "Danemark", "Estonie": "Estonie", "Finlande": "Finlande",
        "Allemagne": "Allemagne", "Grèce": "Grèce", "Hongrie": "Hongrie",
        "Islande": "Islande", "Irlande": "Irlande", "Italie": "Italie",
        "Kosovo": "Kosovo", "Lettonie": "Lettonie", "Liechtenstein": "Liechtenstein",
        "Lituanie": "Lituanie", "Malte": "Malte", "Moldavie": "Moldavie",
        "Monténégro": "Monténégro", "Pays-Bas": "Pays-Bas", 
        "Macédoine du Nord": "Macédoine du Nord", "Norvège": "Norvège",
        "Pologne": "Pologne", "Roumanie": "Roumanie", "Russie": "Russie",
        "Saint-Marin": "Saint-Marin", "Serbie": "Serbie", "Slovaquie": "Slovaquie",
        "Slovénie": "Slovénie", "Suède": "Suède", "Suisse": "Suisse",
        "Royaume-Uni": "Royaume-Uni",
        
        # Variantes
        "UK": "Royaume-Uni", "Great Britain": "Royaume-Uni", "Grande-Bretagne": "Royaume-Uni",
        "Holland": "Pays-Bas", "Hollande": "Pays-Bas"
    }
    
    pays_trouves = set()
    texte_lower = texte.lower()
    
    for pays_recherche, pays_fr in pays_europe.items():
        if pays_recherche.lower() in texte_lower:
            pays_trouves.add(pays_fr)
    
    return sorted(list(pays_trouves))

def _scrape_with_scrapingbee(url):
    """Fonction de secours via ScrapingBee avec options avancées"""
    if not SCRAPINGBEE_API_KEY:
        logging.warning("🚫 Clé ScrapingBee manquante - veuillez définir SCRAPINGBEE_API_KEY")
        return None

    logging.info(f"📡 Appel ScrapingBee pour : {url}")
    try:
        # Configuration avancée pour les sites protégés
        params = {
            "api_key": SCRAPINGBEE_API_KEY,
            "url": url,
            "render_js": "true",
            "wait_for": "body",
            "timeout": "20000",
            "premium_proxy": "true",
            "stealth_proxy": "true",
            "wait": "3000"
        }
        
        response = requests.get(
            "https://app.scrapingbee.com/api/v1/",
            params=params,
            timeout=30
        )
        
        if response.status_code == 200:
            logging.info("✅ ScrapingBee : succès")
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Nettoyer les éléments inutiles
            for tag in soup(["script", "style", "nav", "footer", "aside", "header", "iframe"]):
                tag.decompose()
            
            # Extraction du titre avec plusieurs stratégies
            title = None
            title_selectors = [
                "h1",
                ".title",
                "[class*='title']",
                "meta[property='og:title']",
                "meta[name='title']"
            ]
            
            for selector in title_selectors:
                if selector.startswith("meta"):
                    elem = soup.find("meta", attrs={"property": "og:title"} if "og:title" in selector else {"name": "title"})
                    if elem and elem.get("content"):
                        title = elem.get("content").strip()
                        break
                else:
                    elem = soup.select_one(selector)
                    if elem:
                        title = elem.get_text().strip()
                        if title and len(title) > 5:
                            break
            
            # Extraction du contenu principal
            content = ""
            content_selectors = [
                "article",
                "main",
                ".article-content",
                ".content",
                "[role='main']",
                "#content",
                ".post-content"
            ]
            
            for selector in content_selectors:
                elem = soup.select_one(selector)
                if elem:
                    content = elem.get_text(separator=" ", strip=True)
                    if content and len(content) > 100:
                        break
            
            # Si pas de contenu, prendre tout le body
            if not content or len(content) < 100:
                content = soup.get_text(separator=" ", strip=True)
            
            # Détection des pays européens
            pays_europeens = _detecter_pays_europeens(content)
            
            return {
                "url": url,
                "titre": title or "Titre non trouvé",
                "contenu": content or "Contenu non récupéré",
                "pays_europeens": pays_europeens
            }
        else:
            logging.warning(f"❌ ScrapingBee erreur HTTP {response.status_code}: {response.text[:200]}")
            return None

    except requests.RequestException as e:
        logging.error(f"💥 Erreur de connexion ScrapingBee pour {url}: {e}")
        return None
    except Exception as e:
        logging.error(f"💥 Erreur ScrapingBee pour {url}: {e}")
        return None

def extract_article_data(driver, url):
    """Extraction avec ScrapingBee UNIQUEMENT pour elfagr.org et alyaum.com"""
    
    # ScrapingBee UNIQUEMENT pour elfagr.org et alyaum.com
    if "elfagr.org" in url or "alyaum.com" in url:
        logging.info(f"🔒 Site protégé détecté : {url}")
        logging.info(f"→ Utilisation directe de ScrapingBee...")
        fallback = _scrape_with_scrapingbee(url)
        if fallback:
            return fallback
        else:
            logging.warning(f"⚠️ ScrapingBee échoué, tentative Selenium...")
    
    try:
        driver.get(url)
        
        # Attendre plus longtemps pour les sites dynamiques
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(3)
        except TimeoutException:
            logging.warning(f"⚠️ Timeout lors du chargement de {url}")

        # Gérer les popups de cookies
        close_xpaths = [
            "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'accept')]",
            "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'accepter')]",
            "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'ok')]",
            "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'autoriser')]",
            "//a[contains(@class, 'close')]",
            "//button[contains(@class, 'close')]"
        ]
        
        for xpath in close_xpaths:
            try:
                btn = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                driver.execute_script("arguments[0].click();", btn)
                time.sleep(1)
                logging.info("✓ Popup fermé")
                break
            except:
                continue

        # Extraire le titre
        title = None
        title_selectors = [
            "h1",
            ".article-title",
            ".post-title",
            "[class*='title']",
            "h1[class*='heading']",
            ".entry-title"
        ]
        
        for selector in title_selectors:
            try:
                elem = driver.find_element(By.CSS_SELECTOR, selector)
                title = elem.text.strip()
                if title and len(title) > 5:
                    logging.info(f"✓ Titre trouvé avec {selector}: {title[:50]}...")
                    break
            except:
                continue

        # Si pas de titre, chercher dans les meta tags
        if not title:
            try:
                soup = BeautifulSoup(driver.page_source, "html.parser")
                meta_title = soup.find("meta", property="og:title")
                if meta_title:
                    title = meta_title.get("content", "").strip()
                    logging.info(f"✓ Titre trouvé dans meta og:title")
            except:
                pass

        # Extraire le contenu
        content = ""
        content_selectors = [
            "article",
            ".article-content",
            ".post-content",
            "main",
            ".content",
            "[role='main']",
            "#content",
            ".entry-content"
        ]
        
        for selector in content_selectors:
            try:
                elem = driver.find_element(By.CSS_SELECTOR, selector)
                content = elem.text.strip()
                if content and len(content) > 100:
                    logging.info(f"✓ Contenu trouvé avec {selector} ({len(content)} caractères)")
                    break
            except:
                continue

        # Si pas de contenu, prendre le body
        if not content or len(content) < 100:
            try:
                body = driver.find_element(By.TAG_NAME, "body")
                content = body.text.strip()
                logging.info(f"✓ Contenu extrait du body ({len(content)} caractères)")
            except:
                content = ""

        # Dernière tentative avec BeautifulSoup
        if not content or len(content) < 50:
            soup = BeautifulSoup(driver.page_source, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                tag.decompose()
            content = soup.get_text(separator=" ", strip=True)
            logging.info(f"✓ Contenu extrait avec BeautifulSoup ({len(content)} caractères)")

        # Détection des pays européens
        pays_europeens = _detecter_pays_europeens(content)

        return {
            "url": url,
            "titre": title or "Titre non trouvé",
            "contenu": content or "Contenu non récupéré",
            "pays_europeens": pays_europeens
        }

    except Exception as e:
        logging.error(f"💥 Erreur dans extract_article_data pour {url}: {e}")
        
        return {
            "url": url,
            "titre": "Erreur",
            "contenu": f"Erreur lors du scraping : {str(e)}"
        }