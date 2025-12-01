import os
import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import requests

# Récupérer la clé ScrapingBee
SCRAPINGBEE_API_KEY = "8HWG26F8PCZMTQUO0KY3IK0M3FYZVX6P1G57L52MTZ6RIJ6IA7PVTL4ECQP6HPCJJMOF8OIKFCXVZ2C6"

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

def _scrape_with_scrapingbee(url):
    """Fonction de secours via ScrapingBee avec options avancées"""
    if not SCRAPINGBEE_API_KEY:
        logging.warning("🚫 Clé ScrapingBee manquante")
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
            "premium_proxy": "true",  # Proxy premium pour contourner protections
            "stealth_proxy": "true",  # Mode furtif
            "wait": "3000"  # Attendre 3 secondes après le chargement
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
            
            return {
                "url": url,
                "titre": title or "Titre non trouvé",
                "contenu": content or "Contenu non récupéré",
            }
        else:
            logging.warning(f"❌ ScrapingBee erreur HTTP {response.status_code}: {response.text[:200]}")
            return None

    except Exception as e:
        logging.error(f"💥 Erreur ScrapingBee pour {url}: {e}")
        return None

def extract_article_data(driver, url):
    """Extraction avec détection améliorée des sites protégés"""
    
    # Liste des domaines protégés à traiter directement avec ScrapingBee
    PROTECTED_DOMAINS = ["wahis.woah.org", "alyaum.com", "elfagr.org"]
    
    # Vérifier si c'est un site protégé connu
    if any(domain in url for domain in PROTECTED_DOMAINS):
        logging.info(f"🔒 Site protégé détecté : {url}")
        logging.info(f"→ Utilisation directe de ScrapingBee...")
        fallback = _scrape_with_scrapingbee(url)
        if fallback:
            return fallback
        else:
            logging.warning(f"⚠️ ScrapingBee échoué, tentative Selenium...")
            # Continuer avec Selenium en cas d'échec
    
    try:
        driver.get(url)
        
        # Attendre plus longtemps pour les sites dynamiques
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            # Attendre que le JavaScript se charge
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

        # Extraire le titre avec plusieurs stratégies
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

        # Si pas de titre trouvé, chercher dans les meta tags
        if not title:
            try:
                soup = BeautifulSoup(driver.page_source, "html.parser")
                meta_title = soup.find("meta", property="og:title")
                if meta_title:
                    title = meta_title.get("content", "").strip()
                    logging.info(f"✓ Titre trouvé dans meta og:title")
            except:
                pass

        # Extraire le contenu avec plusieurs stratégies
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

        result = {
            "url": url,
            "titre": title or "Titre non trouvé",
            "contenu": content or "Contenu non récupéré",
        }

        # Vérifier si c'est une page de protection anti-bot
        HUMAN_CHECK_PHRASES = [
            "vérifions que vous êtes humain",
            "checking if the site connection is secure",
            "cloudflare",
            "must verify you are human",
            "sécurité de votre connexion",
            "just a moment",
            "checking your browser",
            "please wait",
            "enable javascript"
        ]
        
        contenu_lower = result["contenu"].lower()
        titre_lower = result["titre"].lower()

        # Si détection de protection ET contenu court
        is_protected = any(phrase in contenu_lower or phrase in titre_lower for phrase in HUMAN_CHECK_PHRASES)
        is_short = len(result["contenu"]) < 200
        
        if is_protected and is_short:
            logging.info(f"🔍 Protection anti-bot détectée pour {url}")
            logging.info(f"→ Tentative avec ScrapingBee...")
            fallback = _scrape_with_scrapingbee(url)
            if fallback and len(fallback["contenu"]) > len(result["contenu"]):
                logging.info(f"✅ ScrapingBee a récupéré plus de contenu ({len(fallback['contenu'])} vs {len(result['contenu'])} caractères)")
                return fallback
            else:
                logging.warning(f"⚠️ ScrapingBee n'a pas amélioré le résultat")
                return result
        else:
            return result

    except Exception as e:
        logging.error(f"💥 Erreur dans extract_article_data pour {url}: {e}")
        
        # Tentative finale avec ScrapingBee en cas d'erreur
        logging.info(f"→ Tentative de récupération avec ScrapingBee...")
        fallback = _scrape_with_scrapingbee(url)
        if fallback:
            return fallback
        
        return {
            "url": url,
            "titre": "Erreur",
            "contenu": f"Erreur lors du scraping : {str(e)}"
        }