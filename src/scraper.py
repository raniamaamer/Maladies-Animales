from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import logging
import os
import requests
from urllib.parse import urlparse
import json

# Configurer le logging
logging.basicConfig(level=logging.INFO)

# ⚙️ Configurable : définissez le chemin de chromedriver ici
CHROMEDRIVER_PATH = r"C:\tools\chromedriver.exe"  # Modifiez ce chemin selon votre système

# 🔑 Clé API ScrapingBee (à remplacer par la vôtre)
SCRAPINGBEE_API_KEY = "1LUZP88NNZZ2ODI23R376AN6JIBU0W9IRIPSZT7JXVDHG6XD3MGCMCTNMUSWJOS74P45MSVCSEV3EMVK"

# 🛡️ Domaines connus comme protégés par Cloudflare (ou bloquants pour Selenium)
CLOUDFLARE_DOMAINS = {
    "www.elfagr.org",
    "www.alyaum.com",
    "www.woodtv.com",
    "www.nouvelles-du-monde.com",
    "equusmagazine.com"
}

# 🍪 Fichier de cookies
COOKIES_FILE = "cookies.json"


def load_cookies(driver):
    """Charge les cookies depuis un fichier JSON si disponible."""
    if os.path.exists(COOKIES_FILE):
        try:
            with open(COOKIES_FILE, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
                for cookie in cookies:
                    try:
                        # Certains champs peuvent causer des erreurs, on les filtre
                        cookie_dict = {
                            'name': cookie.get('name'),
                            'value': cookie.get('value'),
                            'domain': cookie.get('domain'),
                            'path': cookie.get('path', '/'),
                        }
                        # Ajout optionnel de champs si présents
                        if 'expiry' in cookie:
                            cookie_dict['expiry'] = cookie['expiry']
                        if 'secure' in cookie:
                            cookie_dict['secure'] = cookie['secure']
                        if 'httpOnly' in cookie:
                            cookie_dict['httpOnly'] = cookie['httpOnly']
                        
                        driver.add_cookie(cookie_dict)
                    except Exception as e:
                        logging.warning(f"Impossible d'ajouter le cookie {cookie.get('name')}: {e}")
            logging.info(f"✅ Cookies chargés depuis {COOKIES_FILE}")
        except Exception as e:
            logging.error(f"Erreur lors du chargement des cookies: {e}")
    else:
        logging.info(f"ℹ️ Aucun fichier de cookies trouvé ({COOKIES_FILE})")


def save_cookies(driver):
    """Sauvegarde les cookies actuels dans un fichier JSON."""
    try:
        cookies = driver.get_cookies()
        with open(COOKIES_FILE, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, indent=2)
        logging.info(f"✅ Cookies sauvegardés dans {COOKIES_FILE}")
    except Exception as e:
        logging.error(f"Erreur lors de la sauvegarde des cookies: {e}")


def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--lang=fr")
    options.add_argument("--disable-images")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    if CHROMEDRIVER_PATH and os.path.exists(CHROMEDRIVER_PATH):
        service = Service(executable_path=CHROMEDRIVER_PATH)
        logging.info(f"Utilisation de ChromeDriver manuel : {CHROMEDRIVER_PATH}")
    else:
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            logging.info("Téléchargement automatique de ChromeDriver via webdriver-manager...")
            service = Service(ChromeDriverManager().install())
        except ImportError:
            raise ImportError(
                "webdriver-manager n'est pas installé et aucun ChromeDriver manuel n'est fourni.\n"
                "Installez-le avec : pip install webdriver-manager\n"
                "OU définissez un chemin valide dans CHROMEDRIVER_PATH."
            )

    driver = webdriver.Chrome(service=service, options=options)
    return driver


def extract_with_scrapingbee(url):
    """Utilise ScrapingBee pour contourner Cloudflare."""
    logging.info(f"Utilisation de ScrapingBee pour : {url}")
    try:
        response = requests.get(
            "https://app.scrapingbee.com/api/v1/",
            params={
                "api_key": SCRAPINGBEE_API_KEY,
                "url": url,
                "render_js": "true",
                "wait": "3000",
                "premium_proxy": "true",
                "country_code": "fr"
            },
            timeout=30
        )
        if response.status_code == 200:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")
            # Titre
            title = None
            for tag in ["h1", "title"]:
                elem = soup.find(tag)
                if elem and elem.get_text(strip=True):
                    title = elem.get_text(strip=True)
                    break
            # Contenu
            content = ""
            for selector in ["article", ".article-content", ".post-content", "main", "#content", "body"]:
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
                "contenu": content or "Contenu non récupéré (ScrapingBee)"
            }
        else:
            logging.error(f"ScrapingBee error {response.status_code}: {response.text}")
            return {
                "url": url,
                "titre": "Erreur ScrapingBee",
                "contenu": f"Status {response.status_code}"
            }
    except Exception as e:
        logging.error(f"Exception ScrapingBee pour {url}: {e}")
        return {
            "url": url,
            "titre": "Erreur ScrapingBee",
            "contenu": str(e)
        }


def extract_article_data(driver, url):
    # 🔍 Détecter si le domaine nécessite ScrapingBee
    domain = urlparse(url).netloc
    if domain in CLOUDFLARE_DOMAINS:
        return extract_with_scrapingbee(url)

    # 🧾 Sinon, utiliser Selenium comme avant (INCHANGÉ)
    try:
        logging.info(f"Chargement de l'URL : {url}")
        driver.get(url)
        
        # 🍪 Charger les cookies après le premier chargement de la page
        load_cookies(driver)
        
        # Recharger la page avec les cookies
        driver.refresh()
        time.sleep(2)

        # Extraction du titre
        title = None
        title_selectors = ["h1", "header h1", ".article-title", ".post-title", "title"]
        for selector in title_selectors:
            try:
                elem = driver.find_element(By.CSS_SELECTOR, selector)
                title = elem.text.strip()
                if title:
                    break
            except Exception:
                continue

        # Extraction du contenu principal
        content = ""
        content_selectors = ["article", ".article-content", ".post-content", "main", "#content", "body"]
        for selector in content_selectors:
            try:
                elem = driver.find_element(By.CSS_SELECTOR, selector)
                content = elem.text.strip()
                if content:
                    break
            except Exception:
                continue

        # Dernier recours : tout le corps de la page
        if not content:
            try:
                body = driver.find_element(By.TAG_NAME, "body")
                content = body.text.strip()
            except Exception:
                content = ""

        # 🍪 Sauvegarder les cookies à la fin
        save_cookies(driver)

        return {
            "url": url,
            "titre": title or "Titre non trouvé",
            "contenu": content or "Contenu non récupéré",
        }

    except Exception as e:
        logging.error(f"Erreur lors du scraping de {url}: {str(e)}")
        return {
            "url": url,
            "titre": "Erreur",
            "contenu": "Erreur lors du scraping",
        }