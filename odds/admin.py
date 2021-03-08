from django.contrib import admin
from .models import Sport, Competition, Event, Odds, BetfairOdds, Runner, Bookmaker

# Register your models here.
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ('name','id', 'tonybet_code')

class OddsAdmin(admin.ModelAdmin):
    list_display = ('event', 'bookmaker', 'bet_type', 'odds')
    search_fields = ['event__name']
    list_filter = ('event__competition__name','event__start_time')

class EventAdmin(admin.ModelAdmin):
    list_display = ('start_time','name', 'id', 'competition')
    search_fields = ('name',)
    list_filter = ('competition',)

class BetfairOddsAdmin(admin.ModelAdmin):
    search_fields = ['event__name']
    list_filter = ('event__competition__name','event__start_time')

class RunnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'mozzart_name','tonybet_name', 'id')
    list_filter = ('competitions__name',)
    search_fields = ('name',)


admin.site.register(Sport)
admin.site.register(Competition, CompetitionAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Odds,OddsAdmin)
admin.site.register(BetfairOdds, BetfairOddsAdmin)
admin.site.register(Bookmaker)
admin.site.register(Runner, RunnerAdmin)