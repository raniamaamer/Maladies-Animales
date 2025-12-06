# 🐾 Maladies Animales

> Système automatisé d'extraction et d'analyse d'articles sur les maladies animales avec IA locale

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Selenium](https://img.shields.io/badge/Selenium-4.15.2-green.svg)](https://selenium-python.readthedocs.io/)

---

## 📋 Description

Ce projet extrait automatiquement des informations à partir d'articles web sur les maladies animales et génère un dataset CSV enrichi avec :

- 🔍 **Scraping intelligent** : Gère les sites protégés (Cloudflare, WAHIS)
- 🤖 **IA locale (LLM)** : Extraction automatique des métadonnées
- 🌍 **Multilingue** : Détection automatique de la langue
- 📊 **Dashboard interactif** : Visualisation avec Dash/Plotly
- 💾 **Export structuré** : CSV prêt pour analyse

---

## 📚 Technologies Utilisées

| Logo | Technologie | Version | Description |
|------|-------------|---------|-------------|
| ![Selenium](https://img.shields.io/badge/Selenium-43B02A?style=for-the-badge&logo=selenium&logoColor=white&height=20.5) | **Selenium** | 4.15.2 | Automatisation de navigateur pour le scraping web dynamique. Contrôle Chrome/Firefox pour accéder aux sites JavaScript. |
| ![ScrapingBee](https://img.shields.io/badge/ScrapingBee-FFB800?style=for-the-badge&logo=databricks&logoColor=black&height=40)| **ScrapingBee** | API | Service cloud de scraping pour contourner Cloudflare et protections anti-bot. 1000 crédits gratuits. |
| ![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-3776AB?style=for-the-badge&logo=python&logoColor=white&height=20.5) | **BeautifulSoup4** | 4.12.2 | Parser HTML/XML pour extraire données structurées. Simplifie la navigation dans l'arbre DOM. |
| ![lxml](https://img.shields.io/badge/lxml-8A2BE2?style=for-the-badge&logo=xml&logoColor=white&height=20) | **lxml** | 5.0+ | Parser HTML/XML ultra-rapide en C. Utilisé en backend par BeautifulSoup pour accélérer le parsing. |
| ![Ollama](https://img.shields.io/badge/Ollama-000000?style=for-the-badge&logo=llama&logoColor=white&height=20.5) | **Ollama** | - | Runtime local pour LLM (Llama 3.2). Extraction intelligente de métadonnées sans API externe. |
| ![Dash](https://img.shields.io/badge/Dash-008DE4?style=for-the-badge&logo=plotly&logoColor=white&height=20.5) | **Dash** | 2.14.2 | Framework web par Plotly pour créer des dashboards interactifs en Python. Aucun JavaScript requis. |
| ![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white&height=20.5) | **Plotly** | 5.18.0 | Bibliothèque de visualisation interactive (graphiques dynamiques, zoom, export). Moteur graphique de Dash. |
| ![tqdm](https://img.shields.io/badge/tqdm-FFC107?style=for-the-badge&logo=progress&logoColor=black&height=20.5) | **tqdm** | 4.66+ | Barres de progression élégantes pour loops. Affiche ETA, vitesse, et pourcentage en temps réel. |

### 🔧 Dépendances Complémentaires

| Logo | Package | Version | Rôle |
|------|---------|---------|------|
| ![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white&height=20.5) | **pandas** | 2.1.3 | Manipulation et export CSV/Excel |
| ![Langdetect](https://img.shields.io/badge/Langdetect-4B8BBE?style=for-the-badge&logo=google-translate&logoColor=white&height=20.5) | **langdetect** | 1.0.9 | Détection automatique de langue (15+ langues) |
| ![Requests](https://img.shields.io/badge/Requests-FF6C37?style=for-the-badge&logo=python&logoColor=white&height=20.5) | **requests** | 2.31.0 | Requêtes HTTP pour APIs |
| ![WebDriver Manager](https://img.shields.io/badge/WebDriver_Manager-00ADD8?style=for-the-badge&logo=googlechrome&logoColor=white&height=20.5) | **webdriver-manager** | 4.0+ | Gestion automatique des drivers Selenium |
---

## 🎯 Fonctionnalités

| Fonctionnalité | Description |
|----------------|-------------|
| **Scraping adaptatif** | Selenium + ScrapingBee pour sites protégés |
| **Extraction LLM** | Date, lieu, maladie, animal, résumés (50/100/150 mots) |
| **Détection langue** | 🇫🇷 🇸🇦 🇬🇧 🇪🇸 🇷🇺 et plus |
| **Classification source** | Site officiel, média spécialisé, presse |
| **Dashboard** | Graphiques interactifs et filtres dynamiques |
| **Logs détaillés** | Suivi en temps réel du traitement |

---

## 🏗️ Architecture

```
maladies-animales-scraper/
├── 📁 data/
│   ├── input/           # 📥 urls.csv (fichier d'entrée)
│   ├── output/          # 📤 dataset.csv (résultats)
│   └── logs/            # 📝 scraping.log
├── 📁 src/
│   ├── scraper.py       # 🕷️ Selenium + ScrapingBee
│   ├── llm_processor.py # 🤖 Extraction LLM (Ollama)
│   └── utils.py         # 🛠️ Nettoyage, détection langue
├── main.py              # 🚀 Script principal
├── dashboard.py         # 📊 Interface de visualisation
├── test.py              # 🧪 Tests d'installation
└── requirements.txt     # 📦 Dépendances
```

---

## 🚀 Installation Rapide

### 1️⃣ Prérequis

- **Python 3.9+** : [Télécharger](https://www.python.org/downloads/)
- **Google Chrome** : [Télécharger](https://www.google.com/chrome/)
- **Ollama** : [Télécharger](https://ollama.com/download)

### 2️⃣ Installation

```bash
# Cloner le projet
git clone https://github.com/votre-repo/maladies-animales-scraper.git
cd maladies-animales-scraper

# Installer les dépendances
pip install -r requirements.txt

# Télécharger le modèle LLM (Llama 3.2)
ollama pull llama3.2

# Tester l'installation
python test.py
```

### 3️⃣ Configuration ScrapingBee (Sites Protégés)

1. Créer un compte sur [ScrapingBee](https://www.scrapingbee.com) (1000 crédits gratuits)
2. Récupérer votre API key
3. Dans `src/scraper.py`, ligne 8 :

```python
SCRAPINGBEE_API_KEY = "VOTRE_CLE_ICI"
```

⚠️ **Important** : Révoquez la clé après vos tests depuis le [dashboard ScrapingBee](https://www.scrapingbee.com/dashboard)

---

## 📊 Préparation des Données

### Format du fichier d'entrée

Créez `data/input/urls.csv` :

```csv
code,lien
code151,https://lc.cx/nKVbsM
code173,https://wahis.woah.org/#/in-review/5293
code195,https://www.aden-tm.net/news/263310
```

**Colonnes obligatoires :**
- `code` : Identifiant unique (ex: code151)
- `url` : URL de l'article

**Formats acceptés :**
- Délimiteurs : `,` `;` `\t` (auto-détecté)
- Encodage : UTF-8

---

## 🎮 Utilisation

### Lancement du scraping complet

```bash
python main.py
```

**Ce qui se passe :**

```
[1/50] Traitement [code001]
URL: https://wahis.woah.org/#/in-review/5294
============================================================
🔒 Site protégé détecté
📡 Appel ScrapingBee...
✅ Contenu récupéré (1847 caractères)
🌍 Langue détectée: français
🤖 Extraction LLM en cours...
   ✓ Maladie: Bluetongue
   ✓ Animal: Ovins
   ✓ Lieu: Belgique
   ✓ Date: 16/10/2023
📝 Résumés générés (50/100/150 mots)
💾 Sauvegarde...
============================================================
✅ Traité avec succès en 28 secondes
```

### Visualiser le dashboard

```bash
python dashboard.py
```

Accès :
- 🖥️ **PC** : http://127.0.0.1:8050/
- 📱 **Mobile** : http://VOTRE-IP-LOCALE:8050/

---

## 📤 Fichier de Sortie

### `data/output/dataset.csv`

| Colonne | Description | Exemple |
|---------|-------------|---------|
| `code` | Identifiant unique | code151 |
| `url` | URL source | https://... |
| `titre` | Titre de l'article | "Le virus de la fièvre catarrhale a été détecté en Europe" |
| `contenu` | Texte complet nettoyé | "Tridge LogoPlateforme de trading mondiale." (3891 caractères) |
| `langue` | Langue détectée | anglais |
| `nb_caracteres` | Nombre de caractères | 3891 |
| `nb_mots` | Nombre de mots | 617 |
| `date_publication` | Date extraite | 16/10/2023 |
| `lieu` | Pays/région | Belgique |
| `maladie` | Maladie identifiée | Bluetongue |
| `animal` | Espèce concernée | Ovins, Bovins |
| `source_publication` | Type de source | lien raccourci |
| `resume_50_mots` | Résumé court | "Le virus de la fièvre catarrhale ovine (Bluetongue)..." |
| `resume_100_mots` | Résumé moyen | "Le virus de la fièvre catarrhale ovine (Bluetongue)..." |
| `resume_150_mots` | Résumé détaillé | "Le virus de la fièvre catarrhale ovine (Bluetongue)..." |

---

## ⚙️ Configuration Avancée

### Modifier la vitesse de traitement

Dans `src/llm_processor.py`, ligne 30 :

```python
"options": {
    "temperature": 0.1,    # Plus bas = plus précis
    "num_predict": 1000    # Augmenter pour résumés longs
}
```

### Ajouter un site protégé

Dans `src/scraper.py`, ligne 15 :

```python
CLOUDFLARE_DOMAINS = {
    "www.elfagr.org",
    "www.alyaum.com",
    "votre-site.com"  # ← Ajouter ici
}
```

### Changer le modèle LLM

```bash
# Modèle plus rapide
ollama pull llama3.2:1b

# Dans src/llm_processor.py, ligne 18
"model": "llama3.2:1b"
```

---

## 🔧 Résolution de Problèmes

<details>
<summary><b>❌ Erreur : "ChromeDriver not found"</b></summary>

**Solution :**
```bash
pip install --upgrade webdriver-manager
```
Le script télécharge automatiquement ChromeDriver au premier lancement.
</details>

<details>
<summary><b>❌ Erreur : "Ollama connection refused"</b></summary>

**Vérifications :**
```bash
# Démarrer Ollama
ollama serve

# Tester
ollama list
ollama run llama3.2 "test"
```
</details>

<details>
<summary><b>❌ Contenu vide ou "Titre non trouvé"</b></summary>

**Causes possibles :**

1. **Site protégé** → Vérifiez ScrapingBee
2. **Site lent** → Augmentez timeout dans `scraper.py` ligne 161
3. **Structure HTML complexe** → Testez en mode non-headless

**Debug mode (voir navigateur) :**
```python
# Dans src/scraper.py, ligne 13, commenter :
# options.add_argument("--headless")
```
</details>

<details>
<summary><b>❌ LLM trop lent (> 1 minute/article)</b></summary>

**Solutions :**

1. **Modèle plus rapide :**
```bash
ollama pull llama3.2:1b
```

2. **Réduire le contexte** (llm_processor.py ligne 14) :
```python
text[:1000]  # Au lieu de 3500
```

3. **Vérifier GPU :**
```bash
ollama ps  # Doit afficher GPU
```
</details>

<details>
<summary><b>❌ Erreur ScrapingBee : "Incorrect API key"</b></summary>

**Vérifications :**
1. Clé correcte sur [dashboard](https://www.scrapingbee.com/dashboard)
2. Pas d'espaces avant/après la clé
3. Crédits disponibles (1000 gratuits)
</details>

---

## 📈 Performance

| Configuration | Temps/URL | Total 50 URLs |
|---------------|-----------|---------------|
| **Selenium seul** | 3-5 sec | ~4 minutes |
| **+ LLM (Llama 3.2)** | 8-12 sec | ~10 minutes |
| **+ ScrapingBee** | 5-8 sec | +2-3 minutes |
| **Total estimé** | **10-15 sec** | **12-18 minutes** |

**Facteurs d'impact :**
- Vitesse CPU/GPU
- Longueur des articles
- Sites protégés (+3-5 sec)
- Connexion internet

---

## 🎨 Dashboard - Aperçu

Le dashboard Dash/Plotly offre :

### 📊 KPIs en temps réel
- Total d'articles
- Moyenne de mots
- Nombre de maladies
- Nombre d'animaux
- Nombre de lieux

### 📈 Graphiques interactifs
- 🌍 Répartition par langue (donut)
- 📰 Répartition par source (bar)
- 🦠 Top 15 maladies (horizontal bar)
- 🐾 Top 15 animaux (horizontal bar)
- 📍 Top 15 lieux (horizontal bar)
- 📊 Distribution statistique (box plot)

### 🔍 Filtres dynamiques
- Langue
- Type de source
- Lieu
- Maladie
- Animal

### 📋 Tableau de données
- Affichage des 45 derniers articles après nettoyage
- Pagination
- Tri par colonne

---

## 🧪 Tests

### Test complet de l'installation

```bash
python test.py
```

**Résultat attendu :**
```
🧪 TEST D'INSTALLATION
============================================================
🔍 Test des imports...
  ✓ selenium
  ✓ bs4
  ✓ pandas
  ✓ langdetect
✅ Tous les modules sont installés

🔍 Test de Selenium...
✅ Selenium fonctionne correctement

🔍 Test d'Ollama...
  ✓ Ollama est actif
  Modèles installés:
    - llama3.2:latest
✅ Llama 3.2 est installé

🔍 Test de la structure des dossiers...
  ✓ data/input
  ✓ data/output
  ✓ data/logs
✅ Structure des dossiers OK

🔍 Test du fichier d'entrée...
  ✓ Fichier trouvé avec 50 URLs
✅ Fichier d'entrée valide

============================================================
📊 RÉSUMÉ DES TESTS
============================================================
Imports........................ ✅ PASS
Selenium....................... ✅ PASS
Ollama......................... ✅ PASS
Dossiers....................... ✅ PASS
Fichier d'entrée............... ✅ PASS

🎉 TOUS LES TESTS SONT PASSÉS !
```

---

## 💡 Bonnes Pratiques

### Avant de lancer sur 50 URLs

1. **Testez sur 3-5 URLs** :
```csv
code,url
code151,https://lc.cx/nKVbsM
code156,https://www.elfagr.org/4789113
```

2. **Vérifiez la qualité** :
   - Ouvrez `data/output/output_dataset.csv`
   - Vérifiez les titres
   - Vérifiez la longueur du contenu (> 100 mots)

3. **Validez les résumés LLM** :
   - Lisez quelques résumés
   - Vérifiez la cohérence

### Optimisation

- ✅ Traiter par batch de 10-15 URLs
- ✅ Éviter heures de pointe pour ScrapingBee
- ✅ Fermer applications gourmandes
- ✅ Ajouter délais entre requêtes (2 sec recommandé)

### Sécurité

- ✅ Respectez robots.txt
- ✅ Ne partagez jamais vos clés API
- ✅ Révoquez clés de test
- ❌ Ne commitez pas les clés dans Git

---

## 📚 Dépendances Principales

| Package | Version | Description |
|---------|---------|-------------|
| selenium | 4.15.2 | Web scraping |
| beautifulsoup4 | 4.12.2 | Parsing HTML |
| pandas | 2.1.3 | Manipulation données |
| langdetect | 1.0.9 | Détection langue |
| requests | 2.31.0 | Requêtes HTTP |
| dash | 2.14.2 | Dashboard interactif |
| plotly | 5.18.0 | Visualisations |

---

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Fork le projet
2. Ajouter un nouveau remote (`git remote add origin https://github.com/raniamaamer/Maladies-Animales.git`)
3. Commit vos changements (`git commit -m 'Ajout fonctionnalité'`)
4. Push vers la branche (`git push `)

---