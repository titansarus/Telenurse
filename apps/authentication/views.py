# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# from users.backends import SettingsBackend.authenticate as authenticate

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth.models import User
from .forms import LoginForm, SignUpForm
from django.http import HttpResponseRedirect
# from apps.users.models import CustomUser
from django.contrib.auth import get_user_model

User = get_user_model()


def init_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect("/")

    User = get_user_model()
    users = User.objects.all()
    print("++++++++++ users:", users)
    return render(request, "accounts/init-page.html", {})


def login_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect("/")

    form = LoginForm(request.POST or None)
    msg = None
    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            print("++++++++++ username & password:", username, password)
            user = authenticate(username=username, password=password)
            first_user = User.objects.all()[0]
            all_users = User.objects.all()
            print("----- hereeeeee", user, first_user)
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                msg = "Invalid credentials"
        else:
            msg = "Error validating the form"

    return render(request, "accounts/login.html", {"form": form, "msg": msg})


def register_user(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect("/")

    msg = None
    success = False
    if request.method == "POST":
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            userr = form.save()
            print("()()()()", userr)
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)
            msg = 'User created - please <a href="/login">login</a>.'
            success = True
            # return redirect("/login/")
        else:
            msg = "Form is not valid"
    else:
        form = SignUpForm()

    return render(
        request,
        "accounts/register.html",
        {"form": form, "msg": msg, "success": success},
    )
