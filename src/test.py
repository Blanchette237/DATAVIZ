import time
import requests
from sqlalchemy import create_engine, text
from transformers import pipeline

THEMES_OFFICIELS = [
    "Big Data et nouveaux paradigmes de traitement des données",
    "Big Data : cas d’usage avec problématique de gestion",
    "Crowd sourcing, crowd mining, sciences participatives, jeux sérieux",
    "Données ouvertes, Linked Data, RDF",
    "Evaluation de performance et bancs d’essai",
    "Evaluation et optimisation de requêtes",
    "Flux de données et réseaux de capteurs",
    "Fouille de données et découverte de connaissances",
    "Gestion de données et services Web",
    "Gestion de données multimédia",
    "Gestion de données parallèles et distribuées",
    "Gestion de données personnelles",
    "Gestion de données scientifiques",
    "Gestion de données semi-structurées",
    "Gestion de données temporelles",
    "Gestion de données dans le cloud",
    "Gestion des données incertaines et probabilistes",
    "Gestion des transactions et de la concurrence",
    "Modèles d’indexation et de stockage",
    "Modèles, langages, et sémantique des données",
    "Monitoring et réglage des performances",
    "Nettoyage, intégration, et provenance des données",
    "Qualité/valeur des données",
    "Recherche d’information et fouille de texte",
    "Réseaux sociaux et graphes de données",
    "Systèmes de gestion de données embarqués",
    "Sécurité et protection des données privées",
    "Visualisation de données"
]

classificateur = pipeline("zero-shot-classification", model="joeddav/xlm-roberta-large-xnli")

res_ia = classificateur(
    "BeLink: Querying Networks of Facts, Statements and Beliefs",
    THEMES_OFFICIELS,
    hypothesis_template="Le thème de ce texte est {}.",
    multi_label=True
)

theme_1 = res_ia['labels']
score_1 = res_ia['scores']

print(f"Titre : {theme_1} \n ({score_1}%)")

res_ia = classificateur(
    "Belief databases data journalism information extraction reasoning about belief and knowledge semantic web fact-checking",
    THEMES_OFFICIELS,
    hypothesis_template="Le thème de ce texte est {}.",
    multi_label=True
)

theme_1 = res_ia['labels']
score_1 = res_ia['scores']

print(f"Mots clés : {theme_1} \n ({score_1}%)")