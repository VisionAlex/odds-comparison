
from django.http import JsonResponse
from django.utils import timezone
from .models import Event
from datetime import timedelta
from .utils.matched_odds import get_odds, get_betfair_odds, get_back_lay_scores,double_chance_scores


def get_matched_bets(bookmaker_name, number_of_days):
    now = timezone.now()
    matched_bets = []
    events = Event.objects.filter(start_time__gt=now).filter(start_time__lt=now+timedelta(days=number_of_days))
    
    for event in events:
            betfair_odds = get_betfair_odds(event)
            bookmaker_odds = get_odds(event, bookmaker_name)
            back_lay = get_back_lay_scores(bookmaker_odds, betfair_odds)
            double_chance = double_chance_scores(bookmaker_odds,betfair_odds)
            try:
                for item in back_lay:
                    matched_item = {
                        "event": event.name,
                        **item
                    }
                    matched_bets.append(matched_item)
            except Exception as e:
                print(f"ERROR:BACK_LAY [{event.name}] -", e)
            if double_chance:
                try: 
                    for item in double_chance:
                        matched_item = {
                            "event": event.name,
                            **item
                        }
                        matched_bets.append(matched_item)
                except Exception as e:
                    print(f"ERRPR: DOUBLE_CHANGE [{event.name}] - {e}")

    matched_bets.sort(key=lambda x:x['score'], reverse=True)
    return matched_bets    

def matched_bets_view(request, bookmaker):
    if request.method == "GET":
        days= int(request.GET['days'])
        matched_bets = get_matched_bets(bookmaker, days)
        data = {"data": matched_bets }
        return JsonResponse(data)

