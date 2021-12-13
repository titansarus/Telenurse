# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from ..users.forms import LoginForm, RegisterForm, NurseRegisterForm
from .models import Nurse

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
        return HttpResponseRedirect('/')

    form = LoginForm(request.POST or None)
    msg = None

    # Check if request is for posting username and password
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            try:
                # Checks if user exists with input username in form
                user = authenticate(username=username, password=password)

                if user is not None:
                    login(request, user)
                    return redirect('/')  # in case user does not exist or password is invalid
                msg = 'Invalid credentials'

            except User.DoesNotExist:
                msg = 'User with this username does not exist.'
                return render(request, 'accounts/login.html', {'form': form, 'msg': msg})
        else:
            msg = 'Error while validating the form'

    return render(request, 'accounts/login.html', {'form': form, 'msg': msg})


@csrf_protect
def register_view(request):
    """View for registering user."""
    if request.user.is_authenticated:
        return HttpResponseRedirect('/')

    msg = None
    success = False
    is_nurse_form = request.GET.get('type', 'nurse') == 'nurse'
    if request.method == 'POST':
        form = NurseRegisterForm(request.POST, request.FILES) if is_nurse_form else RegisterForm(request.POST)

        try:
            user = User.objects.get(username=form.data['username'])
            if user:
                msg = 'This username has already been taken. Please choose another username.'
        except User.DoesNotExist:
            if form.is_valid():
                form.save()
                success = True
                msg = 'User created - please <a href="/login">login</a>.'
            else:
                msg = 'Form is not valid.'
    else:
        form = NurseRegisterForm() if is_nurse_form else RegisterForm()

    return render(
        request,
        'accounts/register.html',
        {'form': form, 'msg': msg, 'success': success, 'is_nurse_form': is_nurse_form},
    )


@login_required(login_url="/login/")
def nurse_list_view(request):
    nurses = [nurse for nurse in Nurse.objects.all()]
    return render(request, "home/nurse-list.html", {"nurses": nurses})
