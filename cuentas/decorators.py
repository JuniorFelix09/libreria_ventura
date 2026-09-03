from functools import wraps

from django.shortcuts import redirect

from .models import Perfil


def requiere_rol(*roles):
    """Decorador base. Uso: @requiere_rol(Perfil.Rol.ADMIN, Perfil.Rol.CAJERO)"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            try:
                rol = request.user.perfil.rol
            except Perfil.DoesNotExist:
                return redirect('login')
            if rol not in roles:
                return redirect('sin_permiso')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def solo_admin(view_func):
    """Solo el administrador puede entrar a esta vista."""
    return requiere_rol(Perfil.Rol.ADMIN)(view_func)


def solo_cajero(view_func):
    """Solo el cajero puede entrar a esta vista."""
    return requiere_rol(Perfil.Rol.CAJERO)(view_func)


def admin_o_cajero(view_func):
    """Cualquier usuario autenticado con rol válido puede entrar."""
    return requiere_rol(Perfil.Rol.ADMIN, Perfil.Rol.CAJERO)(view_func)