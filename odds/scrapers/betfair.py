from .certs.credentials import USERNAME, PASSWORD, APP_KEY
from django.utils import timezone
import pytz
import betfairlightweight
from pathlib import Path
from odds.models import Competition, Event, Runner, BetfairOdds

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


# Getting odds from Betfair API --> Start

BET_TYPES = {
    1222344: 'Under 3.5 Goals',
    1222345: 'Over 3.5 Goals', 
    47972: 'Under 2.5 Goals', 
    47973: 'Over 2.5 Goals',
}

def save_to_db(odds, event):
    updated_odds = 0
    created_odds = 0
    for key, item in odds.items():
        try:
            obj = BetfairOdds.objects.get(
                event=event,
                bet_type=key,
            )
            obj.last_traded=item['last_traded']
            obj.back_odds = item['back_odds']
            obj.back_size = item['back_size']
            obj.lay_odds = item['lay_odds']
            obj.lay_size = item['lay_size']
            obj.save()
            updated_odds += 1
        except BetfairOdds.DoesNotExist:
                obj = BetfairOdds(
                event=event,
                bet_type=key,
                **item
            )
                obj.save()
                created_odds += 1
    print(f"SUCCESS: {created_odds} odds created and {updated_odds} odds updated.")

def get_match_odds(runners):
    last_traded_1 = runners[0].last_price_traded if runners[0].last_price_traded else 1.01
    back_odds_1 = runners[0].ex.available_to_back[0].price if runners[0].ex.available_to_lay[0].price else 1.01
    back_size_1 = runners[0].ex.available_to_back[0].size if runners[0].ex.available_to_lay[0].size else 0
    lay_odds_1 = runners[0].ex.available_to_lay[0].price if runners[0].ex.available_to_lay[0].price else 1.01
    lay_size_1 = runners[0].ex.available_to_lay[0].size if runners[0].ex.available_to_lay[0].size else 0
    
    last_traded_X = runners[2].last_price_traded if runners[2].last_price_traded else 1.01
    back_odds_X = runners[2].ex.available_to_back[0].price if runners[2].ex.available_to_lay[0].price else 1.01
    back_size_X = runners[2].ex.available_to_back[0].size if runners[2].ex.available_to_lay[0].size else 0
    lay_odds_X = runners[2].ex.available_to_lay[0].price if runners[2].ex.available_to_lay[0].price else 1.01
    lay_size_X = runners[2].ex.available_to_lay[0].size if runners[2].ex.available_to_lay[0].size else 0
    
    last_traded_2 = runners[1].last_price_traded if runners[1].last_price_traded else 1.01
    back_odds_2 = runners[1].ex.available_to_back[0].price if runners[1].ex.available_to_lay[0].price else 1.01
    back_size_2 = runners[1].ex.available_to_back[0].size if runners[1].ex.available_to_lay[0].size else 0
    lay_odds_2 = runners[1].ex.available_to_lay[0].price if runners[1].ex.available_to_lay[0].price else 1.01
    lay_size_2 = runners[1].ex.available_to_lay[0].size if runners[1].ex.available_to_lay[0].size else 0
    return {
        "1": {
            "last_traded": last_traded_1,
            "back_odds": back_odds_1,
            "back_size": back_size_1,
            "lay_odds": lay_odds_1,
            "lay_size": lay_size_1,
        },
        "X": {
            "last_traded": last_traded_X,
            "back_odds": back_odds_X,
            "back_size": back_size_X,
            "lay_odds": lay_odds_X,
            "lay_size": lay_size_X,
        },
        "2": {
            "last_traded": last_traded_2,
            "back_odds": back_odds_2,
            "back_size": back_size_2,
            "lay_odds": lay_odds_2,
            "lay_size": lay_size_2,
        }
    }

def btts_odds_format(runners):
    last_traded_YES = runners[0].last_price_traded if runners[0].last_price_traded else 1.01
    back_odds_YES = runners[0].ex.available_to_back[0].price if runners[0].ex.available_to_lay[0].price else 1.01
    back_size_YES = runners[0].ex.available_to_back[0].size if runners[0].ex.available_to_lay[0].size else 0
    lay_odds_YES = runners[0].ex.available_to_lay[0].price if runners[0].ex.available_to_lay[0].price else 1.01
    lay_size_YES = runners[0].ex.available_to_lay[0].size if runners[0].ex.available_to_lay[0].size else 0
    
    
    last_traded_NO = runners[1].last_price_traded if runners[1].last_price_traded else 1.01
    back_odds_NO = runners[1].ex.available_to_back[0].price if runners[1].ex.available_to_lay[0].price else 1.01
    back_size_NO = runners[1].ex.available_to_back[0].size if runners[1].ex.available_to_lay[0].size else 0
    lay_odds_NO = runners[1].ex.available_to_lay[0].price if runners[1].ex.available_to_lay[0].price else 1.01
    lay_size_NO = runners[1].ex.available_to_lay[0].size if runners[1].ex.available_to_lay[0].size else 0
    return {
        "BTTS_YES": {
            "last_traded": last_traded_YES,
            "back_odds": back_odds_YES,
            "back_size": back_size_YES,
            "lay_odds": lay_odds_YES,
            "lay_size": lay_size_YES,
        },
        "BTTS_NO": {
            "last_traded": last_traded_NO,
            "back_odds": back_odds_NO,
            "back_size": back_size_NO,
            "lay_odds": lay_odds_NO,
            "lay_size": lay_size_NO,
        },
    }

def get_odds():
    events= Event.objects.filter(start_time__gt=timezone.now())
    for event in events:
        try:
            odds_filter = betfairlightweight.filters.market_filter(event_ids=[event.id],market_type_codes=['MATCH_ODDS','OVER_UNDER_25', 'OVER_UNDER_35', 'BOTH_TEAMS_TO_SCORE'])
            price_filter = betfairlightweight.filters.price_projection(price_data=['EX_BEST_OFFERS'])
            catalogue = trading.betting.list_market_catalogue(filter=odds_filter, market_projection=[
            'EVENT',
            'RUNNER_DESCRIPTION'
        ],
        sort="FIRST_TO_START",
        max_results=500)
            markets ={market.market_id:market.market_name for market in catalogue}
            market_book = trading.betting.list_market_book(market_ids=list(markets.keys()),
                                                        price_projection=price_filter )
            for market in market_book:
                market_name = markets[market.market_id]
                runners = market.runners
                if market_name == "Match Odds":
                    match_odds = get_match_odds(runners)
                    save_to_db(match_odds, event)
                
                elif market_name == "Both teams to Score?":
                    btts_odds = btts_odds_format(runners)
                    save_to_db(btts_odds, event)
                else:
                    odds = {}
                    for runner in runners:
                        odds[BET_TYPES[runner.selection_id]] = {
                            "last_traded": runner.last_price_traded if runner.last_price_traded else 1.01,
                            "back_odds": runner.ex.available_to_back[0].price if runner.ex.available_to_lay[0].price else 1.01,
                            "back_size": runner.ex.available_to_back[0].size if runner.ex.available_to_lay[0].price else 1.01,
                            "lay_odds": runner.ex.available_to_lay[0].price if runner.ex.available_to_lay[0].price else 1.01,
                            "lay_size": runner.ex.available_to_lay[0].size if runner.ex.available_to_lay[0].price else 1.01,
                        }
                    save_to_db(odds,event)

        except Exception as e:
            print("ERROR:", event.name, e)




