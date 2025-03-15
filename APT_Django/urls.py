from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("races", views.races, name="races"),
    path("predictions", views.available_predictions, name="predict"),
    path("results", views.current_results, name="results"),
]
