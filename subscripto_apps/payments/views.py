import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from .models import Order, StripeCustomer, SubscriptionPlan
from .utils import create_new_customer


def subscriptions_plans_list(request):
    all_subscriptions = SubscriptionPlan.objects.filter(is_deleted=False).order_by(
        "subscription_order"
    )
    context = {"all_subscriptions": all_subscriptions}
    return render(request, "payments/all_subscriptions_list.html", context)


@login_required
@csrf_exempt
def create_checkout_session(request):
    if request.method == "POST":
        plan_id = request.POST.get("plan_id")
        domain_url = "http://localhost:8000/"
        stripe.api_key = settings.STRIPE_SECRET_KEY
        subscription = SubscriptionPlan.objects.get(id=plan_id)
        try:
            stripe_customer = StripeCustomer.objects.filter(user=request.user).first()
            if not stripe_customer:
                stripe_customer = StripeCustomer.objects.create(user=request.user)
            if not stripe_customer.stripeCustomerId:
                user_full_name = request.user.first_name + " " + request.user.last_name
                new_customer = create_new_customer(user_full_name, request.user.email)
                stripe_customer.stripeCustomerId = new_customer
                stripe_customer.save()
            checkout_session = stripe.checkout.Session.create(
                client_reference_id=request.user.id
                if request.user.is_authenticated
                else None,
                success_url=domain_url
                + "payments/success?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=domain_url + "payments/cancel/",
                payment_method_types=["card"],
                mode="subscription",
                customer=stripe_customer.stripeCustomerId,
                line_items=[
                    {
                        "price": subscription.stripe_price_id,
                        "quantity": 1,
                    }
                ],
            )
            order = Order(
                user=request.user,
                subscription=subscription,
                api_response=checkout_session,
                session_id=checkout_session.id,
                amount=round(subscription.price * 100),
                is_paid=False,
            )
            order.save()
            return redirect(checkout_session.url)
        except (Exception,) as e:
            messages.error(request, e)
            return redirect("payments:subscriptions_plans_list")


@login_required
def payment_success(request):
    return render(request, "payments/success.html")


@login_required
def payment_cancel(request):
    return render(request, "payments/cancel.html")
