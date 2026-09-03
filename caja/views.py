from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from cuentas.decorators import solo_admin, admin_o_cajero
from .models import Caja, Turno, MovimientoCaja
from .forms import AbrirTurnoForm, CerrarTurnoForm, MovimientoForm


@login_required
@admin_o_cajero
def turno_actual(request):
    turno = Turno.objects.filter(
        cajero=request.user, estado=Turno.Estado.ABIERTO
    ).first()

    movimiento_form = MovimientoForm() if turno else None

    if turno and request.method == 'POST' and 'registrar_movimiento' in request.POST:
        movimiento_form = MovimientoForm(request.POST)
        if movimiento_form.is_valid():
            m = movimiento_form.save(commit=False)
            m.turno = turno
            m.registrado_por = request.user
            m.save()
            return redirect('caja:turno_actual')

    ventas      = turno.ventas.filter(anulada=False).order_by('-fecha')[:20] if turno else []
    movimientos = turno.movimientos.all() if turno else []

    return render(request, 'caja/turno_actual.html', {
        'turno': turno,
        'ventas': ventas,
        'movimientos': movimientos,
        'movimiento_form': movimiento_form,
    })


@login_required
@admin_o_cajero
def abrir_turno(request):
    if Turno.objects.filter(cajero=request.user, estado=Turno.Estado.ABIERTO).exists():
        return redirect('caja:turno_actual')

    error = None
    form = AbrirTurnoForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        caja = form.cleaned_data['caja']
        if caja.turno_abierto:
            error = f'"{caja}" ya tiene un turno abierto por otro cajero.'
        else:
            Turno.objects.create(
                caja=caja,
                cajero=request.user,
                monto_inicial=form.cleaned_data['monto_inicial'],
            )
            return redirect('caja:turno_actual')

    return render(request, 'caja/abrir_turno.html', {'form': form, 'error': error})


@login_required
@admin_o_cajero
def cerrar_turno(request, pk=None):
    """Cierra un turno. Sin pk: el cajero cierra su propio turno abierto.
    Con pk: solo un admin puede cerrar el turno de cualquier cajero."""
    es_admin = request.user.perfil.es_admin

    if pk is not None:
        if not es_admin:
            return redirect('sin_permiso')
        turno = get_object_or_404(Turno, pk=pk, estado=Turno.Estado.ABIERTO)
    else:
        turno = get_object_or_404(
            Turno, cajero=request.user, estado=Turno.Estado.ABIERTO
        )

    esperado = turno.calcular_monto_esperado_efectivo()
    form = CerrarTurnoForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        turno.cerrar(form.cleaned_data['monto_contado'])
        return redirect('caja:resumen_cierre', pk=turno.pk)

    return render(request, 'caja/cerrar_turno.html', {
        'turno': turno, 'form': form, 'esperado': esperado,
    })


@login_required
@admin_o_cajero
def resumen_cierre(request, pk):
    turno = get_object_or_404(Turno, pk=pk)
    return render(request, 'caja/resumen_cierre.html', {'turno': turno})


@login_required
@solo_admin
def lista_turnos(request):
    turnos = Turno.objects.select_related('caja', 'cajero').all()
    return render(request, 'caja/lista_turnos.html', {'turnos': turnos})