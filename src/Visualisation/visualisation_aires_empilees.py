"""
Graphique en Aires Empilées (Stacked Area Chart).
Ce script montre l'évolution du volume total de publications, segmenté par
les thèmes majeurs. Les thèmes mineurs sont regroupés dans 'Autres'.
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

def generer_aires_empilees(top_n = 6) :
    """
    Extrait les données, regroupe la "longue traîne" et dessine les aires empilées.
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
        df = pd.read_sql(requete, conn)

    if df.empty :
        print("Aucune donnée trouvée.")
        return

    print("Traitement et regroupement des données...")
    df['annee_edition'] = df['annee_edition'].astype(str).str.strip()

    # Identifier les N thèmes les plus fréquents
    top_themes = df['libelle'].value_counts().nlargest(top_n).index.tolist()

    # Création de la catégorie "Autres"
    df['theme_regroupe'] = df['libelle'].apply(lambda x : x if x in top_themes else 'Autres thèmes')

    # Comptage par année et par thème regroupé
    df_comptage = df.groupby(['annee_edition', 'theme_regroupe']).size().reset_index(name = 'nombre')

    # Création du tableau croisé
    # Lignes = Années, Colonnes = Thèmes, Valeurs = Nombre de publications
    df_pivot = df_comptage.pivot(index = 'annee_edition', columns = 'theme_regroupe', values = 'nombre').fillna(0)

    # Réorganisation des colonnes
    colonnes_themes = [col for col in df_pivot.columns if col != 'Autres thèmes']
    if 'Autres thèmes' in df_pivot.columns :
        colonnes_themes.append('Autres thèmes')
    df_pivot = df_pivot[colonnes_themes]

    # Configuration graphique
    print("Génération du Graphique en Aires Empilées...")

    fig, ax = plt.subplots(figsize = (14, 8))
    fig.suptitle("Volume et Répartition Thématique des Publications BDA", fontsize = 20, fontweight = 'bold')

    # Dessin du graphique
    df_pivot.plot.area(ax = ax, stacked = True, alpha = 0.85, cmap = 'Set2')

    ax.set_ylabel("Volume total de publications", fontsize = 14, fontweight = 'bold')
    ax.set_xlabel("Année d'édition", fontsize = 14, fontweight = 'bold')

    plt.xticks(rotation = 0)

    ax.legend(title = "Thématiques", title_fontsize = '13', fontsize = '11',
              bbox_to_anchor = (1.02, 1), loc = 'upper left')

    # Affichage du quadrillage horizontal en arrière-plan
    ax.grid(axis = 'y', linestyle = '--', alpha = 0.4)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__" :
    generer_aires_empilees(top_n = 6)