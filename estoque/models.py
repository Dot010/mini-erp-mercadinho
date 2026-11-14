from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class Produto(models.Model):
    nome = models.CharField(max_length=120)
    codigo_barras = models.CharField("código de barras", max_length=14, unique=True)
    preco = models.DecimalField(
        "preço",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    estoque = models.PositiveIntegerField(default=0, editable=False)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Movimentacao(models.Model):
    class Tipo(models.TextChoices):
        ENTRADA = "entrada", "Entrada"
        SAIDA = "saida", "Saída"

    produto = models.ForeignKey(
        Produto, on_delete=models.PROTECT, related_name="movimentacoes"
    )
    tipo = models.CharField(max_length=7, choices=Tipo.choices)
    quantidade = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    motivo = models.CharField(max_length=200, blank=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="movimentacoes",
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "movimentação"
        verbose_name_plural = "movimentações"

    def __str__(self):
        return f"{self.get_tipo_display()} de {self.quantidade} {self.produto}"

    def clean(self):
        if (
            self.tipo == self.Tipo.SAIDA
            and self.produto_id
            and self.quantidade
            and self.quantidade > self.produto.estoque
        ):
            raise ValidationError(
                {"quantidade": f"Só tem {self.produto.estoque} no estoque."}
            )