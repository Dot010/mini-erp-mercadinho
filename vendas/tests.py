from decimal import Decimal

from django.core.exceptions import PermissionDenied, ValidationError
from django.test import TestCase
from django.urls import reverse

from contas.models import Usuario
from estoque.models import Movimentacao, Produto
from estoque.services import registrar_movimentacao
from vendas.models import Venda
from vendas.services import cancelar_venda, registrar_venda

SENHA = "Senha-forte-123"
PIX = Venda.Pagamento.PIX


class VendaTest(TestCase):
    def setUp(self):
        self.dono = Usuario.objects.create_superuser(
            email="dono@a.com", password=SENHA, first_name="Jonathan"
        )
        self.bia = Usuario.objects.create_user(
            email="bia@a.com", password=SENHA, first_name="Bia"
        )
        self.arroz = self.produto("Arroz 5kg", "7890000000001", "27.90", estoque=10)
        self.feijao = self.produto("Feijão 1kg", "7890000000002", "8.49", estoque=2)

    def produto(self, nome, codigo, preco, estoque):
        produto = Produto.objects.create(
            nome=nome, codigo_barras=codigo, preco=Decimal(preco)
        )
        registrar_movimentacao(produto, Movimentacao.Tipo.ENTRADA, estoque, self.dono)
        produto.refresh_from_db()
        return produto

    def estoque(self, produto):
        produto.refresh_from_db()
        return produto.estoque

    def vender(self, *itens):
        return registrar_venda(self.bia, list(itens), PIX)

    def test_venda_baixa_o_estoque_de_cada_item(self):
        self.vender((self.arroz, 3), (self.feijao, 1))

        self.assertEqual(self.estoque(self.arroz), 7)
        self.assertEqual(self.estoque(self.feijao), 1)

    def test_total_e_a_soma_exata_dos_itens(self):
        venda = self.vender((self.arroz, 3), (self.feijao, 2))

        self.assertEqual(venda.total, Decimal("100.68"))

    def test_preco_fica_guardado_na_venda(self):
        venda = self.vender((self.arroz, 1))

        self.arroz.preco = Decimal("30.00")
        self.arroz.save()

        item = venda.itens.get()
        self.assertEqual(item.preco_unitario, Decimal("27.90"))

    def test_se_um_item_falha_nada_acontece(self):
        with self.assertRaises(ValidationError):
            self.vender((self.arroz, 3), (self.feijao, 5))

        self.assertEqual(self.estoque(self.arroz), 10)
        self.assertFalse(Venda.objects.exists())
        self.assertFalse(Movimentacao.objects.filter(tipo="saida").exists())

    def test_venda_vazia_e_recusada(self):
        with self.assertRaises(ValidationError):
            self.vender()

    def test_produto_inativo_nao_e_vendido(self):
        self.arroz.ativo = False
        self.arroz.save()

        with self.assertRaises(ValidationError):
            self.vender((self.arroz, 1))

    def test_cada_item_vira_saida_no_historico(self):
        venda = self.vender((self.arroz, 3))

        saida = self.arroz.movimentacoes.get(tipo="saida")
        self.assertEqual(saida.motivo, f"Venda #{venda.pk}")
        self.assertEqual(saida.usuario, self.bia)

    def test_cancelar_devolve_o_estoque(self):
        venda = self.vender((self.arroz, 3))

        cancelar_venda(venda, self.dono)

        venda.refresh_from_db()
        self.assertEqual(venda.status, Venda.Status.CANCELADA)
        self.assertEqual(self.estoque(self.arroz), 10)

    def test_nao_cancela_duas_vezes(self):
        venda = self.vender((self.arroz, 3))
        cancelar_venda(venda, self.dono)

        with self.assertRaises(ValidationError):
            cancelar_venda(venda, self.dono)

        self.assertEqual(self.estoque(self.arroz), 10)

    def test_caixa_nao_cancela(self):
        venda = self.vender((self.arroz, 3))

        with self.assertRaises(PermissionDenied):
            cancelar_venda(venda, self.bia)

        self.assertEqual(self.estoque(self.arroz), 7)


class VendaAdminTest(TestCase):
    def setUp(self):
        self.dono = Usuario.objects.create_superuser(
            email="dono@a.com", password=SENHA, first_name="Jonathan"
        )
        arroz = Produto.objects.create(
            nome="Arroz 5kg", codigo_barras="7890000000001", preco=Decimal("27.90")
        )
        registrar_movimentacao(arroz, Movimentacao.Tipo.ENTRADA, 10, self.dono)
        self.venda = registrar_venda(self.dono, [(arroz, 2)], PIX)
        self.client.force_login(self.dono)
        self.lista = reverse("admin:vendas_venda_changelist")

    def test_admin_mostra_a_venda_com_os_itens(self):
        resposta = self.client.get(
            reverse("admin:vendas_venda_change", args=[self.venda.pk])
        )

        self.assertContains(resposta, "Arroz 5kg")
        self.assertContains(resposta, "55,80")

    def test_acao_de_cancelar_no_admin(self):
        self.client.post(
            self.lista,
            {"action": "cancelar", "_selected_action": [self.venda.pk]},
        )

        self.venda.refresh_from_db()
        self.assertEqual(self.venda.status, Venda.Status.CANCELADA)