from django.db import models


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    nombre    = models.CharField(max_length=200)
    categoria = models.ForeignKey(
        Categoria, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos'
    )
    precio    = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text='Para servicios, este es solo un precio sugerido: podrás cambiarlo en cada venta.',
    )
    stock     = models.PositiveIntegerField(default=0, help_text='No aplica para servicios.')
    es_servicio = models.BooleanField(
        default=False,
        help_text='Actívalo para servicios (fotocopias, impresiones, etc.) sin control de stock y con precio variable en cada venta.',
    )
    aplica_descuento_profesor = models.BooleanField(
        default=False,
        verbose_name='Aplica descuento de profesor',
        help_text='Actívalo solo en los productos/servicios donde el descuento de profesor debe aplicar (ej. copias). El resto del carrito no se descuenta.',
    )
    activo    = models.BooleanField(
        default=True,
        help_text='Desactívalo si ya no se vende, sin borrar su historial en ventas.',
    )

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    def hay_stock(self, cantidad=1):
        if self.es_servicio:
            return True
        return self.stock >= cantidad