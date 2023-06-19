import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from .models import Order, StripeCustomer, SubscriptionPlan, UserSubscription
from .utils import check_subscription_status, create_new_customer


def subscriptions_plans_list(request):
    all_subscriptions = SubscriptionPlan.objects.filter(is_deleted=False).order_by(
        "subscription_order"
    )
    user_subscription_status = False
    if request.user.is_authenticated:
        user_subscription_status = check_subscription_status(request.user)
        if user_subscription_status:
            messages.info(request, "You already have an active subscription plan.")
    context = {
        "all_subscriptions": all_subscriptions,
        "user_subscription_status": user_subscription_status,
    }
    return render(request, "payments/all_subscriptions_list.html", context)


@login_required
@csrf_exempt
def create_checkout_session(request):
    if check_subscription_status(request.user):
        messages.info(request, "You already have an active subscription plan.")
        return redirect("base:home")
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
                if user_full_name == " ":
                    user_full_name = request.user.username
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


@login_required
def my_subscriptions(request):
    current_subscription = None
    all_user_subscriptions = UserSubscription.objects.filter(
        user=request.user
    ).order_by("-created_at")
    if all_user_subscriptions:
        current_subscription = all_user_subscriptions[0]
    return render(
        request,
        "payments/my_subscriptions.html",
        {
            "all_user_subscriptions": all_user_subscriptions,
            "current_subscription": current_subscription,
        },
    )


@login_required
def cancel_subscription(request):
    if request.method == "POST":
        if not check_subscription_status(request.user):
            messages.error(request, "No active subscription found")
            return redirect("payments:my_subscriptions")
        selected_subscription = request.POST.get("current_subscription")
        if selected_subscription:
            current_subscription = (
                UserSubscription.objects.filter(
                    user=request.user, id=selected_subscription
                )
                .order_by("-created_at")
                .first()
            )
            if current_subscription:
                stripe.api_key = settings.STRIPE_SECRET_KEY
                stripe.Subscription.modify(
                    current_subscription.stripe_subscription_id,
                    cancel_at_period_end=True,
                )
                current_subscription.is_cancelled = True
                current_subscription.save()
                messages.success(request, "Subscription cancelled.")
            else:
                messages.success(request, "Matching subscription ID not found.")
        else:
            messages.error(request, "No active subscription id found")
    return redirect("payments:my_subscriptions")
