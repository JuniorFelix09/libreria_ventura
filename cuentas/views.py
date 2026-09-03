from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Perfil


@login_required
def inicio(request):
    """Dashboard de bienvenida. Muestra opciones según el rol."""
    return render(request, 'cuentas/inicio.html')


def sin_permiso(request):
    """Se muestra cuando un cajero intenta entrar a una vista de admin."""
    return render(request, 'cuentas/sin_permiso.html', status=403)
# Create your views here.
