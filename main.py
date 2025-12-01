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
            
            # Vérifier que le fichier a bien au moins 2 colonnes
            if len(df.columns) >= 2:
                logging.info(f"✓ Délimiteur détecté : '{delimiter}'")
                logging.info(f"  Colonnes trouvées : {df.columns.tolist()}")
                return df
        except:
            continue
    
    # Si aucun délimiteur ne fonctionne, essayer sans spécifier
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
    
    # Si une seule colonne qui contient les deux infos, essayer de séparer
    if len(columns) == 1:
        col_name = columns[0]
        # Vérifier si la colonne contient deux valeurs séparées
        first_val = str(df[col_name].iloc[0])
        if ' ' in first_val or '\t' in first_val:
            logging.warning("⚠️  Détection d'une seule colonne avec valeurs séparées")
            logging.warning("    Tentative de séparation automatique...")
            
            # Essayer de séparer
            for sep in [' ', '\t', ';', ',']:
                if sep in first_val:
                    df[['id_temp', 'url_temp']] = df[col_name].str.split(sep, n=1, expand=True)
                    df = df[['id_temp', 'url_temp']]
                    df.columns = ['code', 'lien']
                    logging.info(f"    ✓ Séparation effectuée avec '{sep}'")
                    return 'code', 'lien', df
    
    # Détecter la colonne URL
    url_col = None
    for col in columns:
        if any(keyword in col.lower() for keyword in ['url', 'lien', 'link', 'site', 'web']):
            url_col = col
            break
    
    # Détecter la colonne ID/Code
    id_col = None
    for col in columns:
        if any(keyword in col.lower() for keyword in ['code', 'id', 'identifiant', 'reference', 'ref']):
            id_col = col
            break
    
    # Par défaut : premières colonnes
    if not id_col and len(columns) >= 1:
        id_col = columns[0]
    if not url_col and len(columns) >= 2:
        url_col = columns[1]
    
    return id_col, url_col, df

def main():
    logging.info("🚀 Démarrage du scraping...")
    
    # Charger le fichier d'entrée avec auto-détection
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
    
    # Détecter les colonnes
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
    
    # Vérifier que les colonnes existent
    if id_col not in df_input.columns or url_col not in df_input.columns:
        logging.error(f"❌ Colonnes manquantes dans le fichier")
        return
    
    # Configuration du driver
    try:
        driver = setup_driver()
        logging.info("✓ Driver Selenium initialisé")
    except Exception as e:
        logging.error(f"❌ Erreur d'initialisation du driver : {e}")
        return

    results = []
    total = len(df_input)
    errors = 0

    for idx, row in df_input.iterrows():
        try:
            code = str(row[id_col]).strip()
            url = str(row[url_col]).strip()
            
            # Vérifier que l'URL est valide
            if not url.startswith('http'):
                logging.warning(f"⚠️  URL invalide pour {code}: {url}")
                errors += 1
                continue
            
            logging.info(f"[{idx+1}/{total}] Traitement [{code}] : {url}")

            # Phase 1 : Scraping
            raw_data = extract_article_data(driver, url)
            contenu_clean = clean_text(raw_data["contenu"])
            
            # Vérifier que le contenu n'est pas vide
            if not contenu_clean or len(contenu_clean) < 50:
                logging.warning(f"⚠️  Contenu trop court pour {code} ({len(contenu_clean)} caractères)")
                
                # Si vraiment vide, utiliser le contenu brut
                if len(contenu_clean) < 10:
                    contenu_clean = raw_data["contenu"]
                
                # Si toujours vide, skipper
                if len(contenu_clean) < 20:
                    logging.error(f"❌ Impossible d'extraire du contenu pour {code}, skip")
                    errors += 1
                    continue
            
            langue = detect_language(contenu_clean)
            source_type = get_domain_type(url)

            # Phase 2 : LLM
            logging.info(f"  → Extraction LLM en cours...")
            llm_fields = extract_fields_with_llm(contenu_clean, url)

            # Compter caractères et mots
            nb_caracteres = len(contenu_clean)
            nb_mots = len(contenu_clean.split())

            # Construire la ligne finale
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
            logging.info(f"  ✓ Traité avec succès ({nb_mots} mots, langue: {langue})")

            # Sauvegarde partielle tous les 5 éléments
            if (idx + 1) % 5 == 0:
                pd.DataFrame(results).to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
                logging.info(f"  💾 Sauvegarde intermédiaire ({len(results)} résultats)")

            time.sleep(1)  # Être gentil avec les serveurs

        except KeyboardInterrupt:
            logging.warning("\n⚠️  Interruption par l'utilisateur")
            break
        except Exception as e:
            logging.error(f"❌ Erreur pour la ligne {idx+1} ({code}) : {str(e)}")
            errors += 1
            # Continuer avec l'URL suivante
            continue

    # Fermeture propre
    try:
        driver.quit()
        logging.info("✓ Driver fermé")
    except:
        pass
    
    # Sauvegarde finale
    if results:
        pd.DataFrame(results).to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
    
    # Résumé final
    logging.info("="*60)
    logging.info(f"✅ Scraping terminé :")
    logging.info(f"   • Succès : {len(results)}/{total} URLs")
    logging.info(f"   • Erreurs : {errors}")
    logging.info(f"📁 Résultats sauvegardés dans : {OUTPUT_FILE}")
    logging.info("="*60)

if __name__ == "__main__":
    main()