from django.http import HttpResponse
from django.template import loader


# Create your views here.
def index(request):
    page = loader.get_template("index.html")
    upcoming_races = Race.objects.order_by("race_date").filter(race_finished=False)[:5]
    past_races = Race.objects.order_by("-race_date").filter(race_finished=True)[:5]
    top_5_players = SeasonScore.objects.order_by("-score")[:5]
    return HttpResponse(page.render({
        "upcoming_races": upcoming_races,
        "leaders": top_5_players,
        "past_races": past_races,
    }))


def races(request):
    page = loader.get_template("races.html")
    races_data = Race.objects.all()
    return HttpResponse(page.render({"races": races_data}))


def available_predictions(request):
    page = loader.get_template("predictions.html")
    return HttpResponse(page.render())


def current_results(request):
    page = loader.get_template("results.html")
    return HttpResponse(page.render())
