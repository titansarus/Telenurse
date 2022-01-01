# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from django.test.client import Client
import pytz

from django.urls import reverse
from django.test import TestCase
from django.contrib.gis.geos import Point, LineString

from datetime import datetime
from apps.ads.models import Ad, NurseAd
from model_bakery import baker

from apps.users.models import CustomUser, Nurse
from .models import TrackedPoint, RouteLine
from .forms import TrackingPointForm


class LocationTest(TestCase):
    def create_tracking_point(
            self,
            username="mmd",
            location=Point(7.15, 35.0),
            timestamp=datetime(2020, 9, 16, tzinfo=pytz.UTC),
            ad_id="12",
            altitude=0.5,
            altitude_accuracy=0.5,
            accuracy=0.5,
    ):
        nurse = baker.make(Nurse, username=username)
        ad = baker.make(Ad, id=ad_id)
        nurse_ad = NurseAd.objects.create(ad=ad, nurse=nurse)
        return TrackedPoint.objects.create(
            nurse_ad=nurse_ad,
            timestamp=timestamp,
            location=location,
            altitude=altitude,
            altitude_accuracy=altitude_accuracy,
            accuracy=accuracy,
        )

    def test_tracking_point_creation(self):
        test_tp = self.create_tracking_point()
        self.assertTrue(isinstance(test_tp, TrackedPoint))
        info = "{} ({})".format(test_tp.id,
                                test_tp.timestamp.isoformat())
        self.assertEqual(test_tp.__str__(), info)

    def test_valid_TrackingPointform(self):
        test_tp = self.create_tracking_point()
        data = {
            "username": test_tp.nurse_ad.nurse.username,
            "timestamp": 12,
            "ad_id": test_tp.nurse_ad.ad.id,
            "altitude": test_tp.altitude,
            "altitude_accuracy": test_tp.altitude_accuracy,
            "accuracy": test_tp.accuracy,
            "latitude": 35.5,
            "longitude": 50.0,
        }
        form = TrackingPointForm(data=data)
        self.assertTrue(form.is_valid())



class RouteTest(TestCase):
    def create_route(
            self,
            username="mmd",
            ad_id="12",
            location=LineString([Point(7.15, 35.0), Point(5.6, 37.8)]),
            color="#f55c64",
    ):
        nurse = baker.make(Nurse, username=username)
        ad = baker.make(Ad, id=ad_id)
        nurse_ad = NurseAd.objects.create(ad=ad, nurse=nurse)
        return RouteLine.objects.create(
            nurse_ad=nurse_ad,
            location=location,
            color=color,
        )

    def test_route_creation(self):
        test_route = self.create_route()
        self.assertTrue(isinstance(test_route, RouteLine))
        info = test_route.nurse_ad.nurse.username
        self.assertEqual(test_route.__str__(), info)


class NurseLocationTest(TestCase):
    def setUp(self):
        self.user_admin = CustomUser.objects.create(username='admin', email='admin@email.com', password='', is_superuser=True)
        self.user_admin.set_password('secret')
        self.user_admin.save()

        self.user_non_admin = CustomUser.objects.create(username='nurse', email='nurse@email.com', password='', is_superuser=False)
        self.user_non_admin.set_password('secret')
        self.user_non_admin.save()

        self.nurse = baker.make(Nurse)
        self.nurse_ad = baker.make(NurseAd, nurse=self.nurse)
        self.points = baker.make(TrackedPoint, nurse_ad=self.nurse_ad, _quantity=5)
        ls = LineString([tp.location for tp in self.points])
        self.route_line = baker.make(RouteLine, nurse_ad=self.nurse_ad, location=ls)


    def test_get_nurse_locations_view_not_logged_in(self):
        self.client = Client()
        self.client.logout()
        response = self.client.get(reverse("nurse-location"))
        self.assertEqual(response.status_code, 302)

    def test_get_nurse_locations_view_admin(self):
        self.client = Client()
        self.client.login(username='admin', password='secret')
        response = self.client.get(reverse("nurse-location"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.nurse.username)

    def test_get_nurse_locations_view_nurse(self):
        self.client = Client()
        self.client.login(username='nurse', password='secret')
        response = self.client.get(reverse("nurse-location"))
        self.assertEqual(response.status_code, 302)
