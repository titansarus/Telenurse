# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models


# Create your models here.

class Nurse(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    document = models.FileField(upload_to='documents/%Y/%m/%d')
    location = models.CharField(max_length=1000, blank=True)
    phone_number = models.CharField(max_length=11)

    def __str__(self):
        return f'Nurse with username {self.username} info: {self.first_name} {self.last_name}, {self.email}, ' \
               f'{self.phone_number}'


