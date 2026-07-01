"""
Filtrage Z-Score et Insertion en Base de Données.
Ce script lit l'export IA brut, applique l'algorithme du Z-Score pour
ne retenir que les thèmes pertinents, et met à jour la table de liaison 'est_classe'.
"""

import json
import numpy as np
from sqlalchemy import create_engine, text

# Configuration
DB_USER = 'admin'
DB_PASSWORD = 'admin'
DB_HOST = 'localhost'
DB_NAME = 'conference'

engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")

def extraire_themes_zscore(liste_scores_publi, z_seuil = 2.0) :
    """
    Garde uniquement les thèmes dont le score est anormalement haut par rapport à la
    moyenne de l'article (anomalies positives).
    Retourne une liste de dictionnaires avec le thème et son score.
    """
    if not liste_scores_publi :
        return []

    # On extrait les valeurs numériques pour calculer la distribution
    scores = [item['score'] for item in liste_scores_publi]
    moyenne = np.mean(scores)
    ecart_type = np.std(scores)

    if ecart_type == 0 :
        return [liste_scores_publi[0]]

    themes_gardes = []
    for item in liste_scores_publi :
        # Calcul du Z-Score
        z_score = (item['score'] - moyenne) / ecart_type

        # Si le score dépasse notre seuil de tolérance
        if z_score > z_seuil :
            themes_gardes.append(item)
        else : # La liste est triée donc on arrête
            break

    if not themes_gardes :
        themes_gardes.append(liste_scores_publi[0])

    return themes_gardes

def inserer_themes_en_base() :
    """
    Lit le fichier JSON, applique le filtre, et peuple la table est_classe.
    """
    fichier_json = 'resultats_ia_en.json'
    try :
        with open(fichier_json, 'r', encoding='utf-8') as f :
            data = json.load(f)
    except FileNotFoundError :
        print(f"Erreur : Le fichier '{fichier_json}' est introuvable.")
        return

    print(f"Début du filtrage (Z-Score) et de l'insertion pour {len(data)} publications...\n")

    with engine.begin() as conn :
        print("Nettoyage de la table 'est_classe'...")
        conn.execute(text("TRUNCATE TABLE est_classe"))

        # Création d'un dictionnaire pour traduire rapidement le "nom_en_anglais" en "id_theme"
        requete_themes = text("SELECT libelle_en, id_theme FROM theme_en")
        themes_db = conn.execute(requete_themes).fetchall()
        map_theme_nom_vers_id = {ligne[0]: ligne[1] for ligne in themes_db}

        compteur_insertions = 0

        for publi in data :
            id_publi = publi['id_publication']
            scores_complets = publi.get('all_scores', [])

            # Application de notre algorithme d'extraction
            themes_gagnants = extraire_themes_zscore(scores_complets, z_seuil = 2.0)

            # Insertion dans la base de données
            for theme_gagnant in themes_gagnants :
                nom_theme_en = theme_gagnant['theme']
                score_ia_brut = theme_gagnant['score']

                # On récupère l'ID correspondant au libellé
                id_theme = map_theme_nom_vers_id.get(nom_theme_en)

                if id_theme :
                    # Requête d'insertion dans la table de liaison
                    conn.execute(
                        text("""
                             INSERT INTO est_classe (id_publication, id_theme, score_ia)
                             VALUES (:id_pub, :id_thm, :score)
                             """),
                        {"id_pub": id_publi, "id_thm": id_theme, "score": score_ia_brut}
                    )
                    compteur_insertions += 1

    print(
        f"Opération terminée ! {compteur_insertions} liaisons 'Publication <-> Thème' ont été insérées dans la base de données.")

if __name__ == "__main__" :
    inserer_themes_en_base()