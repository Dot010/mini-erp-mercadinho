from rest_framework import serializers

from .models import Relatorio


class RelatorioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relatorio
        fields = ["id", "inicio", "fim", "status", "dados", "criado_em", "terminado_em"]
        read_only_fields = ["status", "dados", "criado_em", "terminado_em"]

    def validate(self, attrs):
        if attrs["inicio"] > attrs["fim"]:
            raise serializers.ValidationError("A data de início precisa ser antes do fim.")
        return attrs