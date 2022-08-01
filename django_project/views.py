from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render
from django.contrib import messages
from django.core.mail import send_mail

from django.contrib.auth.models import User

from passwords.utils import get_subscriber

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from core.forms import RegisterForm

from .forms import ChangePasswordForm, UsernameForm, ForgotPasswordForm, ChangeEmailForm
from .models import ErrorLog


from passwords.forms import AddPasswordForm
from passwords.models import Subscriber, Password

from .utils import message_owner

import stripe, json

from django.conf import settings
stripe.api_key = settings.STRIPE_API_KEY


@login_required
def homepage_view(request):
    return redirect("passwords:homepage")


@login_required
def create_customer_portal_session(request):
    result = stripe.billing_portal.Session.create(
        customer=get_subscriber(request.user).customer_token,
        return_url="https://app.thepasslock.com",
    )
    return redirect(result["url"])
    # except Exception as e:
    #     ErrorLog.objects.create(
    #         user = request.user.username,
    #         description = f"Failed to create billing Portal Session!"
    #     )
    #     messages.error(request, "Cannot create billing session at this time, please contact PassLock support.")
    return redirect('django_project')


@csrf_exempt
def webhook_failed_billing_view(request):
    payload = request.body
    try:
        event = stripe.Event.construct_from(
            json.loads(payload), stripe.api_key
        )
        sub = Subscriber.objects.get(customer_token=event.data.object['customer'])
        sub.unsubscribe()
        message_owner(
            "Billing Error in PC App",
            "Billing for Subscription Failed | {0}".format(sub.user.email)
        )
    except ValueError as e:
        message_owner(
            "Billing Error in PC App",
            "Billing for Subscription Failed. See Stripe for more info!"
        )
        return HttpResponse(status=400)
    return HttpResponse(status=200)


@login_required
def profile_view(request):
    return render(
        request,
        "django_project/user_profile.html",
        {
            "subscriber": get_subscriber(request.user),
            "password_form": ChangePasswordForm(),
            "email_form": ChangeEmailForm(initial={"email": request.user.email}),
        },
    )


@login_required
def update_user_email(request):
    if request.method == "POST":
        user = request.user
        form = ChangeEmailForm(request.POST)
        if form.is_valid():
            user.username = form.cleaned_data['email']
            user.email = form.cleaned_data['email']
            user.save()
            messages.success(request, "Email changed successfully!")
        else:
            messages.error(request, f"Error, {request.POST['email']} is invalid or already in use!")
            return redirect('profile')

    return redirect('homepage')


@login_required
def update_user_password(request):
    if request.method == "POST":
        form = ChangePasswordForm(request.POST)

        if not form.is_valid():
            return render(
                request,
                "django_project/user_profile.html",
                {"subscriber": get_subscriber(request.user), "form": form},
            )

        # Save new info
        user = request.user
        user.set_password(form.cleaned_data["new_password"])
        user.save()
        messages.success(request, "Password updated successfully!")
    return redirect("passwords:homepage")
