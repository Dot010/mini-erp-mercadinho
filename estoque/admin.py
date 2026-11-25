from django.contrib import admin

from .models import Movimentacao, Produto
from .services import registrar_movimentacao


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ["nome", "codigo_barras", "preco", "estoque", "ativo", "restrito"]
    list_filter = ["ativo", "restrito"]
    search_fields = ["nome", "codigo_barras"]
    readonly_fields = ["estoque"]


@admin.register(Movimentacao)
class MovimentacaoAdmin(admin.ModelAdmin):
    list_display = ["criado_em", "produto", "tipo", "quantidade", "usuario"]
    list_filter = ["tipo"]
    search_fields = ["produto__nome", "motivo"]
    fields = ["produto", "tipo", "quantidade", "motivo"]
    autocomplete_fields = ["produto"]

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        movimentacao = registrar_movimentacao(
            produto=obj.produto,
            tipo=obj.tipo,
            quantidade=obj.quantidade,
            usuario=request.user,
            motivo=obj.motivo,
        )
        obj.pk = movimentacao.pk