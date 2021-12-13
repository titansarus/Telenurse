# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.test import TestCase
from .models import TrackedPoint, RouteLine
from .forms import TrackingPointForm, StopTrackingForm
from datetime import date
from django.contrib.gis.geos import Point, LineString


class LocationTest(TestCase):
    def create_tracking_point(
            self,
            username="mmd",
            location=Point(7.15, 35.0),
            timestamp=date(2020, 9, 16),
            ad_id="12",
            altitude=0.5,
            altitude_accuracy=0.5,
            accuracy=0.5,
    ):
        return TrackedPoint.objects.create(
            username=username,
            timestamp=timestamp,
            location=location,
            ad_id=ad_id,
            altitude=altitude,
            altitude_accuracy=altitude_accuracy,
            accuracy=accuracy,
        )

    def test_tracking_point_creation(self):
        test_tp = self.create_tracking_point()
        self.assertTrue(isinstance(test_tp, TrackedPoint))
        info = "{} ({})".format(test_tp.location.wkt, test_tp.timestamp.isoformat())
        self.assertEqual(test_tp.__str__(), info)

    def test_valid_TrackingPointform(self):
        test_tp = self.create_tracking_point()
        data = {
            "username": test_tp.username,
            "timestamp": 12,
            "ad_id": test_tp.ad_id,
            "altitude": test_tp.altitude,
            "altitude_accuracy": test_tp.altitude_accuracy,
            "accuracy": test_tp.accuracy,
            "latitude": 35.5,
            "longitude": 50.0,
        }
        form = TrackingPointForm(data=data)
        self.assertTrue(form.is_valid())

    def test_valid_StopTrackingPointform(self):
        test_tp = self.create_tracking_point()
        data = {
            "ad_id": test_tp.ad_id,
        }
        form = StopTrackingForm(data=data)
        self.assertTrue(form.is_valid())


class RouteTest(TestCase):
    def create_route(
            self,
            username="mmd",
            ad_id="12",
            location=LineString([Point(7.15, 35.0), Point(5.6, 37.8)]),
            color="#f55c64",
    ):
        return RouteLine.objects.create(
            username=username,
            ad_id=ad_id,
            location=location,
            color=color,
        )

    def test_route_creation(self):
        test_route = self.create_route()
        self.assertTrue(isinstance(test_route, RouteLine))
        info = test_route.username
        self.assertEqual(test_route.__str__(), info)
