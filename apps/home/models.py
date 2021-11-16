# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models


class Ad(models.Model):
    SERVICE_TYPES = (
        ("1", "مراقبت از سالمند"),
        ("2", "مراقبت از افراد کم توان"),
        ("3", "خدمات سرپایی"),
    )
    SEX = (("woman", "خانم"), ("man", "آقا"))
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=11)
    address = models.CharField(max_length=1000)
    start_time = models.DateField()
    end_time = models.DateField()
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES)
    sex = models.CharField(max_length=10, choices=SEX)

    objects = models.Manager()
    def __str__(self):
        return (
            f"Ad info: {self.address}, {self.phone_number}, {self.service_type}, {self.start_time} until "
            f"{self.end_time}"
        )


class NurseAd(models.Model):
    nurse_id = models.CharField(max_length=10000)
    ad_id = models.CharField(max_length=10000)
    current = models.BooleanField()
