from django.contrib import admin
from .models import Caja, Turno, MovimientoCaja


@admin.register(Caja)
class CajaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activa']
    list_editable = ['activa']


@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ['caja', 'cajero', 'estado', 'fecha_apertura', 'monto_inicial', 'diferencia']
    list_filter = ['estado', 'caja']
    readonly_fields = ['monto_esperado_efectivo', 'monto_esperado_tarjeta', 'diferencia', 'fecha_cierre']


@admin.register(MovimientoCaja)
class MovimientoCajaAdmin(admin.ModelAdmin):
    list_display = ['turno', 'tipo', 'monto', 'motivo', 'fecha']
    list_filter = ['tipo']