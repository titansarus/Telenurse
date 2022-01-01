# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import sweetify
from django import template
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models.aggregates import Avg
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.urls import reverse

from apps.ads.forms import AdForm, AdReviewForm
from .models import Ad, NurseAd, AdReview
from ..users.models import Nurse
from ..users.permission_checks import is_user_custom_user, is_user_nurse

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
        if request.GET.get('finished', 0):
            ads = ads.filter(nursead__status=NurseAd.STATUS.FINISHED)
    if not request.GET.get('finished', 0):
        for ad in ads:
            if ad.nursead_set.filter(status=NurseAd.STATUS.FINISHED).count() > 0:
                ad.status = NurseAd.STATUS.FINISHED
            else:
                ad.status = ''

    context = {'user_requests': ads, 'is_nurse': is_nurse, 'is_finished': request.GET.get('finished', 0),
               'admin': request.user.is_superuser}

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
    reviews_selected_columns = reviews.values(
        *['score', 'review', 'nurse_ad_id', 'nurse_ad__nurse__id',
          'nurse_ad__ad__creator_id', 'created_at', 'updated_at'])
    context = {'reviews': reviews_selected_columns, 'is_nurse': False, 'is_superuser': True}
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
    context['id'] = nurse_ad.id
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
