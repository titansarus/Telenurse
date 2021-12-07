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



class AuthenticationTest(TestCase):
    def create_nurse(
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
        return Nurse.objects.create(
            first_name=first_name,
            last_name=last_name,
            username=username,
            password=password,
            email=email,
            document=file_mock,
            phone_number=phone_number,
        )

    def test_nurse_creation(self):
        test_nurse = self.create_nurse()
        self.assertTrue(isinstance(test_nurse, Nurse))
        info = (
            f"Nurse with username {test_nurse.username} info: {test_nurse.first_name} {test_nurse.last_name}, {test_nurse.email}, "
            f"{test_nurse.phone_number}"
        )
        self.assertEqual(test_nurse.__str__(), info)

    def test_init_view_get(self):
        response = self.client.get(reverse("init"))
        self.assertEqual(response.status_code, 200)

    def test_login_view_get(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

    def test_register_view_get(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)

    def test_valid_Loginform(self):
        data = {
            "username": "mmd",
            "password": "mmdpass",
        }
        form = LoginForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_SignUpform(self):
        test_nurse = self.create_nurse()
        data = {
            "first_name": test_nurse.first_name,
            "last_name": test_nurse.last_name,
            "username": test_nurse.username,
            "email": test_nurse.email,
            "password1": test_nurse.password,
            "password2": test_nurse.password,
            "phone_number": test_nurse.phone_number,
        }
        form = SignUpForm(data=data)
        self.assertFalse(form.is_valid())
