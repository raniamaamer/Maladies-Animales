import requests
import json
import logging

def extract_fields_with_llm(text: str, url: str) -> dict:
    """
    Appelle un modèle LLM local pour extraire des champs structurés.
    """
    prompt = f"""
Tu es un expert en épidémiologie vétérinaire. Extrais les informations suivantes du texte.
Réponds UNIQUEMENT en JSON valide, sans explication ni texte supplémentaire.

Texte : {text[:3000]}

Champs à extraire :
- "date_publication" : Date au format JJ/MM/AAAA. Cherche des expressions comme "19 octobre 2023", "Oct 19, 2023", "2023-10-19". Si plusieurs dates, prends la plus proche du début du texte. Si aucune date, mets "inconnue".
- "lieu" : Pays, région ou ville mentionné(e) (ex: "France", "Jura", "Berne"). Si aucun, mets "inconnu".
- "maladie" : Nom exact de la maladie animale (ex: "Maladie hémorragique épizootique", "FCO", "Bluetongue"). Si aucune, mets "inconnue".
- "animal" : Espèce animale concernée (ex: "Bovins", "Ovins", "Équidés"). Si aucune, mets "inconnu".
- "resume_50_mots" : Résumé en environ 50 mots.
- "resume_100_mots" : Résumé en environ 100 mots.
- "resume_150_mots" : Résumé en environ 150 mots.

Exemple de réponse attendue :
{{
  "date_publication": "19/10/2023",
  "lieu": "Suisse, Jura",
  "maladie": "Maladie hémorragique épizootique",
  "animal": "Bovins",
  "resume_50_mots": "...",
  "resume_100_mots": "...",
  "resume_150_mots": "..."
}}
"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2",
                "prompt": prompt,
                "format": "json",
                "stream": False
            },
            timeout=90  # Augmenter timeout pour textes longs
        )
        if response.status_code == 200:
            result = response.json()
            output = json.loads(result["response"])
            
            # Vérifier toutes les clés
            required_keys = ["date_publication", "lieu", "maladie", "animal", 
                           "resume_50_mots", "resume_100_mots", "resume_150_mots"]
            for key in required_keys:
                if key not in output:
                    output[key] = "inconnu" if "resume" not in key else "Résumé non généré"
            
            return output
        else:
            logging.warning(f"Ollama error: {response.text}")
    except Exception as e:
        logging.error(f"Erreur LLM pour {url}: {e}")

    # Valeurs par défaut
    return {
        "date_publication": "inconnue",
        "lieu": "inconnu",
        "maladie": "inconnue",
        "animal": "inconnu",
        "resume_50_mots": "Erreur LLM",
        "resume_100_mots": "Erreur LLM",
        "resume_150_mots": "Erreur LLM"
    }