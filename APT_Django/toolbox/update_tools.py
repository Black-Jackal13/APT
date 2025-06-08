import datetime

from APT_Django.toolbox.tools import fetch_race_data, scoring_algorithm
from APT_Django.models import CupScore, Player, Race, RaceCup, RaceFinisher, RaceScore, RaceSeason, SeasonScore


def update_racefinishers(race: Race) -> bool:
    """
    Update the Race Finishers for a race.
    :param race: Target Race object
    :return: Returns False if the race is not finished.
    """
    if RaceFinisher.objects.filter(race=race).exists():
        return True

    try:
        finishers = fetch_race_data(race.race_name, race.cup_stage,
                                    str(race.race_date.year))
    except AttributeError:
        return False

    RaceFinisher.objects.create(
        race=race,
        place1=finishers[0],
        place2=finishers[1],
        place3=finishers[2],
        place4=finishers[3],
        place5=finishers[4],
        place6=finishers[5],
        place7=finishers[6],
        place8=finishers[7],
        place9=finishers[8],
        place10=finishers[9],
    )

    return True


def update_racescores(race: Race) -> bool:
    """
    Update Racescores for a race.
    :param race: Target Race object
    :return: Returns False if an error occurred. True if all is well.
    """

    # Update finishers
    race_finished = update_racefinishers(race)
    if not race_finished:
        return False

    # Get Players
    participating_players = Player.objects.filter(prediction__race=race)

    # Get Finishers
    finishers = race.racefinisher_set.get()

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

    # Get Tier
    tier = {1: "GOLD", 2: "SILVER", 3: "BRONZE"}[race.race_tier]

    # Get predictions
    if not race.prediction_set.exists():
        return False

    predictions = race.prediction_set.all()

    # Sort predictions
    predictions_dict = {}
    for player in participating_players:
        prediction = predictions.get(player=player)
        predictions_dict[player.player_name] = (
            prediction.player_prediction1,
            prediction.player_prediction2,
            prediction.player_prediction3
        )

    # Calculate Scores
    player_scores, _, scoring_error = scoring_algorithm(tier, predictions_dict, race_finishers)

    # Save Scores for Future
    if scoring_error:
        return False

    for player in participating_players:
        if not RaceScore.objects.filter(player=player, race=race).exists():
            player_score = RaceScore.objects.create(
                race=race,
                player=player,
                score=player_scores[player.player_name],
            )
            player_score.save()

    return True


def update_cupscores(cup: RaceCup):
    """
    Update the Cup scores for a cup.
    :param cup: Target Cup object
    """
    # Update CupScore
    for player in Player.objects.filter(prediction__race__race_cup=cup):
        # Add up Score
        cup_score = 0
        for race_score in RaceScore.objects.filter(race__race_cup=cup, player=player):
            cup_score += race_score.score

        # Update/Create Cup Score
        if not CupScore.objects.filter(player=player, cup=cup).exists():
            player_score = CupScore.objects.create(player=player, cup=cup, score=cup_score)
        else:
            player_score = CupScore.objects.get(player=player, cup=cup)
            player_score.score = cup_score

        # Save Score
        player_score.save()


def update_seasonscores(season: RaceSeason):
    """
    Update the Seasons scores for a season.
    :param season: Target Season object
    """
    for player in Player.objects.filter(prediction__race__race_season=season):
        # Add up Score
        season_score = 0
        for cup_score in CupScore.objects.filter(cup__cup_season=season, player=player):
            season_score += cup_score.score

        # Update/Create Season Score
        if not SeasonScore.objects.filter(player=player, season=season).exists():
            player_score = SeasonScore.objects.create(player=player, season=season, score=season_score)
        else:
            player_score = SeasonScore.objects.get(player=player, season=season)
            player_score.score = season_score

        # Save Score
        player_score.save()


def update_scores() -> None:
    """
    Update the scores for all players.
    :return: None
    """
    for season in RaceSeason.objects.all():
        for cup in RaceCup.objects.filter(cup_season=season):
            for race in Race.objects.filter(race_season=season, race_cup=cup):
                update_racescores(race)

            update_cupscores(cup)

        update_seasonscores(season)


def _time_to_send_prediction_email(race: Race) -> bool:
    """
    Will return True if the prediction email should be sent (<72 hours before the race and email not yet sent).
    :param race: Target Race object
    :return: Return True if <72 hours before the race predictions closed and email not yet sent, otherwise False.
    """
    # 8 o'clock the morning of the race
    predictions_closed = datetime.datetime(race.race_date.year, race.race_date.month, race.race_date.day, 8)

    difference = predictions_closed - datetime.datetime.now()
    return difference < datetime.timedelta(hours=72) and not race.race_predictions_notified


def _time_to_close_predictions(race: Race) -> bool:
    """
    Will return True if predictions should be closed (0800 morning of the race).
    :param race: Target Race object
    :return: Return True if past 0800 morning of the race, otherwise False.
    """
    # 8 o'clock the morning of the race
    predictions_closed = datetime.datetime(race.race_date.year, race.race_date.month, race.race_date.day, 8)

    return predictions_closed < datetime.datetime.now()


def update_status() -> None:
    """
    Update the status of all Races, Cups, and Seasons.
    :return: None
    """
    # Loops Seasons
    for season in RaceSeason.objects.all():

        # Season Finished
        if not season.ongoing:

            # Send Season Results
            if not season.seasonscore_set.get().results_notified:
                #  send_season_results(season)
                season.seasonscore_set.get().results_notified = True

            for cup in RaceCup.objects.filter(cup_season=season):
                cup.ongoing = False

        for cup in RaceCup.objects.filter(cup_season=season):

            # Cup Finished
            if not cup.ongoing:

                # Send Cup Results
                if not cup.cupscore_set.get().results_notified:
                    #  send_cup_results(cup)
                    cup.cupscore_set.get().results_notified = True

                # Close all Races
                for race in Race.objects.filter(race_season=season, race_cup=cup):
                    race.race_predictions_closed = True
                    race.race_finished = True

                    # Send Race Results
                    if not race.racescore_set.get().results_notified:
                        #  send_race_results(race)
                        race.racescore_set.get().results_notified = True

                    race.save()

            else:
                for race in Race.objects.filter(race_season=season, race_cup=cup):
                    # Prediction Email
                    if _time_to_send_prediction_email(race):
                        #  send_prediction_prompt(race)
                        pass

                    # Close Predictions
                    if _time_to_close_predictions(race):
                        race.race_predictions_closed = True

                    # Race Finished
                    if update_racefinishers(race):
                        race.race_finished = True

                    # Update Score
                    if race.race_finished:
                        update_racescores(race)

                    race.save()

            cup.save()

        season.save()


def full_refresh() -> None:
    """
    Runs both main update functions.
    :return: None
    """
    update_status()
    update_scores()

    print("Refreshing and Updating Server...")
