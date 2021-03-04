from celery import shared_task
from .scrapers import betfair
from django.utils import timezone
from .models import Sport, Competition, Event
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

@shared_task
def populate_betfair_events():
    competition_ids = list(Competition.objects.all().values_list('id', flat=True))
    for competition_id in competition_ids:
        betfair.get_events(competition_id)

@shared_task
def populate_betfair_runners():
    competition_ids = list(Competition.objects.all().values_list('id', flat=True))
    for competition_id in competition_ids:
        betfair.get_runners(competition_id)

@shared_task
def clear_past_events():
    now = timezone.now()
    events = Event.objects.filter(start_time__lt=now)
    count = len(events)
    events.delete()
    print(f"SUCCESS: {count} past events DELETED.")

@shared_task
def populate_betfair_odds():
    betfair.get_odds()
