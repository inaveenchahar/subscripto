from django.contrib import admin

from .models import Order, StripeCustomer, SubscriptionPlan

# Register your models here.


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "id",
        "subscription_type",
        "price",
        "is_deleted",
        "created_at",
        "updated_at",
    ]
    list_filter = ["is_deleted", "subscription_type", "created_at", "updated_at"]
    search_fields = ["name", "description"]


@admin.register(StripeCustomer)
class StripeCustomerAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "id",
        "stripeCustomerId",
        "created_at",
        "updated_at",
    ]
    list_filter = ["created_at", "updated_at"]
    search_fields = ["user.username", "user.email", "stripeCustomerId"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "subscription",
        "amount",
        "is_paid",
        "created_at",
        "updated_at",
    ]
    list_filter = [
        "is_paid",
        "subscription__name",
        "created_at",
        "updated_at",
    ]
    search_fields = ["id", "user__id", "user__email"]
