from rest_framework import mixins, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from contas.permissoes import DonoOuEstoquista, SoDono

from .models import Movimentacao, Produto
from .serializers import MovimentacaoSerializer, ProdutoSerializer
from .services import registrar_movimentacao


class ProdutoViewSet(viewsets.ModelViewSet):
    serializer_class = ProdutoSerializer
    http_method_names = ["get", "post", "patch"]

    def get_permissions(self):
        if self.action == "create":
            return [DonoOuEstoquista()]
        if self.action == "partial_update":
            return [SoDono()]
        return [IsAuthenticated()]

    def get_queryset(self):
        produtos = Produto.objects.all()
        codigo = self.request.query_params.get("codigo")
        busca = self.request.query_params.get("busca")
        if codigo:
            produtos = produtos.filter(codigo_barras=codigo)
        if busca:
            produtos = produtos.filter(nome__icontains=busca)
        return produtos


class MovimentacaoViewSet(
    mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet
):
    serializer_class = MovimentacaoSerializer
    permission_classes = [DonoOuEstoquista]
    queryset = Movimentacao.objects.select_related("produto", "usuario")

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        movimentacao = registrar_movimentacao(
            produto=serializer.validated_data["produto"],
            tipo=serializer.validated_data["tipo"],
            quantidade=serializer.validated_data["quantidade"],
            usuario=request.user,
            motivo=serializer.validated_data.get("motivo", ""),
        )
        return Response(
            self.get_serializer(movimentacao).data, status=status.HTTP_201_CREATED
        )