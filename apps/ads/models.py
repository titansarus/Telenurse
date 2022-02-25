from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from ..users.models import Nurse
from ..address.models import Address

import geopy.distance

User = get_user_model()

BASE_PRICE = 500_000
TIME_DELTA_PRICE = 2_000_000
SERVICE_TYPE_BASE_PRICE = 500_000
HQ_COORD = (35.698747319698185, 51.35545136082422)
KILOMETER_BASE_PRICE = 100_000
MAX_DISTANCE_PRICE = 2_000_000
MIN_DISTANCE_PRICE = 0


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
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"Ad info: {self.address}, {self.phone_number}, {self.service_type}, {self.start_time} until "
            f"{self.end_time}"
        )

    @property
    def price(self):
        delta = self.end_time - self.start_time
        service_type_coeff = service_type_coefficient[self.service_type]
        urgency_coeff = urgency_coeffecient[self.urgency]
        distance_price = 0
        if self.address:
            coord1 = (self.address.location[1],self.address.location[0])
            distance = geopy.distance.distance(coord1, HQ_COORD).km
            distance_price = distance * KILOMETER_BASE_PRICE
        distance_price = round(min(max(MIN_DISTANCE_PRICE, distance_price), MAX_DISTANCE_PRICE))
        return urgency_coeff * (
                BASE_PRICE + TIME_DELTA_PRICE * delta.days + SERVICE_TYPE_BASE_PRICE * service_type_coeff + distance_price)


service_type_coefficient = {
    Ad.SERVICE_TYPES.ELDERLY.value: 3,
    Ad.SERVICE_TYPES.DISABLILITY.value: 3,
    Ad.SERVICE_TYPES.OUTPATIENT.value: 0,
    Ad.SERVICE_TYPES.INJECTION.value: 1,
    Ad.SERVICE_TYPES.BLOOD.value: 2,
    Ad.SERVICE_TYPES.PCR.value: 1
}

urgency_coeffecient = {
    Ad.URGENCY.NON_URGENT.value: 1,
    Ad.URGENCY.URGENT.value: 2,
}


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
