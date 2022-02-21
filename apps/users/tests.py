# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.test.client import Client
import mock
from django.test import TestCase
from django.core.files import File
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from model_bakery import baker

from apps.ads.models import AdReview
from .models import CustomUser, Nurse
from .forms import LoginForm, RegisterForm
from .views import USERNAME_EXISTS_ERROR_MSG, EMAIL_EXISTS_ERROR_MSG, PHONE_EXISTS_ERROR_MSG

PASSWORD = "ZrPgASE-123"

DUPLICATE_ERROR_MSG = {'email': EMAIL_EXISTS_ERROR_MSG, 'phone_number': PHONE_EXISTS_ERROR_MSG,
                       'username': USERNAME_EXISTS_ERROR_MSG}


class CustomUserTest(TestCase):
    def create_cu(
            self,
            first_name="mmd",
            last_name="mmdi",
            username="mmd.mmdi",
            password="mmdpass",
            email="mmd@gmail.com",
            phone_number="09129121112",
    ):
        return CustomUser.objects.create(
            first_name=first_name,
            last_name=last_name,
            username=username,
            password=password,
            email=email,
            phone_number=phone_number,
        )

    def test_cu_creation(self):
        test_cu = self.create_cu()
        self.assertTrue(isinstance(test_cu, CustomUser))
        info = test_cu.username
        self.assertEqual(test_cu.__str__(), info)


class NurseTest(TestCase):
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
        response = self.client.get(reverse('init'))
        self.assertEqual(response.status_code, 200)

    def test_login_view_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_register_view_get(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_valid_Loginform(self):
        data = {
            "username": "mmd",
            "password": "mmdpass",
            'g-recaptcha-response': "test"
        }
        form = LoginForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_Registerform(self):
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
        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())

    def duplicate_tester(self, field):
        data = {
            'first_name': "test",
            'last_name': "test",
            'username': "test",
            'email': "a@a.com",
            'password1': PASSWORD,
            'password2': PASSWORD,
            'phone_number': "09123456789",
            'g-recaptcha-response': "test"
        }
        self.client.post("%s?type=user" % reverse('register'), data)
        self.assertTrue(CustomUser.objects.filter(username="test").exists())
        data['username'] = "test2" if field != 'username' else data['username']
        data['email'] = "a2@a.com" if field != 'email' else data['email']
        data['phone_number'] = "09123456789" if field != 'phone_number' else data['phone_number']
        response = self.client.post("%s?type=user" % reverse('register'), data)
        self.assertEqual(response.context['msg'], DUPLICATE_ERROR_MSG[field])

    def test_duplicate_email(self):
        self.duplicate_tester('email')

    def test_duplicate_phone(self):
        self.duplicate_tester('phone_number')

    def test_duplicate_username(self):
        self.duplicate_tester('username')

    def test_register_and_login_view(self):
        doc = SimpleUploadedFile(
            "doc.png", b"test_file_content", content_type="image/png")
        data = {
            'first_name': "mmd",
            'last_name': "mmdi",
            'username': "mmd.mmdi",
            'password1': "AAdfwr321DA",
            'password2': "AAdfwr321DA",
            'email': "mmd@gmail.com",
            'document': doc,
            'phone_number': "09129121112",
            'g-recaptcha-response': "test"
        }

        # test register
        response = self.client.post(reverse('register'), data=data)
        self.assertEqual(response.status_code, 200)

        users = Nurse.objects.filter(username=data['username'])
        self.assertEqual(users.count(), 1)

        self.assertEqual(users[0].first_name, data['first_name'])
        self.assertEqual(users[0].last_name, data['last_name'])
        self.assertEqual(users[0].phone_number, data['phone_number'])
        self.assertEqual(users[0].email, data['email'])
        self.assertIsNotNone(users[0].document)

        # test wrong password for login
        data2 = {
            'username': data['username'],
            'password': 'wrong_pass',
            'g-recaptcha-response': "test"
        }
        response = self.client.post(reverse('login'), data=data2)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['user'].is_active)

        # test correct password for login
        data3 = {
            'username': data['username'],
            'password': data['password1'],
            'g-recaptcha-response': "test"
        }
        response = self.client.post(reverse('login'), data=data3)
        self.assertEqual(response.status_code, 302)


