# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import AdForm
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from .forms import AdForm


def ads_view(request):

    if request.user.is_authenticated:
        return HttpResponseRedirect('/')
    if request.method == "POST":
        pass
    form = AdForm()

    return render(request, 'ads/submit-ads.html', {"form": form})
