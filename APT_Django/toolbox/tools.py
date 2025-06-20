import bs4
import requests
import datetime

from APT_Django.models import Player, Race, RaceCup, RaceSeason


def fetch_race_data(race_name: str, stage: str, race_year: str) -> list[str]:
    """
    Fetches the top ten finishers of a race from the ProcyclingStats website.

    :param race_name: Name of the race
    :param stage: race stage (for cups)
    :param race_year: year of the specific race
    :return: list of top ten finishers
    """

    if stage != "0":
        race_name = race_name.split(" (")[0]

    # Get HTML
    website_link = f"https://www.procyclingstats.com/race/{race_name.lower().replace(" ", "-")}/{race_year}"
    if stage != "0":
        website_link += f"/stage-{stage}"
    print(website_link)
    website_soup = bs4.BeautifulSoup(requests.get(website_link).text, "html.parser")

    # Narrow Down to Find Table
    website_soup = website_soup.find("body").find("div", {"class": "wrapper"})
    website_soup = website_soup.find("div", {"class": "content"})
    website_soup = website_soup.find("div", {"class": "page-content page-object default"})
    website_soup = website_soup.find("div", {"class": "w50 left mb_w100 mg_r2" if stage == "0" else "w68 left mb_w100"})
    if stage == "0":
        website_soup = website_soup.find("span", {"class": "table-cont"})
    else:
        website_soup = website_soup.find("div", {"class": "result-cont"})
        website_soup = website_soup.find("div", {"class": "subTabs"})

    # Table not there (Not a finished race)
    try:
        table_body = website_soup.find("table").find("tbody")
    except AttributeError:
        return []

    # Find the Finishers
    top_ten_finishers = []
    if stage != "0":
        for row in table_body.find_all("tr"):
            finisher_details = row.find_all("td")
            finisher_details = [col.text.strip() for col in finisher_details]
            finisher_lastname = finisher_details[6].split(" ")[0].capitalize()
            top_ten_finishers.append(finisher_lastname)
    else:
        for row in table_body.find_all("tr"):
            finisher_details = row.find_all("td")
            finisher_details = [col.text.strip() for col in finisher_details]
            finisher_lastname = finisher_details[1].split(" ")[0].capitalize()
            top_ten_finishers.append(finisher_lastname)

    return top_ten_finishers


def fetch_startlist(race_name: str, race_year: str) -> list[str]:
    website_link = f"https://www.procyclingstats.com/race/{race_name.lower().replace(' ', '-')}/{race_year}/startlist"

    response = requests.get(website_link)
    soup = bs4.BeautifulSoup(response.text, "html.parser")

    start_list_section = soup.find("ul", {"class": "startlist_v4"})
    riders = []

    for team in start_list_section.find_all("li"):

        riders_cont = team.find("div", {"class": "ridersCont"})
        if riders_cont is None:
            continue

        rider_list = riders_cont.find("ul")
        if rider_list is None:
            continue

        for rider_item in rider_list.find_all("li"):
            rider_tag = rider_item.find("a")
            if rider_tag:
                rider_full_name = rider_tag.text
                rider_names = rider_full_name.strip().split(" ")

                rider_name = ""
                for name in rider_names:
                    if name == name.upper():
                        rider_name += name + " "

                rider_name = rider_name.strip().capitalize()
                riders.append(rider_name)

    riders.sort()

    for rider in riders:
        print(rider)

    return riders


