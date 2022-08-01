from django.http import JsonResponse

from .models import Subscriber, Settings

import stripe

from django.conf import settings
stripe.api_key = settings.STRIPE_API_KEY


# Gets subscriber or creates one if doesn't exist
def get_subscriber(user):
    return Subscriber.objects.get(user=user)


def get_settings():
    return Settings.objects.get(pk=1)


def instant_unlock(user, pk):
    # Retrieve sub and their password
    subscriber = get_subscriber(user)
    password = subscriber.get_password(pk)

    # Bill them for the unlock
    stripe.PaymentIntent.create(
        amount=(get_settings().quick_retrieval_amount * 100),
        currency="usd",
        payment_method=subscriber.payment_method_token,
        customer=subscriber.customer_token,
        confirm=True,
    )

    # Record for analytics
    password.number_of_instant_unlocks = password.number_of_instant_unlocks + 1
    password.save()

    # Return the password to them
    return password
