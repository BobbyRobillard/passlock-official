import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings.production')
os.environ['HTTPS'] = "on"

application = get_wsgi_application()
