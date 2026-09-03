from django import forms
from .models import Caja, MovimientoCaja


class AbrirTurnoForm(forms.Form):
    caja = forms.ModelChoiceField(
        queryset=Caja.objects.filter(activa=True),
        label='Caja física',
        empty_label='Selecciona una caja',
    )
    monto_inicial = forms.DecimalField(
        max_digits=10, decimal_places=2, min_value=0,
        label='Efectivo inicial en gaveta',
        widget=forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0.00'}),
    )


class CerrarTurnoForm(forms.Form):
    monto_contado = forms.DecimalField(
        max_digits=10, decimal_places=2, min_value=0,
        label='Efectivo contado físicamente en gaveta',
        widget=forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0.00'}),
    )


class MovimientoForm(forms.ModelForm):
    class Meta:
        model = MovimientoCaja
        fields = ['tipo', 'monto', 'motivo']
        widgets = {
            'monto':  forms.NumberInput(attrs={'step': '0.01', 'min': '0.01', 'placeholder': '0.00'}),
            'motivo': forms.TextInput(attrs={'placeholder': 'Describe el motivo'}),
        }