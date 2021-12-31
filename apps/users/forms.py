# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm

from apps.users.models import Nurse

User = get_user_model()


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "Username", "class": "form-control"}
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "Password", "class": "form-control"}
        )
    )

    class Meta:
        model = User
        fields = (
            "username",
            "password",
        )


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder": "First Name", "class": "form-control"}
        )
    )

    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder": "Last Name", "class": "form-control"}
        )
    )

    username = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder": "Username", "class": "form-control"}
        )
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={"placeholder": "Email", "class": "form-control"})
    )
    password1 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={"placeholder": "Password", "class": "form-control"}
        )
    )
    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={"placeholder": "Confirm Password", "class": "form-control"}
        )
    )
    phone_number = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Phone Number (+9123456789)", "class": "form-control"}
        )
    )

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
            "password1",
            "password2",
            "phone_number",
        )


class NurseRegisterForm(RegisterForm):
    document = forms.FileField(
        widget=forms.ClearableFileInput(),
        label="Document",
        required=True,
        help_text="Maximum file size: 200MB",
        max_length=200,
    )

    class Meta:
        model = Nurse
        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
            "password1",
            "password2",
            "phone_number",
            "document",
        )


class ChangePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = User
        fields = (
            "old_password",
            "new_password1",
            "new_password2",
        )

class UpdateProfileForm(forms.Form):
    username = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder": "Username", "class": "form-control"}
        )
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={"placeholder": "Email", "class": "form-control"})
    )

    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder": "First Name", "class": "form-control"}
        )
    )

    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder": "Last Name", "class": "form-control"}
        )
    )

    phone_number = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Phone Number (+9123456789)", "class": "form-control"}
        )
    )

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "phone_number",
        )    
