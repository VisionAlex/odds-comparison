from .certs.credentials import USERNAME, PASSWORD, APP_KEY
from django.utils import timezone
import pytz
import betfairlightweight
from pathlib import Path
from odds.models import Competition, Event, Runner

cwd = Path.cwd()

CERTS = cwd / 'odds' / 'scrapers' / 'certs'

trading = betfairlightweight.APIClient(username=USERNAME,
                                       password=PASSWORD,
                                       app_key=APP_KEY,
                                       certs=CERTS)

trading.login()



def get_all_competitions(sport_id):
    market_filter = betfairlightweight.filters.market_filter(event_type_ids=[sport_id,])
    competitions = trading.betting.list_competitions(filter=market_filter)
    return {competition.competition.name: competition.competition.id for competition in competitions}

def get_events(competition_id):
    competition = Competition.objects.get(id=competition_id)
    market_filter = betfairlightweight.filters.market_filter(competition_ids=[competition.id])
    events = trading.betting.list_events(filter=market_filter)
    events_created_count = 0
    for event in events:
        try:
            d, created = Event.objects.get_or_create(
                id=event.event.id,
                competition=competition,
                name =event.event.name,
                start_time=timezone.make_aware(event.event.open_date,timezone=pytz.timezone("Etc/GMT"))
            )
            if created:
                events_created_count += 1
        except Exception as e:
            print("ERROR: ",e)
    print(f"SUCCESS: {events_created_count} events created for {competition.name}")

def get_runners(competition_id):
    competition = Competition.objects.get(id=competition_id)
    market_filter = betfairlightweight.filters.market_filter(
        competition_ids=[competition.id],
        market_type_codes=['MATCH_ODDS'])
    markets = trading.betting.list_market_catalogue(
        filter=market_filter,
        market_projection=['RUNNER_DESCRIPTION', 'EVENT'],
        max_results=200,
    )
    runners_created_count = 0
    for market in markets:
        for runner in market.runners:
            if runner.runner_name != "The Draw":
                obj, created = Runner.objects.get_or_create(
                    id=runner.selection_id,
                    name=runner.runner_name,
                )
                obj.competitions.add(competition)
                obj.save()
                if created:
                    runners_created_count += 1
    print(f"SUCCESS:{runners_created_count} runners added for {competition.name}")