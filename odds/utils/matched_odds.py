

def get_betfair_odds(event):
    odds = {}
    data = event.betfair_odds.all()
    for item in data:
        odds[item.bet_type] = {
                "last_traded": item.last_traded,
                "back_odds": item.back_odds,
                "back_size": item.back_size,
                "lay_odds": item.lay_odds,
                "lay_size": item.lay_size,
            }
        
    return odds

def get_odds(event, bookmaker_name):
    odds = {}
    data = event.odds.filter(bookmaker__name=bookmaker_name)
    if data:
        for item in data:
            odds[item.bet_type] = item.odds
        return odds
    else:
        print(f"No {bookmaker_name} odds for {event.name}")

def get_back_lay_scores(bookmaker_odds, exchange_odds):
    scores = []
    if  not bookmaker_odds or not exchange_odds:
        return scores
    for bet_type in bookmaker_odds.keys():
        try:
            if exchange_odds[bet_type]['lay_odds'] != 1.01:
                score = round((bookmaker_odds[bet_type] / exchange_odds[bet_type]['lay_odds'] -1) *100, 2)
                scores.append({
                    "bet_type": bet_type,
                    "price": bookmaker_odds[bet_type],
                    "lay_odds" : exchange_odds[bet_type]['lay_odds'],
                    "lay_size" : exchange_odds[bet_type]['lay_size'],
                    "score" : score
                })
        except KeyError as e:
            if "1X" in e.args or "X2" in e.args or "12" in e.args:
                continue
            else:
                print("KeyError", e)
    return scores

def double_chance_scores(bookmaker_odds, exchange_odds):
    scores = []
    if not bookmaker_odds or not exchange_odds:
        return scores
    for bet_type in ['1X', 'X2', '12']:
        exchange_bet_type = "1X2".replace(bet_type[0],"").replace(bet_type[1],"")
        if bet_type not in bookmaker_odds:
            continue
        score = round((1- (1 / bookmaker_odds[bet_type] + 1 / exchange_odds[exchange_bet_type]['back_odds']))*100, 2)
        scores.append({
                "bet_type": bet_type,
                "price" : bookmaker_odds[bet_type],
                "exchange": {
                    "bet_type": exchange_bet_type,
                    "price": exchange_odds[exchange_bet_type]['back_odds'],
                    "size": exchange_odds[exchange_bet_type]['back_size'],
                },
                "score" : score,
        })
        return scores


def get_asian_handicap_scores(bookmaker_odds, exchange_odds):
    pass




