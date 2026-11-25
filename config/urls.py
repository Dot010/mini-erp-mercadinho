from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("contas.urls")),
    path("api/", include("estoque.urls")),
    path("api/", include("vendas.urls")),
    path("api-auth/", include("rest_framework.urls")),
    path("api/", include("relatorios.urls")),
]