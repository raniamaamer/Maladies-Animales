# 🐾 Projet Web Scraping - Maladies Animales

Système automatisé d'extraction et d'analyse d'articles sur les maladies animales avec Selenium, ScrapingBee et LLM.

## 📋 Description

Ce projet extrait automatiquement des informations à partir d'URLs d'articles sur les maladies animales et génère un dataset CSV structuré avec :
- Métadonnées (titre, langue, dates, lieux)
- Analyse de contenu (maladie, animal concerné)
- Résumés automatiques (50, 100, 150 mots)
- Gestion des sites protégés (Cloudflare, WAHIS, etc.)

## 🏗️ Architecture

```
animal_disease_scraper/
├── data/
│   ├── input/           # Fichier URLs d'entrée (urls.csv)
│   ├── output/          # Résultats (output_dataset.csv)
│   └── logs/            # Logs d'exécution (scraping.log)
├── src/
│   ├── scraper.py       # Module Selenium + ScrapingBee
│   ├── llm_processor.py # Module LLM (extraction métadonnées résumés)
│   └── utils.py         # Utilitaires (nettoyage, détection langue)
│         
└── main.py              # Script principal
```

## 🚀 Installation

### 1. Prérequis
```bash
# Python 3.8+
python --version

# Chrome/Chromium installé sur votre système
google-chrome --version  # ou chromium --version
```

### 2. Installation des dépendances
```bash
pip install -r requirements.txt
```

**Dépendances principales :**
```txt
selenium==4.15.2
webdriver-manager==4.0.1
beautifulsoup4==4.12.2
lxml==4.9.3
pandas==2.1.3
numpy==1.26.2
langdetect==1.0.9
ollama==0.1.6
requests==2.31.0
tenacity==8.2.3

```

### 3. Installation d'Ollama (LLM local gratuit)

**Windows:**
- Télécharger depuis https://ollama.com/download
- Installer et exécuter
- Ouvrir terminal: `ollama pull llama3.2`

**Vérifier l'installation:**
```bash
ollama list
# Doit afficher : llama3.2:latest
```

### 4. Configuration ScrapingBee (pour sites protégés)

**⚠️ IMPORTANT : Clé API à configurer**

1. Créer un compte sur https://www.scrapingbee.com (1000 crédits gratuits)
2. Récupérer votre API key
3. Dans `src/scraper.py`, ligne 8, remplacer :
```python
SCRAPINGBEE_API_KEY = "VOTRE_CLE_API_ICI"
```

**🔒 Sécurité :** Après vos tests, **révoquez cette clé** depuis le dashboard ScrapingBee.

## 📊 Préparation des Données

### Format du fichier d'entrée

Créez `data/input/urls.csv` avec le format suivant :

```csv
code,url
code151 https://lc.cx/nKVbsM
code152 https://lc.cx/sXWRhi
code153 https://lc.cx/JSB3wp
```

**Colonnes obligatoires:**
- `code` : Identifiant unique (alphanumérique)
- `url` : URL de l'article

**Formats acceptés :**
- Délimiteurs : `,` ou `;` ou `\t` (auto-détecté)
- Encodage : UTF-8

## 🎯 Utilisation

### Lancement du scraping complet

```bash
python main.py
```

Le script va automatiquement :
1. ✅ Charger le fichier `data/input/urls.csv`
2. 🔍 Scraper chaque URL (avec gestion des sites protégés)
3. 🧹 Nettoyer et analyser le contenu
4. 🤖 Extraire les métadonnées avec le LLM
5. 💾 Sauvegarder les résultats dans `data/output/output_dataset.csv`

### Suivi en temps réel

```bash
# Dans un autre terminal
tail -f data/logs/scraping.log
```

### Configuration de la vitesse LLM

Dans `main.py`, ligne 10 :

```python
LLM_MODE = "fast"   # ⚡ Rapide : ~10 sec/article (recommandé)
# ou
LLM_MODE = "normal" # 🎯 Précis : ~30 sec/article
```

## 📊 Flux d'Exécution

