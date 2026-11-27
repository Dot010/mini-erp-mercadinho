import csv

from django.db import transaction
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from contas.permissoes import SoDono

from .calculos import resumo
from .models import Relatorio
from .serializers import RelatorioSerializer
from .tasks import gerar_relatorio


def virgula(valor):
    """O Excel brasileiro lê 278,96, e não 278.96."""
    return valor.replace(".", ",")
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



    @action(detail=True, url_path="csv", url_name="csv")
    def baixar_csv(self, request, pk=None):
        relatorio = self.get_object()
        if relatorio.status != Relatorio.Status.PRONTO:
            return Response(
                {"detail": "O relatório ainda não está pronto."},
                status=status.HTTP_409_CONFLICT,
            )

        dados = relatorio.dados
        nome = f"relatorio_{relatorio.inicio}_{relatorio.fim}.csv"
        resposta = HttpResponse(content_type="text/csv; charset=utf-8")
        resposta["Content-Disposition"] = f'attachment; filename="{nome}"'
        resposta.write("\ufeff")

        escritor = csv.writer(resposta, delimiter=";")
        escritor.writerow(["Período", f"{relatorio.inicio} a {relatorio.fim}"])
        escritor.writerow(["Total vendido", virgula(dados["total"])])
        escritor.writerow(["Vendas", dados["vendas"]])
        escritor.writerow(["Ticket médio", virgula(dados["ticket_medio"])])
        escritor.writerow([])
        escritor.writerow(["Produto", "Unidades"])
        for item in dados["mais_vendidos"]:
            escritor.writerow([item["nome"], item["quantidade"]])
        escritor.writerow([])
        escritor.writerow(["Pagamento", "Vendas", "Total"])
        for linha in dados["por_pagamento"]:
            escritor.writerow([linha["pagamento"], linha["vendas"], virgula(linha["total"])])
        return resposta