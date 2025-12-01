import pandas as pd
from src.scraper import setup_driver, extract_article_data
from src.utils import clean_text, detect_language, get_domain_type
from src.llm_processor import extract_fields_with_llm
import logging
import time
import sys

INPUT_FILE = "data/input/urls.csv"
OUTPUT_FILE = "data/output/output_dataset.csv"

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("data/logs/scraping.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

def load_csv_auto_detect():
    """Charge le CSV en détectant automatiquement le délimiteur"""
    delimiters = [',', ';', '\t', '|', ' ']
    
    for delimiter in delimiters:
        try:
            df = pd.read_csv(INPUT_FILE, sep=delimiter, encoding='utf-8')
            
            if len(df.columns) >= 2:
                logging.info(f"✓ Délimiteur détecté : '{delimiter}'")
                logging.info(f"  Colonnes trouvées : {df.columns.tolist()}")
                return df
        except:
            continue
    
    try:
        df = pd.read_csv(INPUT_FILE, encoding='utf-8')
        if len(df.columns) >= 2:
            return df
    except:
        pass
    
    raise ValueError("Impossible de lire le fichier CSV avec les délimiteurs standards")

def detect_columns(df):
    """Détecte automatiquement les colonnes ID et URL"""
    columns = df.columns.tolist()
    
    if len(columns) == 1:
        col_name = columns[0]
        first_val = str(df[col_name].iloc[0])
        if ' ' in first_val or '\t' in first_val:
            logging.warning("⚠️  Détection d'une seule colonne avec valeurs séparées")
            logging.warning("    Tentative de séparation automatique...")
            
            for sep in [' ', '\t', ';', ',']:
                if sep in first_val:
                    df[['id_temp', 'url_temp']] = df[col_name].str.split(sep, n=1, expand=True)
                    df = df[['id_temp', 'url_temp']]
                    df.columns = ['code', 'lien']
                    logging.info(f"    ✓ Séparation effectuée avec '{sep}'")
                    return 'code', 'lien', df
    
    url_col = None
    for col in columns:
        if any(keyword in col.lower() for keyword in ['url', 'lien', 'link', 'site', 'web']):
            url_col = col
            break
    
    id_col = None
    for col in columns:
        if any(keyword in col.lower() for keyword in ['code', 'id', 'identifiant', 'reference', 'ref']):
            id_col = col
            break
    
    if not id_col and len(columns) >= 1:
        id_col = columns[0]
    if not url_col and len(columns) >= 2:
        url_col = columns[1]
    
    return id_col, url_col, df

def is_content_valid(contenu, titre):
    """Vérifie si le contenu extrait est valide et non une page d'erreur"""
    if not contenu or len(contenu) < 50:
        return False
    
    # Mots-clés indiquant un échec de scraping
    error_keywords = [
        "wahis menu accueil",
        "keyboard_double_arrow_right",
        "retour au tableau de bord",
        "préférences en matière de gestion des cookies",
        "cloudflare",
        "checking if the site connection is secure",
        "just a moment",
        "enable javascript"
    ]
    
    contenu_lower = contenu.lower()
    
    # Vérifier si le contenu contient principalement des mots d'erreur
    error_count = sum(1 for keyword in error_keywords if keyword in contenu_lower)
    
    # Si plus de 2 mots-clés d'erreur ou contenu très court
    if error_count >= 2 or len(contenu) < 100:
        return False
    
    # Vérifier le ratio texte utile / contenu total
    words = contenu.split()
    if len(words) < 30:  # Moins de 30 mots = probablement pas un article
        return False
    
    return True

def main():
    logging.info("🚀 Démarrage du scraping...")
    
    try:
        df_input = load_csv_auto_detect()
        logging.info(f"✓ Fichier chargé : {len(df_input)} URLs à traiter")
    except FileNotFoundError:
        logging.error(f"❌ Fichier introuvable : {INPUT_FILE}")
        return
    except Exception as e:
        logging.error(f"❌ Erreur de lecture du fichier : {e}")
        logging.error("💡 Vérifiez que votre CSV a bien 2 colonnes séparées par , ou ;")
        return
    
    result = detect_columns(df_input)
    if len(result) == 3:
        id_col, url_col, df_input = result
    else:
        id_col, url_col = result[0], result[1]
    
    if not id_col or not url_col:
        logging.error("❌ Impossible de détecter les colonnes ID et URL")
        logging.error(f"Colonnes disponibles : {df_input.columns.tolist()}")
        return
    
    logging.info(f"✓ Colonnes utilisées - ID: '{id_col}', URL: '{url_col}'")
    
    if id_col not in df_input.columns or url_col not in df_input.columns:
        logging.error(f"❌ Colonnes manquantes dans le fichier")
        return
    
    try:
        driver = setup_driver()
        logging.info("✓ Driver Selenium initialisé")
    except Exception as e:
        logging.error(f"❌ Erreur d'initialisation du driver : {e}")
        return

    results = []
    total = len(df_input)
    errors = 0
    skipped = 0

    for idx, row in df_input.iterrows():
        try:
            code = str(row[id_col]).strip()
            url = str(row[url_col]).strip()
            
            if not url.startswith('http'):
                logging.warning(f"⚠️  URL invalide pour {code}: {url}")
                errors += 1
                continue
            
            logging.info(f"\n{'='*60}")
            logging.info(f"[{idx+1}/{total}] Traitement [{code}]")
            logging.info(f"URL: {url}")
            logging.info(f"{'='*60}")

            # Phase 1 : Scraping avec plusieurs tentatives
            max_attempts = 2
            raw_data = None
            
            for attempt in range(max_attempts):
                if attempt > 0:
                    logging.info(f"  → Tentative {attempt + 1}/{max_attempts}")
                    time.sleep(3)  # Attendre entre les tentatives
                
                raw_data = extract_article_data(driver, url)
                
                # Vérifier la validité du contenu
                if is_content_valid(raw_data["contenu"], raw_data["titre"]):
                    logging.info(f"  ✓ Contenu valide récupéré")
                    break
                else:
                    logging.warning(f"  ⚠️ Contenu invalide à la tentative {attempt + 1}")
                    if attempt < max_attempts - 1:
                        logging.info(f"  → Nouvelle tentative...")
            
            # Vérifier si on a un contenu valide
            if not is_content_valid(raw_data["contenu"], raw_data["titre"]):
                logging.error(f"❌ Impossible d'extraire du contenu valide pour {code} après {max_attempts} tentatives")
                logging.error(f"   Contenu récupéré : {raw_data['contenu'][:200]}...")
                errors += 1
                
                # Enregistrer l'échec dans les résultats
                final_row = {
                    "code": code,
                    "url": url,
                    "titre": "Échec du scraping",
                    "contenu": "Le contenu n'a pas pu être extrait (site protégé ou erreur d'accès)",
                    "langue": "inconnu",
                    "nb_caracteres": 0,
                    "nb_mots": 0,
                    "date_publication": "inconnue",
                    "lieu": "inconnu",
                    "maladie": "inconnue",
                    "animal": "inconnu",
                    "source_publication": get_domain_type(url),
                    "resume_50_mots": "Scraping échoué",
                    "resume_100_mots": "Scraping échoué",
                    "resume_150_mots": "Scraping échoué"
                }
                results.append(final_row)
                continue
            
            # Nettoyer le contenu
            contenu_clean = clean_text(raw_data["contenu"])
            
            if len(contenu_clean) < 50:
                logging.warning(f"⚠️  Contenu trop court après nettoyage ({len(contenu_clean)} caractères)")
                contenu_clean = raw_data["contenu"]
            
            langue = detect_language(contenu_clean)
            source_type = get_domain_type(url)

            # Phase 2 : LLM
            logging.info(f"  → Extraction LLM en cours...")
            llm_fields = extract_fields_with_llm(contenu_clean, url)

            nb_caracteres = len(contenu_clean)
            nb_mots = len(contenu_clean.split())

            final_row = {
                "code": code,
                "url": url,
                "titre": raw_data["titre"],
                "contenu": contenu_clean,
                "langue": langue,
                "nb_caracteres": nb_caracteres,
                "nb_mots": nb_mots,
                "date_publication": llm_fields.get("date_publication", "inconnue"),
                "lieu": llm_fields.get("lieu", "inconnu"),
                "maladie": llm_fields.get("maladie", "inconnue"),
                "animal": llm_fields.get("animal", "inconnu"),
                "source_publication": source_type,
                "resume_50_mots": llm_fields.get("resume_50_mots", "Résumé indisponible."),
                "resume_100_mots": llm_fields.get("resume_100_mots", "Résumé indisponible."),
                "resume_150_mots": llm_fields.get("resume_150_mots", "Résumé indisponible.")
            }

            results.append(final_row)
            logging.info(f"  ✅ Traité avec succès")
            logging.info(f"     • Titre: {raw_data['titre'][:50]}...")
            logging.info(f"     • Mots: {nb_mots}")
            logging.info(f"     • Langue: {langue}")

            # Sauvegarde partielle tous les 3 éléments
            if (idx + 1) % 3 == 0:
                pd.DataFrame(results).to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
                logging.info(f"  💾 Sauvegarde intermédiaire ({len(results)} résultats)")

            time.sleep(2)  # Délai entre les requêtes

        except KeyboardInterrupt:
            logging.warning("\n⚠️  Interruption par l'utilisateur")
            break
        except Exception as e:
            logging.error(f"❌ Erreur critique pour la ligne {idx+1} ({code})")
            logging.error(f"   Message: {str(e)}")
            errors += 1
            continue

    # Fermeture propre
    try:
        driver.quit()
        logging.info("\n✓ Driver fermé")
    except:
        pass
    
    # Sauvegarde finale
    if results:
        pd.DataFrame(results).to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
    
    # Résumé final
    success_count = len([r for r in results if r["titre"] != "Échec du scraping"])
    
    logging.info("\n" + "="*60)
    logging.info(f"✅ SCRAPING TERMINÉ")
    logging.info(f"="*60)
    logging.info(f"   • URLs traitées : {total}")
    logging.info(f"   • Succès complets : {success_count}")
    logging.info(f"   • Échecs de scraping : {len(results) - success_count}")
    logging.info(f"   • Erreurs techniques : {errors}")
    logging.info(f"   • Total résultats : {len(results)}")
    logging.info(f"="*60)
    logging.info(f"📁 Fichier de sortie : {OUTPUT_FILE}")
    logging.info(f"="*60)

if __name__ == "__main__":
    main()