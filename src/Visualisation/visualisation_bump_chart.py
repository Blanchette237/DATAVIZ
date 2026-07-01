"""
Bump Chart (Évolution des classements).
Ce script calcule le rang de chaque thème par année d'édition et trace
un graphique de type "course" pour les thèmes les plus populaires.
"""

import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine, text

# Configuration
DB_USER = 'admin'
DB_PASSWORD = 'admin'
DB_HOST = 'localhost'
DB_NAME = 'conference'

engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")

def generer_bump_chart(top_n = 5) :
    """
    Génère un graphique de classement pour les thèmes ayant atteint le Top N.
    """
    print("Connexion à la base de données MariaDB...")

    with engine.connect() as conn :
        requete = text("""
                       SELECT p.annee_edition, t.libelle
                       FROM publication p
                                JOIN est_classe ec ON p.id = ec.id_publication
                                JOIN theme t ON ec.id_theme = t.id
                       WHERE p.annee_edition IS NOT NULL
                       """)
        # on met le résultat dans un dataframe
        df = pd.read_sql(requete, conn)

    if df.empty :
        print("Aucune donnée trouvée.")
        return

    print("Calcul des classements par année...")
    # Nettoyage de l'année
    df['annee_edition'] = df['annee_edition'].astype(str).str.strip()

    # Calcul du nombre de publications par thème et par année
    df_comptage = df.groupby(['annee_edition', 'libelle']).size().reset_index(name = 'nombre')

    # Calcul du RANG
    df_comptage['rang'] = df_comptage.groupby('annee_edition')['nombre'].rank(method = 'min', ascending = False)

    # Filtrage de lisibilité
    # On identifie les thèmes qui ont été au moins une fois dans le Top N
    themes_leaders = df_comptage[df_comptage['rang'] <= top_n]['libelle'].unique()

    # On ne garde que les données des thèmes "leaders" pour le graphique
    df_filtre = df_comptage[df_comptage['libelle'].isin(themes_leaders)]

    # Configuration graphique
    print("Génération du Bump Chart...")
    fig, ax = plt.subplots(figsize = (14, 8))
    fig.suptitle(f"Course des Thèmes BDA : Évolution du Classement (Top {top_n})", fontsize = 20, fontweight = 'bold')

    # On trace une ligne pour chaque thème "leader"
    for theme in themes_leaders :
        # On isole les données de ce thème et on les trie
        df_theme = df_filtre[df_filtre['libelle'] == theme].sort_values('annee_edition')

        # Le tracé : X = Année, Y = Rang
        ax.plot(df_theme['annee_edition'], df_theme['rang'],
                marker = 'o', markersize = 12, linewidth = 4, label = theme)

    # Pour que le Rang 1 soit en haut du graphique
    ax.invert_yaxis()

    # Formatage esthétique
    ax.set_yticks(range(1, top_n + 2))  # Affiche les numéros de rang
    ax.set_ylabel('Classement', fontsize = 14, fontweight = 'bold')
    ax.set_xlabel("Année d'édition", fontsize = 14, fontweight = 'bold')

    # Ajout d'une grille horizontale pour lire les rangs
    ax.grid(axis = 'y', linestyle = '--', alpha = 0.5)

    # Positionnement de la légende à l'extérieur
    ax.legend(bbox_to_anchor = (1.02, 1), loc = 'upper left', fontsize = 11, title = "Thèmes", title_fontsize = 12)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__" :
    generer_bump_chart(top_n = 7)