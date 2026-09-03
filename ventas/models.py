from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone


class Venta(models.Model):

    class MetodoPago(models.TextChoices):
        EFECTIVO = 'EFECTIVO', 'Efectivo'
        TARJETA  = 'TARJETA',  'Tarjeta'
        FIADO    = 'FIADO',    'Fiado (a cuenta)'

    turno  = models.ForeignKey(
        'caja.Turno', on_delete=models.PROTECT, related_name='ventas'
    )
    cajero = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='ventas'
    )
    cliente = models.ForeignKey(
        'clientes.Cliente', on_delete=models.PROTECT, null=True, blank=True, related_name='ventas',
        help_text='Obligatorio si el método de pago es "Fiado". Opcional si aplica descuento de profesor.',
    )
    fecha        = models.DateTimeField(default=timezone.now)
    metodo_pago  = models.CharField(max_length=10, choices=MetodoPago.choices)
    descuento_pct = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text='Porcentaje de descuento de profesor aplicado a esta venta (solo sobre las líneas marcadas).',
    )
    total        = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    anulada      = models.BooleanField(default=False)
    motivo_anulacion = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['-fecha']

    def __str__(self):
        estado = ' [ANULADA]' if self.anulada else ''
        return f'Venta #{self.pk} — {self.fecha:%d/%m/%Y %H:%M}{estado}'

    @property
    def subtotal(self):
        return sum((d.subtotal for d in self.detalles.all()), Decimal('0'))

    @property
    def subtotal_descontable(self):
        """Suma solo de las líneas cuyo producto tiene 'aplica_descuento_profesor' activo."""
        return sum(
            (d.subtotal for d in self.detalles.all() if d.producto.aplica_descuento_profesor),
            Decimal('0'),
        )

    @property
    def monto_descuento(self):
        descuento_pct = Decimal(self.descuento_pct or 0)
        return self.subtotal_descontable * (descuento_pct / Decimal('100'))

    def calcular_total(self):
        return self.subtotal - self.monto_descuento


class DetalleVenta(models.Model):
    """Una línea de la venta: qué producto, cuántas unidades y a qué precio.

    El precio se copia del producto al momento de vender para que un cambio
    futuro de precio no altere el historial de ventas. Para servicios, el
    precio se recibe directamente de la venta (varía cada vez).
    Al guardarse por primera vez descuenta el stock del producto, salvo
    que sea un servicio.
    """

    venta    = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(
        'productos.Producto', on_delete=models.PROTECT, related_name='detalles_venta'
    )
    cantidad        = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Línea de venta'
        verbose_name_plural = 'Líneas de venta'

    def __str__(self):
        return f'{self.cantidad}x {self.producto} @ RD${self.precio_unitario}'

    @property
    def subtotal(self):
        if self.cantidad is None or self.precio_unitario is None:
            return Decimal('0')
        return self.cantidad * self.precio_unitario

    def save(self, *args, **kwargs):
        es_nuevo = self.pk is None

        if es_nuevo:
            if not self.precio_unitario:
                self.precio_unitario = self.producto.precio

            if not self.producto.hay_stock(self.cantidad):
                raise ValueError(
                    f'Stock insuficiente para "{self.producto}": '
                    f'disponible {self.producto.stock}, solicitado {self.cantidad}.'
                )
            if not self.producto.es_servicio:
                self.producto.stock -= self.cantidad
                self.producto.save(update_fields=['stock'])

        super().save(*args, **kwargs)