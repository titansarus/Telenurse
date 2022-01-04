from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm, UserChangeForm

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

    class Meta:
        model = Nurse
        fields = (*RegisterForm.Meta.fields, "document")


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


class UpdateProfileForm(BaseUserForm, UserChangeForm):
    username = forms.CharField(
        disabled=True,
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder": "Username", "class": "form-control"}
        )
    )
