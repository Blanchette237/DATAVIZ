import json
import matplotlib.pyplot as plt

def tracer_histogrammes() :
    # Chargement des données JSON
    fichier_json = '../Themes/resultats_ia_en.json'
    try :
        with open(fichier_json, 'r', encoding = 'utf-8') as f:
            data = json.load(f)
    except FileNotFoundError :
        print(f"Erreur : Le fichier '{fichier_json}' n'existe pas.")
        return

    scores_top1 = []
    scores_top2 = []
    scores_top3 = []

    for publi in data :
        if "all_scores" in publi and len(publi["all_scores"]) >= 3 :
            scores_top1.append(publi['all_scores'][0]['score'])
            scores_top2.append(publi['all_scores'][1]['score'])
            scores_top3.append(publi['all_scores'][2]['score'])
        else :
            print(f"Attention : Données incomplètes pour la publication (ID: {publi.get('id_publication', 'Inconnu')})")

    # Configuration des tranches de 0 à 100 par pas de 10
    tranches = range(0, 101, 10)

    # Création de la figure avec 3 sous-graphiques
    fig, axes = plt.subplots(1, 3, figsize = (15, 5), sharey = True)
    fig.suptitle('Distribution des scores de confiance', fontsize = 16)

    couleurs = ['#4CAF50', '#2196F3', '#FF9800']
    titres = ['Scores du Top 1', 'Scores du Top 2', 'Scores du Top 3']
    donnees = [scores_top1, scores_top2, scores_top3]

    for i in range(3) :
        axes[i].hist(donnees[i], bins = tranches, color = couleurs[i], edgecolor = 'black', alpha = 0.7)
        axes[i].set_title(titres[i])
        axes[i].set_xlabel('Score de confiance (%)')
        axes[i].set_xticks(tranches)
        axes[i].grid(axis = 'y', linestyle = '--', alpha = 0.7)

    axes[0].set_ylabel('Nombre de publications')

    # Ajustement de l'affichage et sauvegarde
    plt.tight_layout()
    plt.savefig('distribution_scores.png', dpi = 300)
    plt.show()

if __name__ == "__main__" :
    tracer_histogrammes()