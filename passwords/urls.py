from django.conf.urls import url, include

from . import views

# Application Routes (URLs)

app_name = "passwords"

urlpatterns = [
    # General Page Views
    url(r"^$", views.homepage_view, name="homepage"),
    url(r"^overview$", views.overview_view, name="overview"),
    url(r"^send-feedback$", views.send_feedback_view, name="send_feedback"),
    url(r"^subscribe/$", views.subscribe_view, name="subscribe"),
    url(r"^handle-subscription-payment/$", views.handle_subscription_payment, name="handle_subscription_payment"),
    url(r"^webhook-unsubscribe/$", views.webhook_unsubscribe, name="webhook_unsubscribe"),
    url(r"^store-password/$", views.store_password_view, name="store_password"),
    url(
        r"^instant-unlock/(?P<pk>\d+)/$",
        views.instant_unlock_view,
        name="instant_unlock",
    ),
    url(
        r"^report-failed-retrieve/(?P<pk>\d+)/$",
        views.report_failed_retrieve,
        name="report_failed_retrieve",
    ),
    url(r"^view-user/(?P<pk>\d+)/$", views.view_user, name="view_user"),
    url(
        r"^delete-password/(?P<pk>\d+)/$",
        views.DeletePasswordView.as_view(),
        name="delete_password",
    ),
    url(
        r"^retrieve-password/(?P<pk>\d+)/$",
        views.retrieve_password_view,
        name="retrieve_password",
    ),
    url(
        r"^update-password/(?P<pk>\d+)/$",
        views.UpdatePasswordView.as_view(),
        name="update_password",
    ),
    url(
        r"^update-password-no-instant/(?P<pk>\d+)/$",
        views.UpdatePasswordNoInstantView.as_view(),
        name="update_password_no_instant",
    ),
]
