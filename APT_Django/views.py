from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader
from django.views.decorators.csrf import csrf_exempt

from APT_Django.toolbox.tools import fetch_startlist, player_prediction_history, time_to_deadline
from APT_Django.toolbox.update_tools import update_racefinishers, update_racescores
from .forms import EnterPrediction, RegisterForm
from .models import CupScore, Player, Prediction, Race, RaceCup, RaceScore, RaceSeason, SeasonScore


# Views
def index(request):
    page = loader.get_template("index.html")
    upcoming_races = Race.objects.order_by("race_date").filter(race_finished=False)[:5]
    past_races = Race.objects.order_by("-race_date").filter(race_finished=True)[:5]
    top_5_players = SeasonScore.objects.order_by("-score")[:5]
    leaders = [
        {
            "name"  : score.player.player_name,
            "score" : score.score,
            "season": score.season.race_season_name
        }
        for score in top_5_players
    ]
    return HttpResponse(page.render({
        "upcoming_races": upcoming_races,
        "leaders"       : leaders,
        "past_races"    : past_races,
    }))


def available_predictions(request):
    page = loader.get_template("predictions.html")
    races_data = Race.objects.filter(race_finished=False, race_predictions_closed=False).order_by("race_date")

    predictions = [
        {
            "race_season": race.race_season,
            "race_cup"   : race.race_cup,
            "race_name"  : race.race_name,
            "time_to"    : time_to_deadline(race).days,
            "race_date"  : race.race_date,
        }
        for race in races_data
    ]

    return HttpResponse(page.render({"races": predictions}))


@csrf_exempt
def make_race_prediction(request, season, cup, race):
    if request.method == "POST":
        form = EnterPrediction(request.POST)

        # Check for a Valid Form
        if not form.is_valid():
            print("Invalid form")
            page = loader.get_template("predict.html")
            form = EnterPrediction()
            return HttpResponse(page.render({"season": season, "race": race, "form": form}))

        # Check if Player exists
        if not Player.objects.filter(player_name=request.POST["player_name"]).exists():
            page = loader.get_template("register_player.html")
            form = RegisterForm()
            return HttpResponse(page.render({"form": form, "info": "Player does not exist."}))

        # Get Player and Race
        player = Player.objects.get(player_name=request.POST["player_name"])
        race_key = Race.objects.get(race_name=race)

        # Edit Prediction
        if Prediction.objects.filter(player=player, race=race_key).exists():
            prediction = Prediction.objects.get(player=player, race=race_key)
            prediction.player_prediction1 = request.POST["prediction_1"]
            prediction.player_prediction2 = request.POST["prediction_2"]
            prediction.player_prediction3 = request.POST["prediction_3"]

        # New Prediction
        else:
            prediction = Prediction.objects.create(
                player=player,
                race=race_key,
                player_prediction1=request.POST["prediction_1"],
                player_prediction2=request.POST["prediction_2"],
                player_prediction3=request.POST["prediction_3"],
            )

        # Save Prediction
        prediction.save()

        return redirect(f"/predictions")
    else:
        page = loader.get_template("predict.html")
        form = EnterPrediction()
        race = Race.objects.get(race_name=race, race_season__race_season_name=season)
        race_name = race.race_name
        race_name_without_stage = race_name

        if race.cup_stage != 0:
            race_name_without_stage = race_name.split("(Stage ")[0].strip()

        race_year = race.race_date.year
        startlist = fetch_startlist(race_name_without_stage, race_year)

        return HttpResponse(page.render({
            "season": season,
            "cup"   : cup,
            "race"  : race_name,
            "racers": startlist,
            "form"  : form}))


def view_race_predictions(request, season, cup, race):
    page = loader.get_template("race_predictions.html")

    season = RaceSeason.objects.get(race_season_name=season)
    cup = RaceCup.objects.get(cup_season=season, cup_name=cup)
    race_details = Race.objects.filter(race_season=season, race_cup=cup).get(race_name=race)
    predictions = race_details.prediction_set.all()

    return HttpResponse(page.render({
        "race": race_details, "predictions": predictions}))


def current_results(request):
    page = loader.get_template("results.html")
    seasons = RaceSeason.objects.all()
    cup_data = RaceCup.objects.order_by("cup_name").filter(ongoing=True)
    recent_races = Race.objects.order_by("-race_date").filter(race_finished=True)[:5]
    return HttpResponse(page.render(
        {
            "seasons": seasons,
            "cups"   : cup_data,
            "races"  : recent_races,
        }
    ))