class ProfileTest(TestCase):
    def setUp(self):
        self.user_non_admin = CustomUser.objects.create(username='nurse',
                                                        email='nurse@email.com',
                                                        password='',
                                                        first_name='a',
                                                        last_name='b',
                                                        phone_number='09125004323',
                                                        is_superuser=False)
        self.user_non_admin.set_password('secret')
        self.user_non_admin.save()

        self.nurses = baker.make(Nurse, _quantity=5)
        baker.make(AdReview, nursead__nurse=self.nurses[0], score=4, _quantity=10)

    def test_edit_profile(self):
        self.client = Client()
        self.client.login(username='nurse', password='secret')

        data = {
            'first_name': "new_a",
            'last_name': "new_b",
            'username': "new_username",  # this should not change
            'email': "new_email@ema.com",
            'phone_number': "09125004399",
        }

        response = self.client.post(reverse('user-profile'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your profile was successfully updated!')

        users = CustomUser.objects.filter(username='nurse')
        self.assertEqual(users.count(), 1)

        self.assertEqual(users[0].first_name, data['first_name'])
        self.assertEqual(users[0].last_name, data['last_name'])
        self.assertEqual(users[0].phone_number, data['phone_number'])
        self.assertEqual(users[0].email, data['email'])

    def test_edit_profile_image(self):
        self.client = Client()
        self.client.login(username='nurse', password='secret')

        self.assertEqual(self.user_non_admin.get_avatar_url(), "/static/assets/img/default-avatar.png")

        with open("./apps/static/assets/img/default-avatar.png", "rb") as f:
            test_content = f.read()

        img = SimpleUploadedFile("doc.png", test_content, content_type="image/png")
        data = {
            'first_name': "new_a",
            'last_name': "new_b",
            'username': "new_username",  # this should not change
            'email': "new_email@ema.com",
            'phone_number': "09125004399",
            'avatar': img,
        }

        response = self.client.post(reverse('user-profile'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your profile was successfully updated!')

        users = CustomUser.objects.filter(username='nurse')
        self.assertEqual(users.count(), 1)

        self.assertEqual(users[0].first_name, data['first_name'])
        self.assertEqual(users[0].last_name, data['last_name'])
        self.assertEqual(users[0].phone_number, data['phone_number'])
        self.assertEqual(users[0].email, data['email'])
        self.assertNotEqual(users[0].get_avatar_url(), "/static/assets/img/default-avatar.png")

    def test_edit_password(self):
        self.client = Client()
        self.client.login(username='nurse', password='secret')

        data = {
            'old_password': "secret",
            'new_password1': "new_secret",
            'new_password2': "new_secret",  # this should not change
        }

        response = self.client.post(reverse('change-password'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your password was successfully updated!')

        users = CustomUser.objects.filter(username='nurse')
        self.assertEqual(users.count(), 1)

        self.client.logout()
        self.assertTrue(self.client.login(username='nurse', password='new_secret'))


class NurseListTest(TestCase):
    def setUp(self):
        self.user_admin = CustomUser.objects.create(username='admin', email='admin@email.com', password='',
                                                    is_superuser=True)
        self.user_admin.set_password('secret')
        self.user_admin.save()

        self.user_non_admin = CustomUser.objects.create(username='nurse', email='nurse@email.com', password='',
                                                        is_superuser=False)
        self.user_non_admin.set_password('secret')
        self.user_non_admin.save()

        self.nurses = baker.make(Nurse, _quantity=5)
        baker.make(AdReview, nursead__nurse=self.nurses[0], score=4, _quantity=10)

    def test_get_nurse_locations_view_not_logged_in(self):
        self.client = Client()
        self.client.logout()
        response = self.client.get(reverse('nurse-list'))
        self.assertEqual(response.status_code, 302)

    def test_get_nurse_locations_view_admin(self):
        self.client = Client()
        self.client.login(username='admin', password='secret')
        response = self.client.get(reverse('nurse-list'))
        self.assertEqual(response.status_code, 200)
        for nurse in self.nurses:
            self.assertContains(response, nurse.username)

        self.assertContains(response, '4.0 / 5.0')

    def test_get_nurse_locations_view_nurse(self):
        self.client = Client()
        self.client.login(username='nurse', password='secret')
        response = self.client.get(reverse('nurse-list'))
        self.assertEqual(response.status_code, 302)
