from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    ordering = ["email"]
    list_display = ["email", "first_name", "papel", "is_active"]
    list_filter = ["papel", "is_active"]
    search_fields = ["email", "first_name"]

    fieldsets = [
        (None, {"fields": ["email", "password"]}),
        ("Dados", {"fields": ["first_name", "last_name", "papel"]}),
        ("Acesso", {"fields": ["is_active", "is_staff", "is_superuser"]}),
    ]
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["email", "first_name", "papel", "password1", "password2"],
            },
        ),
    ]