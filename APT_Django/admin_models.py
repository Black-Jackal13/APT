from django.contrib import admin


class RaceAdmin(admin.ModelAdmin):
    list_display = ("race_name", "race_season", "race_date")


class PlayerAdmin(admin.ModelAdmin):
    list_display = ("player_name", "player_email")


class PredictionAdmin(admin.ModelAdmin):
    list_display = ("player", "race")


class RaceScoreAdmin(admin.ModelAdmin):
    list_display = ("race", "player", "score")


class SeasonScoreAdmin(admin.ModelAdmin):
    list_display = ("season", "player", "score")
