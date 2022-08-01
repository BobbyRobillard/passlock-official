from .base import *


with open("production-secrets.json") as ps:
    production_secrets = json.loads(ps.read())

def get_production_secret(setting, production_secrets=production_secrets):
    """Get the secret variable or return explicit exception."""
    try:
        return production_secrets[setting]
    except KeyError:
        error_msg = "Set the {0} environment variable".format(setting)
        raise ImproperlyConfigured(error_msg)


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_production_secret("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Find out what the IP addresses are at run time
# This is necessary because otherwise Gunicorn will reject the connections
def ip_addresses():
    ip_list = []
    for interface in netifaces.interfaces():
        addrs = netifaces.ifaddresses(interface)
        for x in (netifaces.AF_INET, netifaces.AF_INET6):
            if x in addrs:
                ip_list.append(addrs[x][0]['addr'])
    return ip_list

ALLOWED_HOSTS = ip_addresses() + ["app.thepasslock.com"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': get_production_secret("DB_NAME"),
        'USER': get_production_secret("DB_USER"),
        'PASSWORD': get_production_secret("DB_PASSWORD"),
        'HOST': get_production_secret("DB_HOST"),
        'PORT': '',
    }
}

EMAIL_USE_TLS = True
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = get_production_secret("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = get_production_secret("EMAIL_HOST_PASSWORD")
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = "no-reply@app.thepasslock.com"

# Django Deployment Checklist Items
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_SECONDS = 172_800

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True


X_FRAME_OPTIONS = 'DENY'
