from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied, ValidationError

from .models import ItemVenda, Venda
from .services import cancelar_venda


class ItemVendaInline(admin.TabularInline):
    model = ItemVenda
    fields = ["produto", "quantidade", "preco_unitario", "subtotal"]
    readonly_fields = fields
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display = ["__str__", "criada_em", "operador", "pagamento", "total", "status"]
    list_filter = ["status", "pagamento", "criada_em"]
    readonly_fields = ["operador", "pagamento", "status", "total", "criada_em"]
    inlines = [ItemVendaInline]
    actions = ["cancelar"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.action(description="Cancelar as vendas selecionadas")
    def cancelar(self, request, queryset):
        for venda in queryset:
            try:
                cancelar_venda(venda, request.user)
                self.message_user(request, f"{venda} cancelada.")
            except (PermissionDenied, ValidationError) as erro:
                self.message_user(request, f"{venda}: {erro.args[0]}", messages.ERROR)