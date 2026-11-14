from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError
from rest_framework.views import exception_handler


def tratar_excecoes(exc, context):
    if isinstance(exc, DjangoValidationError):
        exc = ValidationError({"detail": " ".join(exc.messages)})
    return exception_handler(exc, context)