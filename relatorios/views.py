from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from contas.permissoes import SoDono

from .calculos import resumo


class PainelView(APIView):
    permission_classes = [SoDono]

    def get(self, request):
        hoje = timezone.localdate()
        return Response(resumo(hoje, hoje))