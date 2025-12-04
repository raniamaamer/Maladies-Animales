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

- "lieu" : **IMPORTANT** - Identifie le PAYS PRINCIPAL où se déroule l'événement ou d'où provient l'information. 
  * Si l'article parle d'un pays qui surveille/observe/réagit à une situation dans d'autres pays, le lieu est le PAYS QUI SURVEILLE.
  * Exemples : 
    - "Le Maroc surveille les cas en Europe" → lieu = "Maroc"
    - "La France détecte des cas en Suisse" → lieu = "France"
    - "Des cas détectés en Italie" → lieu = "Italie"
  * Donne UNIQUEMENT le pays principal, pas la liste des pays mentionnés.
  * Si aucun lieu clair, mets "inconnu".

- "maladie" : Nom exact de la maladie animale (ex: "Maladie hémorragique épizootique", "FCO", "Bluetongue", "Grippe aviaire"). Si aucune, mets "inconnue".

- "animal" : Espèce animale concernée (ex: "Bovins", "Ovins", "Équidés", "Volailles"). Si plusieurs espèces, liste-les séparées par des virgules. Si aucune, mets "inconnu".

- "resume_50_mots" : Résumé en environ 50 mots maximum.

- "resume_100_mots" : Résumé en environ 100 mots maximum.

- "resume_150_mots" : Résumé en environ 150 mots maximum.

Exemple de réponse attendue :
{{
  "date_publication": "19/10/2023",
  "lieu": "Maroc",
  "maladie": "Maladie hémorragique épizootique",
  "animal": "Bovins, Ovins",
  "resume_50_mots": "Le Maroc surveille l'apparition de la maladie hémorragique épizootique en Europe. L'ONSA met en place des contrôles stricts sur les importations d'animaux vivants pour prévenir l'introduction du virus au Maroc.",
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
                "stream": False,
                "options": {
                    "temperature": 0.3,  # Réduire la créativité pour plus de précision
                    "top_p": 0.9
                }
            },
            timeout=90
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
            
            # Post-traitement du lieu : nettoyer les listes si présentes
            lieu = output.get("lieu", "inconnu")
            if isinstance(lieu, str) and "," in lieu:
                # Prendre uniquement le premier pays mentionné
                output["lieu"] = lieu.split(",")[0].strip()
            
            logging.info(f"✅ Extraction LLM réussie - Lieu: {output['lieu']}")
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