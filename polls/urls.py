from django.urls import path

from polls.models import Poll
from polls.views import PollsView, PollView, submit_answers, StatsView, StatsMenu

urlpatterns = [
    path('',
         PollsView.as_view(model=Poll),
         name='polls'),
    path('<int:pk>/',
         PollView.as_view(),
         name='poll'),
    path('submit_answers/',
         submit_answers,
         name='submit_answers'),
    path('stats_menu/',
         StatsMenu.as_view(model=Poll),
         name='stats_menu'),
    path('stats/<int:pk>/',
         StatsView.as_view(),
         name='stats'),
]
