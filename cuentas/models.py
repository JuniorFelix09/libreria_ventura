from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Perfil(models.Model):

    class Rol(models.TextChoices):
        ADMIN  = 'ADMIN',  'Administrador'
        CAJERO = 'CAJERO', 'Cajero'

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfil',
    )
    rol = models.CharField(
        max_length=10, choices=Rol.choices, default=Rol.CAJERO
    )

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfiles'

    def __str__(self):
        return f'{self.usuario.username} ({self.get_rol_display()})'

    @property
    def es_admin(self):
        return self.rol == self.Rol.ADMIN

    @property
    def es_cajero(self):
        return self.rol == self.Rol.CAJERO


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """Crea el Perfil automáticamente cada vez que se crea un User."""
    if created:
        Perfil.objects.create(usuario=instance)