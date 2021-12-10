from datetime import datetime, timezone
from django.contrib.gis.geos import LineString, Point
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from .forms import TrackingPointForm, StopTrackingForm
from .models import TrackedPoint, RouteLine
from django.shortcuts import get_object_or_404
from apps.ads.models import Ad, NurseAd
from django.contrib.auth.mixins import LoginRequiredMixin


@method_decorator(csrf_exempt, name="dispatch")
class TrackingPointAPIView(View, LoginRequiredMixin):
    """
    Handle simple API to post geolocation.
    """

    def get(self, request):
        myAds = NurseAd.objects.filter(nurse_id=request.user.id)
        context = {"nurse_ads": myAds}

        return render(request, "home/tasks-list.html", context)

    def post(self, request):
        form = TrackingPointForm(request.POST)
        if form.is_valid():
            user = self.request.user
            ad = get_object_or_404(Ad, id=form.cleaned_data["ad_id"])

            tp = TrackedPoint()
            # Timestamp is in milliseconds
            tp.user = user
            tp.ad = ad
            tp.timestamp = datetime.fromtimestamp(
                form.cleaned_data["timestamp"] / 1000, timezone.utc
            )
            tp.location = Point(
                form.cleaned_data["longitude"], form.cleaned_data["latitude"]
            )
            tp.accuracy = form.cleaned_data["accuracy"]
            tp.altitude = form.cleaned_data["altitude"]
            tp.altitude_accuracy = form.cleaned_data["altitude_accuracy"]
            tp.save()

            # update ad's status
            nurse_ad = get_object_or_404(NurseAd, ad=ad)
            nurse_ad.status = NurseAd.STATUS.STARTED
            nurse_ad.save()

            return JsonResponse({"successful": True})
        return JsonResponse({"succesful": False, "errors": form.errors})


@method_decorator(csrf_exempt, name="dispatch")
class RouteCreateView(View, LoginRequiredMixin):
    """
    Create a linestring from individual points.
    """

    def get(self, request):
        my_ads = NurseAd.objects.filter(nurse_id=request.user.id)
        context = {"nurse_ads": my_ads}

        return render(request, "home/tasks-list.html", context)

    def post(self, request):
        form = StopTrackingForm(request.POST)
        if form.is_valid():
            user = self.request.user
            ad = get_object_or_404(Ad, id=form.cleaned_data["ad_id"])

            qs = TrackedPoint.objects.filter(user=user, ad=ad)

            # Create line
            points = [tp.location for tp in qs]
            linestring = LineString(points)
            RouteLine.objects.create(user=user, location=linestring, ad=ad)

            # update ad's status
            nurse_ad = get_object_or_404(NurseAd, ad=ad)
            nurse_ad.status = NurseAd.STATUS.FINISHED
            nurse_ad.save()

            return JsonResponse({"successful": True})
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
