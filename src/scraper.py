# src/scraper.py
import os
import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import requests

# Récupérer la clé ScrapingBee (en dur pour test – À RÉVOQUER APRÈS UTILISATION)
SCRAPINGBEE_API_KEY = "8HWG26F8PCZMTQUO0KY3IK0M3FYZVX6P1G57L52MTZ6RIJ6IA7PVTL4ECQP6HPCJJMOF8OIKFCXVZ2C6"

# === Ancienne fonction setup_driver (inchangée) ===
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

# === Fonction de secours via ScrapingBee ===
def _scrape_with_scrapingbee(url):
    if not SCRAPINGBEE_API_KEY:
        logging.warning("🚫 Clé ScrapingBee manquante")
        return None

    logging.info(f"📡 Appel ScrapingBee pour : {url}")
    try:
        response = requests.get(
            "https://app.scrapingbee.com/api/v1/",  # ✅ Supprimé les espaces
            params={
                "api_key": SCRAPINGBEE_API_KEY,      # ✅ Utilisation de la variable, pas une chaîne
                "url": url,
                "render_js": "true",
                "wait_for": "body",
                "timeout": "15000"
            },
            timeout=20
        )
        if response.status_code == 200:
            logging.info("✅ ScrapingBee : succès")
            soup = BeautifulSoup(response.text, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "aside", "header"]):
                tag.decompose()
            title_elem = soup.find("h1")
            title = title_elem.get_text().strip() if title_elem else "Titre non trouvé"
            content = soup.get_text(separator=" ", strip=True)
            return {
                "url": url,
                "titre": title,
                "contenu": content or "Contenu non récupéré",
            }
        else:
            logging.warning(f"❌ ScrapingBee erreur HTTP {response.status_code}: {response.text[:200]}")
            return None

    except Exception as e:
        logging.error(f"💥 Erreur ScrapingBee pour {url}: {e}")
        return None

# === Fonction compatible avec main.py : extract_article_data(driver, url) ===
def extract_article_data(driver, url):
    try:
        driver.get(url)
        
        # Attendre le body
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
        except TimeoutException:
            pass

        # Essayer de fermer les bannières
        close_xpaths = [
            "//button[contains(text(), 'Accept')]",
            "//button[contains(text(), 'Accepter')]",
            "//button[contains(text(), 'OK')]",
            "//button[contains(text(), 'Autoriser')]"
        ]
        for xpath in close_xpaths:
            try:
                btn = driver.find_element(By.XPATH, xpath)
                driver.execute_script("arguments[0].click();", btn)
                time.sleep(0.5)
                break
            except:
                continue

        # Extraire titre
        title = None
        for selector in ["h1", ".article-title", ".post-title", "[class*='title']"]:
            try:
                elem = driver.find_element(By.CSS_SELECTOR, selector)
                title = elem.text.strip()
                if title and len(title) > 5:
                    break
            except:
                continue

        # Extraire contenu
        content = ""
        for selector in ["article", ".article-content", ".post-content", "main"]:
            try:
                elem = driver.find_element(By.CSS_SELECTOR, selector)
                content = elem.text.strip()
                if content and len(content) > 100:
                    break
            except:
                continue

        if not content:
            try:
                body = driver.find_element(By.TAG_NAME, "body")
                content = body.text.strip()
            except:
                content = ""

        if not content or len(content) < 50:
            soup = BeautifulSoup(driver.page_source, "html.parser")
            for tag in soup(["script", "style", "nav", "footer"]):
                tag.decompose()
            content = soup.get_text(separator=" ", strip=True)

        result = {
            "url": url,
            "titre": title or "Titre non trouvé",
            "contenu": content or "Contenu non récupéré",
        }

        # === Vérifier si c'est une page de vérification humaine ===
        HUMAN_CHECK_PHRASES = [
            "vérifions que vous êtes humain",
            "checking if the site connection is secure",
            "cloudflare",
            "must verify you are human",
            "sécurité de votre connexion"
        ]
        contenu_lower = result["contenu"].lower()
        titre_lower = result["titre"].lower()

        if any(phrase in contenu_lower or phrase in titre_lower for phrase in HUMAN_CHECK_PHRASES):
            logging.info(f"🔍 Détection de protection anti-bot pour {url} → tentative ScrapingBee")
            fallback = _scrape_with_scrapingbee(url)
            if fallback:
                return fallback
            else:
                logging.warning(f"⚠️ ScrapingBee échoué pour {url} – utilisation du contenu brut (probablement Cloudflare)")
                return result
        else:
            return result

    except Exception as e:
        logging.error(f"Erreur dans extract_article_data pour {url}: {e}")
        return {
            "url": url,
            "titre": "Erreur",
            "contenu": f"Erreur lors du scraping : {str(e)}"
        }