"""
HAL (format tableau) -> JSON normalisé :
- title
- year
- authors
- keywords (vide pour l’instant)
- theme (None pour l’instant)
- link
- hal_id
- doc_type

Exécution :
    python src/main.py

Sortie :
    publications.json
"""

import json
import re
import time
import random
from typing import Optional, List, Dict

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


SEARCH_URL = "https://hal.science/search/index?q=Base%20de%20donn%C3%A9e"


def extract_year(text: str) -> Optional[int]:
    """Extrait une année (4 chiffres) depuis une chaîne."""
    if not text:
        return None
    m = re.search(r"\b(19|20)\d{2}\b", text)
    return int(m.group(0)) if m else None


def safe_text(parent, css: str) -> Optional[str]:
    try:
        el = parent.find_element(By.CSS_SELECTOR, css)
        txt = el.text.strip()
        return txt if txt else None
    except Exception:
        return None


def safe_attr(parent, css: str, attr: str) -> Optional[str]:
    try:
        el = parent.find_element(By.CSS_SELECTOR, css)
        val = el.get_attribute(attr)
        return val.strip() if val else None
    except Exception:
        return None


def build_driver(headless: bool = True) -> webdriver.Chrome:
    options = Options()
    if headless:
        options.add_argument("--headless=new")

    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # anti-détection léger
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/121.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(options=options)
    return driver


def scrape_hal_table_format(url: str) -> List[Dict]:
    driver = build_driver(headless=True)
    publications: List[Dict] = []

    try:
        driver.get(url)

        # masquer webdriver après get
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        time.sleep(2 + random.random() * 2)
        driver.refresh()
        time.sleep(2 + random.random() * 2)

        # Chaque résultat est dans un TD : <td class="pl-4 pl-sm-0"> ... </td>
        tds = driver.find_elements(By.CSS_SELECTOR, "td.pl-4.pl-sm-0")

        for td in tds:
            title = safe_text(td, "h3.title-results")

            # lien (a parent autour du titre)
            link = None
            try:
                a = td.find_element(By.CSS_SELECTOR, "a[href]")
                link = a.get_attribute("href")
            except Exception:
                link = None

            # auteurs: tous les <a> dans span.authors-results
            authors: List[str] = []
            try:
                author_links = td.find_elements(By.CSS_SELECTOR, "span.authors-results a")
                authors = [a.text.strip() for a in author_links if a.text.strip()]
            except Exception:
                authors = []

            # citation (contient l'année)
            citation = safe_text(td, "div.citation-results")
            year = extract_year(citation or "")

            # type doc
            doc_type = None
            try:
                # span typdoc a des classes variables : label_COMM, label_THESE, etc.
                doc_type = td.find_element(By.CSS_SELECTOR, "span.typdoc").text.strip()
            except Exception:
                doc_type = None

            # halId (ex: cirad-00187196v1)
            hal_id = safe_text(td, "span.halId-results strong")

            if title and link:
                publications.append(
                    {
                        "title": title,
                        "year": year,
                        "authors": authors,
                        "keywords": [],   # à remplir plus tard sur la page détail
                        "theme": None,    # à calculer plus tard
                        "link": link if link.startswith("http") else "https://hal.science" + link,
                        "hal_id": hal_id,
                        "doc_type": doc_type,
                    }
                )

        return publications

    finally:
        driver.quit()


def save_json(data: List[Dict], filepath: str) -> None:
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    pubs = scrape_hal_table_format(SEARCH_URL)
    print(f"Publications récupérées : {len(pubs)}")

    out_file = "publications.json"
    save_json(pubs, out_file)
    print(f"JSON généré : {out_file}")

    if pubs:
        print("\nAperçu (1er élément) :")
        print(json.dumps(pubs[0], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
