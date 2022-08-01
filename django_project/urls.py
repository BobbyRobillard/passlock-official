from django.conf.urls import url, include
from django.urls import path
from django.contrib import admin

from django.contrib.auth import views as auth_views

from . import views


urlpatterns = [
    path('', views.homepage_view, name='homepage'),
    path('admin/', admin.site.urls),
    url(r"^passwords/", include("passwords.urls")),
    url(r"^auth/", include("core.urls")),
    url(r"^failed-billing/$", views.webhook_failed_billing_view, name="webhook_failed_billing"),
    url(
        r"^customer-portal-session$",
        views.create_customer_portal_session,
        name="create_customer_portal_session",
    ),
    url(r"^profile$", views.profile_view, name="profile"),
    url(r"^update-user-email$", views.update_user_email, name="update_user_email"),
    url(r"^update-user-password$", views.update_user_password, name="update_user_password"),
    # Auth stuff.
    path(
        "password-reset/", auth_views.PasswordResetView.as_view(), name="password_reset"
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
]
