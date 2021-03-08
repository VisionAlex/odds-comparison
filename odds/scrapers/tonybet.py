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

def get_team_names(tonybet_code):
    driver =webdriver.Chrome(options=options)
    URL = f"https://tonybet.com/sport/{tonybet_code}"
    driver.get(URL)
    try:
        element = WebDriverWait(driver,10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "wpt-odd-changer"))
        )

    except Exception as e:
        print(e)

    source = driver.page_source
    # with open("page.html", "w") as f:
    #     f.write(source)
    soup = BeautifulSoup(source, 'lxml')
    matches = soup.select('.wpt-table__body .wpt-table__row')
    team_names = []
    for match in matches:
        try:
            teams = match.select(".wpt-teams__team span")
            home_team = teams[0].text.strip()
            away_team = teams[1].text.strip()
            if home_team not in team_names:
                team_names.append(home_team)
            if away_team not in team_names:
                team_names.append(away_team)
        except Exception as e:
            print(e)
    driver.close()
    return team_names


def get_odds(tonybet_code):
    driver =webdriver.Chrome(options=options)
    URL = f"https://tonybet.com/sport/{tonybet_code}"
    driver.get(URL)
    try:
        element = WebDriverWait(driver,10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "wpt-odd-changer"))
        )

    except Exception as e:
        print(e)

    source = driver.page_source
    # with open("page.html", "w") as f:
    #     f.write(source)
    soup = BeautifulSoup(source, 'lxml')
    matches = soup.select('.wpt-table__body .wpt-table__row')
    scraped_matches = []
    for match in matches:
        obj = {}
        try:
            odds = match.select(".wpt-odd-changer")    
            teams = match.select(".wpt-teams__team span")
            obj['home_team'] = teams[0].text.strip()
            obj['away_team'] = teams[1].text.strip()
            obj['odds'] = {
                "1": odds[0].text,
                "X": odds[1].text,
                "2": odds[2].text,
                "BTTS_YES": odds[3].text,
                "BTTS_NO": odds[4].text,
                f"Over {odds[5].span.text.strip()} Goals": odds[5].find(text=True, recursive=False),
                f"Under {odds[6].span.text.strip()} Goals": odds[6].find(text=True, recursive=False),
            }
            scraped_matches.append(obj)
        except Exception as e:
            print(e)
            continue
    driver.close()
    return scraped_matches

if __name__ == '__main__':
    odds = get_odds('football/england/premier-league')
    print(odds)