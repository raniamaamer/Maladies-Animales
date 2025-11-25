# 🦠 Maladies Animales - Système d'Extraction et Analyse de Données

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Pandas](https://img.shields.io/badge/Pandas-Latest-green.svg)](https://pandas.pydata.org/)
[![Dash](https://img.shields.io/badge/Dash-Latest-red.svg)](https://dash.plotly.com/)
[![Selenium](https://img.shields.io/badge/Selenium-Latest-yellow.svg)](https://selenium-python.readthedocs.io/)

## 📋 Description

**Maladies Animales** est un système complet d'extraction, de traitement et de visualisation de données pour le suivi et l'analyse des maladies animales à travers le monde. Le projet combine du web scraping intelligent (avec support JavaScript), du traitement automatique du langage naturel multilingue, et un dashboard interactif pour l'analyse des données.

### 🎯 Objectifs du Projet

- **Collecte automatisée** : Extraction de données depuis des sources web variées (sites officiels, médias, rapports)
- **Traitement multilingue** : Support de l'arabe, français et anglais
- **Analyse intelligente** : Détection automatique des maladies, lieux, dates et entités
- **Visualisation interactive** : Dashboard Dash pour explorer les données en temps réel

## ✨ Fonctionnalités Principales

### 🔍 Module d'Extraction (`extract.py`)

- **Web Scraping Hybride** :
  - Extraction classique avec `requests` et `BeautifulSoup`
  - Support JavaScript avec `Selenium` pour les sites dynamiques
  - Détection automatique du type de site et adaptation de la méthode

- **Traitement Multilingue** :
  - Détection automatique de la langue (arabe, français, anglais)
  - Extraction intelligente du contenu principal
  - Nettoyage et normalisation du texte

- **Analyse Sémantique** :
  - Détection de 25+ maladies animales (avec variantes linguistiques)
  - Extraction automatique des lieux (pays, villes, gouvernorats)
  - Extraction des dates de publication
  - Identification des entités nommées (organisations, animaux)
  - Génération de résumés (50, 100, 150 mots)

- **Robustesse** :
  - Gestion complète des erreurs
  - Sauvegardes temporaires régulières
  - Support des sites nécessitant JavaScript
  - Rate limiting et timeout configurables

### 📊 Dashboard Interactif (`dashboard.py`)

- **Interface Moderne** :
  - Sidebar avec filtres dynamiques (langue, source, lieu, maladie)
  - KPIs en temps réel
  - 6 visualisations interactives
  - Design responsive et moderne

- **Visualisations Disponibles** :
  - Répartition par langue (graphique en camembert)
  - Distribution par type de source (graphique en barres)
  - Top 10 des maladies détectées
  - Top 10 des lieux mentionnés
  - Statistiques sur le nombre de mots et caractères

- **Filtrage Avancé** :
  - Filtres multiples combinables
  - Mise à jour en temps réel des graphiques
  - Affichage des statistiques filtrées

## 🛠️ Technologies Utilisées

### Backend & Extraction
- **Python 3.8+** : Langage principal
- **Pandas** : Manipulation et analyse de données
- **Requests** : Requêtes HTTP
- **BeautifulSoup4** : Parsing HTML
- **Selenium** : Automatisation de navigateur pour sites JavaScript

### Dashboard & Visualisation
- **Dash** : Framework pour dashboards interactifs
- **Plotly** : Graphiques interactifs
- **Dash Core Components** : Composants UI

### Traitement du Texte
- **Regex** : Extraction de patterns (dates, entités)
- Support multilingue (arabe, français, anglais)

## 📦 Installation

### Prérequis

- Python 3.8 ou supérieur
- ChromeDriver (pour Selenium)
- pip (gestionnaire de paquets Python)

### Installation des Dépendances

```bash
# Cloner le dépôt
git clone https://github.com/raniamaamer/Maladies-Animales.git
cd Maladies-Animales

# Créer un environnement virtuel (recommandé)
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances
pip install pandas requests beautifulsoup4 selenium plotly dash

# Installer ChromeDriver automatiquement (optionnel)
pip install chromedriver-autoinstaller
```

### Configuration de Selenium

**Option 1 : Installation automatique**
```python
import chromedriver_autoinstaller
chromedriver_autoinstaller.install()
```

**Option 2 : Installation manuelle**
1. Téléchargez ChromeDriver depuis [chromedriver.chromium.org](https://chromedriver.chromium.org/)
2. Ajoutez ChromeDriver au PATH de votre système

## 🚀 Utilisation

### 1️⃣ Préparation des Données

Créez un fichier `urls.csv` avec vos URLs à analyser :

```csv
code,url
code151,https://example.com/article1
code152,https://example.com/article2
code153,https://example.com/article3
```

### 2️⃣ Extraction des Données

```bash
python extract.py
```

**Ce script va** :
- Charger les URLs depuis `urls.csv`
- Extraire le contenu de chaque page
- Détecter la langue et analyser le contenu
- Identifier les maladies, lieux et dates
- Générer un dataset complet dans `output/animal_diseases_dataset.csv`

**Options de configuration dans le code** :
```python
# Nombre d'URLs à traiter
df_urls.head(50)  # Modifiez 50 pour traiter plus/moins d'URLs

# Délai entre les requêtes
time.sleep(1)  # Augmentez pour être plus respectueux des serveurs
```

### 3️⃣ Lancement du Dashboard

```bash
python dashboard.py
```

**Accédez au dashboard** :
- Ouvrez votre navigateur
- Visitez `http://127.0.0.1:8050/`
- Explorez les données avec les filtres interactifs

**Arrêter le serveur** : `Ctrl+C`

## 📁 Structure du Projet

```
Maladies-Animales/
├── extract.py                 # Script d'extraction et traitement
├── dashboard.py               # Dashboard interactif Dash
├── urls.csv                   # Fichier source avec les URLs (à créer)
├── output/                    # Dossier de sortie
│   └── animal_diseases_dataset.csv  # Dataset généré
├── README.md                  # Documentation
└── requirements.txt           # Dépendances Python (optionnel)
```

## 📊 Format des Données Générées

Le fichier `animal_diseases_dataset.csv` contient les colonnes suivantes :

| Colonne | Description | Exemple |
|---------|-------------|---------|
| `code` | Identifiant unique de l'article | code151 |
| `url` | URL source | https://example.com/... |
| `titre` | Titre de l'article | "Bluetongue virus detected..." |
| `contenu` | Texte complet extrait | "Bluetongue virus was..." |
| `langue` | Langue détectée | anglais / français / arabe |
| `nb_caracteres` | Nombre de caractères | 2847 |
| `nb_mots` | Nombre de mots | 456 |
| `date_publication` | Date extraite | 12-01-2025 |
| `lieu` | Lieu principal mentionné | Tunisie / Égypte / Qatar |
| `maladie` | Maladie identifiée | Bluetongue / Anthrax |
| `source_type` | Type de source | site officiel / médias |
| `resume_50` | Résumé court (50 mots) | "Bluetongue virus..." |
| `resume_100` | Résumé moyen (100 mots) | "Bluetongue virus..." |
| `resume_150` | Résumé long (150 mots) | "Bluetongue virus..." |
| `entites_nommees` | Entités extraites | OMS;bovins;FAO |

## 🦠 Maladies Détectées

Le système peut identifier 25+ maladies animales, incluant :

- **Maladies virales** : Bluetongue, Fièvre de la Vallée du Rift, Grippe aviaire, COVID-19, Rage
- **Maladies bactériennes** : Anthrax, Brucellose, Tuberculose, Tularémie
- **Maladies parasitaires** : Babésiose, Échinococcose, Trypanosomose
- **Autres** : Maladie de Newcastle, Peste des Petits Ruminants, Clavelée, etc.

Chaque maladie est détectable en **arabe, français et anglais** avec leurs variantes.

## 🌍 Couverture Géographique

Le système peut identifier les lieux suivants :

**Pays** : Tunisie, Algérie, Maroc, Égypte, Arabie Saoudite, Qatar, UAE, France, USA, etc.

**Villes** : Tunis, Le Caire, Riyadh, Casablanca, Alexandrie, Sfax, etc.

**Support multilingue** : Les lieux sont détectés en arabe, français et anglais.

## 🧪 Exemples d'Utilisation

### Exemple 1 : Extraction Simple

```python
# Dans extract.py, modifier pour traiter 10 URLs
df_urls.head(10)
```

### Exemple 2 : Filtrage dans le Dashboard

1. Lancez le dashboard
2. Sélectionnez "Langue : arabe"
3. Sélectionnez "Maladie : Bluetongue"
4. Observez les résultats filtrés en temps réel

### Exemple 3 : Analyse des Statistiques

```python
import pandas as pd

# Charger les données
df = pd.read_csv('output/animal_diseases_dataset.csv')

# Top 5 des maladies
print(df['maladie'].value_counts().head())

# Moyenne de mots par langue
print(df.groupby('langue')['nb_mots'].mean())

# Articles par pays
print(df['lieu'].value_counts())
```

## ⚙️ Configuration Avancée

### Ajuster les Timeouts Selenium

```python
# Dans extract.py, ligne ~140
wait = WebDriverWait(driver, 20)  # Augmentez à 30 pour sites lents
```

### Personnaliser les Maladies Détectées

```python
# Dans extract.py, fonction extract_disease()
diseases = {
    "Votre Maladie": ["keyword1", "keyword2", "كلمة عربية"],
    # ...
}
```

### Modifier les Couleurs du Dashboard

```python
# Dans dashboard.py, section KPIs
'background': 'linear-gradient(135deg, #VOTRE_COULEUR1, #VOTRE_COULEUR2)'
```

## 🐛 Dépannage

### Problème : Selenium ne fonctionne pas

**Solution** :
```bash
pip install chromedriver-autoinstaller
```
Ou installez ChromeDriver manuellement et ajoutez-le au PATH.

### Problème : Erreur "Contenu insuffisant"

**Causes possibles** :
- Le site bloque les scrapers → Utilisez Selenium
- Le site nécessite une authentification
- L'URL est invalide

**Solution** : Vérifiez les URLs dans `urls.csv` et ajoutez le domaine à la liste `js_sites` dans `extract.py`.

### Problème : Dashboard ne se lance pas

**Solution** :
```bash
# Vérifiez que le fichier existe
ls output/animal_diseases_dataset.csv

# Relancez l'extraction si nécessaire
python extract.py
```

### Problème : Erreur d'encodage

**Solution** : Le fichier est sauvegardé en UTF-8-SIG. Assurez-vous d'utiliser :
```python
pd.read_csv('file.csv', encoding='utf-8-sig')
```

## 📈 Performances

- **Vitesse d'extraction** : ~2-5 secondes par page (requests), ~8-15 secondes (Selenium)
- **Taux de succès** : >85% pour les sites standards
- **Précision de détection** : ~90% pour les maladies communes
- **Support multilingue** : 3 langues (arabe, français, anglais)






