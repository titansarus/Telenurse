# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from typing import Tuple

import sweetify
from django.contrib.auth import authenticate, get_user_model, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect

from ..ads.views import is_user_nurse
from .models import Nurse
from .forms import LoginForm, RegisterForm, NurseRegisterForm, ChangePasswordForm

User = get_user_model()

USERNAME_EXISTS_ERROR_MSG = 'This username has already been taken. Please choose another username.'
EMAIL_EXISTS_ERROR_MSG = 'This Email has already been registered. Please choose another Email or login with previous account.'
PHONE_EXISTS_ERROR_MSG = 'This phone number has already been registered. Please choose another phone number or login with previous account.'
PASSWORD_CHANGE_SUCCESS_MSG = 'Your password was successfully updated!'
PASSWORD_CHANGE_ERROR_MSG = 'Please correct the errors in form.'


def init_view(request):
    """Page for choosing whether to login or submit an ad."""
    if request.user.is_authenticated:
        return HttpResponseRedirect("/")

    return render(request, 'accounts/init-page.html', {})


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
                msg = "Invalid credentials"

            except User.DoesNotExist:
                msg = "User with this username does not exist."
                return render(request, 'accounts/login.html', {'form': form, 'msg': msg})
        else:
            msg = "Error while validating the form"

    return render(request, 'accounts/login.html', {'form': form, 'msg': msg})


def check_user_exists(form_data) -> Tuple[bool, str]:
    if User.objects.filter(username=form_data['username']).exists():
        return True, USERNAME_EXISTS_ERROR_MSG
    if User.objects.filter(email=form_data['email']).exists():
        return True, EMAIL_EXISTS_ERROR_MSG
    if User.objects.filter(phone_number=form_data['phone_number']).exists():
        return True, PHONE_EXISTS_ERROR_MSG

    return False, ""


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

        user_exists, msg = check_user_exists(form.data)

        if not user_exists:
            if form.is_valid():
                form.save()
                success = True
                msg = "User created - please <a href='/login'>login</a>."
            else:
                msg = "Form is not valid."
    else:
        form = NurseRegisterForm() if is_nurse_form else RegisterForm()

    return render(
        request,
        'accounts/register.html',
        {'form': form, 'msg': msg, 'success': success, 'is_nurse_form': is_nurse_form},
    )


@login_required(login_url='/login/')
def nurse_list_view(request):
    nurses = [nurse for nurse in Nurse.objects.all()]
    return render(request, 'home/nurse-list.html', {'nurses': nurses})


@login_required(login_url='/login/')
@csrf_protect
def user_profile_view(request):
    def is_password_form(query_dict):
        return 'old_password' in query_dict

    password_form = ChangePasswordForm(request.user)
    profile_form = None

    if request.method == 'POST':
        if is_password_form(request.POST):
            password_form = ChangePasswordForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                sweetify.success(request, title='Success', text=PASSWORD_CHANGE_SUCCESS_MSG, timer=None)
            else:
                sweetify.error(request, title='Error', text=PASSWORD_CHANGE_ERROR_MSG, timer=None)
        else:
            pass  # TODO handle edit profile form

    context = {'password_form': password_form, 'profile_form': profile_form, 'is_nurse': is_user_nurse(request.user)}
    return render(request, 'home/user-profile.html', context)
