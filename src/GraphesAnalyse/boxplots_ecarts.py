import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def tracer_boxplots_ecarts() :
    # Chargement des données JSON
    fichier_json = '../Themes/resultats_ia_en.json'
    try :
        with open(fichier_json, 'r', encoding = 'utf-8') as f :
            data = json.load(f)
    except FileNotFoundError :
        print(f"Erreur : Le fichier '{fichier_json}' n'existe pas.")
        return

    # Dictionnaires pour stocker les listes de différences
    abs_diffs = {f"{i}-{i + 1}": [] for i in range(1, 28)}
    rel_diffs = {f"{i}-{i + 1}": [] for i in range(1, 28)}

    # Traitement des données
    for publi in data :
        # On extrait la liste des 28 scores numériques
        scores = [item['score'] for item in publi['all_scores']]

        if len(scores) < 28 :
            continue

        # Calcul des écarts
        for i in range(27) :
            s_i = scores[i]
            s_i_plus_1 = scores[i + 1]
            label = f"{i + 1}-{i + 2}"

            # Différence absolue
            diff_abs = s_i - s_i_plus_1
            abs_diffs[label].append(diff_abs)

            # Différence relative
            if s_i > 0 :
                diff_rel = diff_abs / s_i
            else :
                diff_rel = 0.0
            rel_diffs[label].append(diff_rel)

    # Conversion en DataFrames Pandas
    df_abs = pd.DataFrame(abs_diffs)
    df_rel = pd.DataFrame(rel_diffs)

    # Création de la figure avec 2 graphiques
    sns.set_theme(style = "whitegrid")
    fig, axes = plt.subplots(2, 1, figsize = (16, 12))

    # Graphique 1 : Différences Absolues
    sns.boxplot(data = df_abs, ax = axes[0], color = "skyblue", showfliers = False)
    axes[0].set_title("Distribution des différences ABSOLUES entre scores de rang i et i+1", fontsize = 14,
                      fontweight = 'bold')
    axes[0].set_ylabel("Différence (Points de %)", fontsize = 12)
    axes[0].set_xlabel("Paires de rangs", fontsize = 12)
    axes[0].tick_params(axis = 'x', rotation = 45)

    # Graphique 2 : Différences Relatives
    sns.boxplot(data = df_rel, ax = axes[1], color = "lightgreen", showfliers = False)
    axes[1].set_title("Distribution des différences RELATIVES ((Score i - Score i+1) / Score i)", fontsize = 14,
                      fontweight = 'bold')
    axes[1].set_ylabel("Différence proportionnelle", fontsize = 12)
    axes[1].set_xlabel("Paires de rangs", fontsize = 12)
    axes[1].tick_params(axis = 'x', rotation = 45)

    plt.tight_layout()
    plt.savefig('boxplots_ecarts_abs_rel.png', dpi = 300)
    plt.show()

if __name__ == "__main__" :
    tracer_boxplots_ecarts()