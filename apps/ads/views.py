from datetime import timedelta
import sweetify
import logging
import json 

from django import template
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models.aggregates import Avg
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.urls import reverse
from django.contrib.gis.geos import Point
from django.utils import timezone

from apps.ads.filters import AdFilter, AdFilterForAdmin
from apps.ads.forms import AdForm, AdReviewForm
from .models import Ad, NurseAd, AdReview
from ..users.models import CustomUser, Nurse
from ..users.permission_checks import is_user_custom_user, is_user_nurse

logger = logging.getLogger(__name__)

AD_DELETED_SUCCESSFULLY_MSG = "Ad deleted successfully"
CANNOT_DELETE_ACCEPTED_MSG = "Cannot delete accepted request"
CANNOT_DELETE_REQUEST_OF_OTHER_MSG = "You cannot delete request of another user"
REQUEST_EDIT_SUCCESS_MSG = "Request edited successfully"
REQUEST_CREATED_SUCCESS_MSG = "Your request has been created. Our Nurses will call you soon."
INVALID_FORM_MSG = "Form is not valid."
CANNOT_RATE_UNFINISHED_TASK_MSG = "You cannot rate a task that is not finished"
REVIEW_EDIT_SUCCESS_MSG = "Review edited successfully!"
REVIEW_CREATE_SUCCESS_MSG = "Review submitted successfully!"


@login_required(login_url='/login/')
def index(request):
    context = {'segment': 'index', 'is_nurse': is_user_nurse(request.user)}
    
    last_seven_days = [timezone.now().date()+timedelta(days=i) for i in range(-6, 1)]
    charts = []
    if request.user.is_superuser:
        charts = [
                {
                    'title': 'Submitted Ads',
                    'id': 'submitted',
                    'labels': [str(s) for s in last_seven_days],
                    'data': [Ad.objects.filter(created_at__gte=d, created_at__lte=d+timedelta(days=1)).count() for d in last_seven_days],
                },
                {
                    'title': 'Completed Tasks',
                    'id': 'completed',
                    'labels': [str(s) for s in last_seven_days],
                    'data': [NurseAd.objects.\
                        filter(status=NurseAd.STATUS.FINISHED, last_updated__gte=d, last_updated__lte=d+timedelta(days=1)).count() 
                        for d in last_seven_days],
                }
            ]
    elif is_user_nurse(request.user):
        charts = [
                {
                    'title': 'Accepted Tasks By You',
                    'id': 'submitted',
                    'labels': [str(s) for s in last_seven_days],
                    'data': [NurseAd.objects.\
                        filter(status=NurseAd.STATUS.ACCEPTED, nurse_id=request.user.id,
                         last_updated__gte=d, last_updated__lte=d+timedelta(days=1)).count() 
                        for d in last_seven_days],                },
                {
                    'title': 'Completed Tasks By You',
                    'id': 'completed',
                    'labels': [str(s) for s in last_seven_days],
                    'data': [NurseAd.objects.\
                        filter(status=NurseAd.STATUS.FINISHED, nurse_id=request.user.id,
                         last_updated__gte=d, last_updated__lte=d+timedelta(days=1)).count() 
                        for d in last_seven_days],
                }
            ]
    else:
        charts = [
                {
                    'title': 'Submitted Ads By You',
                    'id': 'submitted',
                    'labels': [str(s) for s in last_seven_days],
                    'data': [Ad.objects.filter(creator_id=request.user.id,
                        created_at__gte=d, created_at__lte=d+timedelta(days=1)).count() for d in last_seven_days],
                },
        ]

    context['charts'] = charts
    context['data'] = json.dumps({'charts':  charts})

    context['nurses_count'] = Nurse.objects.all().count()
    context['users_count'] = CustomUser.objects.all().count()
    context['ads_count'] = Ad.objects.all().count()
    

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
    if request.user.is_superuser:
        f = AdFilterForAdmin(request.GET, queryset=Ad.objects.all())
    else:
        f = AdFilter(request.GET, queryset=Ad.objects.all())
    ads = f.qs

    is_nurse = is_user_nurse(request.user)
    if request.user.is_superuser:
        ads = ads
        logger.info(f"Get requests list for superuser {request.user.id}")
    elif is_nurse:
        ads = ads.filter(accepted=False)
        logger.info(f"Get requests list for nurse {request.user.id}")
    else:
        ads = ads.filter(creator_id=request.user.id)
        if request.GET.get('finished', 0):
            ads = ads.filter(nursead__status=NurseAd.STATUS.FINISHED)
        logger.info(f"Get requests list for ordinary user {request.user.id}")

    if not request.GET.get('finished', 0):
        for ad in ads:
            if ad.nursead_set.filter(status=NurseAd.STATUS.FINISHED).count() > 0:
                ad.status = NurseAd.STATUS.FINISHED
            else:
                ad.status = ''

            if ad.nursead_set.count() > 0:
                ad.nurse = ad.nursead_set.first().nurse
            else:
                ad.nurse = None

    order_by_fields_names = ['start_time', 'end_time', 'created_at']

    order_by = request.GET.get('order_by')
    if not order_by or (order_by not in order_by_fields_names and order_by[1:] not in order_by_fields_names):
        order_by = None

    if order_by:
        ads = ads.order_by(order_by)
        logger.debug(f"Get requests list in {order_by} order")

    order_by_fields = [
        {
            'id': f if not order_by or not order_by.endswith(f) else "-" + f,
            'name': f.replace('_', ' ').capitalize(),
            'asc': order_by and f == order_by,
            'selected': order_by and order_by.endswith(f),
        }
        for f in order_by_fields_names
    ]

    context = {'user_requests': ads,
               'is_nurse': is_nurse,
               'is_finished': request.GET.get('finished', 0),
               'admin': request.user.is_superuser,
               'filter': f,
               'order_by_fields': order_by_fields}

    return render(request, 'home/requests-list.html', context)


