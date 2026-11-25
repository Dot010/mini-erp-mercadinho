from django.urls import path

from .views import PainelView


urlpatterns = [
    path("painel/", PainelView.as_view(), name="painel"),
]