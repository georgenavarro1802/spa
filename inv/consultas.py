from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q, Sum
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.loader import render_to_string

from inv.forms import AnularFacturaForm, DepositarForm, ChequeProtestadoForm, AreaForm
from inv.funciones import (MiPaginador, url_back,
                           mensaje_excepcion, salva_auditoria, generar_pdf, get_pdf_factura, ok_json, bad_json)
from inv.funciones_excel import (WriteToExcel_Ventas_Resumen, WriteToExcel_Ventas_Detallado,
                                 WriteToExcel_Compras_Resumen, WriteToExcel_Compras_Detallado,
                                 WriteToExcel_Inventarios_Resumen)
from inv.models import (IngresoProducto, Factura, Pago, InventarioReal, Vendedor, DetalleIngresoProducto,
                        TipoProducto, ChequeProtestado, SolicitudCompra, SesionCaja, HistorialCifProducto,
                        HistorialPrecioProducto, Cajero, OrdenServicio, Cliente, Colaborador, Producto,
                        DevolucionIngresoProducto, Area, DetalleFactura, DevolucionVenta, KardexInventario)
from inv.views import addUserData, convertir_fecha
from spa.settings import (MEDIA_URL, ACCION_MODIFICAR, ACCION_ADICIONAR, TIPO_MOVIMIENTO_ENTRADA,
                          ACCION_ELIMINAR, ESTADO_SOLICITUD_APROBADA, ESTADO_SOLICITUD_DENEGADA)


