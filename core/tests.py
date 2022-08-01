from django.urls import reverse
from django.test import TestCase, Client, RequestFactory

from django.contrib.auth.models import User

from django.test import TestCase, Client, TransactionTestCase

from django.db import transaction

from passwords.models import Subscriber, Password
from .forms import RegisterForm

class RegistrationTestCase(TransactionTestCase):
    def setUp(self):
        self.c = Client()

    def test_registration(self):
        # Valid credentials, account created
        response = self.c.post(reverse("core:register"), {
            "username": "test@gmail.com",
            "email": "test@gmail.com",
            "password1": "YoloSwag69!",
            "password2": "YoloSwag69!",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(1, len(User.objects.all()))
        self.assertEqual(1, len(Subscriber.objects.all()))
        self.assertEqual(1, len(Password.objects.all()))

        # Fail to create duplicate account
        response = self.c.post(reverse("core:register"), {
            "username": "test@gmail.com",
            "email": "test@gmail.com",
            "password1": "YoloSwag69!",
            "password2": "YoloSwag69!",
        })
        # Response code 200 because sent back to registration page
        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, len(User.objects.all()))
