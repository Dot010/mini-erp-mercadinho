from rest_framework import serializers

from estoque.models import Produto

from .models import ItemVenda, Venda


class ItemEntradaSerializer(serializers.Serializer):
    produto = serializers.SlugRelatedField(
        slug_field="codigo_barras", queryset=Produto.objects.all()
    )
    quantidade = serializers.IntegerField(min_value=1)


class NovaVendaSerializer(serializers.Serializer):
    pagamento = serializers.ChoiceField(choices=Venda.Pagamento.choices)
    itens = ItemEntradaSerializer(many=True, allow_empty=False)


class ItemVendaSerializer(serializers.ModelSerializer):
    produto = serializers.CharField(source="produto.nome")
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = ItemVenda
        fields = ["produto", "quantidade", "preco_unitario", "subtotal"]


class VendaSerializer(serializers.ModelSerializer):
    operador = serializers.CharField(source="operador.first_name")
    itens = ItemVendaSerializer(many=True)

    class Meta:
        model = Venda
        fields = ["id", "operador", "pagamento", "status", "total", "criada_em", "itens"]