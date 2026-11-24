from rest_framework import serializers

from .models import Movimentacao, Produto


class ProdutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produto
        fields = ["id", "nome", "codigo_barras", "preco", "estoque", "ativo", "restrito"]
        read_only_fields = ["estoque"]


class MovimentacaoSerializer(serializers.ModelSerializer):
    produto_nome = serializers.CharField(source="produto.nome", read_only=True)
    usuario_nome = serializers.CharField(source="usuario.first_name", read_only=True)

    class Meta:
        model = Movimentacao
        fields = [
            "id",
            "produto",
            "produto_nome",
            "tipo",
            "quantidade",
            "motivo",
            "usuario_nome",
            "criado_em",
        ]