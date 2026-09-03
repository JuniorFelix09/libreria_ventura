from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from cuentas.decorators import solo_admin
from .models import Producto, Categoria
from .forms import ProductoForm


@login_required
@solo_admin
def lista_productos(request):
    productos = Producto.objects.select_related('categoria').all()
    return render(request, 'productos/lista.html', {'productos': productos})


@login_required
@solo_admin
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('productos:lista')
    else:
        form = ProductoForm()
    return render(request, 'productos/formulario.html', {'form': form, 'titulo': 'Nuevo producto'})


@login_required
@solo_admin
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('productos:lista')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'productos/formulario.html', {'form': form, 'titulo': 'Editar producto'})


@login_required
@solo_admin
def toggle_activo(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    producto.activo = not producto.activo
    producto.save(update_fields=['activo'])
    return redirect('productos:lista')


@login_required
@solo_admin
def crear_categoria(request):
    """Crea una categoría al vuelo desde el formulario de producto (vía fetch/JS)."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    nombre = request.POST.get('nombre', '').strip()
    if not nombre:
        return JsonResponse({'error': 'Escribe un nombre para la categoría.'}, status=400)

    categoria = Categoria.objects.filter(nombre__iexact=nombre).first()
    if not categoria:
        categoria = Categoria.objects.create(nombre=nombre)

    return JsonResponse({'id': categoria.pk, 'nombre': categoria.nombre})