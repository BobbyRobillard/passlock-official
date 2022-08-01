from datetime import date

from django.db import models

from django.contrib.auth.models import User

from django_project.utils import message_owner

import cryptography
from cryptography.fernet import Fernet

import datetime
import stripe

from django.conf import settings
stripe.api_key = settings.STRIPE_API_KEY


# Create your models here.
class Subscriber(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sign_up_date = models.DateField(auto_now=False, auto_now_add=True)
    customer_token = models.CharField(max_length=150, null=True, blank=True)
    payment_method_token = models.CharField(max_length=150, null=True, blank=True)
    subscription_token = models.CharField(max_length=150, null=True, blank=True)
    subscription_active = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    def get_next_payment_date(self):
        subscription = stripe.Subscription.retrieve(self.subscription_token)
        dt_object = datetime.datetime.fromtimestamp(subscription.current_period_end)
        # Keep only date, split on seperator
        date_split = str(dt_object).split(" ")[0].split("-")
        month_names = {
            "01" : "January",
            "02" : "February",
            "03" : "March",
            "04" : "April",
            "05" : "May",
            "06" : "June",
            "07" : "July",
            "08" : "August",
            "09" : "September",
            "10" : "October",
            "11" : "November",
            "12" : "December",
        }
        month, day, year = month_names[date_split[1]], date_split[2], date_split[0]
        return ("{0} {1}, {2}".format(month, day, year))

    def create_payment_method(self, cc_data):
        # Get or create payment method to attach to customer
        method = stripe.PaymentMethod.create(
            type="card",
            card={
                "number": cc_data['number'],
                "exp_month": cc_data['expiration_month'],
                "exp_year": cc_data['expiration_year'],
                "cvc": cc_data['cvc'],
            },
        )
        self.payment_method_token = method.id
        stripe.PaymentMethod.attach(method.id, customer=self.customer_token)
        self.save()

    def setup_customer(self):
        customer = stripe.Customer.create(
            description="Subscriber: {0}".format(self.user.email)
        )
        self.customer_token = customer.id
        self.save()

    def subscribe(self):
        subscription = stripe.Subscription.create(
            customer=self.customer_token,
            default_payment_method=self.payment_method_token,
            items=[{"price": "price_1IDw3zIg6R6ckEviN31BCa8C"}],
        )
        self.subscription_token = subscription.id
        self.subscription_active = True

        # Save all new tokens
        self.save()

    def unsubscribe(self):
        try:
            stripe.Subscription.delete(self.subscription_token)
        except Exception as e:
            pass

        self.subscription_token = None
        self.customer_token = None
        self.payment_method_token = None
        self.subscription_active = False
        self.save()

        message_owner(
            "User Unsubscribed!",
            "We lost one boys: {0}".format(self.user.email)
        )

    def free_trial_active(self):
        # If the user has been registered for longer than 30 days, or is subscribed
        if self.subscription_active:
            return False
        free_trial_length = Settings.objects.get(pk=1).free_trial_length
        return (datetime.datetime.now().date() - self.sign_up_date).days < free_trial_length

    def get_free_trial_end_date(self):
        # Return the date 30 days after a free trial starts
        free_trial_length = Settings.objects.get(pk=1).free_trial_length
        return self.sign_up_date + datetime.timedelta(days=free_trial_length)

    def is_active_user(self):
        return self.free_trial_active() or self.subscription_active

    def get_passwords(self):
        return Password.objects.filter(subscriber=self)

    def get_password(self, pk):
        return Password.objects.get(pk=pk, subscriber=self)

    def get_num_free_trial_days(self):
        return 30 - (datetime.datetime.now().date() - self.sign_up_date).days


class Password(models.Model):
    subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE)
    name = models.BinaryField(max_length=300, editable=True)
    username = models.BinaryField(max_length=300, editable=True)
    hashed_password = models.BinaryField(max_length=300, editable=True)
    challenge_time = models.PositiveIntegerField(default=True)
    instant_unlock_enabled = models.BooleanField(default=True)
    number_of_retrieves = models.PositiveIntegerField(default=0)
    number_of_instant_unlocks = models.PositiveIntegerField(default=0)
    number_of_attempted_retrieves = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.get_name()

    def get_name(self):
        file = open('key.key', 'rb')
        key = file.read()
        file.close()

        # Need this because postgress converts the bytes to memoryview objects
        # Example and explanation found here: https://www.programiz.com/python-programming/methods/built-in/memoryview
        name = bytes(self.name[0:len(self.name)])

        fernet = Fernet(key)
        decrypted = fernet.decrypt(name)
        return decrypted.decode("utf-8")

    def get_username(self):
        file = open('key.key', 'rb')
        key = file.read()
        file.close()

        username = bytes(self.username[0:len(self.username)])

        fernet = Fernet(key)
        decrypted = fernet.decrypt(username)
        return decrypted.decode("utf-8")

    def get_password(self):
        file = open('key.key', 'rb')
        key = file.read()
        file.close()

        hashed_password = bytes(self.hashed_password[0:len(self.hashed_password)])

        fernet = Fernet(key)
        decrypted = fernet.decrypt(hashed_password)
        return decrypted.decode("utf-8")


class Settings(models.Model):
    def __str__(self):
        return "Main Application Settings"

    subscription_amount = models.PositiveIntegerField(default=1)
    free_trial_length = models.PositiveIntegerField(default=30)
    quick_retrieval_amount = models.PositiveIntegerField(default=20)
