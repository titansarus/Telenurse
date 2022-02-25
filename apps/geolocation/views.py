import sweetify
from datetime import datetime
import logging

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


logger = logging.getLogger(__name__)

@login_required(login_url='/login/')
@user_passes_test(is_user_nurse)
def start_tracking(request, ad_id):
    logger.info(f'start tracking request for ad {ad_id}')

    nurse_ad = get_object_or_404(
        NurseAd, ad_id=ad_id, nurse_id=request.user.id)

    if nurse_ad.status != NurseAd.STATUS.ACCEPTED:
        sweetify.error(request, title="Error",
                       text="You already started this task")

        logger.warning(f"Start tracking request for already started task {nurse_ad.id}")
    else:
        # update ad's status
        nurse_ad.status = NurseAd.STATUS.STARTED
        nurse_ad.save()

        sweetify.success(request, "Tracking started")

        logger.info(f"Started tracking successfully for task {nurse_ad.id}")
    
    return redirect('tasks-list')


@login_required(login_url='/login/')
@user_passes_test(is_user_nurse)
def stop_tracking(request):
    nurse_ad = get_object_or_404(
        NurseAd, nurse_id=request.user.id, status=NurseAd.STATUS.STARTED)
    qs = TrackedPoint.objects.filter(nurse_ad=nurse_ad)

    logger.info(f"Stop tracking request for task {nurse_ad.id}")

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

    logger.info(f"Stopped tracking successfully for task {nurse_ad.id}")

    return redirect('tasks-list')


@method_decorator(csrf_exempt, name='dispatch')
class TrackingPointAPIView(View, LoginRequiredMixin):
    """
    Handle simple API to post geolocation.
    """

    def post(self, request):
        form = TrackingPointForm(request.POST)

        if form.is_valid():
            nurse_ad = get_object_or_404(
                NurseAd, ad_id=form.cleaned_data['ad_id'], nurse_id=self.request.user.id)

            tp = TrackedPoint()
            tp.nurse_ad = nurse_ad
            tp.timestamp = make_aware(datetime.fromtimestamp(form.cleaned_data['timestamp'] / 1000))
            tp.location = Point(
                form.cleaned_data['longitude'], form.cleaned_data['latitude']
            )
            tp.accuracy = form.cleaned_data['accuracy']
            tp.altitude = form.cleaned_data['altitude']
            tp.altitude_accuracy = form.cleaned_data['altitude_accuracy']
            tp.save()

            logger.info(f"Nurse location for task {nurse_ad.id} stored successfully")
            return JsonResponse({'successful': True})

        logger.warning(f"Error in tracking nurse location {nurse_ad.id}")
        return JsonResponse({'succesful': False, 'errors': form.errors})


@method_decorator(user_passes_test(is_user_admin), name='dispatch')
class RoutesListView(View, LoginRequiredMixin):
    """
    List created linestrings.
    """

    def get(self, request):
        lines = RouteLine.objects.all().order_by('-nurse_ad__last_updated')
        
        logger.info(f"Show {len(lines)} routes for user {request.user.id}")

        return render(
            request,
            'home/tasks-route-location.html',
            {"lines": lines},
        )

@csrf_exempt
@login_required(login_url='/login/')
@user_passes_test(is_user_admin)
def get_active_tasks(request):
    active_ads = NurseAd.objects.filter(status=NurseAd.STATUS.STARTED)

    return render(
            request,
            'home/nurse-location.html',
            {"active_ads": active_ads},
        )


@csrf_exempt
@login_required(login_url='/login/')
@user_passes_test(is_user_admin)
def get_nurse_location(request, nurse_id):
    logger.info(f"Get location of nurse {nurse_id} for user {request.user.id}")
    tp = TrackedPoint.objects.filter(nurse_ad__nurse_id=nurse_id).order_by('-timestamp').first()

    if not tp:
        return JsonResponse({'success': False})

    return JsonResponse({'success': True, 'latitude': tp.location.y, 'longitude': tp.location.x})
