from django.urls import path

from . import views
from .webhooks import my_webhook_view

app_name = "payments"

urlpatterns = [
    path(
        "subscription-plans",
        views.subscriptions_plans_list,
        name="subscriptions_plans_list",
    ),
    path("checkout-session", views.create_checkout_session, name="checkout_session"),
    path("success", views.payment_success, name="payment_success"),
    path("cancel", views.payment_cancel, name="payment_cancel"),
    path("webhook", my_webhook_view, name="webhook"),
    path("my-subscriptions", views.my_subscriptions, name="my_subscriptions"),
    path("cancel-susbcription", views.cancel_subscription, name="cancel_subscription"),
]
