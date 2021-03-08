from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

options = Options()
options.headless=True
options.add_argument('start-maximized')
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
chrome_prefs = {}
options.experimental_options["prefs"] = chrome_prefs
chrome_prefs["profile.default_content_settings"] = {"images": 2}

def get_team_names(mozzart_code):
    driver =webdriver.Chrome(options=options)
    URL = f"https://www.mozzartbet.ro/ro#/date/all?cid={mozzart_code}&s=1"
    driver.get(URL)
    try:
        element = WebDriverWait(driver,10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "odd-font"))
        )

    except Exception as e:
        print(e)

    source = driver.page_source
    # with open("page.html", 'w') as f:
    #     f.write(source)
    soup = BeautifulSoup(source, 'lxml')
    matches = soup.select('div.competition div.match')
    team_names = []
    for match in matches:
        try:
            teams = match.select("a.pairs span")
            home_team = teams[1].text.strip()
            away_team = teams[2].text.strip()
            if home_team not in team_names:
                team_names.append(home_team)
            if away_team not in team_names:
                team_names.append(away_team)
        except Exception as e:
            print(e)
    driver.close()
    return team_names



if __name__=="__main__":
    team_names = get_team_names("20")
    print(team_names)
    print(len(team_names))