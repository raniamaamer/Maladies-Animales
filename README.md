# 📊 Système d'Analyse des Maladies Animales

Un système complet d'extraction, d'analyse et de visualisation des données sur les maladies animales à partir de sources web multilingues (français, anglais, arabe).

## 🎯 Vue d'ensemble

Ce projet permet de collecter automatiquement des articles sur les maladies animales, d'en extraire les informations clés (maladie, localisation, date, langue), et de visualiser les résultats dans un dashboard interactif.

## ✨ Fonctionnalités principales

### 🔍 Extraction de données (`extract.py`)
- **Scraping intelligent** : Support des sites statiques (BeautifulSoup) et dynamiques (Selenium)
- **Détection automatique** : Langue, type de source, maladie, localisation
- **Multilinguisme** : Traite le français, l'anglais et l'arabe
- **Extraction enrichie** :
  - Titre et contenu complet
  - Statistiques (nombre de mots/caractères)
  - Date de publication
  - Résumés automatiques (50, 100, 150 mots)
  - Entités nommées (organisations, animaux)
- **Gestion d'erreurs robuste** : Sauvegarde des données valides même en cas d'échec partiel

### 📈 Visualisation (`dashboard.py`)
- **Dashboard interactif Dash/Plotly** avec filtres dynamiques
- **KPIs en temps réel** : Nombre d'articles, mots moyens, maladies, lieux
- **Graphiques multiples** :
  - Répartition par langue (donut chart)
  - Distribution par type de source (bar chart)
  - Top 10 des maladies (horizontal bar)
  - Top 10 des lieux (horizontal bar)
  - Box plots des statistiques textuelles
- **Interface moderne** : Sidebar de filtres + design gradient

## 🦠 Maladies détectées

Le système identifie plus de 30 maladies animales :
- Anthrax, Fièvre de la Vallée du Rift, Bluetongue
- Brucellose, Grippe équine, Rage
- Fièvre Aphteuse, Newcastle, EHD
- Dermatose Nodulaire (LSD), Peste Porcine
- Influenza Aviaire, COVID-19 chez les animaux
- Et bien d'autres...

## 📍 Localisation géographique

Détection automatique de :
- **Pays** : Tunisie, Égypte, Maroc, Arabie Saoudite, France, USA, Chine...
- **Villes** : Tunis, Le Caire, Riyadh, Casablanca, Alexandrie...
- Support des noms en français, anglais et arabe

## 🛠️ Installation

### Prérequis
```bash
Python 3.8+
```

### Dépendances
```bash
pip install pandas requests beautifulsoup4 selenium plotly dash
pip install chromedriver-autoinstaller  # Pour Selenium
```

### Structure du projet
```
animal-disease-tracker/
├── extract.py              # Script d'extraction
├── dashboard.py            # Dashboard interactif
├── urls.csv               # Liste des URLs à scraper
├── output/
│   └── animal_diseases_dataset.csv  # Données extraites
└── README.md
```

## 🚀 Utilisation

### 1️⃣ Préparation des URLs
Créez `urls.csv` avec vos URLs :
```csv
code,url
code151,https://example.com/article1
code152,https://example.com/article2
```

### 2️⃣ Extraction des données
```bash
python extract.py
```

**Sortie :**
- Traite jusqu'à 50 URLs (personnalisable)
- Affiche la progression en temps réel
- Sauvegarde dans `output/animal_diseases_dataset.csv`
- Statistiques finales : langues, sources, maladies, lieux

**Exemple de sortie console :**
```
======================================================================
🦠 EXTRACTION DES NEWS SUR LES MALADIES ANIMALES
🚀 VERSION AMÉLIORÉE - AVEC SUPPORT JAVASCRIPT (SELENIUM)
======================================================================

✅ 50 URLs chargées
🧪 Test de Selenium...
✅ Selenium opérationnel

======================================================================
📄 [1/50] Traitement de code151
======================================================================
🔗 https://example.com/article1
  📥 Téléchargement (requests)...
  ✅ Texte extrait : 3847 caractères
  🌍 Langue : français
  📊 845 mots, 3847 caractères
  📅 Date : 15-03-2025
  📍 Lieu : Tunisie
  🦠 Maladie : Fièvre Catarrhale / Bluetongue
  📰 Source : médias
  ✅ Données enregistrées
```

### 3️⃣ Lancement du dashboard
```bash
python dashboard.py
```

**Accès :**
- Ouvrez votre navigateur à `http://127.0.0.1:8050/`
- Le dashboard se met à jour automatiquement selon les filtres

## 📊 Structure des données

### Fichier de sortie : `animal_diseases_dataset.csv`

