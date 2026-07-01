"""
scanR -> JSON (max infos depuis la page de résultats)

Champs :
- title
- year
- authors (liste)
- details (texte du <i>)
- keywords (vide pour l’instant)
- theme (None)
- link
- source = "scanR"

Exécution :
    python src/scanrtojson.py

Sortie :
    publications_scanr.json
"""

import json
import re
import time
from typing import Optional, List, Dict

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


URL = "https://scanr.enseignementsup-recherche.gouv.fr/search/publications?q=base%20de%20donn%C3%A9e"


def build_driver(headless: bool = True) -> webdriver.Chrome:
    options = Options()
    if headless:
        options.add_argument("--headless=new")

    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/121.0.0.0 Safari/537.36"
    )

    return webdriver.Chrome(options=options)


def accept_cookies_if_present(driver: webdriver.Chrome) -> None:
    try:
        time.sleep(2)
        btn = driver.find_element(By.ID, "onetrust-accept-btn-handler")
        btn.click()
        time.sleep(1)
    except Exception:
        pass


def extract_year(text: str) -> Optional[int]:
    if not text:
        return None
    m = re.search(r"\b(19|20)\d{2}\b", text)
    return int(m.group(0)) if m else None


def safe_text(parent, css: str) -> Optional[str]:
    try:
        el = parent.find_element(By.CSS_SELECTOR, css)
        t = el.text.strip()
        return t if t else None
    except Exception:
        return None


def safe_attr(parent, css: str, attr: str) -> Optional[str]:
    try:
        el = parent.find_element(By.CSS_SELECTOR, css)
        v = el.get_attribute(attr)
        return v.strip() if v else None
    except Exception:
        return None


def extract_authors(result_item) -> List[str]:
    """
    Sur scanR, les auteurs sont dans:
    <p class="fr-mb-0 fr-text--heavy fr-text-sm"> ... </p>

    Le texte peut contenir des guillemets/retours ligne/et.
    On nettoie et on renvoie une liste.
    """
    authors_raw = None

    # Fallbacks (car la classe peut varier)
    for css in [
        "p.fr-text--heavy",     # vu dans ton inspect
        "p.fr-text-heavy",      # autre variante
        "p.fr-text--heavy.fr-text-sm",
        "p.fr-text-heavy.fr-text-sm",
    ]:
        authors_raw = safe_text(result_item, css)
        if authors_raw:
            break

    if not authors_raw:
        return []

    # Nettoyage : enlever guillemets, lignes vides, mots de liaison
    txt = authors_raw.replace('"', "").strip()
    lines = [l.strip() for l in txt.split("\n") if l.strip()]

    cleaned: List[str] = []
    for l in lines:
        # ignorer séparateurs fréquents
        if l.lower() in {"et", ",", ";"}:
            continue
        # parfois une ligne est juste une virgule
        if l in {",", ";"}:
            continue
        print ("AUTHOR LINE:", l)
        cleaned.append(l)

    # Si tout est sur une seule ligne avec virgules
    if len(cleaned) == 1 and "et" in cleaned[0]:
        cleaned = [x.strip() for x in cleaned[0].split("et") if x.strip()]

    # dédoublonner en conservant l'ordre
    uniq = []
    seen = set()
    for a in cleaned:
        if a not in seen:
            uniq.append(a)
            seen.add(a)

    return uniq

def format_authors(authors: list[str]) -> str:
    """
    Formate une liste d'auteurs en français :
    - 1 auteur  -> "A"
    - 2 auteurs -> "A et B"
    - 3+        -> "A, B et C"
    """
    if not authors:
        return ""

    if len(authors) == 1:
        return authors[0]

    if len(authors) == 2:
        return f"{authors[0]} et {authors[1]}"

    return ", ".join(authors[:-1]) + " et " + authors[-1]


def scrape_scanr(url: str) -> List[Dict]:
    driver = build_driver(headless=True)
    pubs: List[Dict] = []

    try:
        driver.get(url)
        time.sleep(5)  # laisser React charger

        accept_cookies_if_present(driver)

        # ✅ Résultats
        items = driver.find_elements(By.CSS_SELECTOR, "div.result-item")

        for item in items:
            title = safe_text(item, "a.fr-link")
            href = safe_attr(item, "a.fr-link", "href")

            if not title or not href:
                continue

            link = href if href.startswith("http") else "https://scanr.enseignementsup-recherche.gouv.fr" + href

            # détails + année
            details = safe_text(item, "p.fr-card__detail i")  # vu dans ton inspect
            year = extract_year(details or "")

            # auteurs
            authors = extract_authors(item)
            authors_display = format_authors(authors)

            pubs.append(
                {
                    "title": title,
                    "year": year,
                    "authors": authors,
                    "authors_display": authors_display,
                    "details": details,    # utile (source, conf/journal, etc.)
                    "keywords": [],        # pas dispo ici (à enrichir sur page détail si besoin)
                    "theme": None,         # calcul plus tard
                    "link": link,
                    "source": "scanR",
                }
            )

        # dédoublonnage par lien
        uniq = {}
        for p in pubs:
            uniq[p["link"]] = p

        return list(uniq.values())

    finally:
        driver.quit()


def save_json(data: List[Dict], filepath: str) -> None:
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    pubs = scrape_scanr(URL)
    print(f"{len(pubs)} résultats trouvés")

    out = "publications_scanr.json"
    save_json(pubs, out)
    print(f"JSON généré : {out}")

    if pubs:
        print("\nAperçu (1er élément) :")
        print(json.dumps(pubs[0], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
