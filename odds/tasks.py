from celery import shared_task
from .scrapers import betfair
from .models import Sport, Competition
import json

@shared_task
def betfair_competitions_as_json():
    competitions = betfair.get_all_competitions(1)
    with open('files/competitions.json', 'w') as f:
        f.write(json.dumps(competitions))

@shared_task
def populate_selected_competitions():
    sport, created = Sport.objects.get_or_create(id=1, name="Soccer")
    with open('files/selected_competitions.json', 'r') as f:
        competitions = json.loads(f.read())
    for name, id in competitions.items():
        obj , created = Competition.objects.get_or_create(id=id, name=name, sport=sport,)
    return "SUCCESS: Populated database with betfair_competitions"
