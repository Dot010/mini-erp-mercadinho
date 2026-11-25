from decimal import Decimal
from unittest import mock

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from contas.models import Usuario
from estoque.models import Movimentacao, Produto
from estoque.services import registrar_movimentacao
from vendas.services import cancelar_venda, registrar_venda

from .models import Relatorio
from .tasks import gerar_relatorio


SENHA = "Senha-forte-123"


class PainelTest(APITestCase):
    def setUp(self):
        self.dono = Usuario.objects.create_user(
            email="dono@a.com", password=SENHA, papel=Usuario.Papel.DONO
        )
        self.bia = Usuario.objects.create_user(
            email="bia@a.com",
            password=SENHA,
            first_name="Bia",
            papel=Usuario.Papel.CAIXA,
        )
        self.arroz = Produto.objects.create(
            nome="Arroz 5kg", codigo_barras="7890000000001", preco=Decimal("27.90")
        )
        self.cafe = Produto.objects.create(
            nome="Café 500g", codigo_barras="7890000000004", preco=Decimal("18.90")
        )
        for produto in (self.arroz, self.cafe):
            registrar_movimentacao(produto, Movimentacao.Tipo.ENTRADA, 20, self.dono)
        self.client.force_authenticate(self.dono)

    def test_sem_vendas_tudo_zerado(self):
        resposta = self.client.get(reverse("painel"))

        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(resposta.data["total"], "0.00")
        self.assertEqual(resposta.data["vendas"], 0)
        self.assertEqual(resposta.data["ticket_medio"], "0.00")

    def test_soma_as_vendas_de_hoje(self):
        registrar_venda(self.bia, [(self.arroz, 2)], "pix")
        registrar_venda(self.bia, [(self.cafe, 1)], "dinheiro")

        dados = self.client.get(reverse("painel")).data

        self.assertEqual(dados["total"], "74.70")
        self.assertEqual(dados["vendas"], 2)
        self.assertEqual(dados["ticket_medio"], "37.35")
        self.assertEqual(dados["mais_vendidos"][0]["nome"], "Arroz 5kg")

    def test_venda_cancelada_nao_conta(self):
        venda = registrar_venda(self.bia, [(self.arroz, 1)], "pix")
        cancelar_venda(venda, self.dono)

        dados = self.client.get(reverse("painel")).data

        self.assertEqual(dados["total"], "0.00")
        self.assertEqual(dados["vendas"], 0)

    def test_caixa_nao_ve_o_painel(self):
        self.client.force_authenticate(self.bia)

        resposta = self.client.get(reverse("painel"))

        self.assertEqual(resposta.status_code, status.HTTP_403_FORBIDDEN)


class RelatorioTest(APITestCase):
    def setUp(self):
        self.dono = Usuario.objects.create_user(
            email="dono@a.com", password=SENHA, papel=Usuario.Papel.DONO
        )
        self.bia = Usuario.objects.create_user(
            email="bia@a.com", password=SENHA, first_name="Bia", papel=Usuario.Papel.CAIXA
        )
        self.arroz = Produto.objects.create(
            nome="Arroz 5kg", codigo_barras="7890000000001", preco=Decimal("27.90")
        )
        registrar_movimentacao(self.arroz, Movimentacao.Tipo.ENTRADA, 20, self.dono)
        self.hoje = timezone.localdate().isoformat()
        self.client.force_authenticate(self.dono)

    def test_pedido_nasce_pendente_e_vai_para_a_fila(self):
        with mock.patch("relatorios.views.gerar_relatorio.delay") as fila:
            with self.captureOnCommitCallbacks(execute=True):
                resposta = self.client.post(
                    reverse("relatorio-list"), {"inicio": self.hoje, "fim": self.hoje}
                )

        self.assertEqual(resposta.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resposta.data["status"], "pendente")
        fila.assert_called_once_with(resposta.data["id"])

    def test_inicio_depois_do_fim_da_erro(self):
        resposta = self.client.post(
            reverse("relatorio-list"), {"inicio": "2026-11-30", "fim": "2026-11-01"}
        )

        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_caixa_nao_pede_relatorio(self):
        self.client.force_authenticate(self.bia)

        resposta = self.client.post(
            reverse("relatorio-list"), {"inicio": self.hoje, "fim": self.hoje}
        )

        self.assertEqual(resposta.status_code, status.HTTP_403_FORBIDDEN)

    def test_tarefa_calcula_e_marca_pronto(self):
        registrar_venda(self.bia, [(self.arroz, 2)], "pix")
        relatorio = Relatorio.objects.create(
            pedido_por=self.dono, inicio=timezone.localdate(), fim=timezone.localdate()
        )

        gerar_relatorio(relatorio.id)

        relatorio.refresh_from_db()
        self.assertEqual(relatorio.status, Relatorio.Status.PRONTO)
        self.assertEqual(relatorio.dados["total"], "55.80")
        self.assertIsNotNone(relatorio.terminado_em)