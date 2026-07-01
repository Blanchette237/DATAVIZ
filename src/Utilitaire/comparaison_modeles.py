import json
import numpy as np

def extraire_themes_top_p(liste_scores_publi, p_seuil = 60.0):
    """ Additionne les scores jusqu'à atteindre un pourcentage de confiance global (P). """
    if not liste_scores_publi :
        return []

    themes_gardes = []
    somme_probabilites = 0.0

    for item in liste_scores_publi :
        themes_gardes.append(item['theme'])
        somme_probabilites += item['score']

        # On s'arrête dès que la somme des scores dépasse notre seuil
        if somme_probabilites >= p_seuil :
            break

    return themes_gardes

def extraire_themes_zscore(liste_scores_publi, z_seuil = 1.5) :
    """ Garde uniquement les thèmes dont le score est anormalement haut par rapport à la moyenne. """
    if not liste_scores_publi :
        return []

    # On extrait les valeurs numériques pour les calculs
    scores = [item['score'] for item in liste_scores_publi]
    moyenne = np.mean(scores)
    ecart_type = np.std(scores)

    if ecart_type == 0 :
        return [liste_scores_publi[0]['theme']]

    themes_gardes = []
    for item in liste_scores_publi :
        # Calcul du Z-Score : à combien d'écarts-types sommes-nous au-dessus de la moyenne ?
        z_score = (item['score'] - moyenne) / ecart_type

        if z_score > z_seuil :
            themes_gardes.append(item['theme'])
        else : # Liste triée donc on arrète
            break

    # On garde toujours au moins le Top 1
    if not themes_gardes :
        themes_gardes.append(liste_scores_publi[0]['theme'])

    return themes_gardes

def extraire_themes_kneedle(liste_scores_publi):
    """ Trouve le point de courbure maximal sur l'ensemble de la courbe. """
    if not liste_scores_publi or len(liste_scores_publi) < 2:
        return [liste_scores_publi[0]['theme']] if liste_scores_publi else []

    scores = [item['score'] for item in liste_scores_publi]
    y_max, y_min = max(scores), min(scores)

    if y_max == y_min :
        return [liste_scores_publi[0]['theme']]

    n = len(scores)
    max_distance = -float('inf')
    index_coude = 0

    for i in range(n) :
        # Normalisation de l'axe X et de l'axe Y
        x_norm = i / (n - 1)
        y_norm = (scores[i] - y_min) / (y_max - y_min)

        # Calcul de la distance par rapport à la ligne droite imaginaire
        distance = y_norm - (1.0 - x_norm)

        # On cherche le point le plus éloigné de cette diagonale
        if distance > max_distance:
            max_distance = distance
            index_coude = i

    # On garde tous les thèmes jusqu'au point de coude inclus
    return [item['theme'] for item in liste_scores_publi[:index_coude + 1]]

def comparer_methodes() :
    fichier_json = 'resultats_ia_en.json'
    try :
        with open(fichier_json, 'r', encoding='utf-8') as f :
            data = json.load(f)
    except FileNotFoundError :
        print(f"Erreur : Le fichier '{fichier_json}' n'existe pas. Lancez d'abord le script d'export.")
        return

    print("Lancement du banc d'essai des algorithmes académiques...\n")

    for index, publi in enumerate(data) :
        titre = publi.get('titre', 'Titre inconnu')
        scores_complets = publi.get('all_scores', [])

        # Affichage des 5 premiers scores pour comprendre le contexte visuellement
        top_scores = [round(s['score'], 1) for s in scores_complets[:5]]

        # Exécution des 3 algorithmes
        res_topp = extraire_themes_top_p(scores_complets, p_seuil=60.0)
        res_zscore = extraire_themes_zscore(scores_complets, z_seuil=2)
        res_kneedle = extraire_themes_kneedle(scores_complets)

        # Affichage formaté
        print(f"Publi {index + 1} : {titre[:60]}...")
        print(f"    Scores (Top 5) : {top_scores}")
        print(f"        Top-P (P=60%) -> {len(res_topp)} thème(s)")
        print(f"        Z-Score (Z=2) -> {len(res_zscore)} thème(s)")
        print(f"        Kneedle (Coude) -> {len(res_kneedle)} thème(s)")
        print("-" * 80)

if __name__ == "__main__":
    comparer_methodes()