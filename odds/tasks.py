from celery import shared_task
from .scrapers import betfair
import json

@shared_task
def betfair_competitions():
    competitions = betfair.get_competitions(1)
    with open('files/competitions.json', 'w') as f:
        f.write(json.dumps(competitions))