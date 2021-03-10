from celery import shared_task
from .scrapers import betfair, mozzart, tonybet, casapariurilor,favbet
from django.utils import timezone
from django.db.models import Q
from .models import Sport, Competition, Event, Runner, Odds, Bookmaker
from .scrapers.utils import team_names_matcher
import json

# Betfair Tasks -----
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
def betfair_populate_events():
    competition_ids = list(Competition.objects.all().values_list('id', flat=True))
    for competition_id in competition_ids:
        betfair.get_events(competition_id)

@shared_task
def betfair_populate_runners():
    competition_ids = list(Competition.objects.all().values_list('id', flat=True))
    for competition_id in competition_ids:
        betfair.get_runners(competition_id)

@shared_task
def betfair_clear_past_events():
    now = timezone.now()
    events = Event.objects.filter(start_time__lt=now)

    count = len(events)
    events.delete()
    print(f"SUCCESS: {count} past events DELETED.")

@shared_task
def betfair_populate_odds():
    betfair.get_odds()

# Mozzart Tasks -----------------
@shared_task
def mozzart_populate_all_soccer_team_names():
    codes = Competition.objects.filter(mozzart_code__isnull=False).exclude(mozzart_code="").values_list('mozzart_code', flat=True)
    for code in codes:
        runners = list(Runner.objects.filter(competitions__mozzart_code=code).values_list('name', flat=True))
        team_names = mozzart.get_team_names(code)
        bookmaker_name = 'mozzart'
        try:
            team_names_matcher(runners, team_names, bookmaker_name)
        except Exception as e:
            print(f"ERROR: {bookmaker_name} [{code}] {e}")
@shared_task    
def mozzart_populate_team_names_by_competition(code):
    runners = list(Runner.objects.filter(competitions__mozzart_code=code).values_list('name', flat=True))
    team_names = mozzart.get_team_names(code)
    team_names_matcher(runners, team_names, "mozzart", forced=True)

@shared_task
def mozzart_populate_odds_by_competition(code):
    bookmaker = Bookmaker.objects.get(name="mozzart")
    scraped_matches = mozzart.get_odds(code)
    for match in scraped_matches:
        try:
            home_team = Runner.objects.get(mozzart_name=match['home_team'])
            away_team = Runner.objects.get(mozzart_name=match['away_team'])
            q1 = Q(name__istartswith=home_team.name)
            q2 = Q(name__iendswith=away_team.name)
            event = Event.objects.get(q1 & q2)
        except Exception as e:
            print(f"ERROR event: [{home_team.name} v {away_team.name}] - {e}")
            continue
        for bet_type in match['odds'].keys():
            try:
                obj = Odds.objects.get(event=event, bookmaker=bookmaker, bet_type=bet_type)
                obj.odds = match['odds'][bet_type]
                obj.save()
                print(f"Odds updated for {obj.event.name} for {bet_type} with {obj.odds}")
            except Odds.DoesNotExist:
                obj = Odds.objects.create(event=event, bookmaker=bookmaker,bet_type=bet_type, odds=match['odds'][bet_type])
                print(f"Odds created for {obj.event.name} for {bet_type} with {obj.odds}")

@shared_task
def mozzart_populate_odds():
    competitions = Competition.objects.filter(mozzart_code__isnull=False).exclude(mozzart_code="").values_list("mozzart_code", flat=True)
    for competition in competitions:
        try:
            mozzart_populate_odds_by_competition(competition)
        except Exception as e:
            print(e)

# Tonybet Tasks -----------------
@shared_task
def tonybet_populate_team_names_by_competition(code):
    runners = list(Runner.objects.filter(competitions__tonybet_code=code).values_list('name', flat=True))
    team_names = tonybet.get_team_names(code)
    team_names_matcher(runners, team_names, "tonybet", forced=False)

@shared_task
def tonybet_populate_all_soccer_team_names():
    codes = Competition.objects.filter(tonybet_code__isnull=False).exclude(tonybet_code="").values_list('tonybet_code', flat=True)
    for code in codes:
        runners = list(Runner.objects.filter(competitions__tonybet_code=code).values_list('name', flat=True))
        team_names = tonybet.get_team_names(code)
        bookmaker_name = 'tonybet'
        try:
            team_names_matcher(runners, team_names, bookmaker_name)
        except Exception as e:
            print(f"ERROR: {bookmaker_name} [{code}] {e}")

@shared_task
def tonybet_populate_odds_by_competition(code):
    bookmaker = Bookmaker.objects.get(name="tonybet")
    scraped_matches = tonybet.get_odds(code)
    for match in scraped_matches:
        try:
            home_team = Runner.objects.get(tonybet_name=match['home_team'])
            away_team = Runner.objects.get(tonybet_name=match['away_team'])
            q1 = Q(name__istartswith=home_team.name)
            q2 = Q(name__iendswith=away_team.name)
            event = Event.objects.get(q1 & q2)
        except Exception as e:
            print(f"ERROR event: [{home_team.name} v {away_team.name}] - {e}")
            continue
        for bet_type in match['odds'].keys():
            try:
                obj = Odds.objects.get(event=event, bookmaker=bookmaker, bet_type=bet_type)
                obj.odds = match['odds'][bet_type]
                obj.save()
                print(f"Odds updated for {obj.event.name} for {bet_type} with {obj.odds}")
            except Odds.DoesNotExist:
                obj = Odds.objects.create(event=event, bookmaker=bookmaker,bet_type=bet_type, odds=match['odds'][bet_type])
                print(f"Odds created for {obj.event.name} for {bet_type} with {obj.odds}")

