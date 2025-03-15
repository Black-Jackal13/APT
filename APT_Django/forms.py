from django import forms


class EnterPrediction(forms.Form):
    player_name = forms.CharField(max_length=100)
    prediction_1 = forms.CharField(max_length=100)
    prediction_2 = forms.CharField(max_length=100)
    prediction_3 = forms.CharField(max_length=100)
