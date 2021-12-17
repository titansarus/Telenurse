# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from ..users.models import Nurse

User = get_user_model()


class Ad(models.Model):
    class SERVICE_TYPES(models.TextChoices):
        ELDERLY = '1', _('Elderly care')
        DISABLILITY = '2', _('Caring for people with disabilities')
        OUTPATIENT = '3', _('Outpatient services')

    class GENDER(models.TextChoices):
        WOMAN = 'W', _('Woman')
        MAN = 'M', _('Man')

    class URGENCY(models.TextChoices):
        URGENT = '1', _('Urgent')
        NON_URGENT = '0', _('Non-urgent')

    creator = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=2, choices=GENDER.choices)
    phone_number = models.CharField(max_length=11)
    address = models.CharField(max_length=1000)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    service_type = models.CharField(
        max_length=2, choices=SERVICE_TYPES.choices)
    urgency = models.CharField(default=URGENCY.NON_URGENT, max_length=2, choices=URGENCY.choices)
    description = models.CharField(max_length=500)
    accepted = models.BooleanField(default=False)

    def __str__(self):
        return (
            f"Ad info: {self.address}, {self.phone_number}, {self.service_type}, {self.start_time} until "
            f"{self.end_time}"
        )


class NurseAd(models.Model):
    class STATUS(models.TextChoices):
        ACCEPTED = 'A', _('Accepted')
        STARTED = 'S', _('Started')
        FINISHED = 'F', _('Finished')

    nurse = models.ForeignKey(Nurse, on_delete=models.CASCADE)
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=2, choices=STATUS.choices, default=STATUS.ACCEPTED)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nurse_id}-{self.ad_id}-{self.status}"
