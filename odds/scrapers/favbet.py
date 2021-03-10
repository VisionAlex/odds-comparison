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

codes = {
    "EUROPA": 922,
    "ROMANIA": 966,
    "ANGLIA": 938,
    "FRANTA": 959,
    "GERMANIA":1012,
    "ITALIA": 964,
    "SPANIA": 1019,
    }


def scrape_odds(source):
    soup = BeautifulSoup(source, 'lxml')
    scraped_matches = {}

    leagues = soup.select("div[class*='EventsContainer_accordionContainer']")
    for league in leagues:
        league_name = league.select("span[class^='EventsContainer_sportTitle']")[0].text
        matches = league.select("div[class*='EventBody_container']")
        league_matches = []
        for match in matches:
            obj = {}
            teams = match.select("span[class*='EventParticipants_participantName']")
            obj['home_team'] = teams[0].text
            obj['away_team'] = teams[1].text
            if obj['home_team'].startswith('Home Goals'):  
                continue
            odds_categories = match.select("div[class*='EventMarket_wrapper']")
            h2h = odds_categories[0].select('span')
            handicap = odds_categories[1].select('span')
            handicap_param = odds_categories[1].select("div[class*='EventMarketContainer_param__Fk7qB']")[0].text
            over_under = odds_categories[2].select('span')
            over_under_param = odds_categories[2].select("div[class*='EventMarketContainer_param']")[0].text
            obj['odds'] = {
                "1": h2h[0].text,
                "X": h2h[1].text,
                "2": h2h[2].text,
                f"Over {over_under_param} Goals": over_under[0].text,
                f"Under {over_under_param} Goals": over_under[1].text,
                f"AH {handicap_param} 1": handicap[0].text,
                f"AH {handicap_param} 2": handicap[1].text,
            }
            league_matches.append(obj)
        scraped_matches[league_name] = league_matches
    return scraped_matches




def scrape_team_names(source):
    soup = BeautifulSoup(source, 'lxml')
    teams_obj = {}

    leagues = soup.select("div[class*='EventsContainer_accordionContainer']")
    for league in leagues:
        league_name = league.select("span[class^='EventsContainer_sportTitle']")[0].text
        team_names = []
        teams = league.select("span[class*='EventParticipants_participantName']")
        for team in teams:
            if team.text not in team_names and not team.text.startswith('Home Goals') and not team.text.startswith('Away Goals'):
                team_names.append(team.text)
        teams_obj[league_name] = team_names    
    return teams_obj


def get_team_names():
    team_names = {}
    driver =webdriver.Chrome(options=options)
    for code in codes.values():
        URL = f"https://www.favbet.ro/ro/sports/category/soccer/{code}"
        driver.get(URL)

        try:
            element = WebDriverWait(driver,10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[class^='OutcomeContainer_outcomeContainer']"))
            )

        except Exception as e:
            print("ERROR", e)

        source = driver.page_source
        teams_obj = scrape_team_names(source)
        team_names.update(teams_obj)
    driver.close()
    return team_names


def get_odds():
    odds = {}
    driver =webdriver.Chrome(options=options)
    for code in codes.values():
        URL = f"https://www.favbet.ro/ro/sports/category/soccer/{code}"
        driver.get(URL)

        try:
            element = WebDriverWait(driver,10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[class^='OutcomeContainer_outcomeContainer']"))
            )

        except Exception as e:
            print("ERROR", e)

        source = driver.page_source
        odds_obj = scrape_odds(source)
        odds.update(odds_obj)
    return odds
        
if __name__ == '__main__':
    odds = get_odds()
    print(odds)