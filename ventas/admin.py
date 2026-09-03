from django.contrib import admin
from .models import Venta, DetalleVenta


class DetalleInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0
    readonly_fields = ['precio_unitario', 'subtotal']


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ['id', 'cajero', 'fecha', 'metodo_pago', 'total', 'anulada']
    list_filter = ['anulada', 'metodo_pago']
    readonly_fields = ['total', 'fecha']
    inlines = [DetalleInline]