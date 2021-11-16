from django import forms


class TrackingPointForm(forms.Form):
    username = forms.CharField(max_length=200)
    timestamp = forms.IntegerField()
    ad_id = forms.IntegerField()
    altitude = forms.FloatField(required=False)
    altitude_accuracy = forms.FloatField(required=False)

    accuracy = forms.FloatField(required=False)
    latitude = forms.FloatField()
    longitude = forms.FloatField()


class StopTrackingForm(forms.Form):
    ad_id = forms.IntegerField()
