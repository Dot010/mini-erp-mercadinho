from rest_framework.routers import SimpleRouter

from .views import MovimentacaoViewSet, ProdutoViewSet

router = SimpleRouter()
router.register("produtos", ProdutoViewSet, basename="produto")
router.register("movimentacoes", MovimentacaoViewSet, basename="movimentacao")

urlpatterns = router.urls