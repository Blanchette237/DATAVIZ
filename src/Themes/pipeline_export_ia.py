"""
Pipeline d'évaluation par Intelligence Artificielle.
Ce script évalue les publications scientifiques et exporte les scores de confiance
pour les 28 thèmes officiels dans un fichier JSON.
"""

import time
import requests
import json
from sqlalchemy import create_engine, text
from transformers import pipeline

# Configuration
DB_USER = 'admin'
DB_PASSWORD = 'admin'
DB_HOST = 'localhost'
DB_NAME = 'conference'

engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")

# Chargement du modèle IA
print("Chargement du modèle d'IA Zero-Shot (Hugging Face)...")
# Utilisation du modèle XLM-Roberta Large
classificateur = pipeline("zero-shot-classification", model="joeddav/xlm-roberta-large-xnli")

def recuperer_resume_hal(titre) :
    """
    Interroge l'API du portail HAL pour tenter de récupérer le résumé d'un article à partir de son titre.
    Retourne le résumé (string) si trouvé, sinon None.
    """
    url = "https://api.archives-ouvertes.fr/search/"
    params = {
        "q": f'title_t:"{titre}"',
        "fl": "abstract_s",
        "wt": "json",
        "rows": 1
    }
    try :
        # Timeout de 5s pour éviter de bloquer le script si l'API HAL est hors-ligne
        reponse = requests.get(url, params=params, timeout=5)
        if reponse.status_code == 200:
            data = reponse.json()
            # Vérification que la recherche a bien retourné au moins un résultat
            if data.get("response", {}).get("numFound", 0) > 0 :
                doc = data["response"]["docs"][0]
                if "abstract_s" in doc :
                    return doc["abstract_s"][0]
    except Exception as e :
        pass

    return None

def lancer_pipeline_json() :
    """
    Lit les données en base, lance l'inférence IA,
    détermine les meileurs scores et sauvegarde les scores complets en JSON.
    """
    resultats_json = []

    with engine.begin() as conn :

        # Récupération des thèmes
        requete_themes = text("""
                              SELECT t.id, te.libelle_en
                              FROM theme t
                                       JOIN theme_en te ON t.id = te.id_theme
                              """)
        themes_db = conn.execute(requete_themes).fetchall()
        liste_noms_themes = [ligne[1] for ligne in themes_db]

        # Récupération des publications à évaluer
        publications = conn.execute(text("SELECT id, titre FROM publication WHERE titre IS NOT NULL")).fetchall()
        total = len(publications)

        print(f"\nDémarrage du traitement pour {total} publications (Export JSON)...\n")

        for index, publi in enumerate(publications) :
            pub_id = publi[0]
            titre = publi[1]

            print(f"    [{index + 1}/{total}] Traitement : {titre[:50]}...")

            # Évaluation du Titre
            res_titre = classificateur(titre, liste_noms_themes, hypothesis_template = "The topic of this text is {}.")

            # On recherche du résumé sur HAL
            resume = recuperer_resume_hal(titre)
            time.sleep(1)

            # On compare le score du titre et le score du résumé
            if resume :
                res_resume = classificateur(resume, liste_noms_themes, hypothesis_template = "The topic of this text is {}.")

                # On conserve le meilleur score
                if res_resume['scores'][0] >= res_titre['scores'][0] :
                    meilleur_res = res_resume
                    source = "Résumé"
                else :
                    meilleur_res = res_titre
                    source = "Titre"
            else:
                meilleur_res = res_titre
                source = "Titre (Fallback)"

            liste_scores_complete = []

            # Le modèle trie automatiquement par ordre décroissant
            for i in range(len(meilleur_res['labels'])) :
                liste_scores_complete.append({
                    "theme": meilleur_res['labels'][i],
                    "score": round(meilleur_res['scores'][i] * 100, 2)
                })

            donnees_publi = {
                "id_publication": pub_id,
                "titre": titre,
                "source_gagnante": source,
                "all_scores": liste_scores_complete
            }

            resultats_json.append(donnees_publi)

    # On sauvegarde le fichier
    with open('resultats_ia_en.json', 'w', encoding = 'utf-8') as f :
        json.dump(resultats_json, f, ensure_ascii = False, indent = 4)

    print("\nTerminé ! Les données brutes ont été exportées dans 'resultats_ia_en.json'.")

if __name__ == "__main__" :
    lancer_pipeline_json()