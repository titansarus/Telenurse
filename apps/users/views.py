from importlib.metadata import requires
from typing import Tuple

import sweetify
from django.contrib.auth import authenticate, get_user_model, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import PasswordResetView
from django.contrib.gis.geos import Point
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.db.models.aggregates import Avg
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes, force_text
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.decorators.csrf import csrf_protect

from apps.ads import models
from .forms import LoginForm, RegisterForm, NurseRegisterForm, ChangePasswordForm, UpdateProfileForm, ActivationForm
from .forms import NurseUpdateProfileForm
from .models import Nurse
from .token import account_activation_token
from ..ads.models import AdReview, NurseAd, Ad
from ..users.permission_checks import is_user_admin, is_user_nurse

User = get_user_model()

USERNAME_EXISTS_ERROR_MSG = "This username has already been taken. Please choose another username."
EMAIL_EXISTS_ERROR_MSG = "This Email has already been registered. Please choose another Email or login with previous account."
PHONE_EXISTS_ERROR_MSG = "This phone number has already been registered. Please choose another phone number or login with previous account."
PASSWORD_CHANGE_SUCCESS_MSG = "Your password was successfully updated!"
PROFILE_UPDATE_SUCCESS_MSG = "Your profile was successfully updated!"
FORM_ERROR_MSG = "Please correct the errors in form."
USER_ID_DOES_NOT_EXIST = "User ID doesn't exist."
USER_NOT_ACTIVE_ON_REGISTER = "User is not activated yet"
ACTIVATE_ACCOUNT_ON_LOGIN = "Please activate account!"
INVALID_CREDENTIALS = "Invalid credentials"
USER_DOES_NOT_EXIST = "User with this username does not exist."
ERROR_VALIDATING_FORM = "Error while validating the form"
ACTIVATION_LINK_INVALID = "Activation link is invalid!"
PLEASE_ACTIVATE_MANUALLY = "Please activate manually using token and uid sent in the Email."
EMAIL_ACTIVATE_SUCESS = "Thank you for your email confirmation. Now you can log in to your account."
USER_CREATED_PLEASE_ACTIVATE = "User created - please activate your account using the link sent to the email."
ACTIVATION_EMAIL_HEADER = "Telenurse: Activation link has been sent to your Email"


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
    msg = request.session.pop('msg', None)

    # Check if request is for posting username and password
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            try:
                # Checks if user exists with input username in form
                user = authenticate(username=username, password=password)

                if user is not None:
                    if user.is_active:
                        login(request, user)
                        return redirect('/')
                    # if user is not activate
                    msg = ACTIVATE_ACCOUNT_ON_LOGIN
                else:
                    msg = INVALID_CREDENTIALS  # In case user does not exist or password is invalid

            except User.DoesNotExist:
                msg = "User with this username does not exist."
                return render(request, 'accounts/login.html', {'form': form, 'msg': msg})
        else:
            msg = "Error while validating the form"

    return render(request, 'accounts/login.html', {'form': form, 'msg': msg})


@csrf_protect
def activate_manually_view(request):
    """View to login from, by entering username and password."""
    if request.user.is_authenticated:
        return HttpResponseRedirect('/')

    form = ActivationForm(request.POST or None)
    msg = request.session.pop('msg', None)

    # Check if request is for posting username and password
    if request.method == 'POST':
        if form.is_valid():
            uid = form.cleaned_data.get('uid')
            token = form.cleaned_data.get('token')
            return activate(request, uid, token)

        msg = ERROR_VALIDATING_FORM

    return render(request, 'accounts/activate_manual.html', {'form': form, 'msg': msg})


def check_user_exists(form_data) -> Tuple[bool, str, User]:
    user = User.objects.filter(username=form_data['username'])
    if user.exists():
        return True, USERNAME_EXISTS_ERROR_MSG, user.first()

    user = User.objects.filter(email=form_data['email'])
    if user.exists():
        return True, EMAIL_EXISTS_ERROR_MSG, user.first()

    user = User.objects.filter(phone_number=form_data['phone_number'])
    if user.exists():
        return True, PHONE_EXISTS_ERROR_MSG, user.first()

    return False, "", None


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
        form = NurseRegisterForm(request.POST, request.FILES) if is_nurse_form else RegisterForm(request.POST,
                                                                                                 request.FILES)
        user_exists, msg, user = check_user_exists(form.data)
        if not user_exists:
            if form.is_valid():
                success = send_activation_email(form, request)
                msg = USER_CREATED_PLEASE_ACTIVATE
            else:
                msg = ERROR_VALIDATING_FORM
        elif not user.is_active:
            msg = USER_NOT_ACTIVE_ON_REGISTER
    else:
        form = NurseRegisterForm() if is_nurse_form else RegisterForm()

    return render(
        request,
        'accounts/register.html',
        {'form': form, 'msg': msg, 'success': success, 'is_nurse_form': is_nurse_form},
    )


