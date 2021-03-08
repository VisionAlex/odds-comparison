from bs4 import BeautifulSoup

with open('page.html', 'r') as f:
    soup = BeautifulSoup(f.read(), 'lxml')

matches = soup.select('div.match')
scraped_matches = []
for match in matches:
    teams = match.select('a.pairs span')
    double_chance = match.select(".part2wrapper")[1].select("span.odd-font")
    print(double_chance)
    break