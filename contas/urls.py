from django.urls import path

from .views import EuView, LoginView

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("eu/", EuView.as_view(), name="eu"),
]