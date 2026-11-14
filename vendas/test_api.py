from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from contas.models import Usuario
from estoque.models import Movimentacao, Produto
from estoque.services import registrar_movimentacao
from vendas.models import Venda

SENHA = "Senha-forte-123"


class VendaAPITest(APITestCase):
    def setUp(self):
        self.dono = Usuario.objects.create_user(
            email="dono@a.com", password=SENHA, papel=Usuario.Papel.DONO
        )
        self.bia = Usuario.objects.create_user(
            email="bia@a.com", password=SENHA, first_name="Bia"
        )
        self.carla = Usuario.objects.create_user(email="carla@a.com", password=SENHA)
        self.estoquista = Usuario.objects.create_user(
            email="estoque@a.com", password=SENHA, papel=Usuario.Papel.ESTOQUISTA
        )
        self.arroz = self.produto("Arroz 5kg", "7890000000001", "27.90", estoque=10)
        self.feijao = self.produto("Feijão 1kg", "7890000000002", "8.49", estoque=2)
        self.vendas = reverse("venda-list")
        self.client.force_authenticate(self.bia)

    def produto(self, nome, codigo, preco, estoque):
        produto = Produto.objects.create(
            nome=nome, codigo_barras=codigo, preco=Decimal(preco)
        )
        registrar_movimentacao(produto, Movimentacao.Tipo.ENTRADA, estoque, self.dono)
        return produto

    def vender(self, *itens, pagamento="pix"):
        corpo = {
            "pagamento": pagamento,
            "itens": [{"produto": codigo, "quantidade": qtd} for codigo, qtd in itens],
        }
        return self.client.post(self.vendas, corpo, format="json")

    def test_caixa_vende_pelo_codigo_de_barras(self):
        resposta = self.vender(("7890000000001", 2), ("7890000000002", 1))

        self.assertEqual(resposta.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resposta.data["total"], "64.29")
        self.assertEqual(resposta.data["operador"], "Bia")
        self.assertEqual(len(resposta.data["itens"]), 2)
        self.assertEqual(Venda.objects.get().operador, self.bia)

    def test_codigo_que_nao_existe_da_400(self):
        resposta = self.vender(("0000000000000", 1))

        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_venda_sem_itens_da_400(self):
        resposta = self.vender()

        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_falta_de_estoque_da_400_e_nada_acontece(self):
        resposta = self.vender(("7890000000001", 2), ("7890000000002", 5))

        self.arroz.refresh_from_db()
        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resposta.data["detail"], "Só tem 2 no estoque.")
        self.assertEqual(self.arroz.estoque, 10)

    def test_pagamento_invalido_da_400(self):
        resposta = self.vender(("7890000000001", 1), pagamento="fiado")

        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_estoquista_nao_vende(self):
        self.client.force_authenticate(self.estoquista)

        resposta = self.vender(("7890000000001", 1))

        self.assertEqual(resposta.status_code, status.HTTP_403_FORBIDDEN)

    def test_caixa_ve_so_as_proprias_vendas(self):
        self.vender(("7890000000001", 1))
        self.client.force_authenticate(self.carla)
        self.vender(("7890000000001", 1))

        self.assertEqual(len(self.client.get(self.vendas).data), 1)

        self.client.force_authenticate(self.dono)
        self.assertEqual(len(self.client.get(self.vendas).data), 2)

    def test_caixa_nao_cancela(self):
        venda_id = self.vender(("7890000000001", 1)).data["id"]

        resposta = self.client.post(reverse("venda-cancelar", args=[venda_id]))

        self.assertEqual(resposta.status_code, status.HTTP_403_FORBIDDEN)

    def test_dono_cancela_e_o_estoque_volta(self):
        venda_id = self.vender(("7890000000001", 3)).data["id"]
        self.client.force_authenticate(self.dono)

        resposta = self.client.post(reverse("venda-cancelar", args=[venda_id]))

        self.arroz.refresh_from_db()
        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(resposta.data["status"], "cancelada")
        self.assertEqual(self.arroz.estoque, 10)

    def test_cancelar_duas_vezes_da_400(self):
        venda_id = self.vender(("7890000000001", 1)).data["id"]
        self.client.force_authenticate(self.dono)
        cancelar = reverse("venda-cancelar", args=[venda_id])
        self.client.post(cancelar)

        resposta = self.client.post(cancelar)

        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)