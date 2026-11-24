from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from estoque.models import Produto


class Venda(models.Model):
    class Pagamento(models.TextChoices):
        DINHEIRO = "dinheiro", "Dinheiro"
        CARTAO = "cartao", "Cartão"
        PIX = "pix", "Pix"

    class Status(models.TextChoices):
        FINALIZADA = "finalizada", "Finalizada"
        CANCELADA = "cancelada", "Cancelada"

    operador = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="vendas"
    )
    pagamento = models.CharField(max_length=8, choices=Pagamento.choices)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.FINALIZADA
    )
    total = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00"), editable=False
    )
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criada_em"]

    def __str__(self):
        return f"Venda #{self.pk}"


class ItemVenda(models.Model):
    venda = models.ForeignKey(Venda, on_delete=models.CASCADE, related_name="itens")
    produto = models.ForeignKey(
        Produto, on_delete=models.PROTECT, related_name="itens_vendidos"
    )
    quantidade = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    preco_unitario = models.DecimalField("preço unitário", max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "item"
        verbose_name_plural = "itens"

    def __str__(self):
        return f"{self.quantidade}x {self.produto}"

    @property
    def subtotal(self):
        return self.preco_unitario * self.quantidade


class Chamado(models.Model):
    class Status(models.TextChoices):
        ABERTO = "aberto", "Aberto"
        LIBERADO = "liberado", "Liberado"
        USADO = "usado", "Usado"

    totem = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="chamados",
    )
    motivo = models.CharField(max_length=200)
    status = models.CharField(
        max_length=8,
        choices=Status.choices,
        default=Status.ABERTO,
    )
    liberado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="chamados_liberados",
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    liberado_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["criado_em"]

    def __str__(self):
        return f"Chamado #{self.pk} ({self.get_status_display()})"
