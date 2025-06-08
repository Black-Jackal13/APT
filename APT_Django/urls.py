from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("predictions", views.available_predictions, name="predictions"),
    path("predictions/predict/<str:season>/<str:cup>/<str:race>", views.make_race_prediction, name="predict"),
    path("predictions/view/<str:season>/<str:cup>/<str:race>", views.view_race_predictions, name="view_predictions"),
    path("results", views.current_results, name="results"),
    path("results/<str:season>", views.season_results, name="season_results"),
    path("results/<str:season>/<str:cup>", views.cup_results, name="cup_results"),
    path("results/<str:season>/<str:cup>/<str:race>", views.race_results, name="race_results"),
    path("players", views.players, name="players"),
    path("players/<str:player>", views.player_details, name="player_details"),
    path("register", views.register_player, name="register_player"),
]
