import os
import json

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open("secrets.json") as b:
    secrets = json.loads(b.read())

def get_secret(setting, secrets=secrets):
    """Get the secret variable or return explicit exception."""
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Set the {0} environment variable".format(setting)
        raise ImproperlyConfigured(error_msg)

# Application definition
INSTALLED_APPS = [
    'django_project',
    'core',
    'passwords',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'csp.middleware.CSPMiddleware',
]

ROOT_URLCONF = 'django_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'django_project.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = "US/Eastern"  # [Changed to local timezone]

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'

# Login Setting
LOGIN_URL = "core:login"

# Django CSP
# Keep our policy as strict as possible
# https://stackoverflow.com/questions/31635692/django-content-security-policy-directive

CSP_DEFAULT_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'", 'fonts.googleapis.com', 'maxcdn.bootstrapcdn.com', 'use.fontawesome.com',)
CSP_SCRIPT_SRC = ("'self'", 'www.redditstatic.com', 'cdn.mouseflow.com', 'ajax.googleapis.com', 'cdnjs.cloudflare.com', 'maxcdn.bootstrapcdn.com', 'www.google.com', 'www.gstatic.com', 'www.googletagmanager.com', 'www.google-analytics.com',)
CSP_FONT_SRC = ("'self'", 'fonts.gstatic.com', 'use.fontawesome.com',)
CSP_IMG_SRC = ("'self'", 'app.thepasslock.com', 'alb.reddit.com')
CSP_MEDIA_SRC = ("'self'",)
CSP_FRAME_SRC = ('www.google.com', 'thepasslock.com',)
CSP_CONNECT_SRC = ('n2.mouseflow.com', 'www.google-analytics.com', 'app.thepasslock.com', "'self'",)

# Stripe Integration
STRIPE_API_KEY = get_secret("STRIPE_API_KEY")

# ReCaptcha In
RECAPTCHA_SECRET_KEY = get_secret("RECAPTCHA_SECRET_KEY")
SILENCED_SYSTEM_CHECKS = ['captcha.recaptcha_test_key_error']
