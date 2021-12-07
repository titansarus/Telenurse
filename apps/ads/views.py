# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from apps.users.models import CustomUser
from .models import Ad, NurseAd
from django.shortcuts import render, get_object_or_404, redirect
import datetime
from apps.ads.forms import SERVICE_TYPES, SEX, AdForm

from django.template.defaulttags import register


@login_required(login_url="/login/")
def index(request):
    context = {"segment": "index"}
    html_template = loader.get_template("home/index.html")
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split("/")[-1]
        if load_template == "admin":
            return HttpResponseRedirect(reverse("admin:index"))
        elif load_template == "nurse-list.html":
            return list_of_nurses(request)
        elif load_template == "ads-list.html":
            return list_of_ads(request)
        elif load_template == "tasks-list.html":
            return my_ads(request)

        context["segment"] = load_template
        html_template = loader.get_template("home/" + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:
        html_template = loader.get_template("home/page-404.html")
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template("home/page-500.html")
        return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def list_of_nurses(request):
    nurses = [nurse for nurse in CustomUser.objects.all()]
    return render(request, "home/nurse-list.html", {"nurses": nurses})


@login_required(login_url="/login/")
def list_of_ads(request):
    ads = [ad for ad in Ad.objects.all() if not ad.accepted]

    context = {"ads": ads, "admin": request.user.is_superuser}

    return render(request, "home/ads-list.html", context)


@login_required(login_url="/login/")
def my_ads(request):
    """Show list of all ads"""
    myAds = [
        get_object_or_404(Ad, pk=nurse_ad.ad_id)
        for nurse_ad in NurseAd.objects.all()
        if int(nurse_ad.nurse_id) == request.user.id
    ]

    situations = {}
    for ad in myAds:
        nurse_ad = get_object_or_404(NurseAd, ad_id=ad.id)
        situations[ad.id] = nurse_ad.situation

    context = {"ads": myAds, "situations": situations}

    return render(request, "home/tasks-list.html", context)


@login_required(login_url="/login/")
def accept_ad(request, ad_id):
    """Create a NurseAd model when ad is accepted"""
    ad = get_object_or_404(Ad, pk=ad_id)

    if not ad.accepted:
        ad.accepted = True
        ad.save()

        nurse_ad = NurseAd(nurse_id=request.user.id, ad_id=ad.id, situation="accepted")
        nurse_ad.save()

    return redirect("/ads-list.html")


@login_required(login_url="/login/")
def start_task(request, ad_id):
    """Change situation of a task from accepted to started"""
    nurse_ad = get_object_or_404(NurseAd, ad_id=ad_id)
    nurse_ad.situation = "started"
    nurse_ad.save()
    # here GPS tracking starts
    print("---------------------started--------------------------")
    return redirect("/tasks-list.html")


@login_required(login_url="/login/")
def end_task(request, ad_id):
    """Change situation of a task from started to finished"""
    nurse_ad = get_object_or_404(NurseAd, ad_id=ad_id)
    nurse_ad.situation = "finished"
    nurse_ad.save()
    print("---------------------ended----------------------------")
    # here GPS tracking stops
    return redirect("/tasks-list.html")


@register.filter
def get_value(dictionary, key):
    return dictionary.get(key)

@register.filter
def get_service_type(ad, service_type):
    return dict(SERVICE_TYPES)[service_type]

@register.filter
def get_gender(ad, gender):
    return dict(SEX)[gender]


def ads_view(request):
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
