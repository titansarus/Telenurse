# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth.models import User
from .forms import LoginForm, SignUpForm
from django.http import HttpResponseRedirect
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_protect

def init_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect("/")

    return render(request, "accounts/init-page.html", {})



@csrf_protect
def login_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect("/")

    form = LoginForm(request.POST or None)
    msg = None
    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                msg = "Invalid credentials"
        else:
            msg = "Error validating the form"

    return render(request, "accounts/login.html", {"form": form, "msg": msg})


@csrf_protect
def register_user(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect("/")

    msg = None
    success = False
    if request.method == "POST":
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            success = True
            msg = 'User created - please <a href="/login">login</a>.'
            # return redirect("/login/")
        else:
            msg = "Form is not valid"
    else:
        form = SignUpForm()

    return render(
        request,
        "accounts/register-test.html",
        {"form": form, "msg": msg, "success": success},
    )
