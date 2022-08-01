from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_http_methods

from django.http import JsonResponse, HttpResponseForbidden, HttpResponse

from django.shortcuts import redirect, render

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from django.views.generic.edit import DeleteView, UpdateView

from django.core.exceptions import ObjectDoesNotExist

from django_project.models import ErrorLog

from .forms import AddPasswordForm, SearchForm, CreditCardForm, UpdatePasswordForm, FeedbackForm
from .models import Password, Settings, Subscriber
from .utils import get_subscriber, instant_unlock, get_settings

from django_project.utils import message_owner

from django.http import HttpResponseRedirect

import cryptography
from cryptography.fernet import Fernet

import json, stripe

from django.conf import settings
stripe.api_key = settings.STRIPE_API_KEY

# ------------------------------------------------------------------------------
# General Views
# ------------------------------------------------------------------------------
@login_required
def homepage_view(request):
    subscriber = get_subscriber(request.user)
    if subscriber.is_active_user():
        return render(
            request,
            "passwords/homepage.html",
            {
                "subscriber": subscriber,
                "password_form": AddPasswordForm(initial={'challenge_time':15, 'instant_unlock_enabled':True}),
                "search_form": SearchForm(),
                "passwords": subscriber.get_passwords(),
                "quick_retrieval_amount": get_settings().quick_retrieval_amount,
                "feedback_form": FeedbackForm()
            },
        )
    return redirect("passwords:subscribe")


@login_required
@require_http_methods(["POST"])
def send_feedback_view(request):
    form = FeedbackForm(request.POST)
    if not form.is_valid():
        return render(
            request,
            "passwords/homepage.html",
            {
                "subscriber": subscriber,
                "password_form": AddPasswordForm(initial={'challenge_time':15, 'instant_unlock_enabled':True}),
                "search_form": SearchForm(),
                "passwords": subscriber.get_passwords(),
                "quick_retrieval_amount": get_settings().quick_retrieval_amount,
                "feedback_form": form
            },
        )
    else:
        message_owner("New feedback from user {0}".format(request.user), "{0} says: {1}".format(request.user,form.cleaned_data['message']))
        messages.success(request, "Your feedback has been sent, and is greatly appreciated!")
    return redirect('homepage')


@login_required
@user_passes_test(lambda u: u.is_superuser)
def overview_view(request):
    num_free_trial = 0
    context = {
        "unsubscribed": len(Subscriber.objects.filter(subscription_active=False)),
        "subscribed": len(Subscriber.objects.filter(subscription_active=True)),
        "instant_unlocks": sum(Password.objects.all().values_list('number_of_instant_unlocks', flat=True)),
        "number_of_retrieves": sum(Password.objects.all().values_list('number_of_retrieves', flat=True)),
        "number_of_attempted_retrieves": sum(Password.objects.all().values_list('number_of_attempted_retrieves', flat=True)),
        "num_free_trial": len([i for i, x in enumerate(Subscriber.objects.all()) if x.free_trial_active()]),
        "num_passwords": len(Password.objects.all()),
        "subscribers": Subscriber.objects.all()
    }
    return render(request, 'passwords/overview.html', context)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def view_user(request, pk):
    context = {
        "subscriber": Subscriber.objects.get(pk=pk)
    }
    return render(request, 'passwords/subscriber.html', context)

# ------------------------------------------------------------------------------
# Subscription Views
# ------------------------------------------------------------------------------
@login_required
def subscribe_view(request):
    sub = get_subscriber(request.user)
    if sub.subscription_active:
        messages.error(request, "You are already subscribed, you cannot subscribe twice with the same account!")
        return redirect("passwords:homepage")
    context = {
        "cc_form": CreditCardForm(),
        "subscriber": get_subscriber(request.user)
    }
    return render(request, "passwords/subscribe.html", context)


