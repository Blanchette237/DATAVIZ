import json
import matplotlib.pyplot as plt
import numpy as np

def tracer_histogramme_ecart() :
    # Chargement des données JSON
    fichier_json = '../Themes/resultats_ia_en.json'
    try :
        with open(fichier_json, 'r', encoding='utf-8') as f :
            data = json.load(f)
    except FileNotFoundError :
        print(f"Erreur : Le fichier '{fichier_json}' n'existe pas.")
        return

    # Calcul des différences entre le 3ème et le 4ème score
    liste_differences = []

    for publi in data :

        # Calcul de la différence
        if len(publi['all_scores']) >= 4 :
            score_3rd = publi['all_scores'][2]['score']
            score_4th = publi['all_scores'][3]['score']

            difference = score_3rd - score_4th
            liste_differences.append(difference)

    if not liste_differences :
        print("Aucune donnée disponible pour le calcul de l'écart (les publications ont moins de 4 thèmes).")
        return

    # Calcul de statistiques pour l'interprétation
    moyenne_ecart = np.mean(liste_differences)
    ecart_type = np.std(liste_differences)

    print(f"\n Statistiques de l'écart (3ème vs 4ème) :")
    print(f"   - Nombre d'articles analysés : {len(liste_differences)}")
    print(f"   - Écart moyen : {moyenne_ecart:.2f} points de %")
    print(f"   - Écart-type : {ecart_type:.2f}")

    # Traçage de l'Histogramme
    plt.figure(figsize = (10, 6))

    # On définit des tranches fines de 0.5% pour bien voir la distribution
    tranches = np.arange(0, max(liste_differences) + 0.5, 0.5)

    plt.hist(liste_differences, bins = tranches, color = '#FF9800', edgecolor = 'black', alpha = 0.8)

    # Ajout d'une ligne pour la moyenne
    plt.axvline(moyenne_ecart, color = 'red', linestyle = 'dashed', linewidth = 2, label = f'Moyenne ({moyenne_ecart:.1f}%)')

    plt.title('Distribution de l\'écart entre le 3ème et le 4ème score de l\'IA', fontsize = 14)
    plt.xlabel('Différence (points de pourcentage %)', fontsize = 12)
    plt.ylabel('Nombre de publications', fontsize = 12)
    plt.xticks(np.arange(0, max(liste_differences) + 1, 1)) # Ticks tous les 1%
    plt.legend()
    plt.grid(axis = 'y', linestyle = '--', alpha = 0.5)

    plt.tight_layout()
    plt.savefig('histogramme_ecart_3rd_4th.png', dpi = 300)
    plt.show()

if __name__ == "__main__":
    tracer_histogramme_ecart()