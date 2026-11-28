from decimal import Decimal

from django.db.models import Count, F, Sum

from vendas.models import ItemVenda, Venda

ZERO = Decimal("0.00")


def dinheiro(valor):
    """Decimal vira texto com 2 casas: o JSON não tem Decimal."""
    return str((valor or ZERO).quantize(Decimal("0.01")))



def resumo(inicio, fim):
    """Os números das vendas do dia `inicio` ao dia `fim` (os dois entram)."""
    finalizadas = Venda.objects.filter(
        criada_em__date__range=(inicio, fim),
        status=Venda.Status.FINALIZADA,
    )

    totais = finalizadas.aggregate(total=Sum("total"), vendas=Count("id"))
    total = totais["total"] or ZERO
    vendas = totais["vendas"]

    por_pagamento = finalizadas.values("pagamento").annotate(
        vendas=Count("id"), total=Sum("total")
    )


    mais_vendidos = (
        ItemVenda.objects.filter(venda__in=finalizadas)
        .values(nome=F("produto__nome"))
        .annotate(quantidade=Sum("quantidade"))
        .order_by("-quantidade")[:5]
    )
    return {
        "inicio": inicio.isoformat(),
        "fim": fim.isoformat(),
        "total": dinheiro(total),
        "vendas": vendas,
        "ticket_medio": dinheiro(total / vendas if vendas else ZERO),
        "por_pagamento": [
            {"pagamento": linha["pagamento"], "vendas": linha["vendas"], "total": dinheiro(linha["total"])}
            for linha in por_pagamento
        ],
        "mais_vendidos": list(mais_vendidos),
    }