from django.urls import path
from .views import matched_bets_view

urlpatterns = [
    path('', matched_bets_view)
]

