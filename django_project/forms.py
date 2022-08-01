from django import forms
from django.contrib.auth.models import User


class ChangePasswordForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    def clean(self):
        data = self.cleaned_data
        if data["new_password"] != data["confirm_password"]:
            raise forms.ValidationError("Error, passwords are not the same!")
        return data


class ChangeEmailForm(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use!")
        return email


class UsernameForm(forms.Form):
    email = forms.EmailField()


class ForgotPasswordForm(forms.Form):
    username = forms.CharField(max_length=50)
