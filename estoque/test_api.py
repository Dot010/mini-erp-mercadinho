from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from contas.models import Usuario
from estoque.models import Produto

SENHA = "Senha-forte-123"


class EstoqueAPITest(APITestCase):
    def setUp(self):
        self.dono = Usuario.objects.create_user(
            email="dono@a.com", password=SENHA, papel=Usuario.Papel.DONO
        )
        self.caixa = Usuario.objects.create_user(email="caixa@a.com", password=SENHA)
        self.estoquista = Usuario.objects.create_user(
            email="estoque@a.com", password=SENHA, papel=Usuario.Papel.ESTOQUISTA
        )
        self.arroz = Produto.objects.create(
            nome="Arroz 5kg", codigo_barras="7890000000001", preco=Decimal("27.90")
        )
        self.produtos = reverse("produto-list")
        self.arroz_url = reverse("produto-detail", args=[self.arroz.pk])
        self.movimentacoes = reverse("movimentacao-list")

    def entrar_como(self, usuario):
        self.client.force_authenticate(usuario)

    def novo_produto(self):
        return self.client.post(
            self.produtos,
            {"nome": "Feijão 1kg", "codigo_barras": "7890000000002", "preco": "8.49"},
            format="json",
        )

    def test_caixa_busca_produto_pelo_codigo(self):
        self.entrar_como(self.caixa)

        resposta = self.client.get(self.produtos, {"codigo": "7890000000001"})

        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(resposta.data[0]["nome"], "Arroz 5kg")
        self.assertEqual(resposta.data[0]["preco"], "27.90")

    def test_busca_pelo_nome(self):
        self.entrar_como(self.caixa)

        resposta = self.client.get(self.produtos, {"busca": "arr"})

        self.assertEqual(len(resposta.data), 1)

    def test_estoquista_cadastra_produto(self):
        self.entrar_como(self.estoquista)

        resposta = self.novo_produto()

        self.assertEqual(resposta.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resposta.data["estoque"], 0)

    def test_caixa_nao_cadastra_produto(self):
        self.entrar_como(self.caixa)

        resposta = self.novo_produto()

        self.assertEqual(resposta.status_code, status.HTTP_403_FORBIDDEN)

    def test_so_o_dono_muda_o_preco(self):
        for usuario in (self.caixa, self.estoquista):
            self.entrar_como(usuario)
            resposta = self.client.patch(self.arroz_url, {"preco": "1.00"}, format="json")
            self.assertEqual(resposta.status_code, status.HTTP_403_FORBIDDEN)

        self.entrar_como(self.dono)
        resposta = self.client.patch(self.arroz_url, {"preco": "29.90"}, format="json")

        self.arroz.refresh_from_db()
        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(self.arroz.preco, Decimal("29.90"))

    def test_estoque_nao_muda_pelo_produto(self):
        self.entrar_como(self.dono)

        self.client.patch(self.arroz_url, {"estoque": 999}, format="json")

        self.arroz.refresh_from_db()
        self.assertEqual(self.arroz.estoque, 0)

    def test_produto_nao_se_apaga_pela_api(self):
        self.entrar_como(self.dono)

        resposta = self.client.delete(self.arroz_url)

        self.assertEqual(resposta.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_estoquista_da_entrada_no_proprio_nome(self):
        self.entrar_como(self.estoquista)

        resposta = self.client.post(
            self.movimentacoes,
            {"produto": self.arroz.pk, "tipo": "entrada", "quantidade": 10},
            format="json",
        )

        self.arroz.refresh_from_db()
        self.assertEqual(resposta.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.arroz.estoque, 10)
        self.assertEqual(self.arroz.movimentacoes.get().usuario, self.estoquista)

    def test_saida_sem_estoque_da_400_com_mensagem(self):
        self.entrar_como(self.estoquista)

        resposta = self.client.post(
            self.movimentacoes,
            {"produto": self.arroz.pk, "tipo": "saida", "quantidade": 5},
            format="json",
        )

        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resposta.data["detail"], "Só tem 0 no estoque.")

    def test_caixa_nao_mexe_no_estoque(self):
        self.entrar_como(self.caixa)

        resposta = self.client.get(self.movimentacoes)

        self.assertEqual(resposta.status_code, status.HTTP_403_FORBIDDEN)