@login_required
@require_http_methods(["POST"])
def handle_subscription_payment(request):
    if not get_subscriber(request.user).subscription_active:
        form = CreditCardForm(request.POST)
        if form.is_valid():
            try:
                sub = get_subscriber(request.user)
                sub.setup_customer()
                sub.create_payment_method(form.cleaned_data)
                sub.subscribe()
                messages.success(request, "You have subscribed successfully.")
                message_owner(
                    "New Subscription Signup",
                    "{0} | has succesfully subscribed!".format(sub.user.username)
                )
                return redirect('homepage')
            except stripe.error.CardError as e:
                messages.error(request, str(e).split(":")[1])
                return render(request, 'passwords/subscribe.html', {"cc_form": form})
            except stripe.error.InvalidRequestError:
                message_owner(
                    "URGENT | Subscription Error",
                    "Message app developer ASAP, something is going wrong with taking payments.\n Customer | {0}".format(sub.user.username)
                )
                messages.error(request, "Wow this is akward... Something funky is happening with our payment system. Contact our support team and we'll make it up to you: support@passwordchallenges.com")
        else:
            return render(request, 'passwords/subscribe.html', {"cc_form": form})
    else:
        messages.error(request, "While we're happy to recieve more money, you can't subscribe twice on the same account.")
    return HttpResponse(status=403)


@csrf_exempt
def webhook_unsubscribe(request):
    payload = request.body
    try:
        event = stripe.Event.construct_from(
            json.loads(payload), stripe.api_key
        )
        sub = Subscriber.objects.get(customer_token=event.data.object['customer'])
        sub.unsubscribe()
    except ValueError as e:
        message_owner(f"Unsubscribing error contact app support.")
        return HttpResponse(status=500)
    return HttpResponse(status=200)

# ------------------------------------------------------------------------------
# Password Storage/Management Views
# ------------------------------------------------------------------------------
@method_decorator(login_required, name="dispatch")
class DeletePasswordView(DeleteView):
    model = Password
    success_url = "/"

    def delete(self, *args, **kwargs):
        sub = get_subscriber(self.request.user)
        if sub.is_active_user():
            if self.get_object().subscriber.user == self.request.user:
                messages.success(
                    self.request,
                    'The password "{0}" has been deleted!'.format(str(self.get_object().get_name())),
                )
                return super(DeletePasswordView, self).delete(*args, **kwargs)
            else:
                ErrorLog.objects.create(
                    user = self.request.user.username,
                    description = f"Tried to delete password with ID: {self.get_object().pk}, which isn't theirs."
                )
                return HttpResponseForbidden()
        else:
            messages.error(
                self.request,
                'You are not an active subscriber, or your free trial has ended.',
            )
        return redirect('homepage')


@method_decorator(login_required, name="dispatch")
class UpdatePasswordNoInstantView(UpdateView):
    model = Password
    form_class = UpdatePasswordForm
    template_name_suffix = "_update_no_instant_form"
    success_url = "/"

    def get(self, request, **kwargs):
        sub = get_subscriber(self.request.user)
        if sub.is_active_user():
            if self.get_object().subscriber.user == self.request.user:
                return super(UpdatePasswordNoInstantView, self).get(request, **kwargs)
            else:
                messages.error(
                    self.request,
                    'You do not own this password, this attempt has been recorded!',
                )
                return HttpResponseForbidden()
        else:
            messages.error(
                self.request,
                'You are not an active subscriber, or your free trial has ended.',
            )
            return redirect('homepage')

    def post(self, request, **kwargs):
        sub = get_subscriber(self.request.user)
        if sub.is_active_user():
            if self.get_object().subscriber.user == self.request.user:
                return super(UpdatePasswordNoInstantView, self).post(request, **kwargs)
            else:
                messages.error(
                    self.request,
                    'You do not own this password, this attempt has been recorded!',
                )
                ErrorLog.objects.create(
                    user = request.user.username,
                    description = f"Tried to update password with ID: {pk}, which isn't theirs."
                )
                return HttpResponseForbidden()
        else:
            messages.error(
                self.request,
                'You are not an active subscriber, or your free trial has ended.',
            )
            return redirect('homepage')


@method_decorator(login_required, name="dispatch")
class UpdatePasswordView(UpdateView):
    model = Password
    form_class = UpdatePasswordForm
    template_name_suffix = "_update_form"
    success_url = "/"

    def get(self, request, **kwargs):
        sub = get_subscriber(self.request.user)
        if sub.is_active_user():
            if self.get_object().subscriber.user == self.request.user:
                return super(UpdatePasswordView, self).get(request, **kwargs)
            else:
                messages.error(
                    self.request,
                    'You do not own this password, this attempt has been recorded!',
                )
                return HttpResponseForbidden()
        else:
            messages.error(
                self.request,
                'You are not an active subscriber, or your free trial has ended.',
            )
            return redirect('homepage')

    def post(self, request, **kwargs):
        sub = get_subscriber(self.request.user)
        if sub.is_active_user():
            if self.get_object().subscriber.user == self.request.user:
                return super(UpdatePasswordView, self).post(request, **kwargs)
            else:
                messages.error(
                    self.request,
                    'You do not own this password, this attempt has been recorded!',
                )
                ErrorLog.objects.create(
                    user = request.user.username,
                    description = f"Tried to update password with ID: {pk}, which isn't theirs."
                )
                return HttpResponseForbidden()
        else:
            messages.error(
                self.request,
                'You are not an active subscriber, or your free trial has ended.',
            )
            return redirect('homepage')


