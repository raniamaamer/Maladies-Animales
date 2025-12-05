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

Texte : {text[:3500]}

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

- "maladie" : **CRITIQUE** - Identifie la maladie animale EXACTEMENT telle que mentionnée dans le texte.
  * RÈGLES STRICTES :
    - "Bluetongue" = "Bluetongue" (OU "Fièvre catarrhale ovine" si mentionné en français)
    - "African swine fever" = "Peste porcine africaine"
    - "Avian influenza" / "Bird flu" = "Grippe aviaire"
    - "Epizootic hemorrhagic disease" / "EHD" = "Maladie hémorragique épizootique"
    - "Foot and mouth disease" / "FMD" = "Fièvre aphteuse"
    - "Lumpy skin disease" = "Dermatose nodulaire contagieuse"
  * NE PAS confondre les maladies ! Lis attentivement le texte pour identifier la bonne maladie.
  * Vérifie que le nom de la maladie apparaît bien dans le texte avant de le retourner.
  * Si le texte parle de "bluetongue virus" ou "BTV", la maladie est "Bluetongue", PAS "Maladie hémorragique épizootique".
  * Si aucune maladie n'est clairement identifiée, mets "inconnue".

- "animal" : Espèce animale concernée (ex: "Bovins", "Ovins", "Équidés", "Volailles", "Porcins"). 
  * Si plusieurs espèces, liste-les séparées par des virgules (ex: "Bovins, Ovins").
  * Si aucune espèce n'est mentionnée, mets "inconnu".

- "resume_50_mots" : Résumé factuel en environ 50 mots maximum. Mentionne la maladie, le lieu et les animaux concernés.

- "resume_100_mots" : Résumé détaillé en environ 100 mots maximum. Inclus le contexte et les mesures prises.

- "resume_150_mots" : Résumé complet en environ 150 mots maximum. Ajoute l'historique et les impacts économiques si mentionnés.

Exemple de réponse attendue :
{{
  "date_publication": "16/10/2023",
  "lieu": "Allemagne",
  "maladie": "Bluetongue",
  "animal": "Ovins, Bovins",
  "resume_50_mots": "Le virus de la fièvre catarrhale ovine (Bluetongue) a été détecté en Allemagne après les Pays-Bas et la Belgique. Un mouton d'une ferme près de la frontière néerlandaise a été diagnostiqué positif, entraînant une quarantaine.",
  "resume_100_mots": "...",
  "resume_150_mots": "..."
}}

RAPPEL IMPORTANT : Vérifie bien que la maladie identifiée correspond aux symptômes et au virus mentionnés dans le texte !
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
                    "temperature": 0.1,  # Encore plus bas pour la précision
                    "top_p": 0.8,
                    "num_predict": 1000  # Augmenter pour les résumés
                }
            },
            timeout=120
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
                output["lieu"] = lieu.split(",")[0].strip()
            
            # Validation de la maladie : vérifier qu'elle n'est pas vide ou générique
            maladie = output.get("maladie", "").strip()
            if not maladie or len(maladie) < 3 or maladie.lower() in ["disease", "virus", "infection"]:
                output["maladie"] = "inconnue"
            
            logging.info(f"✅ Extraction LLM réussie - Lieu: {output['lieu']}, Maladie: {output['maladie']}")
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