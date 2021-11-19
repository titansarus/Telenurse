# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib.auth import login
from .forms import LoginForm, SignUpForm
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import get_user_model

User = get_user_model()

def init_view(request):
    """Page for choosing whether to login or submit an ad."""
    if request.user.is_authenticated:
        return HttpResponseRedirect("/")

    return render(request, "accounts/init-page.html", {})

@csrf_protect
def login_view(request):
    """View to login from, by entering username and password."""
    if request.user.is_authenticated:
        return HttpResponseRedirect("/")

    form = LoginForm(request.POST or None)
    msg = None
    # Check if request is for posting username and password
    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            
            # check whether the user exists in the database and password is valid for that username
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                return redirect("/")
            # in case user does not exist or password is invalid
            else:
                msg = "Invalid credentials"
        else:
            msg = "Error validating the form"

    return render(request, "accounts/login.html", {"form": form, "msg": msg})


@csrf_protect
def register_user(request):
    """View for registering user."""
    if request.user.is_authenticated:
        return HttpResponseRedirect('/')


    msg = None
    success = False
    if request.method == "POST":
        form = SignUpForm(request.POST, request.FILES)
        # check form has valid parts

        user = User.objects.get(username=form.data['username'])
        if user:
            msg = "This username has already been taken. Please choose another username."
        elif form.is_valid():
            form.save()
            success = True
            msg = 'User created - please <a href="/login">login</a>.'
        else:
            msg = "Form is not valid"
            print("password2 errors:", form.errors['password2'])
    else:
        form = SignUpForm()

    return render(
        request,
        "accounts/register.html",
        {"form": form, "msg": msg, "success": success},
    )