def season_results(request, season):
    page = loader.get_template("season_results.html")
    season_data = RaceSeason.objects.get(race_season_name=season)
    cup_data = season_data.racecup_set.all()
    races_data = season_data.race_set.all().filter(race_finished=True)

    season_scores = SeasonScore.objects.filter(season__race_season_name=season).order_by("-score")
    scores = sorted([(player.player.player_name, player.score) for player in season_scores],
                    key=lambda x: x[1], reverse=True)
    standings = [{
        "place": place, "player": score[0], "score": score[1]
    } for place, score in enumerate(scores, start=1)]

    return HttpResponse(page.render(
        {
            "season"   : season_data,
            "cups"     : cup_data,
            "races"    : races_data,
            "standings": standings
        }
    ))


def cup_results(request, season, cup):
    page = loader.get_template("cup_results.html")

    # Get Cup Details
    cup_details = RaceCup.objects.get(cup_season__race_season_name=season, cup_name=cup)
    races = cup_details.race_set.filter(race_finished=True)
    cup_players = Player.objects.filter(cupscore__cup=cup_details).order_by("player_name")

    # Score x Race Table
    race_player_scores = []
    for row, race in enumerate(races):
        race_player_scores.append({"race": race, "scores": [0 for _ in range(cup_players.count())]})
        for col, player in enumerate(cup_players):
            if not RaceScore.objects.filter(race=race, player=player).exists():
                race_player_scores[row]["scores"][col] = 0
            else:
                race_player_scores[row]["scores"][col] = RaceScore.objects.get(race=race, player=player).score

    cup_scores = CupScore.objects.filter(cup__cup_name=cup, cup__cup_season__race_season_name=season).order_by("-score")
    scores = sorted([(player.player.player_name, player.score) for player in cup_scores],
                    key=lambda x: x[1], reverse=True)
    standings = [{
        "place": place, "player": score[0], "score": score[1]
    } for place, score in enumerate(scores, start=1)]

    return HttpResponse(page.render({
        "cup"      : cup,
        "players"  : cup_players,
        "races"    : race_player_scores,
        "standings": standings
    }))


def race_results(request, season, cup, race):
    # Special for Stages
    page = loader.get_template("race_results.html")

    # Get Race Details
    race_details = RaceSeason.objects.get(race_season_name=season).racecup_set.get(cup_name=cup).race_set.get(
        race_name=race)

    # Incomplete Race
    if not race_details.race_finished:
        page = loader.get_template("404.html")
        return HttpResponse(page.render({"info": "Race has not yet finished."}))

    # Finishers Aren't Saved
    if not race_details.racefinisher_set.exists():
        update_successful = update_racefinishers(race_details)

        if not update_successful:
            page = loader.get_template("404.html")
            return HttpResponse(page.render({"info": "Race has not yet finished."}))

    # Get Finishers
    finishers = race_details.racefinisher_set.get()

    race_finishers = [
        finishers.place1,
        finishers.place2,
        finishers.place3,
        finishers.place4,
        finishers.place5,
        finishers.place6,
        finishers.place7,
        finishers.place8,
        finishers.place9,
        finishers.place10,
    ]

    # Get Player Scores
    if not RaceScore.objects.filter(race=race_details).exists():
        update_racescores(race_details)

    # Get Player Scores
    player_scores = RaceScore.objects.filter(race=race_details).order_by("-score")
    player_scores = [(player.player.player_name, player.score) for player in player_scores]
    player_scores = sorted(player_scores, key=lambda x: x[1], reverse=True)

    return HttpResponse(page.render({
        "season"      : season,
        "race"        : race,
        "participated": player_scores,
        "finishers"   : race_finishers,
    }))


def players(request):
    page = loader.get_template("players.html")
    players_info = Player.objects.all()
    return HttpResponse(page.render({"players": players_info}))


def player_details(request, player):
    page = loader.get_template("player_details.html")
    player = Player.objects.get(player_name=player)
    prediction_history = player_prediction_history(player)

    return HttpResponse(page.render({"player": player, "history": prediction_history}))


@csrf_exempt
def register_player(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            error = None
            # Emails don't match
            if not form.cleaned_data["email"] == form.cleaned_data["verify_email"]:
                error = "Emails do not match."

            # Email in Use
            elif Player.objects.filter(player_email=form.cleaned_data["email"]).exists():
                error = "Email already registered."

            # Username in Use
            elif Player.objects.filter(player_name=form.cleaned_data["username"]).exists():
                error = "Username already registered."

            if error:
                page = loader.get_template("register_player.html")
                form = RegisterForm()
                return HttpResponse(page.render({"form": form, "info": error}))

            Player.objects.create(
                player_name=form.cleaned_data["username"],
                player_email=form.cleaned_data["email"],
            ).save()

            return players(request)

    page = loader.get_template("register_player.html")
    form = RegisterForm()
    return HttpResponse(page.render({"form": form}))
