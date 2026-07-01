# Analyse Sémantique & Visualisation des Conférences BDA

## Description du Projet

La conférence **BDA (Bases de Données Avancées)** est un événement majeur regroupant la communauté francophone de la recherche en gestion de données. Au fil des années, des milliers d'articles y ont été publiés.

**Pourquoi ce projet ?** L'objectif est de transformer ces archives textuelles brutes en connaissances exploitables. Ce projet permet de :

- Découvrir comment les grandes thématiques (Big Data, Cloud, Sécurité, etc.) ont évolué au fil du temps.
- Identifier l'émergence ou le déclin de certains sujets de recherche.
- Cartographier les relations entre les chercheurs (qui travaille avec qui et sur quels sujets).
- Démontrer l'efficacité des modèles d'IA "Zero-Shot" pour classifier des textes académiques sans avoir besoin d'un jeu d'entraînement étiqueté manuellement.

Il couvre la chaîne de valeur de la donnée (**Data Engineering, NLP/IA, Data Visualization**) pour aboutir à un tableau de bord analytique complet.

---

## Aperçu des Résultats

Voici un aperçu des visualisations générées par notre pipeline de Data Science :

![Heatmap des thématiques BDA par année](images/heatmap.png)
*La **Heatmap** met en évidence les "points chauds" et les tendances historiques de la conférence.*

![Stacked Area Chart des publications BDA](images/aires_empilees.png)
*Le **Stacked Area Chart** illustre la part de chaque grand thème dans le volume total des publications.*

---

## Structure du Projet

```
projet-bda-dataviz/
│
├── init_database.py                # Initialisation de MariaDB et du référentiel thématique
├── pipeline_export_ia.py           # Moteur d'inférence IA (XLM-Roberta)
├── filtrage_zscore_insertion.py    # Algorithme de validation statistique (Z-Score)
│
├── visualisation_themes_reels.py   # Génération des Nuages de mots
├── visualisation_bump_chart.py     # Génération de la Course de Classement
├── visualisation_heatmap.py        # Génération de la Carte de Chaleur
├── visualisation_aires_empilees.py # Génération des Aires Empilées
├── visualisation_reseau_auteurs.py # Génération du Graphe HTML interactif
│
├── analyse_union_top3.py           # Analyse avancée croisée DB/JSON
├── labo_comparaison_modeles.py     # Banc d'essai analytique (Top-P, Z-Score, Coude)
│
└── README.md                       # Documentation du projet
```

---

## Prérequis et Installation

### 1. Environnement

- Python 3.9 ou supérieur
- MariaDB (ou MySQL) installé et tournant en local

### 2. Base de données

Créez une base de données nommée `conference` dans votre SGBD :

```sql
CREATE DATABASE conference CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

> **Note :** Assurez-vous d'avoir au préalable importé vos tables d'origine, notamment la table `publication` contenant les titres et les années d'édition.

### 3. Dépendances Python

Installez l'ensemble des bibliothèques requises en exécutant la commande suivante :

```bash
pip install sqlalchemy pymysql transformers torch requests pandas matplotlib seaborn wordcloud networkx pyvis numpy
```

---

## Architecture du Projet et Ordre d'Exécution

Le pipeline est conçu pour être exécuté **séquentiellement**. Les scripts sont organisés par phases pour garantir l'intégrité du flux de données.

### Phase 1 — Base de Données & Vérité Terrain

- **`init_database.py`** : Script d'initialisation (idempotent). Il crée l'architecture relationnelle (tables `theme`, `theme_en`, `est_classe`), purge l'historique et injecte le référentiel officiel des 28 thèmes BDA avec leur traduction anglaise optimisée pour l'IA.

### Phase 2 — Pipeline IA (NLP)

- **`pipeline_export_ia.py`** : Le moteur d'analyse. Il extrait les publications de la base, récupère dynamiquement les résumés pertinents (ex : via l'API ouverte de HAL), et soumet les textes au modèle IA **XLM-Roberta-Large**.
  - **Sortie :** Génère le fichier brut `resultats_ia_en.json` contenant les 28 scores de probabilité pour chaque article.

### Phase 3 — Filtrage Statistique & Insertion

- **`filtrage_zscore_insertion.py`** : L'algorithme de validation. Il lit le JSON brut, applique un filtre mathématique **(Z-Score > 2.0)** pour éliminer le "bruit" et ne conserver que les thèmes où l'IA présente une forte anomalie positive de certitude. Il insère ensuite ces résultats validés dans la table de liaison `est_classe`.

### Phase 4 — Data Visualization (Tableau de bord)

Une fois l'étape de filtrage terminée, la base de données est prête. Vous pouvez lancer les scripts de manière **indépendante** pour générer les graphiques (`visualisation_heatmap.py`, `visualisation_reseau_auteurs.py`, etc.).

---

## Utilisation

Pour lancer le pipeline complet depuis votre terminal :

```bash
# 1. Préparation de la base
python init_database.py

# 2. Inférence IA (peut prendre plusieurs minutes selon la taille de la BDD et le CPU/GPU)
python pipeline_export_ia.py

# 3. Filtrage et mise à jour MariaDB
python filtrage_zscore_insertion.py

# 4. Génération d'une visualisation (exemple)
python visualisation_heatmap.py
```


### Pour avoir la carte des editions bda

1. Lancer l’API :
   python -m uvicorn api:app --reload

2. Ouvrir WordPress :
   http://wordpress.test

3. Accéder à la page :
   Éditions BDA


---

## Dépannage (Troubleshooting)

Si vous rencontrez des problèmes lors de l'exécution, voici les solutions aux cas les plus fréquents :

- API FastAPI exposant les données des éditions BDA
- Base de données MySQL
- Visualisation via WordPress (HTML + JS)

### Le modèle XLM-Roberta ne se télécharge pas ou plante au lancement (`pipeline_export_ia.py`)

- **Cause :** Le modèle pèse plusieurs gigaoctets. Une interruption réseau ou un manque d'espace disque (dans le cache `~/.cache/huggingface`) peut corrompre le fichier.
- **Solution :** Vérifiez votre espace disque. Purgez le dossier cache HuggingFace et relancez le script avec une connexion internet stable.

### Les graphiques (Nuages, Heatmap) s'affichent vides

- **Cause :** Le filtrage Z-Score a été trop restrictif ou les données de l'année sont manquantes.
- **Solution :** Vérifiez que votre table `publication` contient bien des données valides dans la colonne `annee_edition`. Vous pouvez également ajuster le paramètre `z_seuil` ou `seuil_publications` dans les scripts de visualisation.

---

## Intégration Web (WordPress)

- Les graphiques générés par Matplotlib/Seaborn peuvent être sauvegardés au format vectoriel `.svg` en remplaçant `plt.show()` par `plt.savefig("nom.svg")` pour une intégration native et légère dans WordPress.
- Le graphe interactif généré par le script de réseau d'auteurs produit une page `graphe_interactif_auteurs.html` intégrable dans n'importe quel CMS via une balise `<iframe>`.

---

## Licence et Crédits

Ce projet a été développé dans le cadre d'un travail académique d'analyse et de visualisation de données.

- **Données brutes :** Issues des archives de la conférence BDA.
- **Modèle IA :** XLM-RoBERTa par Facebook AI via [HuggingFace](https://huggingface.co/).
