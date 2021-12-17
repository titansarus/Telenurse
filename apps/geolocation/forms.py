from django import forms


class TrackingPointForm(forms.Form):
    timestamp = forms.IntegerField()
    ad_id = forms.IntegerField()
    altitude = forms.FloatField(required=False)
    altitude_accuracy = forms.FloatField(required=False)

    accuracy = forms.FloatField(required=False)
    latitude = forms.FloatField()
    longitude = forms.FloatField()
