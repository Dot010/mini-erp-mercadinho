from rest_framework.permissions import BasePermission

from .models import Usuario


class TemPapel(BasePermission):
    papeis = ()
    message = "Seu papel não permite esta ação."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.papel in self.papeis


class SoDono(TemPapel):
    papeis = (Usuario.Papel.DONO,)


class DonoOuEstoquista(TemPapel):
    papeis = (Usuario.Papel.DONO, Usuario.Papel.ESTOQUISTA)


class DonoOuCaixa(TemPapel):
    papeis = (Usuario.Papel.DONO, Usuario.Papel.CAIXA)

class PodeVender(TemPapel):
    papeis = (Usuario.Papel.DONO, Usuario.Papel.CAIXA, Usuario.Papel.TOTEM)


class SoTotem(TemPapel):
    papeis = (Usuario.Papel.TOTEM,)