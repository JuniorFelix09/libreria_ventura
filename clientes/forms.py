from django import forms
from .models import Cliente, AbonoFiado


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            'nombre', 'telefono',
            'es_profesor', 'descuento_pct',
            'permite_fiado', 'limite_fiado',
            'activo',
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Nombre completo'}),
            'telefono': forms.TextInput(attrs={'placeholder': 'Opcional'}),
            'descuento_pct': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'max': '100'}),
            'limite_fiado': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'placeholder': '0 = sin límite'}),
        }


class AbonoForm(forms.ModelForm):
    class Meta:
        model = AbonoFiado
        fields = ['monto', 'nota']
        widgets = {
            'monto': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01', 'placeholder': 'Monto abonado'}),
            'nota': forms.TextInput(attrs={'placeholder': 'Opcional'}),
        }