@shared_task
def tonybet_populate_odds():
    competitions = Competition.objects.filter(tonybet_code__isnull=False).exclude(tonybet_code="").values_list("tonybet_code", flat=True)
    for competition in competitions:
        try:
            tonybet_populate_odds_by_competition(competition)
        except Exception as e:
            print(e)

# casapariurilor tasks --------------------------------------

@shared_task
def casapariurlor_populate_team_names_by_competition(code, forced=False):
    runners = list(Runner.objects.filter(competitions__casapariurilor_code=code).values_list('name', flat=True))
    team_names = casapariurilor.get_team_names(code)
    team_names_matcher(runners, team_names, "casapariurilor", forced=forced)

@shared_task
def casapariurilor_populate_all_soccer_team_names():
    codes = Competition.objects.filter(casapariurilor_code__isnull=False).exclude(casapariurilor_code="").values_list('casapariurilor_code', flat=True)
    for code in codes:
        try:
            runners = list(Runner.objects.filter(competitions__casapariurilor_code=code).values_list('name', flat=True))
            team_names = casapariurilor.get_team_names(code)
            bookmaker_name = 'casapariurilor'
            team_names_matcher(runners, team_names, bookmaker_name)
        except Exception as e:
            print(f"ERROR: {bookmaker_name} [{code}] {e}")


@shared_task
def casapariurilor_populate_odds_by_competition(code):
    bookmaker = Bookmaker.objects.get(name="casapariurilor")
    scraped_matches = casapariurilor.get_odds(code)
    for match in scraped_matches:
        try:
            home_team = Runner.objects.get(casapariurilor_name=match['home_team'])
            away_team = Runner.objects.get(casapariurilor_name=match['away_team'])
            q1 = Q(name__istartswith=home_team.name)
            q2 = Q(name__iendswith=away_team.name)
            event = Event.objects.get(q1 & q2)
        except Exception as e:
            print(f"ERROR event: [{home_team.name} v {away_team.name}] - {e}")
            continue
        for bet_type in match['odds'].keys():
            try:
                obj = Odds.objects.get(event=event, bookmaker=bookmaker, bet_type=bet_type)
                obj.odds = match['odds'][bet_type]
                obj.save()
                print(f"Odds updated for {obj.event.name} for {bet_type} with {obj.odds}")
            except Odds.DoesNotExist:
                obj = Odds.objects.create(event=event, bookmaker=bookmaker,bet_type=bet_type, odds=match['odds'][bet_type])
                print(f"Odds created for {obj.event.name} for {bet_type} with {obj.odds}")


@shared_task
def casapariurilor_populate_odds():
    competitions = Competition.objects.filter(casapariurilor_code__isnull=False).exclude(casapariurilor_code="").values_list("casapariurilor_code", flat=True)
    for competition in competitions:
        try:
            casapariurilor_populate_odds_by_competition(competition)
        except Exception as e:
            print(e)


#favbet tasks ---------------------------------------
@shared_task
def favbet_populate_runners():
    competitions = Competition.objects.filter(favbet_code__isnull=False).exclude(favbet_code="").values_list("favbet_code", flat=True)
    scraped_team_names = favbet.get_team_names()
    for competition in competitions:
        runners = list(Runner.objects.filter(competitions__favbet_code=competition).values_list('name', flat=True))
        team_names = scraped_team_names[competition]
        bookmaker_name = "favbet"

        try:
            team_names_matcher(runners, team_names, bookmaker_name,forced=True)
        except Exception as e:
            print(f"ERROR: {bookmaker_name} [{competition}] {e}")


@shared_task
def favbet_populate_odds():
    competitions = Competition.objects.filter(favbet_code__isnull=False).exclude(favbet_code="").values_list("favbet_code", flat=True)
    bookmaker = Bookmaker.objects.get(name="favbet")
    all_odds = favbet.get_odds()
    for competition in competitions:
        scraped_matches = all_odds[competition]
        for match in scraped_matches:
            try:
                home_team = Runner.objects.get(favbet_name=match['home_team'])
                away_team = Runner.objects.get(favbet_name=match['away_team'])
                q1 = Q(name__istartswith=home_team.name)
                q2 = Q(name__iendswith=away_team.name)
                event = Event.objects.get(q1 & q2)
            except Exception as e:
                print(f"ERROR event: [{home_team.name} v {away_team.name}] - {e}")
                continue
            for bet_type in match['odds'].keys():
                try:
                    obj = Odds.objects.get(event=event, bookmaker=bookmaker, bet_type=bet_type)
                    obj.odds = match['odds'][bet_type]
                    obj.save()
                    print(f"Odds updated for {obj.event.name} for {bet_type} with {obj.odds}")
                except Odds.DoesNotExist:
                    obj = Odds.objects.create(event=event, bookmaker=bookmaker,bet_type=bet_type, odds=match['odds'][bet_type])
                    print(f"Odds created for {obj.event.name} for {bet_type} with {obj.odds}")
    