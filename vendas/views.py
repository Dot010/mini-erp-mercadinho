from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from contas.models import Usuario
from contas.permissoes import DonoOuCaixa, PodeVender

from .models import Venda
from .serializers import NovaVendaSerializer, VendaSerializer
from .services import cancelar_venda, registrar_venda


class VendaViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = VendaSerializer
    permission_classes = [PodeVender]

    def get_queryset(self):
        vendas = Venda.objects.select_related("operador").prefetch_related(
            "itens__produto"
        )
        if self.request.user.papel == Usuario.Papel.DONO:
            return vendas
        return vendas.filter(operador=self.request.user)

    def create(self, request):
        entrada = NovaVendaSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)

        itens = [
            (item["produto"], item["quantidade"])
            for item in entrada.validated_data["itens"]
        ]
        venda = registrar_venda(
            request.user, itens, entrada.validated_data["pagamento"]
        )
        return Response(VendaSerializer(venda).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def cancelar(self, request, pk=None):
        venda = cancelar_venda(self.get_object(), request.user)
        return Response(VendaSerializer(venda).data)