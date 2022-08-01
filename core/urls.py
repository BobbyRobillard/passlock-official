from django.conf.urls import url

from . import views

# Application Routes (URLs)

app_name = "core"

urlpatterns = [
    # Login
    url(r"^login/$", views.login, name="login"),
    # Logout
    url(r"^logout/$", views.logout, name="logout"),
    # Register
    url(r"^register/$", views.register, name="register"),
]
