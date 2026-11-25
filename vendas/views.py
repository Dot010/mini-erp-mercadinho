from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from contas.models import Usuario
from contas.permissoes import DonoOuCaixa, PodeVender, SoTotem

from .models import Chamado, Venda
from .serializers import ChamadoSerializer, NovaVendaSerializer, VendaSerializer
from .services import abrir_chamado, cancelar_venda, liberar_chamado, registrar_venda


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
            request.user,
            itens,
            entrada.validated_data["pagamento"],
            chamado=entrada.validated_data.get("chamado"),  
        )
        return Response(VendaSerializer(venda).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def cancelar(self, request, pk=None):
        venda = cancelar_venda(self.get_object(), request.user)
        return Response(VendaSerializer(venda).data)

class ChamadoViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = ChamadoSerializer


    def get_permissions(self):
        if self.action == "create":
            return [SoTotem()]
        if self.action == "liberar":
            return[DonoOuCaixa()]
        return[PodeVender()]

    def get_queryset(self):
        chamados = Chamado.objects.select_related("totem", "liberado_por")
        if self.request.user.papel == Usuario.Papel.TOTEM:
            return chamados.filter(totem=self.request.user)
        if self.action == "list":
            return chamados.filter(status=Chamado.Status.ABERTO)
        return chamados

    def create(self, request):
        entrada = self.get_serializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        chamado = abrir_chamado(request.user, entrada.validated_data["motivo"])
        return Response(
            self.get_serializer(chamado).data, status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=["post"])
    def liberar(self, request, pk=None):
        chamado = liberar_chamado(self.get_object(), request.user)
        return Response(self.get_serializer(chamado).data)