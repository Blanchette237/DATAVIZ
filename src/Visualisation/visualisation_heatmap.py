"""
Carte de Chaleur (Heatmap).
Ce script croise les années et les thèmes pour révéler les "points chauds"
(concentrations de publications) de la conférence BDA.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine, text

# Configuration
DB_USER = 'admin'
DB_PASSWORD = 'admin'
DB_HOST = 'localhost'
DB_NAME = 'conference'

engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")

def generer_heatmap() :
    """
    Extrait les données, crée une matrice de fréquence et dessine la Heatmap.
    """
    print("Connexion à la base de données MariaDB...")

    with engine.connect() as conn :
        # Récupération des données
        requete = text("""
                       SELECT p.annee_edition, t.libelle
                       FROM publication p
                                JOIN est_classe ec ON p.id = ec.id_publication
                                JOIN theme t ON ec.id_theme = t.id
                       WHERE p.annee_edition IS NOT NULL
                       """)
        df = pd.read_sql(requete, conn)

    if df.empty :
        print("Aucune donnée trouvée.")
        return

    print("Transformation en Matrice (Tableau croisé dynamique)...")

    # Nettoyage des années pour éviter les doublons
    df['annee_edition'] = df['annee_edition'].astype(str).str.strip()

    # Création de la matrice : X = annee_edition, Y = libelle (Thème)
    matrice_themes = pd.crosstab(index = df['libelle'], columns = df['annee_edition'])

    # Tri de la matrice
    matrice_themes['Total'] = matrice_themes.sum(axis = 1)
    matrice_themes = matrice_themes.sort_values(by = 'Total', ascending = False)
    # On retire la colonne 'Total' pour ne pas la dessiner sur le graphique
    matrice_themes = matrice_themes.drop(columns = ['Total'])

    # Configuration graphique
    print("Génération de la Carte de Chaleur...")

    # On ajuste la hauteur du graphique en fonction du nombre de thèmes
    hauteur_fig = max(8, len(matrice_themes) * 0.4)
    plt.figure(figsize = (12, hauteur_fig))

    # Titre du graphique
    plt.title("Densité des Thématiques de Recherche BDA par Année",
              fontsize = 18, fontweight = 'bold', pad = 20)

    # Génération de la Heatmap
    sns.heatmap(
        matrice_themes,
        annot = True, # Ecrit le chiffre exact à l'intérieur de chaque case
        fmt = "d",  # Format "d" pour des nombres entiers
        cmap = "YlOrRd", # Palette de couleurs
        linewidths = 0.5,
        cbar_kws = {'label' : 'Nombre de publications'}  # Légende de la barre de couleur
    )

    # Visuel des axes
    plt.ylabel("Thèmes Officiels", fontsize = 12, fontweight = 'bold')
    plt.xlabel("Année d'édition", fontsize = 12, fontweight = 'bold')

    # Rotation des labels de l'axe X
    plt.xticks(rotation = 0)

    # Ajustement automatique des marges
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    generer_heatmap()