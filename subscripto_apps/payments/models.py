from django.contrib.auth.models import User
from django.db import models

from subscripto_apps.base.models import TimeStampedModel, TimeStampedUUIDModel

# Create your models here.


class SubscriptionPlan(TimeStampedModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.FloatField()
    stripe_price_id = models.CharField(max_length=255, blank=True)
    SUBSCRIPTION_TYPES = (
        ("Day", "Day"),
        ("Month", "Month"),
        ("Year", "Year"),
    )
    subscription_type = models.CharField(
        choices=SUBSCRIPTION_TYPES, default="Monthly", max_length=255
    )
    subscription_order = models.IntegerField(default=1)
    is_deleted = models.BooleanField(default=True)

    def __str__(self):
        return "{} - {} ".format(self.name, self.id)

    class Meta:
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"
        ordering = ["-created_at"]


class StripeCustomer(TimeStampedUUIDModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    stripeCustomerId = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return "{} - {} ".format(self.user.username, self.id)

    class Meta:
        verbose_name = "Stripe Customer"
        verbose_name_plural = "Stripe Customers"
        ordering = ["-created_at"]


class Order(TimeStampedUUIDModel):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    subscription = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    amount = models.IntegerField()
    session_id = models.CharField(
        max_length=255, help_text="Received from stripe", blank=True, null=True
    )
    api_response = models.JSONField(blank=True, null=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return "{} - {} - {} - {}".format(self.id, self.user, self.amount, self.is_paid)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Order"
        verbose_name_plural = "  Orders"


class UserSubscription(TimeStampedUUIDModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subscription = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    stripe_subscription_id = models.CharField(max_length=255)
    valid_from = models.DateTimeField()
    valid_upto = models.DateTimeField()

    def __str__(self):
        return "{} - {}".format(self.user.email, self.subscription.name)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "User Subscription"
        verbose_name_plural = "User Subscriptions"
