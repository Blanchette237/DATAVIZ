from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep, time

driver = webdriver.Chrome()
driver.get("https://scanr.enseignementsup-recherche.gouv.fr/search/publications?q=base%20de%20donn%C3%A9e")
sleep(5)
try:
    time.sleep(5)
    cookie_button = driver.find_element(By.ID, "onetrust-accept-btn-handler")
    cookie_button.click()
    print("Cookies accepted")
except:
    print("No cookie button found or already accepted")

results = driver.find_elements(By.CSS_SELECTOR, "div.result-item")

print(f"{len(results)} résultats trouvés\n")

for r in results:
    # Titre + lien
    title_el = r.find_element(By.CSS_SELECTOR, "a.fr-link")
    title = title_el.text
    link = title_el.get_attribute("href")

    # Auteurs
    try:
        authors = r.find_element(
            By.CSS_SELECTOR, "p.fr-text-heavy"
        ).text
    except:
        authors = None

    # Année (depuis <i>)
    try:
        details = r.find_element(By.CSS_SELECTOR, "p.fr-card__detail i").text
        year = None
        for token in details.split(","):
            token = token.strip()
            if token.isdigit() and len(token) == 4:
                year = token
    except:
        year = None

    print(title, year)

driver.quit()
