# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from apps.ads.forms import AdForm
from .models import Ad, NurseAd
from ..users.models import Nurse


def is_user_nurse(user):
    return Nurse.objects.filter(username=user.username).count() == 1


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
@user_passes_test(is_user_nurse)
def ads_list(request):
    
    ads = [ad for ad in Ad.objects.all() if not ad.accepted]

    context = {'ads': ads, 'admin': request.user.is_superuser, 'is_nurse': True}
    return render(request, 'home/ads-list.html', context)


@login_required(login_url='/login/')
@user_passes_test(lambda user: not is_user_nurse(user))
def requests_list(request):
    """Show list of all ads"""
    my_ads = Ad.objects.filter(creator_id=request.user.id)

    context = {'user_requests': my_ads, 'is_nurse': False}
    return render(request, 'home/user-requests.html', context)


@login_required(login_url='/login/')
@user_passes_test(is_user_nurse)
def tasks_list(request):
    """Show list of all ads"""
    my_ads = NurseAd.objects.filter(nurse_id=request.user.id)

    context = {'nurse_ads': my_ads, 'is_nurse': True}
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


def submit_new_ad_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/')

    msg = None
    success = False
    # if we want to post a form
    if request.method == 'POST':
        form = AdForm(request.POST)
        # check whether the form is valid
        if form.is_valid():
            form.save()
            success = True
            msg = 'Your request has been created. Our Nurses will call you soon.'
        # if is invalid
        else:
            msg = 'Form is not valid.'

    # if we want to get a form
    else:
        form = AdForm()

    return render(request, 'ads/submit-ads.html', {'form': form, 'msg': msg, 'success': success})
