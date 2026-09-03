from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from cuentas.decorators import solo_admin, admin_o_cajero
from .models import Cliente
from .forms import ClienteForm, AbonoForm


@login_required
@admin_o_cajero
def lista(request):
    clientes = Cliente.objects.all()
    return render(request, 'clientes/lista.html', {'clientes': clientes})


@login_required
@solo_admin
def crear(request):
    form = ClienteForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('clientes:lista')
    return render(request, 'clientes/formulario.html', {'form': form, 'titulo': 'Nuevo cliente'})


@login_required
@solo_admin
def editar(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    form = ClienteForm(request.POST or None, instance=cliente)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('clientes:lista')
    return render(request, 'clientes/formulario.html', {'form': form, 'titulo': f'Editar: {cliente.nombre}'})


@login_required
@solo_admin
def toggle_activo(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    cliente.activo = not cliente.activo
    cliente.save(update_fields=['activo'])
    return redirect('clientes:lista')


@login_required
@admin_o_cajero
def detalle(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    form = AbonoForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        abono = form.save(commit=False)
        abono.cliente = cliente
        abono.registrado_por = request.user
        abono.save()
        return redirect('clientes:detalle', pk=cliente.pk)

    ventas_fiado = cliente.ventas.filter(metodo_pago='FIADO').order_by('-fecha')
    abonos = cliente.abonos.all()

    return render(request, 'clientes/detalle.html', {
        'cliente': cliente,
        'form': form,
        'ventas_fiado': ventas_fiado,
        'abonos': abonos,
    })