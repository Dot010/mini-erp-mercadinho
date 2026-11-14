from decimal import Decimal

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction

from contas.models import Usuario
from estoque.models import Movimentacao
from estoque.services import registrar_movimentacao

from .models import ItemVenda, Venda


@transaction.atomic
def registrar_venda(operador, itens, pagamento):
    if not itens:
        raise ValidationError("A venda precisa de pelo menos um item.")

    venda = Venda.objects.create(operador=operador, pagamento=pagamento)
    total = Decimal("0.00")

    for produto, quantidade in itens:
        if not produto.ativo:
            raise ValidationError(f"{produto} não está à venda.")

        saida = registrar_movimentacao(
            produto,
            Movimentacao.Tipo.SAIDA,
            quantidade,
            operador,
            motivo=f"Venda #{venda.pk}",
        )
        item = ItemVenda.objects.create(
            venda=venda,
            produto=saida.produto,
            quantidade=quantidade,
            preco_unitario=saida.produto.preco,
        )
        total += item.subtotal

    venda.total = total
    venda.save(update_fields=["total"])
    return venda


@transaction.atomic
def cancelar_venda(venda, usuario):
    if usuario.papel != Usuario.Papel.DONO:
        raise PermissionDenied("Só o dono pode cancelar uma venda.")

    venda = Venda.objects.select_for_update().get(pk=venda.pk)
    if venda.status == Venda.Status.CANCELADA:
        raise ValidationError("Esta venda já foi cancelada.")

    for item in venda.itens.all():
        registrar_movimentacao(
            item.produto,
            Movimentacao.Tipo.ENTRADA,
            item.quantidade,
            usuario,
            motivo=f"Cancelamento da venda #{venda.pk}",
        )

    venda.status = Venda.Status.CANCELADA
    venda.save(update_fields=["status"])
    return venda