```
main.py
   │
   ├─→ 1. Chargement CSV (auto-détection délimiteur)
   │      └─→ Détection colonnes code/url
   │
   ├─→ 2. Initialisation Selenium
   │
   ├─→ 3. Pour chaque URL :
   │      │
   │      ├─→ Détection site protégé ?
   │      │   ├─→ OUI → ScrapingBee (API)
   │      │   └─→ NON → Selenium direct
   │      │
   │      ├─→ Extraction contenu (titre + texte)
   │      │
   │      ├─→ Validation contenu
   │      │   └─→ Si échec → 2ème tentative
   │      │
   │      ├─→ Nettoyage texte (utils.py)
   │      │
   │      ├─→ Détection langue
   │      │
   │      ├─→ Analyse LLM :
   │      │   ├─→ Extraction métadonnées (date, lieu, maladie, animal)
   │      │   └─→ Génération résumés (50/100/150 mots)
   │      │
   │      └─→ Sauvegarde ligne dans CSV
   │
   └─→ 4. Rapport final
```

## 📝 Fichiers de Sortie

### `data/output/output_dataset.csv`

Dataset final avec toutes les colonnes :

| Colonne | Description | Exemple |
|---------|-------------|---------|
| `code` | Identifiant unique | code152 |
| `url` | URL source | https://... |
| `titre` | Titre de l'article | "Alerte grippe aviaire" |
| `contenu` | Texte complet nettoyé | "Un foyer de grippe..." |
| `langue` | Langue détectée | français / arabic / english |
| `nb_caracteres` | Nombre de caractères | 2847 |
| `nb_mots` | Nombre de mots | 421 |
| `date_publication` | Date extraite | 15-03-2024 |
| `lieu` | Pays/région | France |
| `maladie` | Maladie identifiée | grippe aviaire |
| `animal` | Espèce concernée | poulets |
| `source_publication` | Type de source | site officiel / presse |
| `resume_50_mots` | Résumé court | ... |
| `resume_100_mots` | Résumé moyen | ... |
| `resume_150_mots` | Résumé détaillé | ... |

## ⚙️ Configuration Avancée

### 1. Modifier les sites protégés

Dans `src/scraper.py`, ligne 145 :

```python
PROTECTED_DOMAINS = [
    "wahis.woah.org",
    "alyaum.com",
    "elfagr.org"
]
```

### 2. Changer le modèle LLM

Dans `src/llm_processor.py`, ligne 5 :

```python
MODEL = "llama3.2"      # Recommandé (équilibre vitesse/qualité)
```

### 3. Ajuster les timeouts Selenium

Dans `src/scraper.py`, ligne 161 :

```python
WebDriverWait(driver, 15).until(...)  # Changer 15 → 20 pour sites lents
time.sleep(3)  # Augmenter à 5 si nécessaire
```

### 4. Utiliser un proxy

Dans `src/scraper.py`, fonction `setup_driver()` :

```python
options.add_argument('--proxy-server=http://votre-proxy:port')
```

## 🔧 Résolution de Problèmes

### ❌ Erreur : "ChromeDriver not found"

**Solution :**
```bash
pip install --upgrade webdriver-manager
```

Le script télécharge automatiquement ChromeDriver au premier lancement.

---

### ❌ Erreur : "Ollama connection refused"

**Solution :**
```bash
# Démarrer Ollama
ollama serve

# Dans un autre terminal, vérifier
ollama list
ollama run llama3.2 "test"
```

---

### ❌ Contenu vide ou "Titre non trouvé"

**Causes possibles :**

1. **Site protégé par Cloudflare/Captcha**
   - Vérifiez que ScrapingBee est configuré
   - Ajoutez le domaine dans `PROTECTED_DOMAINS`

2. **Site trop lent à charger**
   - Augmentez le timeout dans `scraper.py` (ligne 161)
   - Augmentez `time.sleep(3)` → `time.sleep(5)`

3. **Structure HTML non reconnue**
   - Testez en mode non-headless : `options.add_argument("--headless")` → commentez cette ligne
   - Vérifiez les sélecteurs CSS dans `scraper.py`

---

### ❌ Erreur ScrapingBee : "Incorrect API key"

**Solution :**
1. Vérifiez votre clé sur https://www.scrapingbee.com/dashboard
2. Vérifiez qu'il n'y a pas d'espaces avant/après la clé
3. Vérifiez que vous avez encore des crédits

---

### ❌ Langue non détectée (affiche "inconnu")

**Solution :**
- Le texte doit contenir au moins 10 caractères
- Pour l'arabe, vérifiez l'encodage UTF-8 du fichier
- Installez la dernière version : `pip install --upgrade langdetect`

