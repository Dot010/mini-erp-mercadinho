from rest_framework.routers import SimpleRouter

from .views import ChamadoViewSet, VendaViewSet

router = SimpleRouter()
router.register("vendas", VendaViewSet, basename="venda")
router.register("chamados", ChamadoViewSet, basename="chamado")

urlpatterns = router.urls