@login_required
def store_password_view(request):
    subscriber = get_subscriber(request.user)
    if subscriber.is_active_user():
        if request.method == "POST":
            form = AddPasswordForm(request.POST)
            if form.is_valid():
                form.save(commit=False)
                form.instance.subscriber = subscriber
                form.save()
            else:
                return render(
                    request,
                    "passwords/homepage.html",
                    {
                        "password_form": form,
                        "show_errors": True,
                        "search_form": SearchForm(),
                        "passwords": subscriber.get_passwords(),
                    },
                )
    else:
        messages.error(request, "You must be subscribed to store a password")
    return redirect("passwords:homepage")


@login_required
def retrieve_password_view(request, pk):
    subscriber = get_subscriber(request.user)
    if not subscriber.is_active_user():
        messages.error(request, "You are not an active subscriber of this software, you cannot retrieve passwords at this time.")
        return redirect('homepage')
    try:
        password = subscriber.get_password(pk)
        password.number_of_retrieves = password.number_of_retrieves + 1
        password.save()
        return JsonResponse(
            {
                "password": password.get_password(),
                "username": password.get_username()
            },
            status=200
        )
    except Exception as e:
        ErrorLog.objects.create(
            user = request.user.username,
            description = f"Tried to access password with ID: {pk}, which isn't theirs."
        )
        return JsonResponse(
            {
                "error": "Something is wrong, either you do not have permission to access this password, or PassLock is experiencing issues. Please contact site support!"
            },
            status=403,
        )


@login_required
def instant_unlock_view(request, pk):
    sub = get_subscriber(request.user)
    if request.method == "POST":
        if not sub.subscription_active:
            unlock_cost = get_settings().quick_retrieval_amount
            messages.error(request, f"You are not a paid subscriber. Please become one to use the instant unlock feature. This costs ${unlock_cost} per use!")
        else:
            try:
                password = instant_unlock(request.user, pk)
                return render(
                    request,
                    "passwords/unlocked-password.html",
                    {
                        "password_form": AddPasswordForm(initial={'challenge_time':15, 'instant_unlock_enabled':True}),
                        "password": password
                    }
                )
            except ObjectDoesNotExist:
                ErrorLog.objects.create(
                    user = request.user.username,
                    description = f"Tried to instant unlock password with ID: {pk}, which isn't theirs."
                )
                messages.error(request, "You do not have permission to access this password, this attempt has been recorded.")
            except Exception as e:
                message_owner(
                    "URGENT | INSTANT UNLOCK PROBLEM",
                    "Contact: {0}, they are experiencing instant unlock problems! For Developer: {1}".format(sub.user.email, str(e))
                )
                messages.error(request, "There seems to be an issue with your billing information, please contact our support team at support@passwordchallenges.com")
    else:
        messages.error(request, "It seems you tried to instant unlock a password via the url bar, we wouldn't recommend doing this.")
        ErrorLog.objects.create(
            user = request.user.username,
            description = f"Tried to instant unlock password via URL Bar with ID: {pk}. User owns password: {sub.get_passwords().filter(pk=pk).exists()}"
        )
    return redirect('homepage')

# ------------------------------------------------------------------------------
# Password Logging/Reporting Views
# ------------------------------------------------------------------------------
@require_http_methods(["POST"])
@login_required
@csrf_exempt
def report_failed_retrieve(request, pk):
    try:
        password = get_subscriber(request.user).get_password(pk)
        password.number_of_attempted_retrieves = password.number_of_attempted_retrieves + 1
        password.save()
    except ObjectDoesNotExist:
        ErrorLog.objects.create(
            user = request.user.username,
            description = f"Report Failed Retrieve | Unauthorized access | User: {request.user}, Password ID: {pk}."
        )
    except Exception as e:
        message_owner("Passlock Reporting Error!", f"Failed to report password retrieval quitting, password pk: {pk}!")
    return JsonResponse({}, status=200)
