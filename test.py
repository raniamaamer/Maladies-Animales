import sys
import io
import os

def _ensure_utf8_io():
    try:
        if getattr(sys.stdout, "reconfigure", None):
            sys.stdout.reconfigure(encoding="utf-8", errors="strict")
            sys.stderr.reconfigure(encoding="utf-8", errors="strict")
        else:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="strict", line_buffering=True)
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="strict", line_buffering=True)
    except Exception:
        try:
            if getattr(sys.stdout, "reconfigure", None):
                sys.stdout.reconfigure(encoding="utf-8", errors="replace")
                sys.stderr.reconfigure(encoding="utf-8", errors="replace")
            else:
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)
                sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace", line_buffering=True)
        except Exception:
            pass


_ensure_utf8_io()
from pathlib import Path

def test_imports():
    """Teste les imports des bibliothèques"""
    print("🔍 Test des imports...")
    
    required_modules = [
        'selenium',
        'bs4',
        'pandas',
        'langdetect',
        'requests',
        'tqdm'
    ]
    
    failed = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"  ✓ {module}")
        except ImportError:
            print(f"  ✗ {module} - MANQUANT")
            failed.append(module)
    
    if failed:
        print(f"\n❌ Modules manquants: {', '.join(failed)}")
        print("Installez-les avec: pip install -r requirements.txt")
        return False
    
    print("✅ Tous les modules sont installés\n")
    return True

def test_selenium():
    """Teste Selenium et ChromeDriver"""
    print("🔍 Test de Selenium...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get("https://www.google.com")
        driver.quit()
        
        print("✅ Selenium fonctionne correctement\n")
        return True
    except Exception as e:
        print(f"❌ Erreur Selenium: {e}\n")
        return False

def test_ollama():
    """Teste la connexion à Ollama"""
    print("🔍 Test d'Ollama...")
    
    try:
        import requests
        
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"  ✓ Ollama est actif")
            print(f"  Modèles installés:")
            for model in models:
                print(f"    - {model['name']}")
            
            model_names = [m['name'] for m in models]
            if any('llama3.2' in name for name in model_names):
                print("✅ Llama 3.2 est installé\n")
                return True
            else:
                print("⚠️  Llama 3.2 non trouvé")
                print("Installez-le avec: ollama pull llama3.2\n")
                return False
        else:
            print("❌ Ollama ne répond pas correctement\n")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter à Ollama")
        print("   Assurez-vous qu'Ollama est démarré:")
        print("   - Linux/Mac: ollama serve")
        print("   - Windows: Ollama devrait démarrer automatiquement\n")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}\n")
        return False

def test_directories():
    """Teste la structure des dossiers"""
    print("🔍 Test de la structure des dossiers...")
    
    base_dir = Path(__file__).parent
    required_dirs = [
        base_dir / "data" / "input",
        base_dir / "data" / "output",
        base_dir / "data" / "logs",
        base_dir / "src"
    ]
    
    all_exist = True
    for directory in required_dirs:
        if directory.exists():
            print(f"  ✓ {directory.relative_to(base_dir)}")
        else:
            print(f"  ✗ {directory.relative_to(base_dir)} - MANQUANT")
            directory.mkdir(parents=True, exist_ok=True)
            print(f"    → Créé automatiquement")
    
    print("✅ Structure des dossiers OK\n")
    return True

def test_input_file():
    """Vérifie si le fichier d'entrée existe"""
    print("🔍 Test du fichier d'entrée...")
    
    input_file = Path(__file__).parent / "data" / "input" / "urls.csv"
    
    if input_file.exists():
        import pandas as pd
        try:
            df = pd.read_csv(input_file)
            print(f"  ✓ Fichier trouvé avec {len(df)} lignes")
            print(f"  Colonnes détectées: {', '.join(df.columns.tolist())}")
            
            # Détecter automatiquement les colonnes URL
            url_columns = [col for col in df.columns if any(keyword in col.lower() 
                          for keyword in ['url', 'lien', 'link', 'site', 'web'])]
            
            # Détecter automatiquement les colonnes d'identifiant
            id_columns = [col for col in df.columns if any(keyword in col.lower() 
                         for keyword in ['code', 'id', 'identifiant', 'reference', 'ref'])]
            
            if url_columns and (id_columns or len(df.columns) >= 2):
                print(f"  ✓ Colonne URL détectée: {url_columns[0]}")
                if id_columns:
                    print(f"  ✓ Colonne ID détectée: {id_columns[0]}")
                else:
                    print(f"  ✓ Colonne ID par défaut: {df.columns[0]}")
                print("✅ Fichier d'entrée valide\n")
                return True
            elif len(df.columns) >= 2:
                print(f"  ⚠️  Colonnes spécifiques non détectées, utilisation par défaut:")
                print(f"     - Colonne ID: {df.columns[0]}")
                print(f"     - Colonne URL: {df.columns[1]}")
                print("✅ Fichier d'entrée utilisable\n")
                return True
            else:
                print(f"  ✗ Le fichier doit avoir au moins 2 colonnes")
                print(f"    Colonnes actuelles: {', '.join(df.columns.tolist())}")
                print("❌ Format du fichier incorrect\n")
                return False
                
        except Exception as e:
            print(f"  ✗ Erreur de lecture: {e}")
            print("❌ Fichier corrompu ou illisible\n")
            return False
    else:
        print("  ✗ Fichier urls.csv non trouvé dans data/input/")
        print("\n  📝 Création d'un fichier exemple...")
        
        # Créer un fichier exemple
        try:
            import pandas as pd
            example_data = {
                'code': ['MAL001', 'MAL002', 'MAL003'],
                'lien': [
                    'https://example.com/maladie1',
                    'https://example.com/maladie2',
                    'https://example.com/maladie3'
                ]
            }
            df_example = pd.DataFrame(example_data)
            df_example.to_csv(input_file, index=False, encoding='utf-8')
            print(f"  ✓ Fichier exemple créé: {input_file}")
            print("  ⚠️  Remplacez-le avec vos vraies données")
            print("✅ Fichier exemple créé\n")
            return True
        except Exception as e:
            print(f"  ✗ Impossible de créer le fichier exemple: {e}")
            print("❌ Créez manuellement urls.csv avec au moins 2 colonnes\n")
            return False

def main():
    """Fonction principale"""
    print("="*60)
    print("🧪 TEST D'INSTALLATION - Projet Maladies Animales")
    print("="*60)
    print()
    
    results = {
        "Imports": test_imports(),
        "Selenium": test_selenium(),
        "Ollama": test_ollama(),
        "Dossiers": test_directories(),
        "Fichier d'entrée": test_input_file()
    }
    
    print("="*60)
    print("📊 RÉSUMÉ DES TESTS")
    print("="*60)
    
    for test, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test:.<30} {status}")
    
    print()
    
    if all(results.values()):
        print("🎉 TOUS LES TESTS SONT PASSÉS !")
        print("Vous pouvez lancer le projet avec: python main.py --phase all")
    else:
        print("⚠️  CERTAINS TESTS ONT ÉCHOUÉ")
        print("Corrigez les problèmes ci-dessus avant de continuer")
    
    print("="*60)

if __name__ == "__main__":
    main()