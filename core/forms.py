from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

import re


class RegisterForm(UserCreationForm):
    agree_to_terms = forms.BooleanField(label="I Have Read and Agree to the Following Terms & Conditions of Use")

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2", "agree_to_terms"]
        labels = {
            "username": "Email",
            "email": "Email Confirmation",
            "password2": "Enter Password Again",
        }

    def clean(self):
        data = self.cleaned_data
        if not re.match(r"[^@]+@[^@]+\.[^@]+", data['username']):
            raise forms.ValidationError({"username": "This is not an email address!"})

        if data['username'] != data['email']:
            raise forms.ValidationError({"email": "Emails must match!"})

        if User.objects.filter(username=data['username']).exists():
            raise forms.ValidationError({"username": "This email is already in use!"})

        return data
