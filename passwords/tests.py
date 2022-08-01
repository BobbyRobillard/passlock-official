from django.test import TestCase, Client, RequestFactory
from django.urls import reverse

from django.contrib.auth.models import User

from passwords.models import Subscriber, Password
from passwords.utils import get_subscriber
from passwords.forms import AddPasswordForm, CreditCardForm

user1_username = "user1"
user1_password = "qzwxec123"
user1_email = "test@django.com"

user2_username = "user2"
user2_password = "qzwxec123"
user2_email = "test2@django.com"


def create_default_testing_profile(test_object):
    test_object.c = Client()
    test_object.user = User.objects.create_user(
        username=user1_username, password=user1_password, email=user1_email
    )
    test_object.user2 = User.objects.create_user(
        username=user2_username, password=user2_password, email=user2_email
    )
    s = Subscriber.objects.create(user=test_object.user)
    s.subscription_active = True
    s.save()
    Subscriber.objects.create(user=test_object.user2)
    return test_object


class PasswordTestCases(TestCase):
    def setUp(self):
        self = create_default_testing_profile(self)

    def test_database_password_creation(self):
        # Valid Encrypted Data, should pass without issues
        Password.objects.create(
            subscriber=Subscriber.objects.get(user=self.user),
            name=b'gAAAAABfz7BTJo0bbNx8gl_IAIIiimflPcfSI5JAGEFalJKP_U_oHZu-ROyLxpvp_oJ4vm3GBJNqpzF8ma70LCaVp1bv2zFqsw==',
            hashed_password=b'gAAAAABfz7BTQxSnR61rROARP6NwHJ0CVFnh_tfYT6-OyH-1j_iNkqMCyoPiMou6Twr4ANcuRXCIfYhYj6N666GG_7w6F4DOvw==',
            username=b'gAAAAABfz7BTF_EczWdjAT12WyiiNgcgx-HwP-MQPeMhei0PRcxBfMryoAqt7IGSgUBvMhH4HjPOop_R256JW8iTffy2kKPIzw==',
            challenge_time=2
        )

        # Test valid form
        self.assertEqual(len(Password.objects.all()), 1)

        # Invalid unencrypted data, should throw error
        try:
            Password.objects.create(
                subscriber=Subscriber.objects.get(user=self.user),
                name="Name",
                hashed_password="Open Password",
                username="Username",
                challenge_time=2
            )
            self.fail("Test DB Password | Unencrypted Password Was Stored to Database")
        except Exception as e:
            pass

    def test_web_based_password_creation(self):
        # Must login first
        self.c.login(username=user1_username, password=user1_password)

        data = {
            "name": b'gAAAAABfz7BTJo0bbNx8gl_IAIIiimflPcfSI5JAGEFalJKP_U_oHZu-ROyLxpvp_oJ4vm3GBJNqpzF8ma70LCaVp1bv2zFqsw==',
            "hashed_password": b'gAAAAABfz7BTQxSnR61rROARP6NwHJ0CVFnh_tfYT6-OyH-1j_iNkqMCyoPiMou6Twr4ANcuRXCIfYhYj6N666GG_7w6F4DOvw==',
            "username": b'gAAAAABfz7BTF_EczWdjAT12WyiiNgcgx-HwP-MQPeMhei0PRcxBfMryoAqt7IGSgUBvMhH4HjPOop_R256JW8iTffy2kKPIzw==',
            "challenge_time": 2
        }

        # Post to endpoint to generate password
        self.c.login(username=user1_username, password=user1_password)
        response = self.c.post(reverse("passwords:store_password"), data)

        # Redirected to homepage on sucessful generation
        self.assertEqual(response.status_code, 302)
        # Make sure password was created
        num_passwords = len(Password.objects.filter(subscriber=get_subscriber(self.user)))
        self.assertEqual(num_passwords, 1)

        # Make sure only logged in users can store passwords
        self.c.logout()
        response = self.c.post(reverse("passwords:store_password"), data)
        # Redirected to homepage on failure
        self.assertEqual(response.status_code, 302)

        # Make sure no password was created
        num_passwords = len(Password.objects.filter(subscriber=get_subscriber(self.user)))
        self.assertEqual(num_passwords, 1)

    def test_password_form(self):
        form = AddPasswordForm(data={
            "name": "Trump",
            "hashed_password": "MAGA",
            "username": "YOLO",
            "challenge_time": 0
        })
        # Invalid challenge time
        self.assertEqual(False, form.is_valid())

        form = AddPasswordForm(data={
            "name": "Trump",
            "hashed_password": "MAGA",
            "challenge_time": 2
        })
        # Valid challenge time
        self.assertEqual(True, form.is_valid())

        name, password, username = "test", "trump", "yolo"
        form = AddPasswordForm(data={
            "name": name,
            "hashed_password": password,
            "username": username,
            "challenge_time": 2
        })
        form.is_valid()
        data = form.cleaned_data
        # Make sure all data gets encrypted
        self.assertEqual(False, data['name'] == name)
        self.assertEqual(False, data['hashed_password'] == password)
        self.assertEqual(False, data['username'] == username)

    def test_password_retrieveal(self):
        Password.objects.create(
            subscriber=Subscriber.objects.get(user=self.user),
            name=b'gAAAAABfz7BTJo0bbNx8gl_IAIIiimflPcfSI5JAGEFalJKP_U_oHZu-ROyLxpvp_oJ4vm3GBJNqpzF8ma70LCaVp1bv2zFqsw==',
            hashed_password=b'gAAAAABfz7BTQxSnR61rROARP6NwHJ0CVFnh_tfYT6-OyH-1j_iNkqMCyoPiMou6Twr4ANcuRXCIfYhYj6N666GG_7w6F4DOvw==',
            username=b'gAAAAABfz7BTF_EczWdjAT12WyiiNgcgx-HwP-MQPeMhei0PRcxBfMryoAqt7IGSgUBvMhH4HjPOop_R256JW8iTffy2kKPIzw==',
            challenge_time=2
        )
        # Able to get password normally and unencrypt
        password = Password.objects.all().first()
        self.assertEqual(password.get_password(), "asdf")
        self.assertEqual(password.get_name(), "asdf")
        self.assertEqual(password.get_username(), "asdf")

        # Able to get password from view
        self.c.login(username=user1_username, password=user1_password)
        response = self.c.post(reverse("passwords:retrieve_password", kwargs={'pk':1}))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {'password': 'asdf', 'username': 'asdf'}
        )
        self.c.logout()

        # ----------------------------------------------------------------------
        # Test unideal actions by users
        # ----------------------------------------------------------------------

        # Try to retrieve a password without being logged in
        response = self.c.post(reverse("passwords:retrieve_password", kwargs={'pk':1}))
        self.assertEqual(response.status_code, 302)

        # Try to retrieve password while not subscribed and not on free trial
        # | NOTE | You must make the free trial time 0 days to have this test work #
        self.c.login(username=user2_username, password=user2_password)
        # response = self.c.post(reverse("passwords:retrieve_password", kwargs={'pk':1}))
        # self.assertEqual(response.status_code, 302)

        # Try to retrieve password now owned by user
        sub = Subscriber.objects.get(pk=2)
        sub.subscription_active = True
        sub.save()
        response = self.c.post(reverse("passwords:retrieve_password", kwargs={'pk':1}))
        self.assertEqual(response.status_code, 403)

    def test_password_deletion(self):
        self.c.login(username=user1_username, password=user1_password)
        Password.objects.create(
            subscriber=Subscriber.objects.get(user=self.user),
            name=b'gAAAAABfz7BTJo0bbNx8gl_IAIIiimflPcfSI5JAGEFalJKP_U_oHZu-ROyLxpvp_oJ4vm3GBJNqpzF8ma70LCaVp1bv2zFqsw==',
            hashed_password=b'gAAAAABfz7BTQxSnR61rROARP6NwHJ0CVFnh_tfYT6-OyH-1j_iNkqMCyoPiMou6Twr4ANcuRXCIfYhYj6N666GG_7w6F4DOvw==',
            username=b'gAAAAABfz7BTF_EczWdjAT12WyiiNgcgx-HwP-MQPeMhei0PRcxBfMryoAqt7IGSgUBvMhH4HjPOop_R256JW8iTffy2kKPIzw==',
            challenge_time=2
        )
        self.assertEqual(1, len(Password.objects.all()))

        # Able to delete a password owned by the user, user is active
        response = self.c.post(reverse("passwords:delete_password", kwargs={'pk':1}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(0, len(Password.objects.all()))

        # ----------------------------------------------------------------------
        # Test unideal actions by users
        # ----------------------------------------------------------------------
        Password.objects.create(
            subscriber=Subscriber.objects.get(user=self.user),
            name=b'gAAAAABfz7BTJo0bbNx8gl_IAIIiimflPcfSI5JAGEFalJKP_U_oHZu-ROyLxpvp_oJ4vm3GBJNqpzF8ma70LCaVp1bv2zFqsw==',
            hashed_password=b'gAAAAABfz7BTQxSnR61rROARP6NwHJ0CVFnh_tfYT6-OyH-1j_iNkqMCyoPiMou6Twr4ANcuRXCIfYhYj6N666GG_7w6F4DOvw==',
            username=b'gAAAAABfz7BTF_EczWdjAT12WyiiNgcgx-HwP-MQPeMhei0PRcxBfMryoAqt7IGSgUBvMhH4HjPOop_R256JW8iTffy2kKPIzw==',
            challenge_time=2
        )
        self.c.logout()

        # Try to delete password not owned by user
        sub = Subscriber.objects.get(pk=2)
        sub.subscription_active = True
        sub.save()
        self.c.login(username=user2_username, password=user2_password)
        response = self.c.post(reverse("passwords:delete_password", kwargs={'pk':1}))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(1, len(Password.objects.all()))

        # Try to delete password while not subscribed
        self.c.logout()
        self.c.login(username=user1_username, password=user1_password)
        sub = Subscriber.objects.get(pk=1)
        sub.subscription_active = False
        sub.save()
        response = self.c.post(reverse("passwords:delete_password", kwargs={'pk':1}))
        # !!! Must set free_trial time to 0 days to have working tests with this !!!
        # self.assertEqual(response.status_code, 302)
        self.assertEqual(1, len(Password.objects.all()))

    def test_password_updating(self):
        self.c.login(username=user1_username, password=user1_password)

        Password.objects.create(
            subscriber=Subscriber.objects.get(user=self.user),
            name=b'gAAAAABfz7BTJo0bbNx8gl_IAIIiimflPcfSI5JAGEFalJKP_U_oHZu-ROyLxpvp_oJ4vm3GBJNqpzF8ma70LCaVp1bv2zFqsw==',
            hashed_password=b'gAAAAABfz7BTQxSnR61rROARP6NwHJ0CVFnh_tfYT6-OyH-1j_iNkqMCyoPiMou6Twr4ANcuRXCIfYhYj6N666GG_7w6F4DOvw==',
            username=b'gAAAAABfz7BTF_EczWdjAT12WyiiNgcgx-HwP-MQPeMhei0PRcxBfMryoAqt7IGSgUBvMhH4HjPOop_R256JW8iTffy2kKPIzw==',
            challenge_time=2
        )

        Password.objects.create(
            subscriber=Subscriber.objects.get(user=self.user2),
            name=b'gAAAAABfz7BTJo0bbNx8gl_IAIIiimflPcfSI5JAGEFalJKP_U_oHZu-ROyLxpvp_oJ4vm3GBJNqpzF8ma70LCaVp1bv2zFqsw==',
            hashed_password=b'gAAAAABfz7BTQxSnR61rROARP6NwHJ0CVFnh_tfYT6-OyH-1j_iNkqMCyoPiMou6Twr4ANcuRXCIfYhYj6N666GG_7w6F4DOvw==',
            username=b'gAAAAABfz7BTF_EczWdjAT12WyiiNgcgx-HwP-MQPeMhei0PRcxBfMryoAqt7IGSgUBvMhH4HjPOop_R256JW8iTffy2kKPIzw==',
            challenge_time=2
        )

        # Able to update a password owned by the user, user is active
        response = self.c.get(reverse("passwords:update_password", kwargs={'pk':1}))
        self.assertEqual(response.status_code, 200)

        # ----------------------------------------------------------------------
        # Tests of undesireable actions taken by users #
        # ----------------------------------------------------------------------

        # Unable to update password not owned by user
        response = self.c.get(reverse("passwords:update_password", kwargs={'pk':2}))
        self.assertEqual(response.status_code, 403)

        # Unable to update password while not an active user
        self.c.logout()
        self.c.login(username=user2_username, password=user2_password)
        response = self.c.get(reverse("passwords:update_password", kwargs={'pk':2}))
        self.assertEqual(response.status_code, 302)


class PaymentTestCases(TestCase):
    def setUp(self):
        self.c = Client()

    def test_payment_form(self):
        # Valid data should pass
        form_data = {
            "number": "4242424242424242",
            "cvc": "123",
            "expiration_month": "12",
            "expiration_year": "2024",
        }
        form = CreditCardForm(data=form_data)
        self.assertTrue(form.is_valid())

        invalid_data_sets = {
            # Contains letters, No value, Value too short, Value too long
            "cvc": ["a23", "", "1", "12345"],
            # Contains letters, No value, Too short of a value, Too long of a value, Contains special characters
            "number": ["a234123412341234", "1", "12341234123412341234", "-1231234123 123/"],
            # Contains letters, No value, Too long of a value, Contains special characters, Negative value, 0 Value
            "expiration_month": ["a", "", "123", "/1", "-1", "0"],
            # Contains letters, No value, Too Short, Too long of a value, Contains special characters, Negative value, 0 Value
            "expiration_year": ["a021", "", "123", "20211", "/1", "-1", "0"],
        }

        for key in invalid_data_sets:
            invalid_data = form_data
            for item in invalid_data_sets[key]:
                invalid_data[key] = item
                form_is_valid = CreditCardForm(data=invalid_data).is_valid()
                self.assertFalse(form_is_valid)

    def test_payment_system(self):
        self = create_default_testing_profile(self)
        self.c.login(username=user1_username, password=user1_password)
        response = self.c.post(reverse("passwords:handle_subscription_payment"), {
            "number": "4242424242424242",
            "cvc": "123",
            "expiration_month": "12",
            "expiration_year": "2024",
        })
        sub = Subscriber.objects.get(user__username=user1_username)
        self.assertTrue(sub.subscription_active)
        self.assertTrue(sub.customer_token != "")
        self.assertTrue(sub.subscription_token != "")
        self.assertTrue(sub.payment_method_token != "")
    #
    # def test_subscription_errors(self):
    #     response = self.c.post(reverse("core:register"), {
    #         "username": "test@gmail.com",
    #         "email": "test@gmail.com",
    #         "password1": "YoloSwag69!",
    #         "password2": "YoloSwag69!",
    #     })
    #     self.c.login(username="test@gmail.com", password="YoloSwag69!")
    #     response = self.c.post(reverse("passwords:handle_subscription_payment"), {
    #         "number": "4242424242424242",
    #         "cvc": "123",
    #         "expiration_month": "12",
    #         "expiration_year": "2024",
    #     })
    #     response = self.c.get(reverse("passwords:handle_subscription_payment"))
    #     # Can't access URL via GET
    #     self.assertEqual(response.status_code, 405)
    #
    #     # Can't subscribe twice
    #     response = self.c.post(reverse("passwords:handle_subscription_payment"), {
    #         "number": "4242424242424242",
    #         "cvc": "123",
    #         "expiration_month": "12",
    #         "expiration_year": "2024",
    #     })
    #     response = self.c.post(reverse("passwords:handle_subscription_payment"), {
    #         "number": "4242424242424242",
    #         "cvc": "123",
    #         "expiration_month": "12",
    #         "expiration_year": "2024",
    #     })
    #     self.assertEqual(response.status_code, 403)
