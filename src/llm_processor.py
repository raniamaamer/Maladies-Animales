import requests
import json
import logging

def extract_fields_with_llm(text: str, url: str) -> dict:
    """
    Appelle un modèle LLM local (ex: via Ollama) pour extraire des champs structurés.
    """
    prompt = f"""
    Tu es un expert en épidémiologie vétérinaire. À partir du texte suivant, extrais les informations demandées.
    Réponds UNIQUEMENT en JSON valide, sans explication.

    Texte : {text[:3000]}  # limiter la taille pour éviter overflow

    Champs à extraire :
    - "date_publication" (chaîne au format JJ/MM/AAAA ou "inconnue")
    - "lieu" (pays ou région mentionnée, sinon "inconnu")
    - "maladie" (nom de la maladie animale, sinon "inconnue")
    - "animal" (espèce animale concernée, sinon "inconnu")
    - "resume_50_mots" (résumé en ~50 mots)
    - "resume_100_mots" (résumé en ~100 mots)
    - "resume_150_mots" (résumé en ~150 mots)
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
            timeout=60
        )
        if response.status_code == 200:
            result = response.json()
            output = json.loads(result["response"])
            # S'assurer que toutes les clés sont présentes
            required_keys = ["date_publication", "lieu", "maladie", "animal", "resume_50_mots", "resume_100_mots", "resume_150_mots"]
            for key in required_keys:
                if key not in output:
                    output[key] = "inconnu" if "resume" not in key else "Résumé non généré"
            return output
        else:
            logging.warning(f"Ollama error: {response.text}")
    except Exception as e:
        logging.error(f"Erreur LLM pour {url}: {e}")

    # Valeurs par défaut en cas d'erreur
    return {
        "date_publication": "inconnue",
        "lieu": "inconnu",
        "maladie": "inconnue",
        "animal": "inconnu",
        "resume_50_mots": "Erreur LLM",
        "resume_100_mots": "Erreur LLM",
        "resume_150_mots": "Erreur LLM"
    }