# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from datetime import date, datetime
import pytz

from django.test import TestCase
from django.urls import reverse

from apps.ads.models import Ad
from ..ads.forms import AdForm
from ..users.models import CustomUser

PASSWORD = "9tAQ6-EDFQGdt31"


def create_ad(
        first_name="mmd",
        last_name="mmdi",
        phone_number="09129121112",
        address="Tehran",
        start_time=date(2020, 9, 16),
        end_time=date(2021, 9, 16),
        service_type="1",
        gender="M",
        accepted=False,
        creator=None
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
        creator=creator
    )


class AdTest(TestCase):
    def setUp(self) -> None:
        self.test_user1 = CustomUser.objects.create(
            first_name="test_user1_fn",
            last_name="test_user1_ln",
            email="test_user1@test.com",
            phone_number="09123456781",
            username="test_user1",
        )
        self.test_user2 = CustomUser.objects.create(
            first_name="test_user2_fn",
            last_name="test_user2_ln",
            email="test_user2@test.com",
            phone_number="09123456782",
            username="test_user2",
        )

        self.admin = CustomUser.objects.create(
            first_name="admin",
            last_name="admin",
            email="admin@test.com",
            phone_number="09123456783",
            username="admin",
        )
        # set_password is necessary. If we set it in create function, it will set the hash not the password.
        self.test_user1.set_password(PASSWORD)
        self.test_user2.set_password(PASSWORD)
        self.admin.set_password(PASSWORD)
        self.admin.is_superuser = True

        self.test_ad1 = create_ad(first_name="test1",
                                  last_name="test1",
                                  phone_number="09129121112",
                                  address="Tehran",
                                  start_time=date(2020, 9, 16),
                                  end_time=date(2020, 9, 16),
                                  service_type="1",
                                  gender="M",
                                  accepted=False,
                                  creator=self.test_user1)
        self.test_ad2 = create_ad(first_name="test2",
                                  last_name="test2",
                                  phone_number="09129121112",
                                  address="Tehran",
                                  start_time=date(2020, 9, 16),
                                  end_time=date(2020, 9, 16),
                                  service_type="1",
                                  gender="M",
                                  accepted=False,
                                  creator=self.test_user2)

        self.test_user1.save()
        self.test_user2.save()
        self.admin.save()
        self.test_ad1.save()
        self.test_ad2.save()

    def test_ad_creation(self):
        test_ad = create_ad()
        self.assertTrue(isinstance(test_ad, Ad))
        info = (
            f"Ad info: {test_ad.address}, {test_ad.phone_number}, {test_ad.service_type}, {test_ad.start_time} until "
            f"{test_ad.end_time}"
        )
        self.assertEqual(test_ad.__str__(), info)

    def test_ad_creation_with_creator(self):
        self.assertTrue(isinstance(self.test_ad1, Ad))
        self.assertTrue(isinstance(self.test_user1, CustomUser))
        self.assertEqual(self.test_ad1.creator, self.test_user1)

    def test_ad_view_get(self):
        response = self.client.get(reverse("submit_ad"))
        self.assertEqual(response.status_code, 200)

    def test_ad_view_post(self):
        test_ad = create_ad()
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
        test_ad = create_ad()
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
        test_ad = create_ad(gender="A")
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

    def test_ad_delete_successfully_by_normal_user(self):
        credentials = {'username': "test_user1", 'password': PASSWORD}
        self.client.login(**credentials)
        test_ad1_id = self.test_ad1.id
        self.assertTrue(Ad.objects.filter(pk=test_ad1_id).count() == 1)
        self.client.get(reverse('delete', kwargs={'ad_id': test_ad1_id}))
        self.assertTrue(Ad.objects.filter(pk=test_ad1_id).count() == 0)

    def test_ad_delete_another_user_ad_unsuccessfully(self):
        credentials = {'username': "test_user2", 'password': PASSWORD}
        self.client.login(**credentials)
        test_ad1_id = self.test_ad1.id
        self.assertTrue(Ad.objects.filter(pk=test_ad1_id).count() == 1)
        self.client.get(reverse('delete', kwargs={'ad_id': test_ad1_id}))
        self.assertFalse(Ad.objects.filter(pk=test_ad1_id).count() == 0)

    def test_ad_delete_accepted_ad_by_normal_user_unsuccessfully(self):
        credentials = {'username': "test_user1", 'password': PASSWORD}
        self.client.login(**credentials)
        test_ad1_id = self.test_ad1.id
        self.test_ad1.accepted = True
        self.test_ad1.save()
        self.assertTrue(Ad.objects.filter(pk=test_ad1_id).count() == 1)
        self.client.get(reverse('delete', kwargs={'ad_id': test_ad1_id}))
        self.assertFalse(Ad.objects.filter(pk=test_ad1_id).count() == 0)

    def test_ad_delete_by_admin_successfully(self):
        credentials = {'username': "admin", 'password': PASSWORD}
        self.client.login(**credentials)
        test_ad1_id = self.test_ad1.id
        self.assertTrue(Ad.objects.filter(pk=test_ad1_id).count() == 1)
        self.client.get(reverse('delete', kwargs={'ad_id': test_ad1_id}))
        self.assertTrue(Ad.objects.filter(pk=test_ad1_id).count() == 0)

    def test_ad_delete_accepted_ad_by_admin_successfully(self):
        credentials = {'username': "admin", 'password': PASSWORD}
        self.client.login(**credentials)
        test_ad1_id = self.test_ad1.id
        self.test_ad1.accepted = True
        self.test_ad1.save()
        self.assertTrue(Ad.objects.filter(pk=test_ad1_id).count() == 1)
        self.client.get(reverse('delete', kwargs={'ad_id': test_ad1_id}))
        self.assertTrue(Ad.objects.filter(pk=test_ad1_id).count() == 0)

    def attempt_to_edit(self, credentials, ad_id):
        self.client.login(**credentials)
        payload = {
            'first_name': "New fn",
            'last_name': "New ln",
            'address': "New address",
            'phone_number': "09987654321",
            'start_time': datetime(2021, 9, 16, 10, 10, 10, 0, pytz.timezone("UTC")),
            'end_time': datetime(2021, 9, 17, 10, 10, 10, 0, pytz.timezone("UTC")),
            'service_type': "2",
            'gender': "W"
        }
        self.client.post(reverse('edit', kwargs={'ad_id': ad_id}), data=payload)
        edited_ad = Ad.objects.get(pk=ad_id)
        return edited_ad, payload

    def ad_equality_check(self, edited_ad, payload, is_equality=True):
        equality_function = self.assertEqual if is_equality else self.assertNotEqual
        equality_function(edited_ad.first_name, payload['first_name'])
        equality_function(edited_ad.last_name, payload['last_name'])
        equality_function(edited_ad.address, payload['address'])
        equality_function(edited_ad.phone_number, payload['phone_number'])
        equality_function(edited_ad.start_time, payload['start_time'])
        equality_function(edited_ad.end_time, payload['end_time'])
        equality_function(edited_ad.service_type, payload['service_type'])
        equality_function(edited_ad.gender, payload['gender'])

    def test_ad_edit_by_normal_user_successfully(self):
        credentials = {'username': "test_user1", 'password': PASSWORD}
        edited_ad, payload = self.attempt_to_edit(credentials, self.test_ad1.id)
        self.ad_equality_check(edited_ad, payload, True)

    def test_ad_edit_by_normal_user_another_user_ad_unsuccessfully(self):
        credentials = {'username': "test_user2", 'password': PASSWORD}
        edited_ad, payload = self.attempt_to_edit(credentials, self.test_ad1.id)
        self.ad_equality_check(edited_ad, payload, False)

    def test_ad_edit_by_admin_successfully(self):
        credentials = {'username': "admin", 'password': PASSWORD}
        previous_creator = self.test_ad1.creator
        edited_ad, payload = self.attempt_to_edit(credentials, self.test_ad1.id)
        self.assertEqual(edited_ad.creator, previous_creator)
        self.ad_equality_check(edited_ad, payload, True)
