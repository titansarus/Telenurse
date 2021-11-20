# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.test import TestCase
from .models import CustomUser
import mock
from django.core.files import File
from django.urls import reverse


class CustomUserTest(TestCase):
    def create_cu(
        self,
        first_name="mmd",
        last_name="mmdi",
        username="mmd.mmdi",
        password="mmdpass",
        email="mmd@gmail.com",
        document_name="mmdphoto.png",
        phone_number="09129121112",
    ):
        file_mock = mock.MagicMock(spec=File)
        file_mock.name = document_name
        return CustomUser.objects.create(
            first_name=first_name,
            last_name=last_name,
            username=username,
            password=password,
            email=email,
            document=file_mock,
            phone_number=phone_number,
        )

    def test_cu_creation(self):
        test_cu = self.create_cu()
        self.assertTrue(isinstance(test_cu, CustomUser))
        info = test_cu.username + " / " + test_cu.password
        self.assertEqual(test_cu.__str__(), info)
