from django import forms
from .models import Producto


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'nombre', 'categoria', 'precio', 'stock',
            'es_servicio', 'aplica_descuento_profesor', 'activo',
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Nombre del producto o servicio'}),
            'precio': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'placeholder': '0.00'}),
            'stock':  forms.NumberInput(attrs={'min': '0', 'placeholder': '0'}),
        }