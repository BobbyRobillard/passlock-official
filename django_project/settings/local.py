from .base import *


with open("local-secrets.json") as ls:
    local_secrets = json.loads(ls.read())

def get_local_secret(setting, local_secrets=local_secrets):
    """Get the secret variable or return explicit exception."""
    try:
        return local_secrets[setting]
    except KeyError:
        error_msg = "Set the {0} environment variable".format(setting)
        raise ImproperlyConfigured(error_msg)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_local_secret("SECRET_KEY")

DEBUG = True

ALLOWED_HOSTS = ["*"]

# Email Backend
EMAIL_HOST = "localhost"
EMAIL_PORT = 1025

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': get_local_secret("DB_NAME"),
        'USER': get_local_secret("DB_USER"),
        'PASSWORD': get_local_secret("DB_PASSWORD"),
        'HOST': get_local_secret("DB_HOST"),
        'PORT': '',
    }
}
