from django.db import models

# Create your models here.

class Sport(models.Model):
    id =models.IntegerField(primary_key=True)
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name

class Bookmaker(models.Model):
    name = models.CharField(max_length=132)

    def __str__(self):
        return self.name
    

class Competition(models.Model):
    id = models.IntegerField(primary_key=True)
    sport = models.ForeignKey(Sport, related_name="competitions", on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    time_zone = models.CharField(max_length=50, blank=True)
    mozzart_code = models.CharField(max_length=20, blank=True)
    casapariurilor_code = models.CharField(max_length=120, blank=True)
    stanley_code = models.CharField(max_length=150, blank=True)
    oddsportal_code = models.CharField(max_length=255, blank=True)
    tonybet_code = models.CharField(max_length=255, blank=True)
    

    def __str__(self):
        return self.name

class Runner(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=150)
    competitions = models.ManyToManyField(Competition)
    mozzart_name = models.CharField(max_length=255, blank=True)
    casapariurilor_name = models.CharField(max_length=255, blank=True)
    stanley_name = models.CharField(max_length=255, blank=True)
    oddsportal_name = models.CharField(max_length=255, blank=True)
    tonybet_name = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name
    



class Event(models.Model):
    id = models.IntegerField(primary_key=True)
    competition = models.ForeignKey(Competition, related_name="events", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    start_time = models.DateTimeField()

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['start_time']




class Odds(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="odds")
    bookmaker = models.ForeignKey(Bookmaker, on_delete=models.CASCADE)
    bet_type = models.CharField(max_length=64)
    odds = models.DecimalField(max_digits=9, decimal_places=2)

    def __str__(self):
        return f"{self.event.name} - {self.bookmaker} - {self.bet_type} - {self.odds}"
    
    class Meta:
        verbose_name_plural = "Odds"
        unique_together = (('event','bookmaker', 'bet_type'))
    

class BetfairOdds(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="betfair_odds")
    bet_type = models.CharField(max_length=32)
    last_traded = models.DecimalField(max_digits=9, decimal_places=3, null=True)
    back_odds = models.DecimalField(max_digits=9, decimal_places=3, null=True)
    back_size = models.DecimalField(max_digits=18, decimal_places=2, null=True)
    lay_odds = models.DecimalField(max_digits=9, decimal_places=3, null=True)
    lay_size = models.DecimalField(max_digits=18, decimal_places=2, null=True)

    def __str__(self):
        return f"{self.event.name} - {self.bet_type} - {self.last_traded}"
    
    class Meta:
        verbose_name_plural = "BetfairOdds"    
        unique_together = (('event', 'bet_type'))