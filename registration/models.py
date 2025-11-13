from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Rol(models.Model):
    nombre = models.CharField(unique=True, max_length=100)

    def __str__(self):
        return self.nombre


def rol_default():
    rol, _ = Rol.objects.get_or_create(nombre="Cliente")
    return rol.id


class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.ForeignKey(Rol, on_delete=models.RESTRICT, default=rol_default)

    def __str__(self):
        return f"{self.user.username} - {self.rol.nombre}"


@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        PerfilUsuario.objects.get_or_create(user=instance, rol_id=rol_default())