def scoring_algorithm(
        tier: str,  # (GOLD, SILVER or BRONZE)
        predicted_finishers: dict[str, tuple[str, ]],
        top_ten_finishers: list[str]
) -> tuple[dict[str, int], list[tuple[str, int]], bool]:
    """
    Calculate points based on a player's prediction and the top_ten_finishers results.

    :param tier: The race tier (GOLD, SILVER, or BRONZE).
    :type tier: Str
    :param predicted_finishers: Players and their predicted top 3 finishers (first, second, third).
    :type predicted_finishers: Dict[str: tuple[str, str, str]]
    :param top_ten_finishers: The top_ten_finishers top 3 finishers.
    :type top_ten_finishers: List[str, str, str]

    :return: The total points awarded to the player based on prediction accuracy, the standings, and a boolean value
    that will be True if an error was encountered and False otherwise.
    """
    # Point values
    point_values = {
        "GOLD": {
            "podium": (15, 12, 9),
            "miss": -3,
            "joker": 3,
            "ppp": 15
        },
        "SILVER": {
            "podium": (10, 8, 6),
            "miss": -2,
            "joker": 2,
            "ppp": 10
        },
        "BRONZE": {
            "podium": (5, 4, 3),
            "miss": -1,
            "joker": 1,
            "ppp": 5
        },
    }
    current_values = point_values[tier]

    scores = {player: 0 for player in predicted_finishers.keys()}
    standings = []

    # Get Prediction Frequencies
    prediction_frequency = {}
    for player in predicted_finishers:
        for finisher in predicted_finishers[player]:
            if finisher in prediction_frequency:
                prediction_frequency[finisher] += 1
            else:
                prediction_frequency[finisher] = 1

    # Cycle Players
    top_three_finishers = top_ten_finishers[:3]
    for player in predicted_finishers:

        for index, predicted_finisher in enumerate(predicted_finishers[player]):
            try:
                top_three_finishers[index]
            except IndexError:
                scores = {player: 0 for player in predicted_finishers.keys()}
                return scores, [player for player in predicted_finishers.keys()], True

            # Correct Predictions
            if predicted_finisher == top_three_finishers[index]:
                scores[player] += current_values["podium"][index]
                # Double Points (more than 6 players)
                if prediction_frequency[predicted_finisher] <= 2 and len(predicted_finishers.keys()) >= 6:
                    scores[player] += current_values["podium"][index]

                # Triple Points (more than 6 players)
                elif prediction_frequency[predicted_finisher] == 1 and len(predicted_finishers.keys()) >= 6:
                    scores[player] += current_values["podium"][index]

            # Missed Predictions
            elif predicted_finisher in top_three_finishers and predicted_finisher != top_three_finishers[index]:
                scores[player] += min(
                    current_values["podium"][index],
                    current_values["podium"][top_three_finishers.index(predicted_finisher)]
                )

                scores[player] += current_values["miss"]*max(
                    index-top_three_finishers.index(predicted_finisher),
                    top_three_finishers.index(predicted_finisher)-index
                )

        # PPP
        if predicted_finishers[player] == top_three_finishers:
            scores[player] += current_values["ppp"]

        # Place in Standings
        temp_standings = standings.copy()
        for index, _, score in enumerate(temp_standings):
            if score < scores[player]:
                standings.insert(index, (player, scores[player]))
                break

    # Joker Points
    if len(predicted_finishers.keys()) >= 6:
        in_top_ten = set()
        for player in predicted_finishers:
            for finisher in predicted_finishers[player]:
                if finisher not in top_ten_finishers:
                    break
            else:
                in_top_ten.add(player)

        joker_players = set()
        for player in in_top_ten:
            for comparison in in_top_ten:
                if predicted_finishers[player] == predicted_finishers[comparison]:
                    break
            else:
                joker_players.add(player)

        for player in joker_players:
            print(f"{player} is a joker!")
            scores[player] += current_values["joker"]

    return scores, standings, False


def get_cup_total(player: Player, cup: RaceCup) -> int:
    """
    Get player total score for a specific cup.

    :param player: Player object
    :param cup: Targeted Cup object
    :return: total score
    """
    score = 0

    races = Race.objects.filter(race_cup=cup).filter(prediction__player=player)
    for race in races:
        score += race.racescore_set.get(player=player).score

    return score


def get_season_total(player: Player, season: RaceSeason) -> int:
    """
    Get player total score for a specific season.

    :param player: Player object
    :param season: Targeted Season object
    :return: total score
    """
    score = 0

    races = Race.objects.filter(race_season=season).filter(prediction__player=player)
    for race in races:
        score += race.racescore_set.get(player=player).score

    return score


def get_player_overall_score(player: Player) -> int:
    """
    Get alltime score for a specific player.

    :param player: Player object
    :return: score
    """
    score = 0

    races = Race.objects.filter(prediction__player=player)
    for race in races:
        score += race.racescore_set.get(player=player).score

    return score


def player_prediction_history(player: Player) -> dict[str: str | int]:
    """
    Get player prediction history for all the finished races they've participated in.

    :param player: Target Player object
    :type player: Player
    :return: dictionary with player prediction history
    """
    # Participating Races
    finished_races = Race.objects.filter(prediction__player=player).filter(race_finished=True)

    player_race_details = [
        {
            "race": race,
            "prediction1": race.prediction_set.get(player=player).player_prediction1,
            "prediction2": race.prediction_set.get(player=player).player_prediction2,
            "prediction3": race.prediction_set.get(player=player).player_prediction3,
            "tier": {1: "GOLD", 2: "Silver", 3: "Bronze"}[race.race_tier],
            "score": race.racescore_set.get(player=player).score,
        }
        for race in finished_races
    ]

    return player_race_details


def time_to_deadline(race: Race) -> datetime.timedelta:
    """
    Findes the deadline for a specific race.
    :param race: Target Race object
    :return: Timedelta of deadline
    """
    deadline = datetime.datetime(race.race_date.year, race.race_date.month, race.race_date.day, 8)
    time_to = deadline - datetime.datetime.now()

    return time_to
