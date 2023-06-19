from django.urls import path

from . import views

app_name = "base"

urlpatterns = [
    path("", views.homepage, name="home"),
    path("premium-content", views.premium_page, name="premium_content"),
]
