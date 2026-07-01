"""
Initialisation et création du référentiel bilingue.
Ce script configure l'architecture de la base de données et
injecte les 28 thèmes officiels (FR/EN) nécessaires à la classification IA.
"""

from sqlalchemy import create_engine, text

# Configuration
DB_USER = 'admin'
DB_PASSWORD = 'admin'
DB_HOST = 'localhost'
DB_NAME = 'conference'

connection_string = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
engine = create_engine(connection_string)

# Dictionnaire traduisant les thèmes officiels français en anglais
THEMES_TRADUCTION = {
    "Big Data et nouveaux paradigmes de traitement des données": "Big Data and new data processing paradigms",
    "Big Data : cas d’usage avec problématique de gestion": "Big Data: use cases with management issues",
    "Crowd sourcing, crowd mining, sciences participatives, jeux sérieux": "Crowdsourcing, crowd mining, citizen science, serious games",
    "Données ouvertes, Linked Data, RDF": "Open data, Linked Data, RDF",
    "Evaluation de performance et bancs d’essai": "Performance evaluation and benchmarks",
    "Evaluation et optimisation de requêtes": "Query evaluation and optimization",
    "Flux de données et réseaux de capteurs": "Data streams and sensor networks",
    "Fouille de données et découverte de connaissances": "Data mining and knowledge discovery",
    "Gestion de données et services Web": "Data management and Web services",
    "Gestion de données multimédia": "Multimedia data management",
    "Gestion de données parallèles et distribuées": "Parallel and distributed data management",
    "Gestion de données personnelles": "Personal data management",
    "Gestion de données scientifiques": "Scientific data management",
    "Gestion de données semi-structurées": "Semi-structured data management",
    "Gestion de données temporelles": "Temporal data management",
    "Gestion de données dans le cloud": "Cloud data management",
    "Gestion des données incertaines et probabilistes": "Uncertain and probabilistic data management",
    "Gestion des transactions et de la concurrence": "Transaction management and concurrency",
    "Modèles d’indexation et de stockage": "Indexing and storage models",
    "Modèles, langages, et sémantique des données": "Data models, languages, and semantics",
    "Monitoring et réglage des performances": "Performance monitoring and tuning",
    "Nettoyage, intégration, et provenance des données": "Data cleaning, integration, and data provenance",
    "Qualité/valeur des données": "Data quality and value",
    "Recherche d’information et fouille de texte": "Information retrieval and text mining",
    "Réseaux sociaux et graphes de données": "Social networks and data graphs",
    "Systèmes de gestion de données embarqués": "Embedded data management systems",
    "Sécurité et protection des données privées": "Security and privacy protection",
    "Visualisation de données": "Data visualization"
}

def init_db() :
    """
    Crée l'architecture complète de la base de données (si elle n'existe pas),
    purge l'historique, et peuple le référentiel bilingue.
    """
    with engine.begin() as conn :
        print("Étape 1 : Création de l'architecture des tables...")

        # Création de la table principale des thèmes (Français)
        conn.execute(text("""
                          CREATE TABLE IF NOT EXISTS theme
                          (
                              id      INT AUTO_INCREMENT PRIMARY KEY,
                              libelle VARCHAR(255) NOT NULL UNIQUE
                          )
                          """))

        # Création de la table des traductions (Anglais)
        conn.execute(text("""
                          CREATE TABLE IF NOT EXISTS theme_en
                          (
                              id_theme   INT PRIMARY KEY,
                              libelle_en VARCHAR(255) NOT NULL,
                              FOREIGN KEY (id_theme) REFERENCES theme (id) ON DELETE CASCADE
                          )
                          """))

        # Création de la table de liaison entre les publications et les thèmes
        conn.execute(text("""
                          CREATE TABLE IF NOT EXISTS est_classe
                          (
                              id_publication INT,
                              id_theme       INT,
                              score_ia       FLOAT,
                              PRIMARY KEY (id_publication, id_theme),
                              FOREIGN KEY (id_publication) REFERENCES publication (id) ON DELETE CASCADE,
                              FOREIGN KEY (id_theme) REFERENCES theme (id) ON DELETE CASCADE
                          )
                          """))

        print("Étape 2 : Nettoyage des données existantes...")
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        conn.execute(text("TRUNCATE TABLE est_classe"))
        conn.execute(text("TRUNCATE TABLE theme_en"))
        conn.execute(text("TRUNCATE TABLE theme"))
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))

        print(f"Étape 3 : Insertion du référentiel ({len(THEMES_TRADUCTION)} thèmes)...")

        for theme_fr, theme_en in THEMES_TRADUCTION.items() :
            # Insertion du thème français
            result = conn.execute(
                text("INSERT INTO theme (libelle) VALUES (:lbl)"),
                {"lbl": theme_fr}
            )

            # Récupération de l'ID auto-incrémenté
            id_genere = result.lastrowid

            # Insertion de la traduction anglaise associée au même ID
            conn.execute(
                text("INSERT INTO theme_en (id_theme, libelle_en) VALUES (:id, :lbl_en)"),
                {"id": id_genere, "lbl_en": theme_en}
            )

        print("\nBase de données initialisée avec succès !")

if __name__ == "__main__":
    init_db()