from celery import shared_task
from django.utils import timezone


from .calculos import resumo
from .models import Relatorio


@shared_task
def gerar_relatorio(relatorio_id):
    relatorio = Relatorio.objects.get(pk=relatorio_id)
    try:
        relatorio.dados = resumo(relatorio.inicio, relatorio.fim)
        relatorio.status = Relatorio.Status.PRONTO
    except Exception:
        relatorio.status = Relatorio.Status.ERRO
        raise
    finally:
        relatorio.terminado_em = timezone.now()
        relatorio.save(update_fields=["dados", "status", "terminado_em"])