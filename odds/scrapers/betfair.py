from .certs.credentials import USERNAME, PASSWORD, APP_KEY
import betfairlightweight
from pathlib import Path

cwd = Path.cwd()

CERTS = cwd / 'odds' / 'scrapers' / 'certs'

trading = betfairlightweight.APIClient(username=USERNAME,
                                       password=PASSWORD,
                                       app_key=APP_KEY,
                                       certs=CERTS)

trading.login()



def get_competitions(sport_id):
    market_filter = betfairlightweight.filters.market_filter(event_type_ids=[sport_id])
    competitions = trading.betting.list_competitions(filter=market_filter)
    return {competition.competition.name: competition.competition.id for competition in competitions}

