from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class UsuarioManager(BaseUserManager):
    use_in_migrations = True 

    def _criar(self, email, password, **campos):
        if not email:
            raise ValueError('O email deve ser fornecido.')
        email = self.normalize_email(email)
        usuario = self.model(email=email, **campos)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    
    def create_user(self, email, password=None, **campos):
        campos.setdefault("is_staff", False)
        campos.setdefault("is_superuser", False)
        return self._criar(email, password, **campos)

    def create_superuser(self, email, password=None, **campos):
        campos.setdefault("is_staff", True)
        campos.setdefault("is_superuser", True)
        campos.setdefault("papel", Usuario.Papel.DONO)
        return self._criar(email, password, **campos)


class Usuario(AbstractUser):
    class Papel(models.TextChoices):
        DONO = "dono", "Dono"
        CAIXA = "caixa", "Caixa"
        ESTOQUISTA = "estoquista", "Estoquista"
        TOTEM = "totem", "Totem"

    username = None
    email = models.EmailField("e-mail", unique=True)
    papel = models.CharField(max_length=12, choices=Papel.choices, default=Papel.CAIXA)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name"]

    objects = UsuarioManager()

    def __str__(self):
        return f"{self.first_name} ({self.get_papel_display()})"