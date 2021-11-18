# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import forms
from ..home import models
from django.utils import timezone

SERVICE_TYPES = (
    ('1', 'Elderly care'),
    ('2', 'Caring for people with disabilities'),
    ('3', 'Outpatient services')
)
SEX = (
    ('woman', 'Woman'),
    ('man', 'Man')
)


def past_years(ago):
    this_year = timezone.now().year
    return list(range(this_year, this_year - ago - 1))


class AdForm(forms.ModelForm):
    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "First name",
                "class": "form-control"
            }
        ))

    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Last Name",
                "class": "form-control"
            }
        ))

    phone_number = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Phone Number",
                "class": "form-control"
            }
        ))

    address = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Address",
                "class": "form-control"
            }
        ))

    start_time = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "placeholder": "yyyy-mm-dd",
                "class": "form-control datetimepicker-input"
            }
        )
    )

    end_time = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "placeholder": "yyyy-mm-dd",
                "class": "form-control datetimepicker-input"
            }
        ))

    service_type = forms.ChoiceField(
        choices=SERVICE_TYPES, required=True
        # widget=forms.CheckboxInput(
        #     attrs={
        #         "placeholder": "Service Type",
        #         "class": "form-control"
        #     }
        # )

    )

    sex = forms.ChoiceField(
        choices=SEX,
        # widget=forms.CheckboxInput(
        #     attrs={
        #         "placeholder": "Sex",
        #         "class": "form-control"
        #     }
        # )
    )

    class Meta:
        model = models.Ad
        fields = ('first_name', 'last_name', 'phone_number', 'address', 'start_time', 'end_time', 'service_type', 'sex')
