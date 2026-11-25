from django.db import transaction
from django.utils import timezone
from rest_framework import mixins, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from contas.permissoes import SoDono

from .calculos import resumo
from .models import Relatorio
from .serializers import RelatorioSerializer
from .tasks import gerar_relatorio

from contas.permissoes import SoDono

from .calculos import resumo


class PainelView(APIView):
    permission_classes = [SoDono]

    def get(self, request):
        hoje = timezone.localdate()
        return Response(resumo(hoje, hoje))


class RelatorioViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = RelatorioSerializer
    permission_classes = [SoDono]
    queryset = Relatorio.objects.all()

    def perform_create(self, serializer):
        relatorio = serializer.save(pedido_por=self.request.user)
        transaction.on_commit(lambda: gerar_relatorio.delay(relatorio.id))