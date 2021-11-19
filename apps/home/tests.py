# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.test import TestCase
from .models import NurseAd


class NurseAdTest(TestCase):
    def create_nurse_ad(
        self,
        nurse_id="1",
        ad_id="1",
        situation="started",
    ):
        return NurseAd.objects.create(
            nurse_id=nurse_id,
            ad_id=ad_id,
            situation=situation,
        )

    def test_nurse_ad_creation(self):
        test_nurse_ad = self.create_nurse_ad()
        self.assertTrue(isinstance(test_nurse_ad, NurseAd))
        info = test_nurse_ad.nurse_id + " " + test_nurse_ad.ad_id + " " + test_nurse_ad.situation
        self.assertEqual(test_nurse_ad.__str__(), info)
