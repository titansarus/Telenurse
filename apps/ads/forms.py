# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import forms
from . import models


class AdForm(forms.ModelForm):
    """Create a form for registering an Ad"""

    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder": "First name", "class": "form-control"}
        )
    )

    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder": "Last Name", "class": "form-control"}
        )
    )

    phone_number = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Phone Number (+9999999999)",
                "class": "form-control"
            }
        ))

    address = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder": "Address", "class": "form-control"}
        )
    )

    start_time = forms.DateTimeField(
        required=True,
        widget=forms.DateTimeInput(
            attrs={
                "placeholder": "yyyy-mm-dd hh:mm",
                "class": "form-control datetimepicker-input",
            }
        )
    )

    end_time = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={
                "placeholder": "yyyy-mm-dd hh:mm",
                "class": "form-control datetimepicker-input",
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

    class Meta:
        model = models.Ad
        fields = (
            "first_name",
            "last_name",
            "phone_number",
            "address",
            "start_time",
            "end_time",
            "service_type",
            "gender",
        )