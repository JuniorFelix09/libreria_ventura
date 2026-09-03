from django.conf import settings
from django.db import models
from django.utils import timezone


class Cliente(models.Model):
    nombre   = models.CharField(max_length=150)
    telefono = models.CharField(max_length=20, blank=True)

    es_profesor = models.BooleanField(
        default=False,
        help_text='Si está activo, se le aplica el descuento configurado abajo en cada venta.',
    )
    descuento_pct = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        verbose_name='Descuento (%)',
        help_text='Porcentaje de descuento a aplicar. Solo tiene efecto si "Es profesor" está activo.',
    )

    permite_fiado = models.BooleanField(
        default=False,
        help_text='Si está activo, este cliente puede llevarse productos a cuenta (fiado).',
    )
    limite_fiado = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        help_text='Deuda máxima permitida antes de bloquear nuevas ventas fiadas. 0 = sin límite.',
    )

    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    @property
    def total_fiado(self):
        return (
            self.ventas.filter(metodo_pago='FIADO', anulada=False)
            .aggregate(total=models.Sum('total'))['total'] or 0
        )

    @property
    def total_abonado(self):
        return self.abonos.aggregate(total=models.Sum('monto'))['total'] or 0

    @property
    def saldo_pendiente(self):
        return self.total_fiado - self.total_abonado

    def puede_fiar(self, monto):
        if not self.permite_fiado:
            return False
        if self.limite_fiado == 0:
            return True
        return (self.saldo_pendiente + monto) <= self.limite_fiado


class AbonoFiado(models.Model):
    """Pago que un cliente hace para abonar a su deuda fiada."""

    cliente        = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='abonos')
    monto          = models.DecimalField(max_digits=10, decimal_places=2)
    fecha          = models.DateTimeField(default=timezone.now)
    nota           = models.CharField(max_length=255, blank=True)
    registrado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'Abono a fiado'
        verbose_name_plural = 'Abonos a fiado'
        ordering = ['-fecha']

    def __str__(self):
        return f'Abono RD${self.monto} — {self.cliente} ({self.fecha:%d/%m/%Y})'