from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/121.0.0.0 Safari/537.36"
)

driver = webdriver.Chrome(options=options)
driver.get("https://hal.science/search/index?q=Base%20de%20donn%C3%A9e")
driver.execute_script(
    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
)

driver.refresh()
# driver.execute_script("location.reload();")

titles = driver.find_elements(By.CSS_SELECTOR, "h3.title-results")

print(f"{len(titles)} titres trouvés\n")

for t in titles[:5]:
    print(t.text)

driver.quit()
