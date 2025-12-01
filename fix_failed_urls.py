import pandas as pd
import requests
from tqdm import tqdm
import time
import sys

# Configuration des fichiers
OUTPUT_CSV = "data/output/output_dataset.csv"
INPUT_CSV = "data/input/urls.csv"
RETRY_FILE = "data/input/urls_to_retry.csv"
EXPANDED_FILE = "data/input/urls_expanded_retry.csv"

def identify_failed_urls():
    """Identifie les URLs qui ont échoué lors du scraping"""
    
    print("="*70)
    print("🔍 ÉTAPE 1: IDENTIFICATION DES URLs PROBLÉMATIQUES")
    print("="*70)
    print()
    
    try:
        df = pd.read_csv(OUTPUT_CSV, encoding='utf-8')
        print(f"✓ {len(df)} résultats chargés")
        print()
        
        # Critères d'échec
        failed_urls = []
        
        # 1. Contenu trop court (< 100 mots)
        short_content = df[df['nb_mots'] < 100].copy()
        short_content['raison'] = 'Contenu trop court'
        failed_urls.append(short_content)
        
        # 2. Pages Cloudflare
        cloudflare = df[df['contenu'].str.contains('Cloudflare|Ray ID|vérifier la sécurité', case=False, na=False)].copy()
        cloudflare['raison'] = 'Page Cloudflare'
        failed_urls.append(cloudflare)
        
        # 3. Erreurs de scraping
        errors = df[df['titre'].str.contains('Erreur|non trouvé', case=False, na=False)].copy()
        errors['raison'] = 'Erreur de scraping'
        failed_urls.append(errors)
        
        # 4. Contenu "inconnu" partout
        unknown = df[
            (df['date_publication'] == 'inconnue') & 
            (df['lieu'] == 'inconnu') & 
            (df['maladie'] == 'inconnue') &
            (df['nb_mots'] < 200)
        ].copy()
        unknown['raison'] = 'Données incomplètes'
        failed_urls.append(unknown)
        
        # Combiner et supprimer les doublons
        all_failed = pd.concat(failed_urls, ignore_index=True)
        all_failed = all_failed.drop_duplicates(subset=['code'])
        
        print("📊 STATISTIQUES DES ÉCHECS")
        print("-"*70)
        print(f"Contenu trop court : {len(short_content)}")
        print(f"Pages Cloudflare : {len(cloudflare)}")
        print(f"Erreurs de scraping : {len(errors)}")
        print(f"Données incomplètes : {len(unknown)}")
        print()
        print(f"🔄 Total URLs à re-scraper : {len(all_failed)}/{len(df)}")
        print()
        
        if len(all_failed) > 0:
            # Afficher quelques exemples
            print("📝 EXEMPLES D'URLs PROBLÉMATIQUES")
            print("-"*70)
            for idx, row in all_failed.head(10).iterrows():
                print(f"{row['code']}: {row['url']}")
                print(f"  → Raison: {row['raison']} ({row['nb_mots']} mots)")
            print()
            
            # Sauvegarder la liste
            retry_df = all_failed[['code', 'url', 'raison', 'nb_mots']].copy()
            retry_df.to_csv(RETRY_FILE, index=False, encoding='utf-8')
            
            print(f"💾 Liste sauvegardée : {RETRY_FILE}")
            print()
            
            return all_failed
        else:
            print("✅ Aucune URL problématique détectée !")
            return None
            
    except FileNotFoundError:
        print(f"❌ Fichier introuvable : {OUTPUT_CSV}")
        return None
    except Exception as e:
        print(f"❌ Erreur : {e}")
        import traceback
        traceback.print_exc()
        return None

