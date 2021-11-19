from datetime import datetime, timezone
from django.contrib.gis.geos import LineString, Point
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, View
from django.contrib.auth.decorators import login_required
from .forms import TrackingPointForm, StopTrackingForm
from .models import TrackedPoint, RouteLine
from django.shortcuts import get_object_or_404
from apps.home.models import Ad, NurseAd
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect


@method_decorator(csrf_exempt, name="dispatch")
class TrackingPointAPIView(View, LoginRequiredMixin):
    """
    Handle simple API to post geolocation.
    """

    # @login_required(login_url="/login/")
    def get(self, request):
        print("-------------------get start track----------------------")
        myAds = [
            get_object_or_404(Ad, pk=nurse_ad.ad_id)
            for nurse_ad in NurseAd.objects.all()
            if int(nurse_ad.nurse_id) == self.request.user.id
        ]

        situations = {}
        for ad in myAds:
            nurse_ad = get_object_or_404(NurseAd, ad_id=ad.id)
            situations[ad.id] = nurse_ad.situation

        context = {"ads": myAds, "situations": situations}

        return render(request, "home/tasks-list.html", context)

    def post(self, request):
        form = TrackingPointForm(request.POST)
        print("-------------------post start track----------------------")
        if form.is_valid():
            tp = TrackedPoint()
            # Timestamp is in milliseconds
            tp.username = form.cleaned_data["username"]
            tp.timestamp = datetime.fromtimestamp(
                form.cleaned_data["timestamp"] / 1000, timezone.utc
            )
            tp.location = Point(
                form.cleaned_data["longitude"], form.cleaned_data["latitude"]
            )
            tp.ad_id = form.cleaned_data["ad_id"]
            tp.accuracy = form.cleaned_data["accuracy"]
            tp.altitude = form.cleaned_data["altitude"]
            tp.altitude_accuracy = form.cleaned_data["altitude_accuracy"]
            tp.save()

            nurse_ad = get_object_or_404(NurseAd, ad_id=form.cleaned_data["ad_id"])
            print("1. start nurse_ad:", nurse_ad)
            nurse_ad.situation = "started"
            nurse_ad.save()
            print("2. start nurse_ad:", nurse_ad)
            print("\t---------------------ad started----------------------")
            # return JsonResponse({"successful": True})
            self.get(self.request)
        return JsonResponse({"succesful": False, "errors": form.errors})


@method_decorator(csrf_exempt, name="dispatch")
class RouteCreateView(View, LoginRequiredMixin):
    """
    Create a linestring from individual points.
    """

    def get(self, request):
        print("-------------------route created----------------------")
        myAds = [
            get_object_or_404(Ad, pk=nurse_ad.ad_id)
            for nurse_ad in NurseAd.objects.all()
            if int(nurse_ad.nurse_id) == self.request.user.id
        ]

        situations = {}
        for ad in myAds:
            nurse_ad = get_object_or_404(NurseAd, ad_id=ad.id)
            situations[ad.id] = nurse_ad.situation

        context = {"ads": myAds, "situations": situations}

        return render(request, "home/tasks-list.html", context)

    def post(self, request):
        form = StopTrackingForm(request.POST)
        print("-------------------post end track----------------------")
        if form.is_valid():
            username = self.request.user.username
            qs = TrackedPoint.objects.filter(
                username=username, ad_id=form.cleaned_data["ad_id"]
            )
            # Create line
            points = [tp.location for tp in qs]
            linestring = LineString(points)
            RouteLine.objects.create(
                username=username, location=linestring, ad_id=form.cleaned_data["ad_id"]
            )

            nurse_ad = get_object_or_404(NurseAd, ad_id=form.cleaned_data["ad_id"])
            print("1. end nurse_ad:", nurse_ad)
            nurse_ad.situation = "finished"
            nurse_ad.save()
            print("2. end nurse_ad:", nurse_ad)
            print("\t---------------------ad done--------------------")
            # self.get(self.request)
            # return JsonResponse({"successful": True})
            self.get(self.request)
        return JsonResponse({"succesful": False, "errors": form.errors})


class RoutesListView(View, LoginRequiredMixin):
    """
    List created linestrings.
    """

    def get(self, request):
        lines = RouteLine.objects.all()
        return render(
            request,
            "home/nurse-location.html",
            {"lines": lines, "tracked_lines_page": " active"},
        )
