from django.contrib.gis import forms
from django_starfield import Stars

from apps.address.models import Address
from . import models


class AdForm(forms.ModelForm):
    """Create a form for registering an Ad"""

    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={'placeholder': "First name", 'class': "form-control"}
        )
    )

    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={'placeholder': "Last Name", 'class': "form-control"}
        )
    )

    phone_number = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                'placeholder': "Phone Number (+9123456789)",
                'class': "form-control"
            }
        ))

    address_details = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={'placeholder': "Address", 'class': "form-control"}
        )
    )

    start_time = forms.DateTimeField(
        required=True,
        widget=forms.DateTimeInput(
            attrs={
                'placeholder': "yyyy-mm-dd hh:mm",
                'class': "form-control datetimepicker-input",
            }
        )
    )

    end_time = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={
                'placeholder': "yyyy-mm-dd hh:mm",
                'class': "form-control datetimepicker-input",
            }
        )
    )

    # type of service which nurse must do
    service_type = forms.ChoiceField(
        required=True,
        choices=models.Ad.SERVICE_TYPES.choices
    )

    # patient gender
    gender = forms.ChoiceField(
        required=True,
        choices=models.Ad.GENDER.choices
    )

    # request urgency
    urgency = forms.ChoiceField(
        required=True,
        choices=models.Ad.URGENCY.choices
    )

    # description
    description = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={'placeholder': "Write your description here", 'class': "form-control"}
        )
    )

    address_location = forms.PointField(
        required=False,
        widget=forms.OSMWidget(attrs={'map_width': "auto", 'map_height': 300})
    )


    def save(self, commit=True):
        ad = super().save(commit=False)
        ad.address = Address.objects.create(details=self.cleaned_data['address_details'], location=self.cleaned_data['address_location'])
        if (creator := self.cleaned_data.get('creator', None)) is not None:
            ad.creator = creator
        ad.save()
        return ad

    class Meta:
        model = models.Ad
        fields = (
            "first_name",
            "last_name",
            "phone_number",
            "start_time",
            "end_time",
            "service_type",
            "gender",
            "urgency",
            "description",
        )


class AdReviewForm(forms.ModelForm):
    review = forms.CharField(
        widget=forms.Textarea(
            attrs={'placeholder': "Write your review here", 'class': "form-control"}
        )
    )

    score = forms.IntegerField(
        widget=Stars,
        max_value=5,
        min_value=0
    )

    class Meta:
        model = models.AdReview
        fields = (
            "review",
            "score",
        )
