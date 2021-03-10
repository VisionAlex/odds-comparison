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

def get_team_names(league):
    driver = webdriver.Chrome(options=options)
    URL = f"https://www.casapariurilor.ro/pariuri-online/fotbal/{league}"
    driver.get(URL)

    try:
        element = WebDriverWait(driver,10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "odds-value"))
        )

    except Exception as e:
        print(e)
    
    source = driver.page_source
    soup = BeautifulSoup(source, 'lxml')


    matches = soup.select('span.market-name')
    team_names = []
    for match in matches:
        teams = match.text.strip().split(' - ')
        for team in teams:
            if team not in team_names:
                team_names.append(team)
    
    driver.close()
    return team_names

def get_odds(league):
    driver = webdriver.Chrome(options=options)
    URL = f"https://www.casapariurilor.ro/pariuri-online/fotbal/{league}"
    driver.get(URL)

    try:
        element = WebDriverWait(driver,10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "odds-value"))
        )

    except Exception as e:
        print(e)
    
    source = driver.page_source
    soup = BeautifulSoup(source, 'lxml')

    matches = soup.select('table.events-table tr.tablesorter-hasChildRow')
    scraped_matches = []
    for match in matches:
        obj = {}
        try:
            teams = match.find('span', class_='market-name').text.strip().split(' - ')
            odds = match.select('span.odds-value')
            obj['home_team'] = teams[0]
            obj['away_team'] = teams[1]
            obj['odds'] = {
                '1': odds[0].text,
                'X': odds[1].text,
                '2': odds[2].text,
                '1X': odds[3].text,
                '12': odds[4].text,
                'X2': odds[5].text,
            }
            scraped_matches.append(obj)
        except Exception as e:
            print(e)
            continue
    driver.close()
    return scraped_matches



if __name__ == "__main__":
    odds = get_odds('liga-campionilor')
    print(odds)