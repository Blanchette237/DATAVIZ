"""
L'Union des Top 3 annuels.
Ce script fusionne les résultats IA avec les années de publication,
calcule le Top 3 des thèmes pour chaque année, puis génère l'Union mathématique
de tous ces Tops.
"""

import json
import numpy as np
from collections import Counter
from sqlalchemy import create_engine, text

# Configuration
DB_USER = 'admin'
DB_PASSWORD = 'admin'
DB_HOST = 'localhost'
DB_NAME = 'conference'

engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")

def extraire_themes_zscore(liste_scores_publi, z_seuil = 2.0) :
    """
    Filtre le bruit de l'IA et ne garde que les anomalies positives (Z-Score).
    """
    if not liste_scores_publi :
        return []

    scores = [item['score'] for item in liste_scores_publi]
    moyenne = np.mean(scores)
    ecart_type = np.std(scores)

    if ecart_type == 0 :
        return [liste_scores_publi[0]['theme']]

    themes_gardes = []
    for item in liste_scores_publi :
        z_score = (item['score'] - moyenne) / ecart_type
        if z_score > z_seuil :
            themes_gardes.append(item['theme'])
        else :
            break

    if not themes_gardes :
        themes_gardes.append(liste_scores_publi[0]['theme'])

    return themes_gardes

def charger_annees_depuis_db() :
    """
    Renvoie un dictionnaire liant le titre à l'année.
    Format de retour : { "Titre de la publication": "2019", ... }
    """
    map_titre_annee = {}
    print("Connexion à la base de données...")

    with engine.connect() as conn :
        # Requête simple sur la table publication
        requete = text("SELECT titre, annee_edition FROM publication WHERE annee_edition IS NOT NULL")
        resultats = conn.execute(requete).fetchall()

        for titre, annee_edition in resultats :
            # On nettoie l'année au cas où et on la stocke en chaîne de caractères
            annee = str(annee_edition).strip()
            # Nettoyage basique du titre pour faciliter la jointure avec le JSON
            titre_propre = str(titre).strip()
            map_titre_annee[titre_propre] = annee

    print(f"{len(map_titre_annee)} dates de publications récupérées depuis la DB.")
    return map_titre_annee

def calculer_union_top3() :
    # Chargement des données
    map_titre_annee = charger_annees_depuis_db()

    if not map_titre_annee :
        print("Erreur : Aucune donnée trouvée dans la table 'publication'.")
        return

    try :
        with open('../Themes/resultats_ia_en.json', 'r', encoding ='utf-8') as f :
            res_ia = json.load(f)
        print("Fichier 'resultats_ia_en.json' chargé avec succès.\n")
    except FileNotFoundError :
        print("Erreur : Fichier 'resultats_ia_en.json' introuvable.")
        return

    print("Début du croisement des données et de l'analyse...\n")

    # Agrégation des thèmes par année
    themes_par_annee = {}
    publications_ignorees = 0

    for publi in res_ia :
        titre = publi.get('titre', '').strip()
        scores_complets = publi.get('all_scores', [])

        # On cherche l'année en utilisant le titre comme clé
        annee = map_titre_annee.get(titre)

        if annee and scores_complets :
            # Extraction des vrais thèmes avec notre filtre scientifique
            themes_valides = extraire_themes_zscore(scores_complets, z_seuil = 2.0)

            if annee not in themes_par_annee :
                themes_par_annee[annee] = []

            themes_par_annee[annee].extend(themes_valides)
        else :
            publications_ignorees += 1

    if publications_ignorees > 0 :
        print(f"{publications_ignorees} publications du JSON ont été ignorées (année inconnue dans la DB ou pas de scores).")

    # Calcul du Top 3 par année et de l'Union finale
    union_des_top3 = set()

    print("\nCLASSEMENTS ANNUELS \n")
    for annee, liste_themes in sorted(themes_par_annee.items()) :
        compteur = Counter(liste_themes)
        top_3_annee = compteur.most_common(3)

        print(f"Top 3 pour l'édition BDA {annee} :")
        for rang, (theme, compte) in enumerate(top_3_annee) :
            print(f"    {rang + 1}. {theme} ({compte} occurences)")
            # Ajout du thème dans l'Union globale
            union_des_top3.add(theme)
        print("-" * 40)

    # Résultat final
    print("\n================================================")
    print("RÉSULTAT FINAL : L'UNION DES TOP 3 HISTORIQUES")
    print("================================================\n")
    print(f"L'analyse révèle {len(union_des_top3)} thématiques majeures qui ont dominé la conférence :\n")

    for i, theme in enumerate(sorted(union_des_top3)) :
        print(f" {i+1}. {theme}")

if __name__ == "__main__":
    calculer_union_top3()