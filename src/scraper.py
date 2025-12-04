from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
import logging
import os
import requests
from urllib.parse import urlparse
import json
import re

logging.basicConfig(level=logging.INFO)

CHROMEDRIVER_PATH = r"C:\tools\chromedriver.exe"
SCRAPINGBEE_API_KEY = "1LUZP88NNZZ2ODI23R376AN6JIBU0W9IRIPSZT7JXVDHG6XD3MGCMCTNMUSWJOS74P45MSVCSEV3EMVK"

CLOUDFLARE_DOMAINS = {
    "www.elfagr.org",
    "www.alyaum.com",
    "www.woodtv.com",
    "woodtv.com",
    "www.nouvelles-du-monde.com",
    "equusmagazine.com"
}

COOKIES_FILE = "cookies.json"

def resolve_short_url(url):
    """Résout les URLs raccourcies (lc.cx, bit.ly, etc.)"""
    if any(short in url for short in ['lc.cx', 'bit.ly', 'tinyurl.com', 't.co']):
        try:
            response = requests.head(url, allow_redirects=True, timeout=10)
            resolved_url = response.url
            logging.info(f"✅ URL résolue : {url} → {resolved_url}")
            return resolved_url
        except Exception as e:
            logging.warning(f"⚠️ Impossible de résoudre {url}: {e}")
    return url

def load_cookies(driver):
    """Charge les cookies sauvegardés"""
    if os.path.exists(COOKIES_FILE):
        try:
            with open(COOKIES_FILE, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
                for cookie in cookies:
                    try:
                        cookie_dict = {
                            'name': cookie.get('name'),
                            'value': cookie.get('value'),
                            'domain': cookie.get('domain'),
                            'path': cookie.get('path', '/'),
                        }
                        if 'expiry' in cookie:
                            cookie_dict['expiry'] = cookie['expiry']
                        if 'secure' in cookie:
                            cookie_dict['secure'] = cookie['secure']
                        if 'httpOnly' in cookie:
                            cookie_dict['httpOnly'] = cookie['httpOnly']
                        
                        driver.add_cookie(cookie_dict)
                    except Exception as e:
                        logging.warning(f"Cookie non ajouté {cookie.get('name')}: {e}")
            logging.info(f"✅ Cookies chargés")
        except Exception as e:
            logging.error(f"Erreur cookies: {e}")

def save_cookies(driver):
    """Sauvegarde les cookies actuels"""
    try:
        cookies = driver.get_cookies()
        with open(COOKIES_FILE, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, indent=2)
        logging.info(f"✅ Cookies sauvegardés")
    except Exception as e:
        logging.error(f"Erreur sauvegarde cookies: {e}")

def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--lang=fr")
    options.add_argument("--disable-images")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    if CHROMEDRIVER_PATH and os.path.exists(CHROMEDRIVER_PATH):
        service = Service(executable_path=CHROMEDRIVER_PATH)
        logging.info(f"Utilisation de ChromeDriver : {CHROMEDRIVER_PATH}")
    else:
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
        except ImportError:
            raise ImportError("webdriver-manager manquant ou ChromeDriver invalide")

    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(30)
    return driver

def extract_with_scrapingbee(url):
    """Utilise ScrapingBee pour contourner Cloudflare"""
    logging.info(f"🐝 ScrapingBee : {url}")
    try:
        response = requests.get(
            "https://app.scrapingbee.com/api/v1/",
            params={
                "api_key": SCRAPINGBEE_API_KEY,
                "url": url,
                "render_js": "true",
                "wait": "5000",
                "premium_proxy": "true",
                "country_code": "fr"
            },
            timeout=45
        )
        if response.status_code == 200:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extraction titre
            title = None
            for tag in ["h1", "title"]:
                elem = soup.find(tag)
                if elem and elem.get_text(strip=True):
                    title = elem.get_text(strip=True)
                    break
            
            # Extraction contenu
            content = ""
            for selector in ["article", ".article-content", ".post-content", "main", "#content"]:
                elem = soup.select_one(selector)
                if elem and elem.get_text(strip=True):
                    content = elem.get_text(strip=True)
                    break
            
            if not content:
                body = soup.find("body")
                content = body.get_text(strip=True) if body else ""
            
            return {
                "url": url,
                "titre": title or "Titre non trouvé (ScrapingBee)",
                "contenu": content or "Contenu vide (ScrapingBee)"
            }
        else:
            logging.error(f"ScrapingBee erreur {response.status_code}")
            return {
                "url": url,
                "titre": "Erreur ScrapingBee",
                "contenu": f"Status {response.status_code}"
            }
    except Exception as e:
        logging.error(f"Exception ScrapingBee {url}: {e}")
        return {
            "url": url,
            "titre": "Erreur ScrapingBee",
            "contenu": str(e)
        }

def extract_article_data(driver, url, max_retries=3):
    # Résoudre URLs raccourcies
    url = resolve_short_url(url)
    
    # Détecter Cloudflare
    domain = urlparse(url).netloc
    if domain in CLOUDFLARE_DOMAINS:
        return extract_with_scrapingbee(url)
    
    # Selenium avec retry
    for attempt in range(max_retries):
        try:
            logging.info(f"📄 Chargement [{attempt+1}/{max_retries}]: {url}")
            driver.get(url)
            
            # Charger cookies
            load_cookies(driver)
            driver.refresh()
            time.sleep(3)
            
            # Extraction titre
            title = None
            title_selectors = ["h1", "header h1", ".article-title", ".post-title", "title"]
            for selector in title_selectors:
                try:
                    elem = driver.find_element(By.CSS_SELECTOR, selector)
                    title = elem.text.strip()
                    if title:   
                        break
                except:
                    continue
            
            # Extraction contenu
            content = ""
            content_selectors = ["article", ".article-content", ".post-content", "main", "#content", "body"]
            for selector in content_selectors:
                try:
                    elem = driver.find_element(By.CSS_SELECTOR, selector)
                    content = elem.text.strip()
                    if content and len(content) > 200:
                        break
                except:
                    continue
            
            # Dernier recours
            if not content or len(content) < 100:
                try:
                    body = driver.find_element(By.TAG_NAME, "body")
                    content = body.text.strip()
                except:
                    content = "Contenu non accessible"
            
            # Sauvegarder cookies
            save_cookies(driver)
            
            return {
                "url": url,
                "titre": title or "Titre non trouvé",
                "contenu": content or "Contenu vide",
            }
        
        except TimeoutException:
            if attempt < max_retries - 1:
                logging.warning(f"⏱️ Timeout {url}, retry {attempt+2}/{max_retries}")
                time.sleep(5)
            else:
                logging.error(f"❌ Timeout définitif : {url}")
                return {
                    "url": url,
                    "titre": "Timeout",
                    "contenu": "Le site n'a pas répondu"
                }
        
        except Exception as e:
            logging.error(f"❌ Erreur scraping {url}: {e}")
            return {
                "url": url,
                "titre": "Erreur",
                "contenu": f"Erreur: {str(e)}"
            }