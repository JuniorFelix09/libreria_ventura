from django.conf import settings
from django.db import models
from django.utils import timezone


class Caja(models.Model):
    """Caja física (la gaveta). Ej: 'Caja 1', 'Caja 2'."""

    nombre = models.CharField(max_length=50, unique=True)
    activa = models.BooleanField(
        default=True,
        help_text='Desactívala si esa caja deja de usarse, sin borrar su historial.',
    )

    class Meta:
        verbose_name = 'Caja'
        verbose_name_plural = 'Cajas'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    @property
    def turno_abierto(self):
        return self.turnos.filter(estado=Turno.Estado.ABIERTO).first()


class Turno(models.Model):
    """Una apertura/cierre de una Caja por un cajero.

    Las ventas y movimientos se ligan al Turno, no a la Caja directamente:
    así las dos cajas operan en paralelo sin pisarse, y cada una cierra sola.
    """

    class Estado(models.TextChoices):
        ABIERTO = 'ABIERTO', 'Abierto'
        CERRADO = 'CERRADO', 'Cerrado'

    caja = models.ForeignKey(Caja, on_delete=models.PROTECT, related_name='turnos')
    cajero = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='turnos'
    )
    estado = models.CharField(
        max_length=10, choices=Estado.choices, default=Estado.ABIERTO
    )

    fecha_apertura = models.DateTimeField(default=timezone.now)
    monto_inicial = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text='Efectivo con el que se abre la gaveta al inicio del turno.',
    )

    fecha_cierre = models.DateTimeField(null=True, blank=True)
    monto_esperado_efectivo = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text='Calculado al cerrar: inicial + efectivo vendido + ingresos - retiros.',
    )
    monto_esperado_tarjeta = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text='Total vendido por tarjeta (informativo, no se cuenta físico).',
    )
    monto_contado = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text='Conteo físico que ingresa el cajero al cerrar.',
    )
    diferencia = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text='monto_contado - monto_esperado_efectivo. (+) sobrante, (-) faltante.',
    )

    class Meta:
        verbose_name = 'Turno'
        verbose_name_plural = 'Turnos'
        ordering = ['-fecha_apertura']
        constraints = [
            models.UniqueConstraint(
                fields=['caja'],
                condition=models.Q(estado='ABIERTO'),
                name='una_caja_un_turno_abierto',
            ),
        ]

    def __str__(self):
        return f'{self.caja} · {self.cajero} ({self.fecha_apertura:%d/%m/%Y %H:%M})'

    def _total_ventas(self, metodo_pago):
        return (
            self.ventas.filter(metodo_pago=metodo_pago, anulada=False)
            .aggregate(total=models.Sum('total'))['total'] or 0
        )

    def _total_movimientos(self, tipo):
        return (
            self.movimientos.filter(tipo=tipo)
            .aggregate(total=models.Sum('monto'))['total'] or 0
        )

    @property
    def total_ventas_efectivo(self):
        from ventas.models import Venta
        return self._total_ventas(Venta.MetodoPago.EFECTIVO)

    @property
    def total_ventas_tarjeta(self):
        from ventas.models import Venta
        return self._total_ventas(Venta.MetodoPago.TARJETA)

    def calcular_monto_esperado_efectivo(self):
        from ventas.models import Venta
        ingresos = self._total_movimientos(MovimientoCaja.Tipo.INGRESO)
        retiros  = self._total_movimientos(MovimientoCaja.Tipo.RETIRO)
        return (
            self.monto_inicial
            + self._total_ventas(Venta.MetodoPago.EFECTIVO)
            + ingresos
            - retiros
        )

    def cerrar(self, monto_contado):
        """Cierra el turno, calcula diferencia y guarda. Devuelve la diferencia."""
        if self.estado == self.Estado.CERRADO:
            raise ValueError('Este turno ya está cerrado.')
        from ventas.models import Venta
        self.monto_esperado_efectivo = self.calcular_monto_esperado_efectivo()
        self.monto_esperado_tarjeta  = self._total_ventas(Venta.MetodoPago.TARJETA)
        self.monto_contado           = monto_contado
        self.diferencia              = self.monto_contado - self.monto_esperado_efectivo
        self.estado                  = self.Estado.CERRADO
        self.fecha_cierre            = timezone.now()
        self.save()
        return self.diferencia


class MovimientoCaja(models.Model):
    """Movimientos de efectivo que no son ventas: retiros, cambios de fondo, etc."""

    class Tipo(models.TextChoices):
        RETIRO  = 'RETIRO',  'Retiro'
        INGRESO = 'INGRESO', 'Ingreso / cambio de fondo'

    turno          = models.ForeignKey(Turno, on_delete=models.CASCADE, related_name='movimientos')
    tipo           = models.CharField(max_length=10, choices=Tipo.choices)
    monto          = models.DecimalField(max_digits=10, decimal_places=2)
    motivo         = models.CharField(max_length=255)
    fecha          = models.DateTimeField(default=timezone.now)
    registrado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'Movimiento de caja'
        verbose_name_plural = 'Movimientos de caja'
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.get_tipo_display()} RD${self.monto} — {self.turno}'