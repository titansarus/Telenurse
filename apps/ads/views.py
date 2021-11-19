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


def ads_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/')

    msg = None
    success = False
    # if we want to post a form
    if request.method == 'POST':
        form = AdForm(request.POST)
        # check whether the form is valid
        if form.is_valid():
            form.save()
            success = True
            msg = 'Your request has been created. Our Nurses will call you soon.'
        # if is invalid
        else:
            msg = 'Form is not valid.'

    # if we want to get a form
    else:
        form = AdForm()

    return render(request, 'ads/submit-ads.html', {'form': form, 'msg': msg, 'success': success})
