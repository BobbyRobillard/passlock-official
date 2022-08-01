from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.auth import (
    login as auth_login,
    authenticate as auth_authenticate,
    logout as auth_logout,
)
from django.conf import settings
from django.core.exceptions import SuspiciousOperation

from django.contrib import messages

from .forms import RegisterForm
from .utils import setup_demo_password

from django_project.utils import message_owner

from django.conf import settings

import requests
import time


# Login
def login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            ''' Begin reCAPTCHA validation '''
            recaptcha_response = request.POST.get('g-recaptcha-response')
            data = {
                'secret': settings.RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }
            r = ''
            while r == '':
                # Make sure requests doesn't timeout recaptcha
                try:
                    r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
                    break
                except Exception as e:
                    time.sleep(3)
                    continue

            result = r.json()
            ''' End reCAPTCHA validation '''

            if result['success']:
                username = form.cleaned_data.get("username")
                raw_password = form.cleaned_data.get("password")
                user = auth_authenticate(username=username, password=raw_password)
                auth_login(request, user)
                next_page = request.GET.get("next", "homepage")
                return redirect(next_page)
    else:
        form = AuthenticationForm()

    context = {"form": form}
    return render(request, "registration/login_page.html", context)


# Logout
def logout(request):
    auth_logout(request)
    return redirect('homepage')


# Register a new user
def register(request):
    # Handle new user signup
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            ''' Begin reCAPTCHA validation '''
            recaptcha_response = request.POST.get('g-recaptcha-response')
            data = {
                'secret': settings.RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }
            r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
            result = r.json()
            ''' End reCAPTCHA validation '''

            if result['success']:
                form.save()
                setup_demo_password(form)
                messages.success(request, "Welcome to Passlock")
                auth_login(request, form.instance)
                message_owner("New User Signup", f"The user {request.POST['email']} just signed up!")
                return redirect("homepage")
    else:
        form = RegisterForm()

    # Display page to register
    return render(request, "registration/register.html", {"form": form})
