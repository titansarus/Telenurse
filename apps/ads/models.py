from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from ..users.models import Nurse
from ..address.models import Address

User = get_user_model()


class Ad(models.Model):
    class SERVICE_TYPES(models.TextChoices):
        ELDERLY = '1', _('Elderly care')
        DISABLILITY = '2', _('Caring for people with disabilities')
        OUTPATIENT = '3', _('Outpatient services'),
        INJECTION = '4', _('Injection services'),
        BLOOD = '5', _('Blood test'),
        PCR = '6', _('PCR test'),

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
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    service_type = models.CharField(
        max_length=2, choices=SERVICE_TYPES.choices)
    urgency = models.CharField(default=URGENCY.NON_URGENT, max_length=2, choices=URGENCY.choices)
    description = models.CharField(max_length=500, blank=True)
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


class AdReview(models.Model):
    nurse_ad = models.OneToOneField(NurseAd, on_delete=models.CASCADE, related_name='review')
    score = models.IntegerField(default=0, validators=[MaxValueValidator(5), MinValueValidator(0)])
    review = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nurse_ad.nurse_id}-{self.nurse_ad.ad.creator_id}-{self.score}-{self.review}"
