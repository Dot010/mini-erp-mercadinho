from django.conf import settings
from django.db import models



class Relatorio(models.Model):
    class Status(models.TextChoices):
        PENDENTE  = "pendente", "Pendente"
        PRONTO = "pronto", "Pronto"
        ERRO = "erro", "Erro"


    pedido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="relatorios"
    )
    inicio = models.DateField()
    fim = models.DateField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDENTE)
    dados = models.JSONField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    terminado_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-criado_em"]

    def __str__(self):
        return f"Relatório {self.inicio} a {self.fim} ({self.status})"