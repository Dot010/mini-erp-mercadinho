from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import ProtectedError
from django.test import TestCase
from django.urls import reverse

from contas.models import Usuario
from estoque.models import Movimentacao, Produto
from estoque.services import registrar_movimentacao

ENTRADA = Movimentacao.Tipo.ENTRADA
SAIDA = Movimentacao.Tipo.SAIDA


class EstoqueTest(TestCase):
    def setUp(self):
        self.dono = Usuario.objects.create_superuser(
            email="dono@a.com", password="Senha-forte-123", first_name="Jonathan"
        )
        self.arroz = Produto.objects.create(
            nome="Arroz 5kg", codigo_barras="7890000000001", preco=Decimal("27.90")
        )

    def movimentar(self, tipo, quantidade):
        return registrar_movimentacao(self.arroz, tipo, quantidade, self.dono)

    def test_produto_novo_comeca_sem_estoque(self):
        self.assertEqual(self.arroz.estoque, 0)

    def test_entrada_soma_no_estoque(self):
        self.movimentar(ENTRADA, 10)

        self.arroz.refresh_from_db()
        self.assertEqual(self.arroz.estoque, 10)

    def test_saida_tira_do_estoque(self):
        self.movimentar(ENTRADA, 10)

        self.movimentar(SAIDA, 3)

        self.arroz.refresh_from_db()
        self.assertEqual(self.arroz.estoque, 7)

    def test_saida_maior_que_o_estoque_e_recusada(self):
        self.movimentar(ENTRADA, 2)

        with self.assertRaises(ValidationError):
            self.movimentar(SAIDA, 5)

        self.arroz.refresh_from_db()
        self.assertEqual(self.arroz.estoque, 2)
        self.assertEqual(self.arroz.movimentacoes.count(), 1)

    def test_cada_movimentacao_fica_no_historico(self):
        self.movimentar(ENTRADA, 10)
        self.movimentar(SAIDA, 3)

        historico = self.arroz.movimentacoes.all()

        self.assertEqual(historico.count(), 2)
        self.assertEqual(historico[0].usuario, self.dono)

    def test_codigo_de_barras_nao_repete(self):
        with self.assertRaises(IntegrityError):
            Produto.objects.create(
                nome="Outro", codigo_barras="7890000000001", preco=Decimal("1.00")
            )

    def test_produto_com_historico_nao_pode_ser_apagado(self):
        self.movimentar(ENTRADA, 1)

        with self.assertRaises(ProtectedError):
            self.arroz.delete()

    def test_preco_e_exato(self):
        self.assertEqual(self.arroz.preco * 3, Decimal("83.70"))


class EstoqueAdminTest(TestCase):
    def setUp(self):
        self.dono = Usuario.objects.create_superuser(
            email="dono@a.com", password="Senha-forte-123", first_name="Jonathan"
        )
        self.arroz = Produto.objects.create(
            nome="Arroz 5kg", codigo_barras="7890000000001", preco=Decimal("27.90")
        )
        self.client.force_login(self.dono)
        self.nova = reverse("admin:estoque_movimentacao_add")

    def lancar(self, tipo, quantidade):
        return self.client.post(
            self.nova,
            {"produto": self.arroz.pk, "tipo": tipo, "quantidade": quantidade},
        )

    def test_admin_lanca_entrada_no_nome_de_quem_esta_logado(self):
        resposta = self.lancar("entrada", 5)

        self.arroz.refresh_from_db()
        self.assertEqual(resposta.status_code, 302)
        self.assertEqual(self.arroz.estoque, 5)
        self.assertEqual(Movimentacao.objects.get().usuario, self.dono)

    def test_admin_mostra_erro_se_faltar_estoque(self):
        resposta = self.lancar("saida", 5)

        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Só tem 0 no estoque.")
        self.assertFalse(Movimentacao.objects.exists())

    def test_movimentacao_nao_pode_ser_apagada(self):
        movimentacao = registrar_movimentacao(self.arroz, ENTRADA, 1, self.dono)

        resposta = self.client.post(
            reverse("admin:estoque_movimentacao_delete", args=[movimentacao.pk])
        )

        self.assertEqual(resposta.status_code, 403)
        self.assertTrue(Movimentacao.objects.exists())