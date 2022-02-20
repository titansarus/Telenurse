from typing import Tuple

import sweetify
from django.contrib.auth import authenticate, get_user_model, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.db.models.aggregates import Avg
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.decorators.csrf import csrf_protect
from django.contrib.gis.geos import Point

from .forms import LoginForm, RegisterForm, NurseRegisterForm, ChangePasswordForm, UpdateProfileForm
from .models import Nurse
from .token import account_activation_token
from ..ads.models import AdReview
from ..users.permission_checks import is_user_admin, is_user_nurse

User = get_user_model()

USERNAME_EXISTS_ERROR_MSG = "This username has already been taken. Please choose another username."
EMAIL_EXISTS_ERROR_MSG = "This Email has already been registered. Please choose another Email or login with previous account."
PHONE_EXISTS_ERROR_MSG = "This phone number has already been registered. Please choose another phone number or login with previous account."
PASSWORD_CHANGE_SUCCESS_MSG = "Your password was successfully updated!"
PROFILE_UPDATE_SUCCESS_MSG = "Your profile was successfully updated!"
FORM_ERROR_MSG = "Please correct the errors in form."
USER_ID_DOES_NOT_EXIST = "User ID doesn't exist."


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


def check_info_uniqueness(form_data, cur_user_id) -> Tuple[bool, str]:
    users = User.objects.filter(email=form_data['email'])
    if users.exists() and users.first().id != cur_user_id:
        return False, EMAIL_EXISTS_ERROR_MSG
    users = User.objects.filter(phone_number=form_data['phone_number'])
    if users.exists() and users.first().id != cur_user_id:
        return False, PHONE_EXISTS_ERROR_MSG

    return True, ""


@csrf_protect
def register_view(request):
    """View for registering user."""
    if request.user.is_authenticated:
        return HttpResponseRedirect('/')

    msg = None
    success = False
    is_nurse_form = request.GET.get('type', 'nurse') == 'nurse'
    if request.method == 'POST':
        form = NurseRegisterForm(request.POST, request.FILES) if is_nurse_form else RegisterForm(request.POST, request.FILES)

        user_exists, msg = check_user_exists(form.data)

        if not user_exists:
            if form.is_valid():
                user= form.save(commit=False)
                user.is_active = False
                user.save()
                current_site = get_current_site(request)
                mail_subject = 'Activation link has been sent to your email id'
                message = render_to_string('accounts/activate_email_account.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                    'token':account_activation_token.make_token(user),
                })
                to_email = form.cleaned_data.get('email')
                email = EmailMessage(
                    mail_subject, message, to=[to_email]
                )
                email.send()
                success = True
                msg = "User created - please activate your account. <a href='/login'>login</a>."
            else:
                msg = "Form is not valid."
    else:
        form = NurseRegisterForm() if is_nurse_form else RegisterForm()

    return render(
        request,
        'accounts/register.html',
        {'form': form, 'msg': msg, 'success': success, 'is_nurse_form': is_nurse_form},
    )

@csrf_protect
def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')

@login_required(login_url='/login/')
@user_passes_test(is_user_admin)
def nurse_list_view(request):
    nurses = []
    for nurse in Nurse.objects.all():
        reviews = AdReview.objects.filter(nurse_ad__nurse=nurse)
        if reviews:
            average = reviews.filter(score__gt=0).aggregate(average=Avg('score'))
            nurse.average = average['average']
        else:
            nurse.average = 0
        nurses.append(nurse)
    return render(request, 'home/nurse-list.html', {'nurses': nurses})


@login_required(login_url='/login/')
@csrf_protect
def user_profile_view(request):
    initial = {}
    if request.user.address:
        initial={'address_details': request.user.address.details, 'address_location': request.user.address.location }
    
    initial['address_location'] = initial.get('address_location', None) or Point(51.3890, 35.6892, srid=4326)
    
    profile_form = UpdateProfileForm(instance=request.user, initial=initial)

    if request.method == 'POST':
        profile_form = UpdateProfileForm(request.POST, request.FILES,  instance=request.user)
        is_info_unique, msg = check_info_uniqueness(profile_form.data, request.user.id)
        if not is_info_unique:
            sweetify.error(request, title='Error', text=msg)
        elif profile_form.is_valid():
            profile_form.save()
            sweetify.success(request, title='Success', text=PROFILE_UPDATE_SUCCESS_MSG, timer=None)
        else:
            sweetify.error(request, title='Error', text=FORM_ERROR_MSG, timer=None)

    context = {'profile_form': profile_form, 'is_nurse': is_user_nurse(request.user)}
    return render(request, 'home/user-profile.html', context)


@login_required(login_url='/login/')
@csrf_protect
def change_password_view(request):
    password_form = ChangePasswordForm(request.user)

    if request.method == 'POST':
        password_form = ChangePasswordForm(request.user, request.POST)
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            sweetify.success(request, title='Success', text=PASSWORD_CHANGE_SUCCESS_MSG, timer=None)
        else:
            sweetify.error(request, title='Error', text=FORM_ERROR_MSG, timer=None)

    context = {'password_form': password_form, 'is_nurse': is_user_nurse(request.user)}
    return render(request, 'home/change-password.html', context)


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = reverse_lazy('login')
