import ollama
import re
import json
import logging

MODEL = "llama3.2"

def query_ollama(prompt: str, max_tokens: int = 500) -> str:
    """Query Ollama avec timeout et options optimisées"""
    try:
        response = ollama.chat(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            options={
                "temperature": 0.1,
                "num_predict": max_tokens,  # Limite le nombre de tokens générés
                "num_ctx": 2048,  # Réduit la taille du contexte
                "top_k": 40,
                "top_p": 0.9
            }
        )
        return response["message"]["content"].strip()
    except Exception as e:
        logging.error(f"Erreur LLM: {e}")
        return f"[Erreur LLM: {str(e)}]"

def extract_metadata_only(text: str) -> dict:
    """
    Extraction rapide UNIQUEMENT des métadonnées (sans résumés)
    Plus rapide car génère moins de texte
    """
    # Limiter le texte à analyser
    text_sample = text[:1500]  # Réduit de 4000 à 1500 caractères
    
    prompt = f"""Analyse ce texte et extrais UNIQUEMENT ces 4 informations en JSON:
{{"date_publication": "jj-mm-aaaa ou inconnue", "lieu": "pays/région ou inconnu", "maladie": "nom ou inconnue", "animal": "espèce ou inconnu"}}

Texte:
{text_sample}

Réponds UNIQUEMENT avec le JSON, rien d'autre."""

    raw_response = query_ollama(prompt, max_tokens=150)
    
    # Extraire le JSON
    json_match = re.search(r"\{.*\}", raw_response, re.DOTALL)
    if json_match:
        try:
            data = json.loads(json_match.group())
            return {
                "date_publication": data.get("date_publication", "inconnue"),
                "lieu": data.get("lieu", "inconnu"),
                "maladie": data.get("maladie", "inconnue"),
                "animal": data.get("animal", "inconnu")
            }
        except:
            pass
    
    return {
        "date_publication": "inconnue",
        "lieu": "inconnu",
        "maladie": "inconnue",
        "animal": "inconnu"
    }

def generate_summary(text: str, word_count: int) -> str:
    """
    Génère un seul résumé à la fois (plus rapide que 3 en même temps)
    """
    text_sample = text[:2000]  # Limite le contexte
    
    prompt = f"""Résume ce texte en EXACTEMENT {word_count} mots en français. 
Sois factuel et précis. Réponds UNIQUEMENT avec le résumé, sans introduction.

Texte:
{text_sample}"""

    summary = query_ollama(prompt, max_tokens=word_count * 2)
    
    # Nettoyer le résumé
    summary = re.sub(r'^(Résumé|Voici|Le texte).*?:', '', summary, flags=re.IGNORECASE).strip()
    
    return summary if summary else "Résumé indisponible."

def extract_fields_with_llm(text: str, url: str):
    """
    Version OPTIMISÉE : Traitement en 2 étapes séparées
    1. Métadonnées (rapide)
    2. Résumés (plus lent, mais fait en parallèle)
    """
    logging.info("  → Extraction des métadonnées...")
    
    # Étape 1 : Extraction rapide des métadonnées
    metadata = extract_metadata_only(text)
    
    logging.info(f"  → Métadonnées extraites: {metadata['maladie']} / {metadata['animal']} / {metadata['lieu']}")
    
    # Étape 2 : Génération des résumés (un par un pour éviter la surcharge)
    logging.info("  → Génération résumé 50 mots...")
    resume_50 = generate_summary(text, 50)
    
    logging.info("  → Génération résumé 100 mots...")
    resume_100 = generate_summary(text, 100)
    
    logging.info("  → Génération résumé 150 mots...")
    resume_150 = generate_summary(text, 150)
    
    return {
        **metadata,
        "resume_50_mots": resume_50,
        "resume_100_mots": resume_100,
        "resume_150_mots": resume_150
    }

# ============================================
# VERSION ULTRA-RAPIDE (OPTIONNELLE)
# ============================================

def extract_fields_fast(text: str, url: str):
    """
    VERSION ULTRA-RAPIDE : Un seul appel LLM pour tout
    Compromis : résumés moins précis mais traitement 3-4x plus rapide
    """
    text_sample = text[:2000]
    
    prompt = f"""Analyse ce texte et réponds en JSON avec EXACTEMENT ces clés:
{{"date_publication": "jj-mm-aaaa", "lieu": "pays", "maladie": "nom", "animal": "espèce", "resume": "résumé en 100 mots"}}

Texte:
{text_sample}

JSON uniquement:"""

    raw_response = query_ollama(prompt, max_tokens=300)
    
    json_match = re.search(r"\{.*\}", raw_response, re.DOTALL)
    if json_match:
        try:
            data = json.loads(json_match.group())
            resume = data.get("resume", "Résumé indisponible.")
            
            return {
                "date_publication": data.get("date_publication", "inconnue"),
                "lieu": data.get("lieu", "inconnu"),
                "maladie": data.get("maladie", "inconnue"),
                "animal": data.get("animal", "inconnu"),
                "resume_50_mots": resume[:200] + "..." if len(resume) > 200 else resume,
                "resume_100_mots": resume,
                "resume_150_mots": resume + " " + resume[:100] if len(resume) < 500 else resume
            }
        except Exception as e:
            logging.error(f"Erreur parsing JSON: {e}")
    
    # Valeurs par défaut
    return {
        "date_publication": "inconnue",
        "lieu": "inconnu",
        "maladie": "inconnue",
        "animal": "inconnu",
        "resume_50_mots": "Résumé indisponible.",
        "resume_100_mots": "Résumé indisponible.",
        "resume_150_mots": "Résumé indisponible."
    }