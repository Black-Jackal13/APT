from django.db import models


class RaceSeason(models.Model):
    race_season_name = models.CharField(max_length=100)
    ongoing = models.BooleanField(default=True)

    def __str__(self):
        return self.race_season_name


class RaceCup(models.Model):
    cup_name = models.CharField(max_length=100)
    cup_season = models.ForeignKey(RaceSeason, on_delete=models.CASCADE)
    ongoing = models.BooleanField(default=True)

    def __str__(self):
        return self.cup_name


class Race(models.Model):
    race_season = models.ForeignKey(RaceSeason, on_delete=models.CASCADE)
    race_cup = models.ForeignKey(RaceCup, on_delete=models.CASCADE, default=None)
    cup_stage = models.IntegerField(default=0)
    race_name = models.CharField(max_length=100)
    race_date = models.DateField()
    race_tier = models.IntegerField(default=1)  # 1 is Gold, 2 is Silver, 3 is Bronze
    race_predictions_notified = models.BooleanField(default=False)
    race_predictions_closed = models.BooleanField(default=False)
    race_finished = models.BooleanField(default=False)

    def __str__(self):
        return self.race_name


class Player(models.Model):
    player_name = models.CharField(max_length=100)
    player_email = models.EmailField()

    def __str__(self):
        return self.player_name


class Prediction(models.Model):
    race = models.ForeignKey(Race, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    player_prediction1 = models.TextField()
    player_prediction2 = models.TextField()
    player_prediction3 = models.TextField()

    def __str__(self):
        return self.player.player_name


class RaceFinisher(models.Model):
    race = models.ForeignKey(Race, on_delete=models.CASCADE)
    place1 = models.TextField()
    place2 = models.TextField()
    place3 = models.TextField()
    place4 = models.TextField()
    place5 = models.TextField()
    place6 = models.TextField()
    place7 = models.TextField()
    place8 = models.TextField()
    place9 = models.TextField()
    place10 = models.TextField()

    def __str__(self):
        return self.race.race_name


class SeasonScore(models.Model):
    season = models.ForeignKey(RaceSeason, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    score = models.IntegerField()
    results_notified = models.BooleanField(default=False)

    def __str__(self):
        return self.player.player_name + " " + str(self.score)


class CupScore(models.Model):
    cup = models.ForeignKey(RaceCup, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    score = models.IntegerField()
    results_notified = models.BooleanField(default=False)

    def __str__(self):
        return self.player.player_name + " " + str(self.score)


class RaceScore(models.Model):
    race = models.ForeignKey(Race, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    score = models.IntegerField()
    results_notified = models.BooleanField(default=False)

    def __str__(self):
        return self.player.player_name + " " + str(self.score)
