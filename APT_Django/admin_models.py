from django.contrib import admin


class RaceCupAdmin(admin.ModelAdmin):
    list_display = ("cup_name", "cup_season")


class RaceAdmin(admin.ModelAdmin):
    list_display = ("race_name", "race_season", "race_cup", "cup_stage", "race_date")


class PlayerAdmin(admin.ModelAdmin):
    list_display = ("player_name", "player_email")


class PredictionAdmin(admin.ModelAdmin):
    list_display = ("player", "race")


class RaceScoreAdmin(admin.ModelAdmin):
    list_display = ("race", "player", "score")


class CupScoreAdmin(admin.ModelAdmin):
    list_display = ("cup", "player", "score")


class SeasonScoreAdmin(admin.ModelAdmin):
    list_display = ("season", "player", "score")