---

### ❌ LLM trop lent (> 1 minute par article)

**Solutions :**

1. **Activer le mode fast** (main.py ligne 10)
   ```python
   LLM_MODE = "fast"
   ```

2. **Utiliser un modèle plus petit**
   ```bash
   ollama pull llama3.2:1b
   ```
   Puis dans `llm_processor.py` :
   ```python
   MODEL = "llama3.2:1b"
   ```

3. **Vérifier l'utilisation GPU**
   ```bash
   ollama ps  # Doit afficher GPU si disponible
   ```

4. **Réduire le contexte** (llm_processor.py ligne 39)
   ```python
   text_sample = text[:1000]  # Au lieu de 1500
   ```

---

### ❌ CSV mal formaté ou caractères étranges

**Solution :**
```python
# Dans main.py, forcer l'encodage UTF-8
df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
```

## 🎨 Personnalisation

### Ajouter un nouveau champ LLM

**1. Modifier le prompt** dans `src/llm_processor.py` ligne 39 :

```python
prompt = f"""... extrais les informations :
- "date_publication"
- "lieu"
- "maladie"
- "animal"
- "nombre_cas"  # ← Nouveau champ
...
"""
```

**2. Ajouter le champ par défaut** ligne 62 :

```python
return {
    ...,
    "nombre_cas": data.get("nombre_cas", "inconnu")
}
```

**3. Mettre à jour main.py** ligne 190 :

```python
final_row = {
    ...,
    "nombre_cas": llm_fields.get("nombre_cas", "inconnu")
}
```

### Changer le format de date

Dans `src/llm_processor.py`, prompt ligne 42 :

```python
- "date_publication" (format YYYY-MM-DD, "inconnue" si absente)
```

## 📊 Exemples de Résultats

### Exemple 1 : Site standard (succès)

**Input :**
```csv
code123,https://example.com/article-grippe-aviaire
```

**Output :**
```csv
code123,https://example.com/article-grippe-aviaire,"Foyer de grippe aviaire détecté","Un nouveau foyer...",français,1847,273,12-03-2024,Bretagne,grippe aviaire,poulets,presse,"Un foyer de grippe aviaire a été détecté en Bretagne..."
```

---

### Exemple 2 : Site protégé WAHIS (avec ScrapingBee)

**Input :**
```csv
code171,https://wahis.woah.org/#/in-review/5294
```

**Logs :**
```
🔒 Site protégé détecté : https://wahis.woah.org/#/in-review/5294
→ Utilisation directe de ScrapingBee...
📡 Appel ScrapingBee pour : https://wahis.woah.org/#/in-review/5294
✅ ScrapingBee : succès
✓ Contenu valide récupéré
```

---

### Exemple 3 : Échec de scraping

**Output :**
```csv
code999,https://site-inaccessible.com,"Échec du scraping","Le contenu n'a pas pu être extrait",inconnu,0,0,inconnue,inconnu,inconnue,inconnu,inconnu,"Scraping échoué"
```

## 🤝 Alternatives LLM

### 1. Ollama (Recommandé - Gratuit)
✅ Gratuit, local, pas de limite  
✅ Multilingue excellent  
✅ Pas besoin d'API key  
✅ Fonctionne hors ligne  

**Modèles recommandés :**
- `llama3.2` : Équilibre vitesse/qualité (par défaut)
- `llama3.2:1b` : Plus rapide, qualité correcte
- `llama3.1:8b` : Meilleure qualité, plus lent

---

## 📈 Performance

| Étape | Temps moyen | Notes |
|-------|-------------|-------|
| Scraping (Selenium) | 3-5 sec/URL | Sites standards |
| Scraping (ScrapingBee) | 5-8 sec/URL | Sites protégés |
| Analyse LLM (fast) | 8-12 sec/article | Mode rapide |
| Analyse LLM (normal) | 25-35 sec/article | Mode précis |
| **Total (50 URLs, fast)** | **12-18 minutes** | Recommandé |
| **Total (50 URLs, normal)** | **28-38 minutes** | Production |

**Facteurs d'impact :**
- Vitesse CPU/GPU
- Longueur des articles
- Sites protégés (+ lent)
- Modèle LLM utilisé

## 🐛 Logs et Debugging

### Fichiers de logs

