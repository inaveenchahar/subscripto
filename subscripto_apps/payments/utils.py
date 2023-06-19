import datetime

import stripe

from .models import UserSubscription


def create_new_customer(name, email):
    new_customer = stripe.Customer.create(email=email, name=name)
    return new_customer["id"]


def user_subscription_details(user):
    data = {"name": None, "valid_from": None, "valid_upto": None, "is_active": False}
    if UserSubscription.objects.filter(
        valid_upto__gte=datetime.datetime.now(), user=user
    ).exists():
        user_subscription = (
            UserSubscription.objects.filter(
                valid_upto__gte=datetime.datetime.now(), user=user
            )
            .order_by("-created_at")
            .first()
        )
        data = {
            "name": user_subscription.subscription.name,
            "valid_from": user_subscription.valid_from,
            "valid_upto": user_subscription.valid_upto,
            "is_active": True,
        }
    return data


def check_subscription_status(user):
    if UserSubscription.objects.filter(
        valid_upto__gte=datetime.datetime.now(), user=user
    ).exists():
        return True
    return False
