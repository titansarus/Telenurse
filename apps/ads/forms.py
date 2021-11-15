# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import forms

SERVICE_TYPES = (
    ('1', 'Elderly care'),
    ('2', 'Caring for people with disabilities'),
    ('3', 'Outpatient services')
)
SEX = (
    ('woman', 'Woman'),
    ('man', 'Man')
)


class AdForm(forms.Form):
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
                "placeholder": "Start Time",
                "class": "form-control"
            }
        ))

    end_time = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "placeholder": "End Time",
                "class": "form-control"
            }
        ))

    # todo: check this shits
    service_type = forms.ChoiceField(
        choices=SERVICE_TYPES,
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
