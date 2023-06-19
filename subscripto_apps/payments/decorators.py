# Standard Library
import datetime

from django.contrib import messages
from django.shortcuts import redirect
# Third Party Stuff
from django.utils import timezone

from .models import UserSubscription


def active_subscription_required(function):
    def wrap(request, *args, **kwargs):
        if UserSubscription.objects.filter(
            user=request.user, valid_upto__gte=datetime.datetime.now()
        ):
            return function(request, *args, **kwargs)
        else:
            messages.info(request, "You need active subscription plan to see this page")
            return redirect("payments:my_subscriptions")

    return wrap
