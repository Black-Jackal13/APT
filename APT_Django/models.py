from django.db import models


class RaceSeason(models.Model):
    race_season_name = models.CharField(max_length=100)

    def __str__(self):
        return self.race_season_name


class Race(models.Model):
    race_season = models.ForeignKey(RaceSeason, on_delete=models.CASCADE)
    race_name = models.CharField(max_length=100)
    race_date = models.DateField()
    race_finished = models.BooleanField(default=False)

    def __str__(self):
        return self.race_name


class Player(models.Model):
    player_name = models.CharField(max_length=100)
    player_email = models.EmailField()
    password = models.CharField(max_length=256)

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

    def __str__(self):
        return self.player.player_name + " " + str(self.score)


class RaceScore(models.Model):
    race = models.ForeignKey(Race, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    score = models.IntegerField()

    def __str__(self):
        return self.player.player_name + " " + str(self.score)
