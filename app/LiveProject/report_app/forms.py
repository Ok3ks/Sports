from django import forms

class playerForm(forms.Form):
    player_id = forms.IntegerField(required= True)

class leagueForm(forms.Form):
    league_id = forms.IntegerField(required=True)