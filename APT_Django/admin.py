from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(RaceSeason)
admin.site.register(Race)
admin.site.register(Player)
admin.site.register(Prediction)
admin.site.register(RaceFinisher)
admin.site.register(SeasonScore)
admin.site.register(RaceScore)