@login_required(redirect_field_name='ret', login_url='/login')
def view(request):
    ex = None
    data = {'title': u'Consultas'}
    addUserData(request, data)
    empresaid = request.session['empresa'].id

    if request.method == 'POST':
        action = request.POST['action']

        if action == 'detalles_pagos_vendedor':
            factura = Factura.objects.get(pk=request.POST['fid'])
            pagos = []
            detalle_pago = ''
            for p in factura.pago_set.all():
                if p.es_efectivo():
                    detalle_pago = 'EFECTIVO'
                elif p.es_cheque():
                    cheque = p.pago_cheque()
                    detalle_pago = 'CHEQUE No. %s de %s, emitido por %s, [%s] (Postfecha: %s)' % (
                        cheque.numero, cheque.banco.nombre, cheque.emite,
                        'Depositado' if cheque.depositado else 'NO Depositado', 'SI' if cheque.postfechado else 'NO')
                elif p.es_deposito():
                    deposito = p.pago_deposito()
                    detalle_pago = 'DEPOSITO No. %s efectuado por %s' % (deposito.numero, deposito.efectuadopor)
                elif p.es_transferencia():
                    transferencia = p.pago_transferencia()
                    detalle_pago = 'TRANSFERENCIA No. %s efectuada por %s' % (transferencia.numero, transferencia.efectuadopor)
                elif p.es_tarjeta():
                    tarjeta = p.pago_tarjeta()
                    detalle_pago = 'TARJETA %s de %s, REF: %s, Poseedor: %s (Proc.Pago: %s)' % (tarjeta.tipotarjeta,
                                                                                                tarjeta.banco.nombre,
                                                                                                tarjeta.referencia,
                                                                                                tarjeta.poseedor,
                                                                                                tarjeta.procesadorpago)
                elif p.es_retencion():
                    retencion = p.pago_retencion()
                    detalle_pago = 'RETENCION No. %s' % retencion.numero

                pagos.append((p.fecha.strftime('%d-%m-%Y'), p.tipo(), p.valor, detalle_pago))

            return ok_json(data={"pagos": pagos,
                                 "numerofactura": factura.numero,
                                 "clientefactura": factura.cliente.__str__(),
                                 "totalpagado": factura.pagado})

        if action == 'detalles_pagos_colaborador':
            factura = Factura.objects.get(pk=request.POST['fid'])
            pagos = []
            detalle_pago = ''
            for p in factura.pago_set.all():
                if p.es_efectivo():
                    detalle_pago = 'EFECTIVO'
                elif p.es_cheque():
                    cheque = p.pago_cheque()
                    detalle_pago = 'CHEQUE No. %s de %s, emitido por %s, [%s] (Postfecha: %s)' % (
                        cheque.numero, cheque.banco.nombre, cheque.emite,
                        'Depositado' if cheque.depositado else 'NO Depositado', 'SI' if cheque.postfechado else 'NO')
                elif p.es_deposito():
                    deposito = p.pago_deposito()
                    detalle_pago = 'DEPOSITO No. %s efectuado por %s' % (deposito.numero, deposito.efectuadopor)
                elif p.es_transferencia():
                    transferencia = p.pago_transferencia()
                    detalle_pago = 'TRANSFERENCIA No. %s efectuada por %s' % (transferencia.numero, transferencia.efectuadopor)
                elif p.es_tarjeta():
                    tarjeta = p.pago_tarjeta()
                    detalle_pago = 'TARJETA %s de %s, REF: %s, Poseedor: %s (Proc.Pago: %s)' % (
                        tarjeta.tipotarjeta, tarjeta.banco.nombre, tarjeta.referencia, tarjeta.poseedor, tarjeta.procesadorpago)
                elif p.es_retencion():
                    retencion = p.pago_retencion()
                    detalle_pago = 'RETENCION No. %s' % retencion.numero

                pagos.append((p.fecha.strftime('%d-%m-%Y'), p.tipo(), p.valor, detalle_pago))

            return ok_json(data={"pagos": pagos,
                                 "numerofactura": factura.numero,
                                 "clientefactura": factura.cliente.__str__(),
                                 "totalpagado": factura.pagado})

        elif action == 'detalles_pagos_cajero':
            factura = Factura.objects.get(pk=request.POST['fid'])
            pagos = []
            detalle_pago = ''
            for p in factura.pago_set.all():
                if p.es_efectivo():
                    detalle_pago = 'EFECTIVO'
                elif p.es_cheque():
                    cheque = p.pago_cheque()
                    detalle_pago = 'CHEQUE No. %s de %s, emitido por %s, [%s] (Postfecha: %s)' % (
                        cheque.numero, cheque.banco.nombre, cheque.emite,
                        'Depositado' if cheque.depositado else 'NO Depositado', 'SI' if cheque.postfechado else 'NO')
                elif p.es_deposito():
                    deposito = p.pago_deposito()
                    detalle_pago = 'DEPOSITO No. %s efectuado por %s' % (deposito.numero, deposito.efectuadopor)
                elif p.es_transferencia():
                    transferencia = p.pago_transferencia()
                    detalle_pago = 'TRANSFERENCIA No. %s efectuada por %s' % (
                        transferencia.numero, transferencia.efectuadopor)
                elif p.es_tarjeta():
                    tarjeta = p.pago_tarjeta()
                    detalle_pago = 'TARJETA %s de %s, REF: %s, Poseedor: %s (Proc.Pago: %s)' % (
                        tarjeta.tipotarjeta, tarjeta.banco.nombre, tarjeta.referencia, tarjeta.poseedor,
                        tarjeta.procesadorpago)
                elif p.es_retencion():
                    retencion = p.pago_retencion()
                    detalle_pago = 'RETENCION No. %s' % retencion.numero

                pagos.append((p.fecha.strftime('%d-%m-%Y'), p.tipo(), p.valor, detalle_pago))

            return ok_json(data={"pagos": pagos,
                                 "numerofactura": factura.numero,
                                 "clientefactura": factura.cliente.__unicode__(),
                                 "totalpagado": factura.pagado})

        elif action == 'anular_factura':
            factura = Factura.objects.get(pk=request.POST['id'])
            f = AnularFacturaForm(request.POST)
            usuario = request.user.username
            if f.is_valid():
                try:
                    with transaction.atomic():
                        factura.motivoanulacion = f.cleaned_data['motivo']
                        factura.usuarioanula = usuario
                        factura.valida = False
                        factura.save()

                        # Actualizar Inventario
                        for d in factura.detalles.all():
                            if InventarioReal.objects.filter(producto=d.producto).exists():
                                inventarioreal = InventarioReal.objects.filter(producto=d.producto)[0]
                                inventarioreal.cantidad += d.cantidad
                                if DetalleIngresoProducto.objects.filter(producto=d.producto).exists():
                                    ultimoingresoprod = DetalleIngresoProducto.objects.filter(producto=d.producto).latest('id')
                                    inventarioreal.valor += ultimoingresoprod.valor
                                else:
                                    inventarioreal.valor += d.valor
                                inventarioreal.costo = round(inventarioreal.valor / inventarioreal.cantidad, 2)
                                inventarioreal.save()
                            else:
                                inventarioreal = InventarioReal(producto=d.producto, cantidad=d.cantidad,
                                                                costo=d.precio, valor=d.valor)
                                inventarioreal.save()

                        salva_auditoria(request, factura, ACCION_ELIMINAR)
                        return ok_json()

                except Exception:
                    return bad_json(error=1)
            else:
                return bad_json(error=1)

        elif action == 'depositar_cheque':
            pago = Pago.objects.get(pk=request.POST['id'])
            f = DepositarForm(request.POST)
            if f.is_valid():
                try:
                    with transaction.atomic():
                        cheque = pago.pago_cheque()
                        if cheque:
                            if f.cleaned_data['fechadepositado'] > datetime.now().date():
                                return bad_json(mensaje=u"Error, la fecha es mayor que hoy")
                            cheque.depositado = True
                            cheque.fechadepositado = f.cleaned_data['fechadepositado']
                            cheque.save()
                            salva_auditoria(request, cheque, ACCION_ADICIONAR)
                            return ok_json()
                        else:
                            raise Exception

                except Exception:
                    return bad_json(error=1)
            else:
                return bad_json(error=1)

        elif action == 'protestar_cheque':
            pago = Pago.objects.get(pk=request.POST['id'])
            f = ChequeProtestadoForm(request.POST)
            if f.is_valid():
                try:
                    with transaction.atomic():
                        cheque = pago.pago_cheque()
                        factura = pago.factura
                        if cheque:
                            if f.cleaned_data['fecha'] > datetime.now().date():
                                return bad_json(mensaje=u"Error, la fecha es mayor que hoy")
                            cheque.protestado = True
                            cheque.save()
                            protesto = ChequeProtestado(cheque=cheque,
                                                        motivo=f.cleaned_data['motivo'],
                                                        fecha=f.cleaned_data['fecha'])
                            protesto.save()
                            factura.save()  # recalcular pagado y estado cancelada en factura
                            salva_auditoria(request, protesto, ACCION_ADICIONAR)
                            return ok_json()
                        else:
                            raise Exception

                except Exception:
                    return bad_json(error=1)
            else:
                return bad_json(error=1)

        elif action == 'aprobar_solicitud_cliente':
            try:
                solicitud = SolicitudCompra.objects.get(pk=request.POST['scid'])
                with transaction.atomic():
                    solicitud.estado = ESTADO_SOLICITUD_APROBADA
                    solicitud.save()
                    salva_auditoria(request, solicitud, ACCION_MODIFICAR)
                    return ok_json()

            except Exception:
                return bad_json(error=1)

        elif action == 'aprobar_solicitud_vendedor':
            try:
                solicitud = SolicitudCompra.objects.get(pk=request.POST['svid'])
                with transaction.atomic():
                    solicitud.estado = ESTADO_SOLICITUD_APROBADA
                    solicitud.save()
                    salva_auditoria(request, solicitud, ACCION_MODIFICAR)
                    return ok_json()
            except Exception:
                return bad_json(error=1)

        elif action == 'denegar_solicitud_cliente':
            try:
                solicitud = SolicitudCompra.objects.get(pk=request.POST['scid'])
                with transaction.atomic():
                    solicitud.estado = ESTADO_SOLICITUD_DENEGADA
                    solicitud.save()
                    salva_auditoria(request, solicitud, ACCION_MODIFICAR)
                    return ok_json()
            except Exception:
                return bad_json(error=1)

        elif action == 'denegar_solicitud_vendedor':
            try:
                solicitud = SolicitudCompra.objects.get(pk=request.POST['svid'])
                with transaction.atomic():
                    solicitud.estado = ESTADO_SOLICITUD_DENEGADA
                    solicitud.save()
                    salva_auditoria(request, solicitud, ACCION_MODIFICAR)
                    return ok_json()
            except Exception:
                return bad_json(error=1)

        elif action == 'trasladoinv':
            inventario = InventarioReal.objects.get(pk=request.POST['id'])
            f = AreaForm(request.POST)
            if f.is_valid():
                try:
                    with transaction.atomic():
                        inventario.area = f.cleaned_data['area']
                        inventario.save()
                        salva_auditoria(request, inventario, ACCION_MODIFICAR)
                        return ok_json()
                except Exception:
                    return bad_json(error=1)
            else:
                return bad_json(error=1)

        elif action == 'imprimir_factura':
            try:
                factura = Factura.objects.get(pk=request.POST['fid'])
                # FPDF Factura
                pdfname = get_pdf_factura(factura, empresaid, request.user.username)
                return ok_json(data={'reportfile': '/'.join([MEDIA_URL, 'documentos', 'userreports', request.user.username, pdfname])})
            except Exception:
                return bad_json(error=1)

        if action == 'devolucion_compra':
            try:
                compra = IngresoProducto.objects.get(pk=request.POST['idc'])
                with transaction.atomic():
                    # Actualizar Inventario Real
                    if Area.objects.exists():
                        if Area.objects.filter(es_principal=True):
                            area = Area.objects.filter(es_principal=True)[0]
                        else:
                            area = Area.objects.all()[0]
                    else:
                        area = Area(nombre='Matriz', es_principal=True)
                        area.save()

                    for elemento in request.POST['lista'].split(','):
                        idelem = int(elemento.split(":")[0])
                        cantelem = int(elemento.split(":")[1])
                        detallecompra = DetalleIngresoProducto.objects.get(pk=idelem)
                        producto = detallecompra.producto

                        # Actualizar Inventario si es producto
                        if producto:
                            devolucion = DevolucionIngresoProducto(compra=compra,
                                                                   detallecompra=detallecompra,
                                                                   cantidad=cantelem,
                                                                   costo=detallecompra.costo)
                            devolucion.save()

                            producto.actualizar_inventario_salida(devolucion, area, "C")

                    compra.valor_devolucion = compra.calcular_valor_devolucion()
                    compra.save()
                    return ok_json()

            except Exception:
                return bad_json(error=1)

        if action == 'devolucion_venta':
            try:
                venta = Factura.objects.get(pk=request.POST['idv'])
                with transaction.atomic():
                    if venta.tiene_pagos_asociados():
                        return bad_json(mensaje=u'La factura tiene al menos un pago asociado')
                    # Actualizar Inventario Real
                    if Area.objects.exists():
                        if Area.objects.filter(es_principal=True):
                            area = Area.objects.filter(es_principal=True)[0]
                        else:
                            area = Area.objects.all()[0]
                    else:
                        area = Area(nombre='Matriz', es_principal=True)
                        area.save()

                    for elemento in request.POST['lista'].split(','):
                        idelem = int(elemento.split(":")[0])
                        cantelem = int(elemento.split(":")[1])
                        detalleventa = DetalleFactura.objects.get(pk=idelem)
                        producto = detalleventa.producto

                        # Actualizar Inventario si es producto
                        if producto:
                            devolucion = DevolucionVenta(venta=venta,
                                                         detalleventa=detalleventa,
                                                         cantidad=cantelem,
                                                         precio=detalleventa.precio)
                            devolucion.save()

                            # COSTO Y SALDO ANTES DEL MOVIMIENTO
                            saldoinicialvalor = detalleventa.producto.valor_inventario(area)
                            saldoinicialcantidad = detalleventa.producto.stock_inventario(area)

                            # ACTUALIZAR INVENTARIO REAL
                            costoproducto = round((saldoinicialvalor / saldoinicialcantidad), 2) if saldoinicialcantidad else 0
                            producto.actualizar_inventario_ingreso(costoproducto, devolucion.cantidad, area)
                            inventario = producto.mi_inventario(area)

                            # ACTUALIZAR KARDEX
                            kardex = KardexInventario(producto=detalleventa.producto,
                                                      inventario=inventario,
                                                      tipomovimiento=TIPO_MOVIMIENTO_ENTRADA,
                                                      ddevventa=devolucion,
                                                      saldoinicialvalor=saldoinicialvalor,
                                                      saldoinicialcantidad=saldoinicialcantidad,
                                                      cantidad=devolucion.cantidad,
                                                      costo=costoproducto,
                                                      valor=round((costoproducto * devolucion.cantidad), 2))
                            kardex.save()

                            # COSTO Y SALDO DESPUES DEL MOVIMIENTO
                            saldofinalvalor = detalleventa.producto.valor_inventario(area)
                            saldofinalcantidad = detalleventa.producto.stock_inventario(area)
                            kardex.saldofinalcantidad = saldofinalcantidad
                            kardex.saldofinalvalor = saldofinalvalor
                            kardex.save()

                    # Actualizar valor devuelto en la venta
                    venta.valor_devolucion = venta.calcular_valor_devolucion()
                    venta.save()
                    return ok_json()
            except Exception as ex:
                return bad_json(error=1)

        return bad_json(error=0)
    else:
        if 'action' in request.GET:
            action = request.GET['action']

            if action == 'detalles_vendedor':
                try:
                    data['vendedor'] = Vendedor.objects.get(pk=request.GET['id'])
                    return render_to_response('consultas/detalles_vendedor.html', data)
                except Exception as ex:
                    pass

            elif action == 'detalles_colaborador':
                try:
                    data['colaborador'] = Colaborador.objects.get(pk=request.GET['id'])
                    return render_to_response('consultas/detalles_colaborador.html', data)
                except Exception as ex:
                    pass

            elif action == 'detalles_cajero':
                try:
                    data['cajero'] = Cajero.objects.get(pk=request.GET['id'])
                    return render_to_response('consultas/detalles_cajero.html', data)
                except Exception as ex:
                    pass

            elif action == 'anular_factura':
                try:
                    data['title'] = u'Anular Factura'
                    data['factura'] = Factura.objects.get(pk=request.GET['id'])
                    data['form'] = AnularFacturaForm()
                    return render_to_response('consultas/anular_factura.html', data)
                except Exception as ex:
                    pass

            elif action == 'detalle_factura':
                try:
                    data['factura'] = factura = Factura.objects.get(pk=request.GET['fid'])
                    data['detalles'] = factura.detallefactura_set.all()
                    return render_to_response('consultas/detallefacturas.html', data)
                except Exception as ex:
                    pass

            elif action == 'detalle_compra':
                try:
                    data['compra'] = compra = IngresoProducto.objects.get(pk=request.GET['cid'])
                    data['detalles'] = compra.detalleingresoproducto_set.all()
                    return render_to_response('consultas/detallecompras.html', data)
                except Exception as ex:
                    pass

            elif action == 'detalle_solicitud_cliente':
                try:
                    data['solicitud'] = solicitud = SolicitudCompra.objects.get(pk=request.GET['scid'])
                    data['detalles'] = solicitud.detallesolicitudcompra_set.filter(solicitud__vendedor__isnull=True)
                    return render_to_response('consultas/detallesolicitudc.html', data)
                except Exception as ex:
                    pass

            elif action == 'detalle_solicitud_vendedor':
                try:
                    data['solicitud'] = solicitud = SolicitudCompra.objects.get(pk=request.GET['svid'])
                    data['detalles'] = solicitud.detallesolicitudcompra_set.filter(solicitud__vendedor__isnull=False)
                    return render_to_response('consultas/detallesolicitudv.html', data)
                except Exception as ex:
                    pass

            elif action == 'depositar_cheque':
                try:
                    data['title'] = 'Depositar Cheque'
                    data['pago'] = Pago.objects.get(pk=request.GET['id'])
                    data['form'] = DepositarForm(initial={'fechadepositado': datetime.now().date()})
                    return render_to_response('consultas/depositar_cheque.html', data)
                except Exception as ex:
                    pass

            elif action == 'protestar_cheque':
                try:
                    data['title'] = 'Protestar Cheque'
                    data['pago'] = Pago.objects.get(pk=request.GET['id'])
                    data['form'] = ChequeProtestadoForm(initial={'fecha': datetime.now().date()})
                    return render_to_response('consultas/protestar_cheque.html', data)
                except Exception as ex:
                    pass

            elif action == 'trasladoinv':
                try:
                    data['title'] = 'Traslado de Inventarios'
                    data['inventario'] = inventario = InventarioReal.objects.get(pk=request.GET['id'])
                    form = AreaForm()
                    form.excluir_area_actual(inventario.area)
                    data['form'] = form
                    return render_to_response('consultas/trasladoinv.html', data)
                except Exception as ex:
                    pass

            elif action == 'imprimir_inventario':
                try:
                    categoria = None
                    inventarios = InventarioReal.objects.all().order_by('producto__tipoproducto')
                    total_cif = inventarios.aggregate(suma=Sum('costo'))['suma']
                    total_valor = inventarios.aggregate(suma=Sum('valor'))['suma']
                    if int(request.GET['cid']) > 0:
                        categoria = TipoProducto.objects.get(pk=request.GET['cid'])
                        inventarios = inventarios.filter(producto__tipoproducto=categoria)
                        total_cif = inventarios.aggregate(suma=Sum('costo'))['suma']
                        total_valor = inventarios.aggregate(suma=Sum('valor'))['suma']
                    data['categoria'] = categoria
                    data['inventarios'] = inventarios
                    data['total_cif'] = total_cif
                    data['total_valor'] = total_valor
                    data['hoy'] = datetime.now().date()
                    html = render_to_string('consultas/imprimir_inventario.html', data)
                    return generar_pdf(html)
                except Exception as ex:
                        pass

            elif action == 'consulta_ventas':
                try:
                    data['title'] = 'Consulta de ventas'
                    searchv = None
                    if 'sv' in request.GET:
                        searchv = request.GET['sv']

                    ventas = Factura.objects.all()
                    if searchv:
                        ventas = ventas.filter(Q(numero__icontains=searchv) |
                                               Q(cliente__ruc__icontains=searchv) |
                                               Q(cliente__nombre__icontains=searchv) |
                                               Q(cliente__direccion__icontains=searchv) |
                                               Q(vendedor__cedula__icontains=searchv) |
                                               Q(vendedor__nombre__icontains=searchv))

                    paging = MiPaginador(ventas, 25)
                    p = 1
                    try:
                        if 'page' in request.GET:
                            p = int(request.GET['page'])
                        page = paging.page(p)
                    except:
                        page = paging.page(1)
                    data['paging'] = paging
                    data['rangospaging'] = paging.rangos_paginado(p)
                    data['page'] = page
                    data['ventas'] = page.object_list
                    data['searchv'] = searchv if searchv else ""
                    return render_to_response('consultas/consulta_ventas.html', data)
                except Exception as ex:
                    pass

            elif action == 'exportar_resumen_ventas':
                try:
                    data['title'] = u'Exportar resumen de ventas a excel'
                    searchv = None
                    datos = Factura.objects.filter(ventas_por_mayor=True)
                    if 's' in request.GET and request.GET['s'] != "":
                        searchv = request.GET['s']
                        datos = datos.filter(Q(numero__icontains=searchv) |
                                             Q(cliente__ruc__icontains=searchv) |
                                             Q(cliente__nombre__icontains=searchv) |
                                             Q(cliente__direccion__icontains=searchv) |
                                             Q(vendedor__cedula__icontains=searchv) |
                                             Q(vendedor__nombre__icontains=searchv))
                    response = HttpResponse(content_type='application/vnd.ms-excel')
                    response['Content-Disposition'] = 'attachment; filename=report.xlsx'
                    xlsx_data = WriteToExcel_Ventas_Resumen(datos, searchv)
                    response.write(xlsx_data)
                    return response
                except Exception as ex:
                    pass

            elif action == 'exportar_detallado_ventas':
                try:
                    data['title'] = u'Exportar detallado de la venta a excel'
                    venta = Factura.objects.get(pk=int(request.GET['id']))
                    response = HttpResponse(content_type='application/vnd.ms-excel')
                    response['Content-Disposition'] = 'attachment; filename=report.xlsx'
                    xlsx_data = WriteToExcel_Ventas_Detallado(venta)
                    response.write(xlsx_data)
                    return response
                except Exception as ex:
                    pass

            elif action == 'consulta_compras':
                try:
                    data['title'] = 'Consulta de compras'
                    searchc = None
                    if 'sc' in request.GET:
                        searchc = request.GET['sc']

                    compras = IngresoProducto.objects.all()
                    if searchc:
                        compras = compras.filter(Q(numerodocumento__icontains=searchc) |
                                                 Q(proveedor__identificacion__icontains=searchc) |
                                                 Q(proveedor__nombre__icontains=searchc) |
                                                 Q(proveedor__nombre__icontains=searchc) |
                                                 Q(descripcion__icontains=searchc))

                    paging = MiPaginador(compras, 30)
                    p = 1
                    try:
                        if 'page' in request.GET:
                            p = int(request.GET['page'])
                        page = paging.page(p)
                    except:
                        page = paging.page(1)
                    data['paging'] = paging
                    data['rangospaging'] = paging.rangos_paginado(p)
                    data['page'] = page
                    data['compras'] = page.object_list
                    data['searchc'] = searchc if searchc else ""
                    return render_to_response('consultas/consulta_compras.html', data)
                except Exception as ex:
                    pass

            elif action == 'devolucion_compra':
                try:
                    data['title'] = u'Devolución de compra'
                    data['compra'] = compra = IngresoProducto.objects.get(pk=request.GET['id'])
                    data['detalles'] = compra.detalleingresoproducto_set.all()
                    data['detalles_devolucion'] = compra.devolucioningresoproducto_set.all()
                    return render_to_response('consultas/devolucion_compra.html', data)
                except Exception as ex:
                    pass

            elif action == 'devolucion_venta':
                try:
                    data['title'] = u'Devolución de venta'
                    data['venta'] = venta = Factura.objects.get(pk=request.GET['id'])
                    data['detalles'] = venta.detallefactura_set.all()
                    data['detalles_devolucion'] = venta.devolucionventa_set.all()
                    return render_to_response('consultas/devolucion_venta.html', data)
                except Exception as ex:
                    pass

            elif action == 'exportar_resumen_compras':
                try:
                    data['title'] = u'Exportar resumen de compras a excel'
                    searchc = None
                    datos = IngresoProducto.objects.all()
                    if 's' in request.GET and request.GET['s'] != "":
                        searchc = request.GET['s']
                        datos = datos.filter(Q(numerodocumento__icontains=searchc) |
                                             Q(proveedor__identificacion__icontains=searchc) |
                                             Q(proveedor__nombre__icontains=searchc) |
                                             Q(proveedor__nombre__icontains=searchc) |
                                             Q(descripcion__icontains=searchc))
                    response = HttpResponse(content_type='application/vnd.ms-excel')
                    response['Content-Disposition'] = 'attachment; filename=report.xlsx'
                    xlsx_data = WriteToExcel_Compras_Resumen(datos, searchc)
                    response.write(xlsx_data)
                    return response
                except Exception as ex:
                    pass

            elif action == 'exportar_detallado_compras':
                try:
                    data['title'] = u'Exportar detallado de la compra a excel'
                    compra = IngresoProducto.objects.get(pk=int(request.GET['id']))
                    response = HttpResponse(content_type='application/vnd.ms-excel')
                    response['Content-Disposition'] = 'attachment; filename=report.xlsx'
                    xlsx_data = WriteToExcel_Compras_Detallado(compra)
                    response.write(xlsx_data)
                    return response
                except Exception as ex:
                    pass

            elif action == 'consulta_pagos':
                try:
                    data['title'] = 'Consulta de pagos'
                    searchp = None
                    if 'sp' in request.GET:
                        searchp = request.GET['sp']

                    pagos = Pago.objects.all()
                    if searchp:
                        pagos = pagos.filter(Q(factura__numero__icontains=searchp) |
                                             Q(factura__cliente__nombre__icontains=searchp) |
                                             Q(factura__cliente__ruc__icontains=searchp) |
                                             Q(factura__vendedor__cedula__icontains=searchp) |
                                             Q(factura__vendedor__nombre__icontains=searchp))

                    paging = MiPaginador(pagos, 30)
                    p = 1
                    try:
                        if 'page' in request.GET:
                            p = int(request.GET['page'])
                        page = paging.page(p)
                    except:
                        page = paging.page(1)
                    data['paging'] = paging
                    data['rangospaging'] = paging.rangos_paginado(p)
                    data['page'] = page
                    data['pagos'] = page.object_list
                    data['searchp'] = searchp if searchp else ""
                    return render_to_response('consultas/consulta_pagos.html', data)
                except Exception as ex:
                    pass

            elif action == 'consulta_inventarios':
                try:
                    data['title'] = 'Consulta de inventarios'
                    searchi = None
                    categoria = None
                    ordenar = None
                    inicio = None
                    fin = None
                    if 'cid' in request.GET and int(request.GET['cid']) > 0:
                        categoria = TipoProducto.objects.get(pk=int(request.GET['cid']))
                    if 'oid' in request.GET and int(request.GET['oid']) > 0:
                        ordenar = int(request.GET['oid'])
                    if 'si' in request.GET:
                        searchi = request.GET['si']
                    if 'inicio' in request.GET:
                        inicio = convertir_fecha(request.GET['inicio'])
                    if 'fin' in request.GET:
                        fin = convertir_fecha(request.GET['fin'])

                    inventarios = InventarioReal.objects.all()
                    if searchi:
                        inventarios = inventarios.filter(Q(producto__codigo__icontains=searchi) |
                                                         Q(producto__descripcion__icontains=searchi) |
                                                         Q(producto__alias__icontains=searchi))

                    if categoria:
                        inventarios = inventarios.filter(producto__tipoproducto=categoria).order_by('producto__orden')

                    if ordenar:
                        if ordenar == 1:
                            inventarios = inventarios.order_by('cantidad')
                        else:
                            inventarios = inventarios.order_by('-cantidad')

                    if inicio and fin:
                        inventarios = inventarios.filter(producto__detallefactura__isnull=False,
                                                         producto__detallefactura__factura__fecha__gte=inicio,
                                                         producto__detallefactura__factura__fecha__lte=fin).distinct()
                    paging = MiPaginador(inventarios, 30)
                    p = 1
                    try:
                        if 'page' in request.GET:
                            p = int(request.GET['page'])
                        page = paging.page(p)
                    except:
                        page = paging.page(1)
                    data['paging'] = paging
                    data['rangospaging'] = paging.rangos_paginado(p)
                    data['page'] = page
                    data['inventarios'] = page.object_list
                    data['searchi'] = searchi if searchi else ""
                    data['categoria'] = categoria if categoria else ""
                    data['tipos_producto'] = TipoProducto.objects.all()
                    data['ordenid'] = int(ordenar) if ordenar else 0
                    data['categoriaid'] = categoria.id if categoria else 0
                    data['inicio'] = inicio if inicio else ""
                    data['fin'] = fin if fin else ""
                    data['hoy'] = datetime.now().date()
                    return render_to_response('consultas/consulta_inventarios.html', data)
                except Exception as ex:
                    pass

            elif action == 'kardex_inventario':
                try:
                    data['title'] = u'Kardex de Inventario'
                    data['producto'] = producto = Producto.objects.get(pk=request.GET['id'])
                    data['movimientos'] = producto.kardexinventario_set.all()
                    return render_to_response("consultas/kardex.html", data)
                except Exception as ex:
                    pass

            elif action == 'exportar_resumen_inventarios':
                try:
                    data['title'] = u'Exportar inventarios a excel'
                    searchi = None
                    categoria = None
                    ordenar = None
                    inicio = None
                    fin = None
                    if 'cid' in request.GET and int(request.GET['cid']) > 0:
                        categoria = TipoProducto.objects.get(pk=int(request.GET['cid']))
                    if 'oid' in request.GET and int(request.GET['oid']) > 0:
                        ordenar = int(request.GET['oid'])
                    if 'si' in request.GET:
                        searchi = request.GET['si']
                    if 'inicio' in request.GET and request.GET['inicio'] != "":
                        inicio = convertir_fecha(request.GET['inicio'])
                    if 'fin' in request.GET and request.GET['fin'] != "":
                        fin = convertir_fecha(request.GET['fin'])

                    datos = InventarioReal.objects.all()
                    if searchi:
                        datos = datos.filter(Q(producto__codigo__icontains=searchi) |
                                             Q(producto__descripcion__icontains=searchi) |
                                             Q(producto__alias__icontains=searchi) |
                                             Q(producto__proveedor__nombre__icontains=searchi) |
                                             Q(producto__proveedor__identificacion__icontains=searchi))
                    if categoria:
                        datos = datos.filter(producto__tipoproducto=categoria).order_by('producto__orden')
                    if inicio and fin:
                        datos = datos.filter(producto__detallefactura__isnull=False,
                                             producto__detallefactura__factura__fecha__gte=inicio,
                                             producto__detallefactura__factura__fecha__lte=fin).distinct()
                    if ordenar:
                        if ordenar == 1:
                            datos = datos.order_by('cantidad')
                        else:
                            datos = datos.order_by('-cantidad')

                    response = HttpResponse(content_type='application/vnd.ms-excel')
                    response['Content-Disposition'] = 'attachment; filename=report.xlsx'
                    xlsx_data = WriteToExcel_Inventarios_Resumen(datos, categoria, ordenar, searchi, inicio, fin)
                    response.write(xlsx_data)
                    return response
                except Exception as ex:
                    pass

            elif action == 'consulta_cif':
                try:
                    data['title'] = 'Consulta de costos'
                    searchcif = None
                    if 'scif' in request.GET:
                        searchcif = request.GET['scif']
                    if searchcif:
                        historial_cif = HistorialCifProducto.objects.filter(Q(producto__codigo__icontains=searchcif) |
                                                                            Q(producto__descripcion__icontains=searchcif) |
                                                                            Q(producto__alias__icontains=searchcif) |
                                                                            Q(compra__numerodocumento__icontains=searchcif) |
                                                                            Q(compra__descripcion__icontains=searchcif) |
                                                                            Q(compra__proveedor__nombre__icontains=searchcif) |
                                                                            Q(compra__proveedor__identificacion__icontains=searchcif))
                    else:
                        historial_cif = HistorialCifProducto.objects.all()

                    paging = MiPaginador(historial_cif, 25)
                    p = 1
                    try:
                        if 'page' in request.GET:
                            p = int(request.GET['page'])
                        page = paging.page(p)
                    except:
                        page = paging.page(1)
                    data['paging'] = paging
                    data['rangospaging'] = paging.rangos_paginado(p)
                    data['page'] = page
                    data['historial_cif'] = page.object_list
                    data['searchcif'] = searchcif if searchcif else ""
                    return render_to_response('consultas/consulta_cif.html', data)
                except Exception as ex:
                    pass

            elif action == 'consulta_precios':
                try:
                    data['title'] = 'Consulta de cambios precios'
                    searchprecios = None
                    if 'sprecios' in request.GET:
                        searchprecios = request.GET['sprecios']
                    if searchprecios:
                        historial_precios = HistorialPrecioProducto.objects.filter(
                            Q(producto__codigo__icontains=searchprecios) |
                            Q(producto__descripcion__icontains=searchprecios) |
                            Q(producto__alias__icontains=searchprecios) |
                            Q(modulo=searchprecios))
                    else:
                        historial_precios = HistorialPrecioProducto.objects.all()

                    paging = MiPaginador(historial_precios, 25)
                    p = 1
                    try:
                        if 'page' in request.GET:
                            p = int(request.GET['page'])
                        page = paging.page(p)
                    except:
                        page = paging.page(1)
                    data['paging'] = paging
                    data['rangospaging'] = paging.rangos_paginado(p)
                    data['page'] = page
                    data['historial_precios'] = page.object_list
                    data['searchprecios'] = searchprecios if searchprecios else ""
                    return render_to_response('consultas/consulta_precios.html', data)
                except Exception as ex:
                    pass

            elif action == 'consulta_vendedores':
                try:
                    data['title'] = 'Consulta de vendedores'
                    lista_vendedores = []
                    for vendedor in Vendedor.objects.filter(factura__isnull=False, factura__valida=True).distinct():
                        lista_vendedores.append((vendedor, vendedor.valor_ventas(), vendedor.valor_pagos(),
                                                 vendedor.valor_pendiente(), vendedor.cantidad_ventas(),
                                                 vendedor.comision_ventas()))
                    data['lista_vendedores'] = lista_vendedores
                    return render_to_response('consultas/consulta_vendedores.html', data)
                except Exception as ex:
                    pass

            elif action == 'consulta_colaboradores':
                try:
                    data['title'] = 'Consulta de colaboradores'
                    lista_colaboradores = []
                    for colaborador in Colaborador.objects.filter(detallefactura__isnull=False,
                                                                  detallefactura__factura__valida=True).distinct():
                        lista_colaboradores.append((colaborador,
                                                    colaborador.valor_ventas(),
                                                    colaborador.valor_pagos(),
                                                    colaborador.valor_pendiente(),
                                                    colaborador.cantidad_ventas(),
                                                    colaborador.comision_ventas()))
                    data['lista_colaboradores'] = lista_colaboradores
                    return render_to_response('consultas/consulta_colaboradores.html', data)

                except Exception as ex:
                    pass

            elif action == 'consulta_cajeros':
                try:
                    data['title'] = 'Consulta de cajeros'
                    lista_cajeros = []
                    for cajero in Cajero.objects.filter(factura__isnull=False, factura__valida=True).distinct():
                        lista_cajeros.append((cajero,
                                              cajero.valor_ventas(),
                                              cajero.valor_pagos(),
                                              cajero.valor_pendiente(),
                                              cajero.cantidad_ventas(),
                                              cajero.comision_ventas()))
                    data['lista_cajeros'] = lista_cajeros

                    # Sesiones activas
                    lista_sesiones_cajeros = []
                    for sesion in SesionCaja.objects.filter(abierta=True):
                        lista_sesiones_cajeros.append((sesion.cajero,
                                                       sesion.valor_ventas(),
                                                       sesion.valor_pagos(),
                                                       sesion.valor_pendiente(),
                                                       sesion.cantidad_ventas(),
                                                       sesion.comision_ventas()))
                    data['lista_sesiones_cajeros'] = lista_sesiones_cajeros
                    return render_to_response('consultas/consulta_cajeros.html', data)
                except Exception as ex:
                    pass

            elif action == 'consulta_ordenes_servicio':
                try:
                    data['title'] = 'Consulta de ordenes de servicio'
                    search = None
                    clienteid = None
                    colaboradorid = None
                    facturadas = None

                    if 's' in request.GET:
                        search = request.GET['s']

                    if 'cli' in request.GET and int(request.GET['cli']) > 0:
                        clienteid = int(request.GET['cli'])

                    if 'col' in request.GET and int(request.GET['col']) > 0:
                        colaboradorid = int(request.GET['col'])

                    if 'f' in request.GET and int(request.GET['f']) > 0:
                        facturadas = 1 if int(request.GET['f']) == 1 else 2

                    ordenes = OrdenServicio.objects.all()
                    if search:
                        ordenes = ordenes.filter(Q(cliente__nombre__icontains=search),
                                                 Q(factura__numero__icontains=search)).distinct()
                    if clienteid:
                        ordenes = ordenes.filter(cliente__id=clienteid)

                    if colaboradorid:
                        ordenes = ordenes.filter(colaborador__id=colaboradorid)

                    if facturadas:
                        if facturadas == 1:
                            ordenes = ordenes.filter(factura_asignada__isnull=False)
                        else:
                            ordenes = ordenes.filter(factura_asignada__isnull=True)

                    paging = MiPaginador(ordenes, 30)
                    p = 1
                    try:
                        if 'page' in request.GET:
                            p = int(request.GET['page'])
                        page = paging.page(p)
                    except:
                        page = paging.page(1)
                    data['paging'] = paging
                    data['rangospaging'] = paging.rangos_paginado(p)
                    data['page'] = page
                    data['ordenes'] = page.object_list
                    data['search'] = search if search else ""
                    data['clientes'] = Cliente.objects.filter(ordenservicio__isnull=False).distinct()
                    data['colaboradores'] = Colaborador.objects.filter(ordenservicio__isnull=False).distinct()
                    data['clienteid'] = clienteid if clienteid else ""
                    data['colaboradorid'] = colaboradorid if colaboradorid else ""
                    data['facturadas'] = facturadas if facturadas else ""
                    return render_to_response('consultas/consulta_ordenes_servicio.html', data)
                except Exception as ex:
                    pass

            elif action == 'detalle_orden_servicio':
                try:
                    data['orden'] = orden = OrdenServicio.objects.get(pk=request.GET['id'])
                    data['detalles'] = orden.ordenserviciodetalle_set.all()
                    return render_to_response('ordenes/detalles.html', data)
                except Exception as ex:
                    pass

            return HttpResponseRedirect(url_back(request, mensaje_excepcion(ex.args[0])))

        else:
            return HttpResponseRedirect('/consultas?action=consulta_ventas')
