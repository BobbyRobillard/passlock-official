from django.contrib import admin

from .models import Subscriber, Password, Settings

# Register your models here.
admin.site.register(Subscriber)
admin.site.register(Password)
admin.site.register(Settings)
