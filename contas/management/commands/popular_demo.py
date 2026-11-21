from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from contas.models import Usuario
from estoque.models import Movimentacao, Produto
from estoque.services import registrar_movimentacao

EQUIPE = [
    ("dono@mercadinho.com", "Jonathan", Usuario.Papel.DONO),
    ("bia@mercadinho.com", "Bia", Usuario.Papel.CAIXA),
    ("carlos@mercadinho.com", "Carlos", Usuario.Papel.ESTOQUISTA),
    ("totem@mercadinho.com", "Totem 1", Usuario.Papel.TOTEM),
]

PRODUTOS = [
    ("Arroz 5kg", "7890000000001", "27.90", 12),
    ("Feijão 1kg", "7890000000002", "8.49", 0),
    ("Óleo de soja 900ml", "7890000000003", "7.49", 4),
    ("Café 500g", "7890000000004", "18.90", 24),
    ("Leite integral 1L", "7890000000005", "5.29", 36),
]


class Command(BaseCommand):
    help = "Cria a equipe e os produtos de exemplo (só para o seu PC)."

    def add_arguments(self, parser):
        parser.add_argument("--senha", required=True, help="Senha dos 3 usuários")

    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("Só roda com DEBUG=True. Nunca em produção.")

        senha = options["senha"]
        dono = None
        for email, nome, papel in EQUIPE:
            usuario, criado = Usuario.objects.get_or_create(
                email=email, defaults={"first_name": nome, "papel": papel}
            )
            if criado:
                usuario.set_password(senha)
                usuario.is_staff = papel == Usuario.Papel.DONO
                usuario.is_superuser = papel == Usuario.Papel.DONO
                usuario.save()
            if papel == Usuario.Papel.DONO:
                dono = usuario

        for nome, codigo, preco, quantidade in PRODUTOS:
            produto, criado = Produto.objects.get_or_create(
                codigo_barras=codigo, defaults={"nome": nome, "preco": Decimal(preco)}
            )
            if criado and quantidade:
                registrar_movimentacao(
                    produto,
                    Movimentacao.Tipo.ENTRADA,
                    quantidade,
                    dono,
                    motivo="Estoque inicial",
                )

        self.stdout.write(self.style.SUCCESS("Pronto! Entre com:"))
        for email, _, papel in EQUIPE:
            self.stdout.write(f"  {email}  ({papel})")