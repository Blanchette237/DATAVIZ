"""
Visualisation - Nuages de mots.
Ce script extrait les thèmes classés en base de données, les groupe par année
d'édition et génère une visualisation comparative des tendances.
"""

import matplotlib.pyplot as plt
from wordcloud import WordCloud
from sqlalchemy import create_engine, text
from collections import Counter

# Configuration
DB_USER = 'admin'
DB_PASSWORD = 'admin'
DB_HOST = 'localhost'
DB_NAME = 'conference'

engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")

def generer_visualisation_reelle() :
    """
    Récupère les thèmes depuis la DB et affiche les nuages de mots par année.
    """
    print("Connexion à la base de données MariaDB...")

    themes_par_annee = {}

    with engine.connect() as conn :
        requete = text("""
            SELECT p.annee_edition, t.libelle
            FROM publication p
            JOIN est_classe ec ON p.id = ec.id_publication
            JOIN theme t ON ec.id_theme = t.id
            WHERE p.annee_edition IS NOT NULL
        """)

        resultats = conn.execute(requete).fetchall()

        if not resultats :
            print("Aucune donnée trouvée dans la table 'est_classe'.")
            return

        # Agrégation des thèmes par année d'édition
        for annee_edition, libelle_theme in resultats :
            annee = str(annee_edition).strip()

            if annee not in themes_par_annee :
                themes_par_annee[annee] = []
            themes_par_annee[annee].append(libelle_theme)

    # Tri chronologique des années
    annees_triees = sorted(themes_par_annee.keys())
    nb_annees = len(annees_triees)

    if nb_annees == 0 :
        print("Aucune année valide n'a été trouvée pour générer les graphiques.")
        return

    # configuration graphique
    cols = 2
    rows = (nb_annees + 1) // cols
    rows = max(1, rows)

    fig, axes = plt.subplots(rows, cols, figsize = (16, 5 * rows))
    fig.suptitle("Évolution des Thématiques de Recherche",
                 fontsize = 22, fontweight = 'bold', y = 0.98)

    # Transformation des axes en liste plate
    axes_list = axes.flatten() if nb_annees > 1 else [axes]

    print(f"Génération des nuages pour {nb_annees} année(s) distincte(s)...")

    for i, annee in enumerate(annees_triees) :
        liste_themes = themes_par_annee[annee]
        frequences = Counter(liste_themes)

        # Création du nuage de mots
        wordcloud = WordCloud(
            width = 800,
            height = 400,
            background_color = 'white',
            colormap = 'plasma',
            prefer_horizontal = 0.7
        ).generate_from_frequencies(frequences)

        ax = axes_list[i]
        ax.imshow(wordcloud, interpolation = 'bilinear')
        ax.set_title(f"BDA {annee}", fontsize = 18, pad = 10, color = 'black')
        ax.axis('off')

    # Nettoyage des graphiques vides
    for j in range(i + 1, len(axes_list)) :
        axes_list[j].axis('off')

    plt.tight_layout(pad = 4.0)
    print("Visualisation terminée !")
    plt.show()

if __name__ == "__main__" :
    generer_visualisation_reelle()