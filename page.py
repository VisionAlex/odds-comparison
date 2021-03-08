from bs4 import BeautifulSoup

with open('page.html', 'r') as f:
    soup = BeautifulSoup(f.read(), 'lxml')

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
            f"Over {odds[5].span.text} Goals": odds[5].find(text=True, recursive=False),
            f"Under {odds[6].span.text} Goals": odds[6].find(text=True, recursive=False),
        }
        scraped_matches.append(obj)
    except Exception as e:
        print(e)
        continue


print(scraped_matches)