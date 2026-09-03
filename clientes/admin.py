from django.contrib import admin
from .models import Cliente, AbonoFiado


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'telefono', 'es_profesor', 'permite_fiado', 'saldo_pendiente', 'activo']
    list_filter = ['es_profesor', 'permite_fiado', 'activo']
    search_fields = ['nombre', 'telefono']


@admin.register(AbonoFiado)
class AbonoFiadoAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'monto', 'fecha', 'registrado_por']
    list_filter = ['fecha']