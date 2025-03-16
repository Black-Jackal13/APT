from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(RaceSeason)
admin.site.register(Race)
admin.site.register(Players)
admin.site.register(Predictions)
admin.site.register(RaceFinishers)
admin.site.register(SeasonScores)
admin.site.register(RaceScores)