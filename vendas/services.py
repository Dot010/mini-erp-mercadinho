from decimal import Decimal

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from contas.models import Usuario
from estoque.models import Movimentacao
from estoque.services import registrar_movimentacao

from .models import Chamado, ItemVenda, Venda


@transaction.atomic
def registrar_venda(operador, itens, pagamento, chamado=None):
    if not itens:
        raise ValidationError("A venda precisa de pelo menos um item.")
    conferir_totem(operador, itens, chamado)
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

@transaction.atomic
def abrir_chamado(totem, motivo):
    aberto = totem.chamados.filter(status=Chamado.Status.ABERTO).first()
    if aberto:
        return aberto

    totem.chamados.filter(status=Chamado.Status.LIBERADO).update(
        status=Chamado.Status.USADO
    )
    return Chamado.objects.create(totem=totem, motivo=motivo)

@transaction.atomic
def liberar_chamado(chamado, funcionario):
    if funcionario.papel not in (Usuario.Papel.DONO, Usuario.Papel.CAIXA):
        raise PermissionDenied("Só o dono ou um caixa libera o totem.")


    chamado = Chamado.objects.select_for_update().get(pk=chamado.pk)
    if chamado.status != Chamado.Status.ABERTO:
        raise ValidationError("Este chamado já foi atendido.")

    chamado.status = Chamado.Status.LIBERADO
    chamado.liberado_por = funcionario
    chamado.liberado_em = timezone.now()
    chamado.save(update_fields=["status", "liberado_por", "liberado_em"])
    return chamado

def conferir_totem(operador, itens, chamado):
    if operador.papel != Usuario.Papel.TOTEM:
        return
    if not any(produto.restrito for produto, _ in itens):
        return
    if chamado is None:
        raise ValidationError("Tem produtos para maiores de 18 anos: Chame um atendente.")


    chamado = Chamado.objects.select_for_update().get(pk=chamado.pk)
    if chamado.totem_id != operador.pk or chamado.status != Chamado.Status.LIBERADO:
        raise ValidationError("Esse chamado não foi liberado para este totem.")

    chamado.status = Chamado.Status.USADO
    chamado.save(update_fields=["status"])