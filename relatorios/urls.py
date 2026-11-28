from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import PainelView, RelatorioViewSet

router = SimpleRouter()
router.register("relatorios", RelatorioViewSet, basename="relatorio")

urlpatterns = [
    path("painel/", PainelView.as_view(), name="painel"),
] + router.urls