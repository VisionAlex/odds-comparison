from bs4 import BeautifulSoup

codes = {
    "EUROPA": 922,
    "ROMANIA": 966,
    "ANGLIA": 938,
    "FRANTA": 959,
    "GERMANIA":1012,
    "ITALIA": 964,
    "SPANIA": 1019,


}

with open('page.html', 'r') as f:
    soup = BeautifulSoup(f.read(), 'lxml')

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

print(scraped_matches)

