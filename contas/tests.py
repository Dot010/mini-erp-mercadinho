from django.contrib.auth import authenticate
from django.test import TestCase
from django.urls import reverse

from contas.models import Usuario

SENHA = "Senha-forte-123"


class UsuarioTest(TestCase):
    def test_cria_usuario_com_email(self):
        usuario = Usuario.objects.create_user(
            email="caixa@MERCADINHO.com", password=SENHA, first_name="Bia"
        )

        self.assertEqual(usuario.email, "caixa@mercadinho.com")
        self.assertTrue(usuario.check_password(SENHA))
        self.assertFalse(usuario.is_staff)

    def test_papel_padrao_e_caixa(self):
        usuario = Usuario.objects.create_user(email="a@a.com", password=SENHA)

        self.assertEqual(usuario.papel, Usuario.Papel.CAIXA)

    def test_sem_email_da_erro(self):
        with self.assertRaises(ValueError):
            Usuario.objects.create_user(email="", password=SENHA)

    def test_email_nao_repete(self):
        Usuario.objects.create_user(email="a@a.com", password=SENHA)

        with self.assertRaises(Exception):
            Usuario.objects.create_user(email="a@a.com", password=SENHA)

    def test_superusuario_e_dono(self):
        dono = Usuario.objects.create_superuser(email="dono@a.com", password=SENHA)

        self.assertEqual(dono.papel, Usuario.Papel.DONO)
        self.assertTrue(dono.is_staff)
        self.assertTrue(dono.is_superuser)

    def test_login_pelo_email(self):
        Usuario.objects.create_user(email="a@a.com", password=SENHA)

        self.assertIsNotNone(authenticate(email="a@a.com", password=SENHA))
        self.assertIsNone(authenticate(email="a@a.com", password="errada"))

    def test_admin_lista_usuarios(self):
        dono = Usuario.objects.create_superuser(email="dono@a.com", password=SENHA)
        self.client.force_login(dono)

        resposta = self.client.get(reverse("admin:contas_usuario_changelist"))

        self.assertEqual(resposta.status_code, 200)