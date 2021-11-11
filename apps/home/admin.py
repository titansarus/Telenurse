# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin

from .models import Nurse, Ad

# Register your models here.
admin.site.register(Nurse)
admin.site.register(Ad)
