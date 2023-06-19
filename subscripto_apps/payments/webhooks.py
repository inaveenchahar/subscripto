from datetime import datetime

import stripe
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt

from .models import Order, StripeCustomer, SubscriptionPlan, UserSubscription


@csrf_exempt
def my_webhook_view(request):
    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
    event = None

    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_ENDPOINT_SECRET
        )
    except ValueError:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return HttpResponse(status=400)
    print("**" * 20, event["type"], "**" * 20)
    if event.type == "invoice.payment_succeeded":
        session = event["data"]["object"]
        add_user_subscription_record(session)

    # Handle the checkout.session.completed event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        # Check if the order is already paid (for example, from a card payment)
        #
        # A delayed notification payment will have an `unpaid` status, as
        # you're still waiting for funds to be transferred from the customer's
        # account.
        if session.payment_status == "paid":
            # Fulfill the purchase
            fulfill_order(session)

    elif event["type"] == "checkout.session.async_payment_succeeded":
        session = event["data"]["object"]
        # Fulfill the purchase
        fulfill_order(session)

    elif event["type"] == "checkout.session.async_payment_failed":
        # session = event['data']['object']
        pass

    # Passed signature verification
    return HttpResponse(status=200)


def fulfill_order(session):
    order = Order.objects.filter(session_id=session.id).first()
    if order:
        if order.is_paid:
            return redirect("payments:success")
        elif session.payment_status == "paid":
            order.is_paid = True
            order.save()


def add_user_subscription_record(session):
    stripe_customer = StripeCustomer.objects.get(stripeCustomerId=session.customer)
    price_id = session["lines"]["data"][0]["price"]["id"]
    subscription = SubscriptionPlan.objects.get(stripe_price_id=price_id)
    UserSubscription.objects.create(
        user=stripe_customer.user,
        subscription=subscription,
        stripe_subscription_id=session.get("subscription"),
        valid_from=datetime.utcfromtimestamp(
            session["lines"]["data"][0]["period"]["start"]
        ),
        valid_upto=datetime.utcfromtimestamp(
            session["lines"]["data"][0]["period"]["end"]
        ),
    )
