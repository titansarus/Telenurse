# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
# from .forms import LoginForm, SignUpForm
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect


def ads_view(request):
    return render(request, 'ads/submit-ads.html', {})