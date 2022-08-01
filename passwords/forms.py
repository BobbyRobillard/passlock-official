from django import forms

from .models import Password

from cryptography.fernet import Fernet

TIME_CHOICES = []
for i in range(5, 65, 5):
    TIME_CHOICES.append((i, f"{i} minutes"))


class AddPasswordForm(forms.ModelForm):

    username = forms.CharField(
                    required=False,
                    max_length=100,
                    label="Username (optional)"
                )

    class Meta:
        model = Password
        fields = ["name", "username", "hashed_password", "instant_unlock_enabled", "challenge_time", ]
        labels = {
            "name": "Password Name",
            "hashed_password": "Password to Store",
            "challenge_time": "Password Retrieval Time",
        }
        widgets = {
            "challenge_time": forms.Select(
                choices = (TIME_CHOICES),
            )
        }

    def clean_challenge_time(self):
        val = self.cleaned_data["challenge_time"]
        if val < 5 or val > 60:
            raise forms.ValidationError(
                "Challenge time must be between 5 and 60 minutes!"
            )
        return val

    def clean_name(self):  # Encrypt the submitted password
        # Get the key from the file
        file = open('key.key', 'rb')
        key = file.read()
        file.close()

        name = self.cleaned_data['name'].encode()
        fernet = Fernet(key)
        name = fernet.encrypt(name)
        return name

    def clean_username(self):  # Encrypt the submitted password
        # Get the key from the file
        file = open('key.key', 'rb')
        key = file.read()
        file.close()

        username = self.cleaned_data['username'].encode()
        fernet = Fernet(key)
        username = fernet.encrypt(username)
        return username

    def clean_hashed_password(self):  # Encrypt the submitted password
        # Get the key from the file
        file = open('key.key', 'rb')
        key = file.read()
        file.close()

        password = self.cleaned_data['hashed_password'].encode()
        fernet = Fernet(key)
        password = fernet.encrypt(password)
        return password


class UpdatePasswordForm(forms.ModelForm):
    class Meta:
        model = Password
        fields = ["name", "instant_unlock_enabled"]

    def clean_name(self):  # Encrypt the submitted password
        # Get the key from the file
        file = open('key.key', 'rb')
        key = file.read()
        file.close()

        name = self.cleaned_data['name'].encode()
        fernet = Fernet(key)
        name = fernet.encrypt(name)
        return name


class SearchForm(forms.Form):
    query = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Search Passwords..."})
    )


class CreditCardForm(forms.Form):
    number = forms.CharField(max_length=19)
    cvc = forms.CharField(max_length=4)
    expiration_month = forms.CharField(max_length=2, label="Expiration Month (XX)")
    expiration_year = forms.CharField(max_length=4, label="Expiration Year (XXXX)")

    def clean_expiration_year(self):
        expiration_year = self.cleaned_data['expiration_year']

        if not expiration_year.isnumeric():
            raise forms.ValidationError("Invalid expiration year.")

        if (len(expiration_year) is not 4):
            raise forms.ValidationError("Invalid expiration year.")

        return expiration_year

    def clean_expiration_month(self):
        expiration_month = self.cleaned_data['expiration_month']

        if not expiration_month.isnumeric():
            raise forms.ValidationError("Invalid expiration month.")

        if not (len(expiration_month) >= 1 and len(expiration_month) <= 2):
            raise forms.ValidationError("Invalid expiration month.")

        if (int(expiration_month) > 12) or (int(expiration_month) == 0):
            raise forms.ValidationError("Invalid expiration month.")

        return expiration_month

    def clean_cvc(self):
        cvc = self.cleaned_data['cvc']

        if not cvc.isnumeric():
            raise forms.ValidationError("This is not a valid cvc number.")

        if not (len(cvc) >= 3 and len(cvc) <= 4):
            raise forms.ValidationError("Invalid cvc number length.")

        return cvc

    def clean_number(self):
        number = self.cleaned_data['number']
        number = number.replace("-", "").replace("/", "").replace(" ", "")

        if not number.isnumeric():
            raise forms.ValidationError("This is not a valid number format.")

        if not (len(number) >= 15 and len(number) <= 16):
            raise forms.ValidationError("Invalid cc number length.")

        return number


class FeedbackForm(forms.Form):
    message = forms.CharField(max_length=500)