| Colonne | Description | Exemple |
|---------|-------------|---------|
| `code` | Identifiant unique | code151 |
| `url` | URL source | https://example.com/... |
| `titre` | Titre de l'article | "Alerte Fièvre Catarrhale..." |
| `contenu` | Texte complet | "Un nouveau foyer de..." |
| `langue` | Langue détectée | français / anglais / arabe |
| `nb_caracteres` | Nombre de caractères | 3847 |
| `nb_mots` | Nombre de mots | 845 |
| `date_publication` | Date (DD-MM-YYYY) | 15-03-2025 |
| `lieu` | Pays/Ville | Tunisie |
| `maladie` | Maladie détectée | Fièvre Catarrhale / Bluetongue |
| `source_type` | Type de source | médias / site officiel / réseaux sociaux |
| `resume_50` | Résumé 50 mots | "Un nouveau foyer de..." |
| `resume_100` | Résumé 100 mots | "Un nouveau foyer de..." |
| `resume_150` | Résumé 150 mots | "Un nouveau foyer de..." |
| `entites_nommees` | Entités extraites | OMS;bovins;WOAH |

## 🎨 Captures d'écran du Dashboard

### Vue d'ensemble
- **KPIs** : Nombre total d'articles, mots moyens, maladies uniques, lieux
- **Filtres latéraux** : Langue, Source, Lieu, Maladie

### Graphiques
1. **Répartition par langue** (donut) : Français 58%, Arabe 22%, Anglais 10%, Non détecté 10%
2. **Répartition par source** (bar) : Médias 31, Sites officiels 14, Non classé 5
3. **Top 10 maladies** : Fièvre Catarrhale 9, Non identifiée 7, LSD 7...
4. **Top 10 lieux** : France 9, USA 7, Non spécifié 7...
5. **Distribution statistique** (box plots) : Nombre de mots et caractères

## 🔧 Configuration avancée

### Modifier le nombre d'URLs traitées
Dans `extract.py`, ligne 389 :
```python
for idx, row in df_urls.head(50).iterrows():  # Changez 50
```

### Ajouter une maladie
Dans `extract.py`, fonction `extract_disease()` :
```python
diseases = {
    "Votre Maladie": ["keyword1", "keyword2", "الكلمة_العربية"],
    # ...
}
```

### Personnaliser le dashboard
Dans `dashboard.py` :
- **Couleurs** : Modifiez `color_discrete_sequence`, `color_continuous_scale`
- **Hauteur graphiques** : Paramètre `height` dans chaque figure
- **KPIs** : Section `kpis` du callback

## ⚠️ Gestion des erreurs

### Problème : "Aucune donnée valide"
**Solution :**
1. Vérifiez que `extract.py` a été exécuté
2. Contrôlez `output/animal_diseases_dataset.csv`
3. Assurez-vous qu'il contient des entrées avec `langue != 'N/A'`

### Problème : Selenium ne fonctionne pas
**Solution :**
```bash
pip install chromedriver-autoinstaller
```
Ou téléchargez ChromeDriver manuellement : https://chromedriver.chromium.org/

### Problème : Contenu insuffisant (< 100 caractères)
**Causes possibles :**
- Site bloque le scraping
- Contenu chargé en JavaScript (vérifiez que Selenium fonctionne)
- URL invalide ou paywall

**Solution :**
- Les entrées en erreur sont marquées avec `langue = 'N/A'`
- Elles sont exclues des statistiques mais conservées dans le CSV

## 📈 Statistiques d'exemple

D'après l'extraction de 50 URLs :
- ✅ **45 entrées valides** / 50 totales
- ❌ **5 entrées en erreur** (contenu insuffisant)

**Répartition par langue :**
- Français : 26 (58%)
- Arabe : 10 (22%)
- Anglais : 5 (11%)
- Non détecté : 4 (9%)

**Top 3 maladies :**
1. Fièvre Catarrhale / Bluetongue : 9 articles
2. Non identifiée : 7 articles
3. Dermatose Nodulaire (LSD) : 7 articles

**Top 3 lieux :**
1. France : 9 articles
2. USA : 7 articles
3. Non spécifié : 7 articles

## 🤝 Contribution

Pour améliorer le projet :
1. **Ajoutez des maladies** dans `extract_disease()`
2. **Enrichissez les localisations** dans `extract_location()`
3. **Améliorez la détection de langue** dans `detect_language()`
4. **Proposez de nouveaux graphiques** dans `dashboard.py`

## 📝 Licence

Ce projet est fourni à des fins éducatives et de recherche. Respectez les conditions d'utilisation des sites web scrapés.

## 🙏 Crédits

- **Scraping** : BeautifulSoup, Selenium
- **Analyse** : Pandas, Regex
- **Visualisation** : Plotly, Dash
- **Données** : Sources officielles (WOAH, médias internationaux)

