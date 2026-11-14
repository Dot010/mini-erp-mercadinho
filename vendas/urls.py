from rest_framework.routers import SimpleRouter

from .views import VendaViewSet

router = SimpleRouter()
router.register("vendas", VendaViewSet, basename="venda")

urlpatterns = router.urls