from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from contas.models import Usuario

SENHA = "Senha-forte-123"


class LoginAPITest(APITestCase):
    def setUp(self):
        cache.clear()
        self.bia = Usuario.objects.create_user(
            email="bia@a.com", password=SENHA, first_name="Bia"
        )
        self.login = reverse("login")

    def entrar(self, senha):
        return self.client.post(
            self.login, {"email": "bia@a.com", "password": senha}, format="json"
        )

    def test_login_devolve_token_e_papel(self):
        resposta = self.entrar(SENHA)

        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertIn("token", resposta.data)
        self.assertEqual(resposta.data["usuario"]["papel"], "caixa")
        self.assertNotIn("password", resposta.data["usuario"])

    def test_senha_errada_da_401(self):
        resposta = self.entrar("errada")

        self.assertEqual(resposta.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_abre_a_rota_eu(self):
        token = self.entrar(SENHA).data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        resposta = self.client.get(reverse("eu"))

        self.assertEqual(resposta.data["email"], "bia@a.com")

    def test_sem_token_nao_entra(self):
        resposta = self.client.get(reverse("eu"))

        self.assertEqual(resposta.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_muitas_tentativas_sao_bloqueadas(self):
        for _ in range(5):
            self.entrar("errada")

        resposta = self.entrar(SENHA)

        self.assertEqual(resposta.status_code, status.HTTP_429_TOO_MANY_REQUESTS)