from importlib.metadata import requires
from random import choice
from statistics import mode
from django.contrib.gis import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm, UserChangeForm
from apps.address.models import Address
from apps.ads import models

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


class BaseUserForm(forms.ModelForm):
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

    phone_number = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Phone Number (+9123456789)", "class": "form-control"}
        )
    )

    avatar = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput()
    )

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
            "phone_number",
            "avatar"
        )


class RegisterForm(BaseUserForm, UserCreationForm):
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

    class Meta:
        model = User
        fields = (*BaseUserForm.Meta.fields, "password1", "password2")


class NurseRegisterForm(RegisterForm):
    document = forms.FileField(
        widget=forms.ClearableFileInput(),
        label="Document",
        required=True,
        help_text="Maximum file size: 200MB",
        max_length=200,
    )

    expertise_level = forms.ChoiceField(
        choices=models.Nurse.EXPERTISE_LEVELS.choices, required=True)

    class Meta:
        model = Nurse
        fields = (
            *RegisterForm.Meta.fields,
            "document",
            "expertise_level",
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


class ActivationForm(forms.Form):
    uid = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "uid", "class": "form-control"}
        )
    )
    token = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "Token", "class": "form-control"}
        )
    )


class UpdateProfileForm(BaseUserForm, UserChangeForm):
    username = forms.CharField(
        disabled=True,
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder": "Username", "class": "form-control"}
        )
    )

    address_details = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={'placeholder': "Address", 'class': "form-control"}
        )
    )

    address_location = forms.PointField(
        required=False,
        widget=forms.OSMWidget(attrs={'map_width': 400, 'map_height': 300})
    )

    def save(self, commit=True):
        address = Address.objects.create(
            details=self.cleaned_data['address_details'], location=self.cleaned_data['address_location'])
        user = super().save(commit=False)
        user.address = address
        user.save()
        return user


class NurseUpdateProfileForm(UpdateProfileForm, UserChangeForm):
    expertise_level = forms.ChoiceField(
        choices=models.Nurse.EXPERTISE_LEVELS.choices, required=True)

    class Meta:
        model = Nurse
        fields = (
            *UpdateProfileForm.Meta.fields,
            "expertise_level",
        )




