from fuzzywuzzy import fuzz, process
from odds.models import Runner

def team_names_matcher(runners, bookmaker_names, bookmaker, forced=False):
    bookmaker_attribute = bookmaker +"_name"
    if len(bookmaker_names) != len(runners):
        error_message= f"{len(bookmaker_names)} names | {len(runners)}"
        if forced == False:
            raise Exception(error_message)

    remaining_bookmaker_names = bookmaker_names.copy()
    for i in range(100,0,-10):
        for name in bookmaker_names:
            best_match = process.extractOne(name, runners, score_cutoff=i)
            if best_match:
                obj = Runner.objects.get(name=best_match[0])
                setattr(obj,bookmaker_attribute, name)
                obj.save()
                runners.remove(best_match[0])
                print(f"{obj.name} saved with {name}")
                remaining_bookmaker_names.remove(name)
        bookmaker_names = remaining_bookmaker_names.copy()
    if len(remaining_bookmaker_names) == 0:
        print(f"SUCCESS: All names matched succesfully. Runners left:{len(runners)}")
    else:
        print(f"FAILURE: Check logs for errors: {len(remaining_bookmaker_names)} not matched")