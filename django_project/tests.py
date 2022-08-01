from django.test import TestCase, Client, RequestFactory
from django.urls import reverse

from django.contrib.auth.models import User

from .forms import ChangeSettingsForm
from passwords.models import Subscriber

user1_username = "user1"
user1_password = "qzwxec123"
user1_email = "test@django.com"


def create_default_testing_profile(test_object):
    test_object.c = Client()
    test_object.user = User.objects.create_user(
        username=user1_username, password=user1_password, email=user1_email
    )
    test_object.subscriber = Subscriber.objects.create(user=test_object.user)
    return test_object


class ProfileTestCase(TestCase):
    def setUp(self):
        self = create_default_testing_profile(self)

    def test_email_form(self):
        form = ChangeSettingsForm(data={
                "email": "Maga2020@gmail.com",
                "new_password": user1_password,
                "confirm_password": user1_password,
            }
        )
        # Test valid form
        self.assertEqual(
            form.is_valid(), True
        )

        # Test duplicate email
        form = ChangeSettingsForm(data={
                "email": user1_email,
                "new_password": user1_password,
                "confirm_password": "asd",
            }
        )

        self.assertEqual(
            form.errors["email"], ["This email is already in use."]
        )

        # Test non-matching passwords
        form = ChangeSettingsForm(data={
                "email": "obama@gmail.com",
                "new_password": "asdf",
                "confirm_password": user1_password,
            }
        )

        self.assertEqual(
            form.errors['__all__'], ['Error, passwords are not the same!']
        )
    # def test_set_invalid_current_profile(self):
    #     self.c.login(username=user1_username, password=user1_password)
    #     response = self.c.post(reverse("macros:set_current_profile", kwargs={"pk": 3}))
    #     self.assertEqual(response.status_code, 404)
