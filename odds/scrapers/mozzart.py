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

def get_odds(mozzart_code):
    driver =webdriver.Chrome(options=options)
    driver.set_window_size(1920, 1080)
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
    scraped_matches = []
    for match in matches:
        obj = {}
        try:
            match_odds = match.select(".part2wrapper")[0].select("span.odd-font")
            double_chance = match.select(".part2wrapper")[1].select("span.odd-font")
            over_under = match.select(".part2wrapper")[2].select("span.odd-font")
            
            special = match.select("span.sp-mark")
            if special:
                continue
            teams = match.select("a.pairs span")
            obj['home_team'] = teams[0].text.strip()
            obj['away_team'] = teams[1].text.strip()
            obj['odds'] = {
                '1': match_odds[0].text,
                'X': match_odds[1].text,
                '2': match_odds[2].text,
                '1X': double_chance[0].text,
                '12': double_chance[1].text,
                'X2': double_chance[2].text,
                'Under 2.5 Goals': over_under[0].text,
                'Over 2.5 Goals': over_under[1].text,
                'Over 3.5 Goals': over_under[2].text,
            }
            scraped_matches.append(obj)
        except Exception as e:
            print(e)
            continue
    
    driver.close()    
    return scraped_matches

if __name__=="__main__":
    odds = get_odds("20")
    print(odds)