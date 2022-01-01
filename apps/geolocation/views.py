import sweetify
from datetime import datetime

from django.contrib.gis.geos import LineString, Point
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.utils.timezone import make_aware

from apps.ads.models import NurseAd
from ..users.permission_checks import is_user_nurse, is_user_admin
from .forms import TrackingPointForm
from .models import TrackedPoint, RouteLine


@login_required(login_url='/login/')
@user_passes_test(is_user_nurse)
def start_tracking(request, ad_id):
    nurse_ad = get_object_or_404(
        NurseAd, ad_id=ad_id, nurse_id=request.user.id)

    if nurse_ad.status != NurseAd.STATUS.ACCEPTED:
        sweetify.error(request, title="Error",
                       text="You already started this task")
    else:
        # update ad's status
        nurse_ad.status = NurseAd.STATUS.STARTED
        nurse_ad.save()

        sweetify.success(request, "Tracking started")

    return redirect('tasks-list')


@login_required(login_url='/login/')
@user_passes_test(is_user_nurse)
def stop_tracking(request):
    nurse_ad = get_object_or_404(
        NurseAd, nurse_id=request.user.id, status=NurseAd.STATUS.STARTED)
    qs = TrackedPoint.objects.filter(nurse_ad=nurse_ad)

    # Create line
    points = [tp.location for tp in qs]
    if len(points) <= 1:
        points = [points[0], points[0]]
    linestring = LineString(points)
    RouteLine.objects.create(nurse_ad=nurse_ad, location=linestring)

    # update ad's status
    nurse_ad.status = NurseAd.STATUS.FINISHED
    nurse_ad.save()

    sweetify.success(request, "Tracking ended")

    return redirect('tasks-list')


@method_decorator(csrf_exempt, name="dispatch")
class TrackingPointAPIView(View, LoginRequiredMixin):
    """
    Handle simple API to post geolocation.
    """

    def post(self, request):
        form = TrackingPointForm(request.POST)
        if form.is_valid():
            nurse_ad = get_object_or_404(
                NurseAd, ad_id=form.cleaned_data["ad_id"], nurse_id=self.request.user.id)

            tp = TrackedPoint()
            tp.nurse_ad = nurse_ad
            tp.timestamp = make_aware(datetime.fromtimestamp(form.cleaned_data["timestamp"] / 1000))
            tp.location = Point(
                form.cleaned_data["longitude"], form.cleaned_data["latitude"]
            )
            tp.accuracy = form.cleaned_data["accuracy"]
            tp.altitude = form.cleaned_data["altitude"]
            tp.altitude_accuracy = form.cleaned_data["altitude_accuracy"]
            tp.save()

            return JsonResponse({"successful": True})

        return JsonResponse({"succesful": False, "errors": form.errors})


@method_decorator(user_passes_test(is_user_admin), name='dispatch')
class RoutesListView(View, LoginRequiredMixin):
    """
    List created linestrings.
    """

    def get(self, request):
        print(request.user, request.user.is_superuser)
        lines = RouteLine.objects.all().order_by('-nurse_ad__last_updated')
        return render(
            request,
            "home/nurse-location.html",
            {"lines": lines, "tracked_lines_page": " active"},
        )
