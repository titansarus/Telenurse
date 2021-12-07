# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from datetime import date
from django.urls import reverse
from ..ads.forms import AdForm
from apps.ads.models import Ad
from django.test import TestCase


class AdTest(TestCase):
    def create_ad(
        self,
        first_name="mmd",
        last_name="mmdi",
        phone_number="09129121112",
        address="Tehran",
        start_time=date(2020, 9, 16),
        end_time=date(2021, 9, 16),
        service_type="1",
        gender="M",
        accepted=False,
    ):
        return Ad.objects.create(
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            address=address,
            start_time=start_time,
            end_time=end_time,
            service_type=service_type,
            gender=gender,
            accepted=accepted,
        )

    def test_ad_creation(self):
        test_ad = self.create_ad()
        self.assertTrue(isinstance(test_ad, Ad))
        info = (
            f"Ad info: {test_ad.address}, {test_ad.phone_number}, {test_ad.service_type}, {test_ad.start_time} until "
            f"{test_ad.end_time}"
        )
        self.assertEqual(test_ad.__str__(), info)

    def test_ad_view_get(self):
        response = self.client.get(reverse("submit_ad"))
        self.assertEqual(response.status_code, 200)

    def test_ad_view_post(self):
        test_ad = self.create_ad()
        data = {
            "first_name": test_ad.first_name,
            "last_name": test_ad.last_name,
            "phone_number": test_ad.phone_number,
            "address": test_ad.address,
            "start_time": test_ad.start_time,
            "end_time": test_ad.end_time,
            "service_type": test_ad.service_type,
            "gender": test_ad.gender,
        }
        response = self.client.post(reverse("submit_ad"), data)
        self.assertEqual(response.status_code, 200)

    def test_valid_Adform(self):
        test_ad = self.create_ad()
        data = {
            "first_name": test_ad.first_name,
            "last_name": test_ad.last_name,
            "phone_number": test_ad.phone_number,
            "address": test_ad.address,
            "start_time": test_ad.start_time,
            "end_time": test_ad.end_time,
            "service_type": test_ad.service_type,
            "gender": test_ad.gender,
        }
        form = AdForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_Adform(self):
        test_ad = self.create_ad(gender="Man")
        data = {
            "first_name": test_ad.first_name,
            "last_name": test_ad.last_name,
            "phone_number": test_ad.phone_number,
            "address": test_ad.address,
            "start_time": test_ad.start_time,
            "end_time": test_ad.end_time,
            "service_type": test_ad.service_type,
            "gender": test_ad.gender,
        }
        form = AdForm(data=data)
        self.assertFalse(form.is_valid())
