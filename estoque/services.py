from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Movimentacao, Produto


@transaction.atomic
def registrar_movimentacao(produto, tipo, quantidade, usuario, motivo=""):
    produto = Produto.objects.select_for_update().get(pk=produto.pk)

    if tipo == Movimentacao.Tipo.SAIDA:
        if quantidade > produto.estoque:
            raise ValidationError(f"Só tem {produto.estoque} no estoque.")
        produto.estoque -= quantidade
    else:
        produto.estoque += quantidade

    produto.save(update_fields=["estoque"])

    return Movimentacao.objects.create(
        produto=produto,
        tipo=tipo,
        quantidade=quantidade,
        usuario=usuario,
        motivo=motivo,
    )