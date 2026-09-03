from decimal import Decimal, InvalidOperation

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from cuentas.decorators import admin_o_cajero, solo_admin
from caja.models import Turno
from productos.models import Producto
from clientes.models import Cliente
from .models import Venta, DetalleVenta


@login_required
@admin_o_cajero
def nueva_venta(request):
    turno = Turno.objects.filter(cajero=request.user, estado=Turno.Estado.ABIERTO).first()
    if not turno:
        return render(request, 'ventas/sin_turno.html')

    productos = Producto.objects.filter(activo=True).filter(
        Q(es_servicio=True) | Q(stock__gt=0)
    ).select_related('categoria')
    clientes = Cliente.objects.filter(activo=True).filter(
        Q(es_profesor=True) | Q(permite_fiado=True)
    )
    error = None

    if request.method == 'POST':
        metodo_pago = request.POST.get('metodo_pago')
        cliente_id = request.POST.get('cliente_id') or None
        cliente = Cliente.objects.filter(pk=cliente_id).first() if cliente_id else None

        if metodo_pago not in ['EFECTIVO', 'TARJETA', 'FIADO']:
            error = 'Selecciona un método de pago.'
        elif metodo_pago == 'FIADO' and not cliente:
            error = 'Selecciona un cliente para vender fiado.'
        elif metodo_pago == 'FIADO' and not cliente.permite_fiado:
            error = f'"{cliente.nombre}" no tiene permiso de fiado.'
        else:
            lineas = []
            for p in productos:
                try:
                    cantidad = int(request.POST.get(f'cant_{p.pk}', 0))
                except ValueError:
                    cantidad = 0
                if cantidad <= 0:
                    continue

                if p.es_servicio:
                    precio_txt = request.POST.get(f'precio_{p.pk}', '')
                    try:
                        precio = Decimal(precio_txt)
                    except (InvalidOperation, ValueError):
                        precio = None
                    if not precio or precio <= 0:
                        error = f'Ingresa un precio válido para "{p.nombre}".'
                        break
                    lineas.append((p, cantidad, precio))
                else:
                    lineas.append((p, cantidad, None))

            if not error:
                if not lineas:
                    error = 'Agrega al menos un producto o servicio a la venta.'
                else:
                    subtotal_estimado = sum(
                        (precio if precio else p.precio) * cantidad for p, cantidad, precio in lineas
                    )
                    subtotal_descontable = sum(
                        (
                            (precio if precio else p.precio) * cantidad
                            for p, cantidad, precio in lineas if p.aplica_descuento_profesor
                        ),
                        Decimal('0'),
                    )
                    descuento_pct = cliente.descuento_pct if (cliente and cliente.es_profesor) else Decimal('0')
                    total_estimado = subtotal_estimado - (subtotal_descontable * (descuento_pct / 100))

                    if metodo_pago == 'FIADO' and not cliente.puede_fiar(total_estimado):
                        error = (
                            f'"{cliente.nombre}" excede su límite de fiado '
                            f'(saldo actual RD${cliente.saldo_pendiente}, límite RD${cliente.limite_fiado}).'
                        )

                    if not error:
                        try:
                            with transaction.atomic():
                                venta = Venta.objects.create(
                                    turno=turno, cajero=request.user, metodo_pago=metodo_pago,
                                    cliente=cliente, descuento_pct=descuento_pct,
                                )
                                for p, cantidad, precio in lineas:
                                    DetalleVenta.objects.create(
                                        venta=venta, producto=p,
                                        cantidad=cantidad,
                                        precio_unitario=precio if precio else p.precio,
                                    )
                                venta.total = venta.calcular_total()
                                venta.save(update_fields=['total'])
                            return redirect('ventas:detalle', pk=venta.pk)
                        except ValueError as e:
                            error = str(e)

    return render(request, 'ventas/nueva_venta.html', {
        'turno': turno, 'productos': productos, 'clientes': clientes, 'error': error,
    })


@login_required
@admin_o_cajero
def detalle_venta(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    return render(request, 'ventas/detalle_venta.html', {'venta': venta})


@login_required
@solo_admin
def anular_venta(request, pk):
    venta = get_object_or_404(Venta, pk=pk, anulada=False)
    if request.method == 'POST':
        motivo = request.POST.get('motivo', 'Sin motivo especificado')
        with transaction.atomic():
            for d in venta.detalles.all():
                if not d.producto.es_servicio:
                    d.producto.stock += d.cantidad
                    d.producto.save(update_fields=['stock'])
            venta.anulada = True
            venta.motivo_anulacion = motivo
            venta.save(update_fields=['anulada', 'motivo_anulacion'])
        return redirect('ventas:detalle', pk=pk)
    return render(request, 'ventas/anular_venta.html', {'venta': venta})