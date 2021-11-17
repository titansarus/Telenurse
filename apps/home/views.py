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
        elif load_template == "my-ads-list.html":
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

    context = {'ads': ads}

    return render(request, "home/ads-list.html", context)


@login_required(login_url="/login/")
def my_ads(request):
    myAds = [get_object_or_404(Ad, pk=nurse_ad.ad_id) for nurse_ad in NurseAd.objects.all() if
             int(nurse_ad.nurse_id) == request.user.id]

    context = {'ads': myAds}

    return render(request, "home/my-ads-list.html", context)


@login_required(login_url="/login/")
def accept_ad(request, ad_id):
    ad = get_object_or_404(Ad, pk=ad_id)

    if not ad.accepted:
        ad.accepted = True
        ad.save()

        nurse_ad = NurseAd(nurse_id=request.user.id, ad_id=ad.id, situation='accepted')
        nurse_ad.save()

    return redirect('/ads-list.html')


@login_required(login_url="/login/")
def start_task(request, ad_id):
    nurse_ad = get_object_or_404(NurseAd, ad_id=ad_id)
    nurse_ad.situation = 'started'
    nurse_ad.save()

    # here GPS tracking starts

    return redirect('/my-ads-list.html')


@login_required(login_url="/login/")
def end_task(request, ad_id):
    nurse_ad = get_object_or_404(NurseAd, ad_id=ad_id)
    nurse_ad.situation = 'finished'
    nurse_ad.save()

    # here GPS tracking stops

    return redirect('/my-ads-list.html')
