from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from subscripto_apps.payments.decorators import active_subscription_required


def homepage(request):
    return render(request, "base/home.html")


@login_required
@active_subscription_required
def premium_page(request):
    return render(request, "base/premium_page.html")