```bash
# Log principal
data/logs/scraping.log

# Voir en temps réel
tail -f data/logs/scraping.log

# Chercher les erreurs
grep "ERROR" data/logs/scraping.log
grep "❌" data/logs/scraping.log
```

### Logs détaillés

Le script génère des logs structurés :

```
============================================================
[6/50] Traitement [code156]
URL: https://www.elfagr.org/4789113
============================================================
🔒 Site protégé détecté : https://www.elfagr.org/4789113
→ Utilisation directe de ScrapingBee...
📡 Appel ScrapingBee pour : https://www.elfagr.org/4789113
✅ ScrapingBee : succès
✓ Contenu valide récupéré
→ Extraction LLM en cours (mode: fast)...
→ Extraction des métadonnées...
→ Métadonnées extraites: grippe aviaire / poulets / Égypte
→ Génération résumé 50 mots...
→ Génération résumé 100 mots...
→ Génération résumé 150 mots...
✅ Traité avec succès
   • Titre: تفشي أنفلونزا الطيور في القاهرة
   • Mots: 486
   • Langue: arabic
💾 Sauvegarde intermédiaire (6 résultats)
```

### Mode debug (voir le navigateur)

Dans `src/scraper.py`, ligne 13, **commenter** :

```python
# options.add_argument("--headless")  # ← Désactivé
```

Le navigateur s'ouvrira et vous verrez le scraping en direct.

## 💡 Conseils et Bonnes Pratiques

### 🎯 Avant de lancer sur 50 URLs

1. **Testez sur 3-5 URLs d'abord**
   ```csv
   code,url
   test1,https://example1.com
   test2,https://example2.com
   ```

2. **Vérifiez la qualité du scraping**
   - Ouvrez `output.csv`
   - Vérifiez que les titres sont corrects
   - Vérifiez la longueur du contenu (> 100 mots)

3. **Validez les résumés LLM**
   - Lisez quelques résumés
   - Vérifiez qu'ils sont en français
   - Vérifiez la cohérence

### ⚡ Optimiser les performances

1. **Utiliser le mode fast** (ligne 10 main.py)
2. **Traiter par batch** : 10-15 URLs à la fois
3. **Éviter les heures de pointe** pour ScrapingBee
4. **Fermer les autres applications** qui consomment RAM/CPU

### 🔒 Sécurité et Éthique

1. **Respectez les robots.txt**
   ```bash
   curl https://example.com/robots.txt
   ```

2. **Ajoutez des délais** entre requêtes (déjà fait : 2 sec)

3. **Ne partagez jamais vos clés API**
   - ✅ Utilisez `.env`
   - ❌ Ne commitez pas les clés dans Git

4. **Révoquez les clés de test**
   - ScrapingBee : https://www.scrapingbee.com/dashboard

### 📊 Gérer de gros volumes

Pour > 100 URLs :

1. **Divisez le fichier** en plusieurs CSV
2. **Lancez en parallèle** (avec prudence)
3. **Surveillez les crédits** ScrapingBee
4. **Sauvegardez régulièrement** (déjà fait : tous les 3 articles)

## 📚 Ressources et Documentation

### Dépendances Principales

- **Selenium** : https://selenium-python.readthedocs.io
- **BeautifulSoup4** : https://www.crummy.com/software/BeautifulSoup/bs4/doc/
- **Ollama** : https://ollama.ai/docs
- **ScrapingBee** : https://www.scrapingbee.com/documentation
- **Pandas** : https://pandas.pydata.org/docs/

### Tutoriels

- Selenium : https://realpython.com/modern-web-automation-with-python-and-selenium/
- Web Scraping éthique : https://www.scrapehero.com/how-to-prevent-getting-blacklisted-while-scraping/
- Ollama guides : https://github.com/ollama/ollama/tree/main/docs

## 📞 Support et Contribution

### Problème non résolu ?

1. ✅ Vérifiez les logs : `data/logs/scraping.log`
2. ✅ Testez Ollama : `ollama run llama3.2 "test"`
3. ✅ Testez ScrapingBee : vérifiez les crédits
4. ✅ Testez sur une seule URL simple d'abord

### Améliorations futures

- [ ] Support multi-threading
- [ ] Interface web (Flask/Streamlit)
- [ ] Export en JSON/Excel
- [ ] Détection automatique de la langue du résumé
- [ ] Cache des résultats pour éviter re-scraping
---