@login_required(login_url='/login/')
@user_passes_test(lambda user: is_user_nurse(user) or user.is_superuser)
def review_list(request):
    if is_user_nurse(request.user):
        return review_list_nurse(request)
    if request.user.is_superuser:
        return review_list_superuser(request)
    return HttpResponseForbidden()


def review_list_nurse(request):
    reviews = AdReview.objects.filter(nurse_ad__nurse=request.user)
    average = reviews.filter(score__gt=0).aggregate(average=Avg('score'))
    reviews_selected_columns = reviews.values(*['score', 'review', 'updated_at'])
    context = {'reviews': reviews_selected_columns, 'is_nurse': True, 'average': average, 'is_superuser': False}
    return render(request, 'home/review-score-list.html', context)


def review_list_superuser(request):
    reviews = AdReview.objects.all()
    reviews.values()
    context = {'reviews': reviews, 'is_nurse': False, 'is_superuser': True}
    return render(request, 'home/review-score-list.html', context)


@login_required(login_url='/login/')
@user_passes_test(is_user_nurse)
def tasks_list(request):
    """Show list of all ads"""
    my_ads = NurseAd.objects.filter(nurse_id=request.user.id).extra(
        select={'is_top': "status = 'S'", 'is_bottom': "status = 'F'"}).order_by('-is_top', 'is_bottom',
                                                                                 '-last_updated')

    active_tasks = my_ads.filter(status=NurseAd.STATUS.STARTED)
    active_task = active_tasks[0] if active_tasks else None

    context = {'nurse_ads': my_ads,
               'is_nurse': True, 'active_task': active_task}
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

    return redirect('requests-list')


@login_required(login_url='/login/')
@user_passes_test(lambda user: is_user_custom_user(user) or user.is_superuser)
def delete_ad(request, ad_id):
    """Delete an Ad by custom user"""
    ad = get_object_or_404(Ad, pk=ad_id)
    if request.user.is_superuser or (not ad.accepted and ad.creator == request.user):
        sweetify.success(request, AD_DELETED_SUCCESSFULLY_MSG)
        ad.delete()
    elif ad.creator != request.user:
        sweetify.error(request, title="Error",
                       text=CANNOT_DELETE_REQUEST_OF_OTHER_MSG)
    elif ad.accepted:
        sweetify.error(request, title="Error",
                       text=CANNOT_DELETE_ACCEPTED_MSG)

    return redirect('requests-list')


def create_update_ad_view(request, ad_id=None):
    initial = {}
    context = {}
    if request.user.is_authenticated:
        context['base_template'] = 'layouts/base.html'
        initial = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'address_details': request.user.address.details if request.user.address else '',
            'address_location': request.user.address.location if request.user.address else None,
            'phone_number': request.user.phone_number,
        }
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
        context['ad_price'] = ad.price
        is_edit = True
        initial = ad.__dict__
        initial['address_details']= ad.address.details if ad.address else ''
        initial['address_location']= ad.address.location if ad.address else None
        initial['start_time'] = ad.start_time.strftime("%Y-%m-%dT%H:%M")
        initial['end_time'] = ad.end_time.strftime("%Y-%m-%dT%H:%M")
    else:
        ad = Ad()

    initial['address_location'] = initial.get('address_location', None) or Point(51.3890, 35.6892, srid=4326)

    form = AdForm(request.POST or None, instance=ad, initial=initial)
    if request.method == 'POST':
        # check whether the form is valid
        if form.is_valid():
            if request.user.is_authenticated and not request.user.is_superuser:
                form.cleaned_data['creator'] = request.user
            form.save()
            success = True
            msg = REQUEST_EDIT_SUCCESS_MSG if is_edit else REQUEST_CREATED_SUCCESS_MSG
            sweetify.success(request, title="Success", text=msg, timer=None)
        # if is invalid
        else:
            msg = INVALID_FORM_MSG
            sweetify.error(request, title="Error", text=msg, timer=None)

    context.update({'form': form, 'success': success, 'user': request.user})

    return render(request, 'ads/submit-ads.html', context)


@login_required(login_url='/login/')
@user_passes_test(is_user_custom_user)
def submit_review(request, ad_id=None):
    context = {}
    if not ad_id:
        return HttpResponseNotFound()

    nurse_ad = get_object_or_404(NurseAd, ad_id=ad_id, ad__creator=request.user)

    if not nurse_ad or nurse_ad.ad.creator != request.user:
        sweetify.error(request, title="Unauthorized")
        return redirect('/')
    if nurse_ad.status != nurse_ad.STATUS.FINISHED:
        sweetify.error(request, title="Error", text=CANNOT_RATE_UNFINISHED_TASK_MSG)
        return redirect('/')
    context['id'] = nurse_ad.ad.id
    review = AdReview()
    is_edit = False
    if hasattr(nurse_ad, 'review'):
        review = nurse_ad.review
        is_edit = True
    form = AdReviewForm(request.POST or None, instance=review)
    if request.method == 'POST':
        if form.is_valid():
            review = form.save(False)
            review.nurse_ad = nurse_ad
            review.save()
            msg = REVIEW_EDIT_SUCCESS_MSG if is_edit else REVIEW_CREATE_SUCCESS_MSG
            sweetify.success(request, title="Success", text=msg, timer=None)
        else:
            msg = INVALID_FORM_MSG
            sweetify.error(request, title="Error", text=msg, timer=None)

    context.update({'form': form, 'user': request.user, 'nurse_ad': nurse_ad})

    return render(request, 'ads/submit-review.html', context)
