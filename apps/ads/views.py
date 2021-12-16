# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import sweetify
from django import template
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.urls import reverse

from apps.ads.forms import AdForm
from .models import Ad, NurseAd
from ..users.models import Nurse, CustomUser


def is_user_nurse(user):
    return Nurse.objects.filter(username=user.username).count() == 1


def is_user_custom_user(user):
    return CustomUser.objects.filter(username=user.username).count() == 1


@login_required(login_url='/login/')
def index(request):
    context = {'segment': 'index', 'is_nurse': is_user_nurse(request.user)}
    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url='/login/')
def pages(request):
    context = {'is_nurse': is_user_nurse(request.user)}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]
        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))

        context['segment'] = load_template
        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))


@login_required(login_url='/login/')
def requests_list(request):
    """Show list of all ads"""
    is_nurse = is_user_nurse(request.user)
    if request.user.is_superuser:
        ads = list(Ad.objects.all())
    elif is_nurse:
        ads = [ad for ad in Ad.objects.all() if not ad.accepted]
    else:
        ads = Ad.objects.filter(creator_id=request.user.id)

    context = {'user_requests': ads, 'is_nurse': is_nurse}

    return render(request, 'home/requests-list.html', context)


@login_required(login_url='/login/')
@user_passes_test(is_user_nurse)
def tasks_list(request):
    """Show list of all ads"""
    my_ads = NurseAd.objects.filter(nurse_id=request.user.id)

    context = {'nurse_ads': my_ads, 'is_nurse': True, }
    return render(request, 'home/tasks-list.html', context)


@login_required(login_url='/login/')
@user_passes_test(is_user_nurse)
def accept_ad(request, ad_id):
    """Create a NurseAd model when ad is accepted"""
    ad = get_object_or_404(Ad, pk=ad_id)

    if not ad.accepted:
        ad.accepted = True
        ad.save()

        nurse = get_object_or_404(Nurse, id=request.user.id)

        nurse_ad = NurseAd(nurse=nurse, ad=ad)
        nurse_ad.save()

    return redirect('ads-list')


@login_required(login_url='/login/')
@user_passes_test(lambda user: is_user_custom_user(user) or user.is_superuser)
def delete_ad(request, ad_id):
    """Delete an Ad by custom user"""
    ad = get_object_or_404(Ad, pk=ad_id)
    if request.user.is_superuser or (not ad.accepted and ad.creator == request.user):
        sweetify.success(request, "Ad deleted successfully")
        ad.delete()
    elif ad.creator != request.user:
        sweetify.error(request, title="Error", text="You cannot delete request of another user")
    elif ad.accepted:
        sweetify.error(request, title="Error", text="Cannot delete accepted request")

    return redirect('requests-list')


@login_required(login_url='/login/')
@user_passes_test(is_user_nurse)
def start_task(request, ad_id):
    """Change situation of a task from accepted to started"""
    nurse_ad = get_object_or_404(NurseAd, ad_id=ad_id)
    nurse_ad.status = NurseAd.STATUS.STARTED
    nurse_ad.save()
    # here GPS tracking starts
    print('---------------------started--------------------------')
    return redirect('tasks-list')


@login_required(login_url='/login/')
@user_passes_test(is_user_nurse)
def end_task(request, ad_id):
    """Change situation of a task from started to finished"""
    nurse_ad = get_object_or_404(NurseAd, ad_id=ad_id)
    nurse_ad.status = NurseAd.STATUS.FINISHED
    nurse_ad.save()
    print('---------------------ended----------------------------')
    # here GPS tracking stops
    return redirect('tasks-list')


def create_update_ad_view(request, ad_id=None):
    context = {}
    if request.user.is_authenticated:
        context['base_template'] = 'layouts/base.html'
    else:
        context['base_template'] = 'layouts/logged-out-base.html'

    success = False
    is_edit = False

    # if ad_id exist, we want to edit, else create new Ad
    if ad_id:
        ad = get_object_or_404(Ad, pk=ad_id)
        if ad.creator != request.user and not request.user.is_superuser:
            sweetify.error(request, title="Unauthorized")
            return redirect('/')
        context['id'] = ad_id
        is_edit = True
    else:
        ad = Ad()

    form = AdForm(request.POST or None, instance=ad)
    if request.method == 'POST':
        # check whether the form is valid
        if form.is_valid():
            if request.user.is_authenticated and not request.user.is_superuser:
                form.cleaned_data['creator'] = request.user
            form.save()
            success = True
            msg = "Request edited successfully" if is_edit else "Your request has been created. Our Nurses will call you soon."
            sweetify.success(request, title="Success", text=msg, timer=None)
        # if is invalid
        else:
            msg = "Form is not valid."
            sweetify.error(request, title="Error", text=msg, timer=None)

    context.update({'form': form, 'success': success, 'user': request.user})

    return render(request, 'ads/submit-ads.html', context)
