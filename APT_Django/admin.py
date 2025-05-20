from django.contrib import admin
from .models import *
from .admin_models import *

# Register your models here.
admin.site.register(RaceSeason)
admin.site.register(RaceCup, RaceCupAdmin)
admin.site.register(Race, RaceAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Prediction, PredictionAdmin)
admin.site.register(RaceFinisher)
admin.site.register(SeasonScore, SeasonScoreAdmin)
admin.site.register(CupScore, CupScoreAdmin)
admin.site.register(RaceScore, RaceScoreAdmin)
