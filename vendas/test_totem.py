from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from contas.models import Usuario
from estoque.models import Movimentacao, Produto
from estoque.services import registrar_movimentacao
from vendas.models import Chamado

SENHA = "Senha-forte-123"


class TotemAPITest(APITestCase):
    def setUp(self):
        self.dono = Usuario.objects.create_user(
            email="dono@a.com", password=SENHA, papel=Usuario.Papel.DONO
        )
        self.bia = Usuario.objects.create_user(
            email="bia@a.com",
            password=SENHA,
            first_name="Bia",
            papel=Usuario.Papel.CAIXA
        )
        self.totem = Usuario.objects.create_user(
            email="totem1@a.com",
            password=SENHA,
            first_name= "Totem 1",
            papel=Usuario.Papel.TOTEM,
        )
        self.arroz = self.produto("Arroz 5kg", "7890000000001", "27.90")
        self.cerveja = self.produto(
            "Cerveja lata", "7890000000007", "4.99", restrito=True
        )

    def produto(self, nome, codigo, preco, restrito=False):
        produto = Produto.objects.create(
            nome=nome, codigo_barras=codigo, preco=Decimal(preco), restrito=restrito
        )
        registrar_movimentacao(produto, Movimentacao.Tipo.ENTRADA, 10, self.dono)
        return produto

    def vender(self, *codigos, chamado=None):
        self.client.force_authenticate(self.totem)
        return self.client.post(
            reverse("venda-list"),
            {
                "pagamento": "pix",
                "itens": [{"produto": c, "quantidade": 1} for c in codigos],
                "chamado": chamado,
            },
            format="json",
        )

    def chamar(self):
        self.client.force_authenticate(self.totem)
        resposta = self.client.post(
            reverse("chamado-list"), {"motivo": "Cerveja lata"}, format="json"
        )
        return resposta.data["id"]

    def liberar(self, chamado_id, quem):
        self.client.force_authenticate(quem)
        return self.client.post(reverse("chamado-liberar", args=[chamado_id]))

    def test_totem_vende_produto_livre_sem_chamado(self):
        resposta = self.vender("7890000000001")


        self.assertEqual(resposta.status_code, status.HTTP_201_CREATED)

    def test_cerveja_sem_chamado_e_recusada(self):
        resposta = self.vender("7890000000001", "7890000000007")

        self.cerveja.refresh_from_db()
        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.cerveja.estoque, 10)


    def test_caixa_libera_e_o_totem_vende(self):
        chamado_id = self.chamar()

        self.assertEqual(self.liberar(chamado_id, self.bia).status_code, 200)
        resposta = self.vender("7890000000007", chamado=chamado_id)


        self.assertEqual(resposta.status_code, status.HTTP_201_CREATED)
        chamado = Chamado.objects.get(pk=chamado_id)
        self.assertEqual(chamado.status, Chamado.Status.USADO)
        self.assertEqual(chamado.liberado_por, self.bia)


    def test_chamado_nao_liberado_nao_serve(self):
        chamado_id = self.chamar()

        resposta = self.vender("7890000000007", chamado=chamado_id)

        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_chamado_so_vale_uma_vez(self):
        chamado_id = self.chamar()
        self.liberar(chamado_id, self.bia)
        self.vender("7890000000007", chamado=chamado_id)

        resposta = self.vender("7890000000007", chamado=chamado_id)

        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_chamar_de_novo_devolve_o_mesmo(self):
        self.assertEqual(self.chamar(), self.chamar())

    def test_totem_nao_libera_o_proprio_chamado(self):
        chamado_id = self.chamar()

        resposta = self.liberar(chamado_id, self.totem)

        self.assertEqual(resposta.status_code, status.HTTP_403_FORBIDDEN)

    def test_caixa_nao_abre_chamado(self):
        self.client.force_authenticate(self.bia)

        resposta = self.client.post(
            reverse("chamado-list"), {"motivo": "x"}, format="json"
        )

        self.assertEqual(resposta.status_code, status.HTTP_403_FORBIDDEN)