def expand_url(short_url, timeout=10):
    """Développe une URL raccourcie en suivant les redirections"""
    try:
        # Utiliser HEAD pour suivre les redirections
        response = requests.head(
            short_url, 
            allow_redirects=True, 
            timeout=timeout,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
        )
        final_url = response.url
        
        # Si HEAD ne fonctionne pas, essayer GET
        if final_url == short_url or any(short in final_url for short in ['lc.cx', 'bit.ly']):
            response = requests.get(
                short_url,
                allow_redirects=True,
                timeout=timeout,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
            final_url = response.url
        
        return final_url
        
    except requests.exceptions.Timeout:
        return short_url
    except requests.exceptions.RequestException:
        return short_url
    except Exception:
        return short_url

def expand_failed_urls(failed_df):
    """Développe les URLs raccourcies parmi les URLs échouées"""
    
    print("="*70)
    print("🔗 ÉTAPE 2: DÉVELOPPEMENT DES URLs RACCOURCIES")
    print("="*70)
    print()
    
    if failed_df is None or len(failed_df) == 0:
        print("⚠️ Aucune URL à traiter")
        return None
    
    # Identifier les URLs raccourcies
    short_patterns = ['lc.cx', 'bit.ly', 'tinyurl', 't.co', 'goo.gl']
    is_short = failed_df['url'].astype(str).apply(
        lambda x: any(pattern in x.lower() for pattern in short_patterns)
    )
    
    short_urls = failed_df[is_short]
    
    print(f"🔍 URLs raccourcies détectées : {len(short_urls)}/{len(failed_df)}")
    
    if len(short_urls) == 0:
        print("✓ Aucune URL raccourcie à développer")
        print()
        # Sauvegarder quand même pour le re-scraping
        failed_df[['code', 'url', 'raison']].to_csv(EXPANDED_FILE, index=False, encoding='utf-8')
        print(f"💾 Fichier sauvegardé : {EXPANDED_FILE}")
        return failed_df
    
    print()
    print("🔄 Développement en cours...")
    print("-"*70)
    
    expanded_urls = []
    changed_count = 0
    
    for idx, row in tqdm(failed_df.iterrows(), total=len(failed_df), desc="Progression"):
        original_url = str(row['url']).strip()
        
        # Développer seulement si raccourcie
        if any(pattern in original_url.lower() for pattern in short_patterns):
            expanded = expand_url(original_url)
            
            if expanded != original_url:
                changed_count += 1
                if changed_count <= 5:
                    print(f"\n  ✓ {row['code']}: {original_url}")
                    print(f"    → {expanded}")
            
            expanded_urls.append(expanded)
        else:
            expanded_urls.append(original_url)
        
        time.sleep(0.3)  # Pause pour éviter la surcharge
    
    print()
    print("-"*70)
    
    # Créer le DataFrame final
    result_df = failed_df.copy()
    result_df['url_originale'] = result_df['url']
    result_df['url'] = expanded_urls
    
    # Sauvegarder
    output_df = result_df[['code', 'url', 'url_originale', 'raison']].copy()
    output_df.to_csv(EXPANDED_FILE, index=False, encoding='utf-8')
    
    print()
    print("="*70)
    print("✅ DÉVELOPPEMENT TERMINÉ")
    print("="*70)
    print(f"📊 Statistiques :")
    print(f"   • Total URLs : {len(failed_df)}")
    print(f"   • URLs développées : {changed_count}")
    print(f"   • URLs non modifiées : {len(failed_df) - changed_count}")
    print()
    print(f"💾 Fichier sauvegardé : {EXPANDED_FILE}")
    print()
    
    return result_df

def generate_report(failed_df):
    """Génère un rapport détaillé"""
    
    print("="*70)
    print("📋 ÉTAPE 3: RAPPORT FINAL")
    print("="*70)
    print()
    
    if failed_df is None or len(failed_df) == 0:
        print("✅ Aucun problème détecté !")
        return
    
    # Statistiques par raison
    print("📊 RÉPARTITION PAR TYPE D'ÉCHEC")
    print("-"*70)
    for raison, group in failed_df.groupby('raison'):
        count = len(group)
        pct = (count / len(failed_df)) * 100
        print(f"{raison:.<40} {count:>4} ({pct:>5.1f}%)")
    print()
    
    # URLs Cloudflare
    cloudflare = failed_df[failed_df['raison'] == 'Page Cloudflare']
    if len(cloudflare) > 0:
        print("🛡️ URLs BLOQUÉES PAR CLOUDFLARE")
        print("-"*70)
        print("Ces URLs sont difficiles à scraper automatiquement.")
        print("Options :")
        print("  1. Utiliser undetected-chromedriver (déjà proposé)")
        print("  2. Scraping manuel")
        print("  3. Accepter la perte de ces données")
        print()
    
    # URLs avec contenu court
    short = failed_df[failed_df['raison'] == 'Contenu trop court']
    if len(short) > 0:
        print("📝 URLs AVEC CONTENU COURT")
        print("-"*70)
        print("Ces URLs peuvent nécessiter :")
        print("  1. Un temps d'attente plus long (JavaScript)")
        print("  2. Des sélecteurs CSS différents")
        print("  3. Vérification manuelle de la validité de l'URL")
        print()
    
    # Prochaines étapes
    print("="*70)
    print("🚀 PROCHAINES ÉTAPES")
    print("="*70)
    print()
    print("1️⃣  OPTION 1 : Re-scraper avec le fichier généré")
    print("   Modifiez main.py :")
    print(f"   INPUT_FILE = \"{EXPANDED_FILE}\"")
    print("   Puis lancez : python main.py")
    print()
    print("2️⃣  OPTION 2 : Installer undetected-chromedriver")
    print("   pip install undetected-chromedriver")
    print("   Puis utilisez le scraper amélioré")
    print()
    print("3️⃣  OPTION 3 : Vérification manuelle")
    print(f"   Ouvrez {EXPANDED_FILE} et vérifiez les URLs")
    print()
    print("="*70)

def main():
    """Fonction principale"""
    print("="*70)
    print("🔧 OUTIL DE CORRECTION DES URLs ÉCHOUÉES")
    print("="*70)
    print()
    
    # Étape 1 : Identifier les URLs problématiques
    failed_df = identify_failed_urls()
    
    if failed_df is None or len(failed_df) == 0:
        print("\n✅ Aucune URL problématique détectée !")
        print("Votre scraping semble avoir bien fonctionné.")
        return
    
    print()
    
    # Étape 2 : Développer les URLs raccourcies
    expanded_df = expand_failed_urls(failed_df)
    
    print()
    
    # Étape 3 : Générer le rapport
    generate_report(expanded_df)

if __name__ == "__main__":
    main()