def send_activation_email(form, request):
    user = form.save(commit=False)
    user.is_active = False
    user.save()
    current_site = get_current_site(request)
    mail_subject = ACTIVATION_EMAIL_HEADER
    html_message = render_to_string('accounts/activate_email_account.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': request.scheme
    })
    plain_message = strip_tags(html_message)
    to_email = form.cleaned_data.get('email')
    email = EmailMultiAlternatives(
        mail_subject, plain_message, to=[to_email],
    )
    email.attach_alternative(html_message, "text/html")
    email.send()
    success = True
    return success


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
        request.session['msg'] = EMAIL_ACTIVATE_SUCESS
        return redirect('login')
    else:
        request.session['msg'] = ACTIVATION_LINK_INVALID + " " + PLEASE_ACTIVATE_MANUALLY
        return redirect('activate-manual')


@login_required(login_url='/login/')
def nurse_list_view(request):
    nurses = []
    for nurse in Nurse.objects.all():
        reviews = AdReview.objects.filter(nurse_ad__nurse=nurse)
        if reviews:
            average = reviews.filter(
                score__gt=0).aggregate(average=Avg('score'))
            nurse.average = average['average']
        else:
            nurse.average = 0
        nurse.expertise_level = models.Nurse.EXPERTISE_LEVELS(
            nurse.expertise_level).label
        nurses.append(nurse)
    return render(request, 'home/nurse-list.html', {'nurses': nurses})

@login_required(login_url='/login/')
def nurse_detail_view(request):
    n_username = request.GET.get('username')
    n_id = get_object_or_404(Nurse, username=n_username)
    ads_ids = [e.ad_id for e in NurseAd.objects.filter(nurse_id=n_id).all().iterator()]
    ads = Ad.objects.filter(id__in=ads_ids).all()

    context = {'nurse_ads': ads, 'is_admin': is_user_admin(request.user)}
    return render(request, 'home/nurse-detail.html', context)

@login_required(login_url='/login/')
@csrf_protect
def user_profile_view(request):
    initial = {}
    if request.user.address:
        initial = {'address_details': request.user.address.details,
                   'address_location': request.user.address.location}
    initial['address_location'] = initial.get(
        'address_location', None) or Point(51.3890, 35.6892, srid=4326)

    is_nurse = is_user_nurse(request.user)
    if is_nurse:
        profile_form = NurseUpdateProfileForm(
            instance=request.user, initial=initial)
        nurse = get_object_or_404(Nurse, id=request.user.id)
        profile_form.expertise_level_value = Nurse.EXPERTISE_LEVELS(
            nurse.expertise_level).label
    else:
        profile_form = UpdateProfileForm(
            instance=request.user, initial=initial)

    if request.method == 'POST':
        if is_nurse:
            profile_form = NurseUpdateProfileForm(
                request.POST, request.FILES, instance=nurse)
        else:
            profile_form = UpdateProfileForm(
                request.POST, request.FILES, instance=request.user)
        is_info_unique, msg = check_info_uniqueness(
            profile_form.data, request.user.id)
        if not is_info_unique:
            sweetify.error(request, title='Error', text=msg)
        elif profile_form.is_valid():
            profile_form.save()
            sweetify.success(request, title='Success',
                             text=PROFILE_UPDATE_SUCCESS_MSG, timer=None)
        else:
            sweetify.error(request, title='Error',
                           text=FORM_ERROR_MSG, timer=None)

    context = {'profile_form': profile_form,
               'is_nurse': is_user_nurse(request.user)}
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
            sweetify.success(request, title='Success',
                             text=PASSWORD_CHANGE_SUCCESS_MSG, timer=None)
        else:
            sweetify.error(request, title='Error',
                           text=FORM_ERROR_MSG, timer=None)

    context = {'password_form': password_form,
               'is_nurse': is_user_nurse(request.user)}
    return render(request, 'home/change-password.html', context)


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = reverse_lazy('login')
