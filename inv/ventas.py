import json

from itertools import chain

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

from inv.funciones import (salva_auditoria, url_back, mensaje_excepcion, get_pdf_factura, bad_json, ok_json)
from inv.models import *
from inv.views import addUserData, convertir_fecha
from spa.settings import ACCION_ADICIONAR, MEDIA_URL


class ErrorVentas(Exception):

    def __init__(self, valor):
        self.valor = valor

    def __str__(self):
        return "Error " + str(self.valor)


@login_required(redirect_field_name='ret', login_url='/login')
def view(request):
    ex = None
    data = {'title': u'Ventas'}
    addUserData(request, data)

    empresaid = request.session['empresa'].id
    usuario = request.user

    if not data['es_cajero']:
        return HttpResponseRedirect("/?info=El usuario no tiene permisos como cajero")
    data['cajero'] = cajero = usuario.cajero_set.all()[0]

    if not cajero.tiene_sesioncaja_abierta():
        return HttpResponseRedirect("/?info=NO TIENE SESION DE CAJA ABIERTA")

    data['sesioncaja'] = sesioncaja = cajero.get_sesion_caja_abierta()

    if request.method == 'POST':
        action = request.POST['action']

        if action == 'guardar':
            try:
                with transaction.atomic():

                    # Para comprobar si se generara la venta a partir de una orden de servicio
                    orden = None
                    if 'oid' in request.POST and request.POST['oid'] != '':
                        orden = OrdenServicio.objects.get(pk=int(request.POST['oid']))

                    # JSON con los datos generales y productos
                    datos = json.loads(request.POST['items'])

                    formadepago_efectivo = False
                    if int(datos['formadepago']) == 1:
                        formadepago_efectivo = True

                    if Cliente.objects.filter(identificacion=datos['ruccliente']).exists():
                        cliente = Cliente.objects.filter(identificacion=datos['ruccliente'])[0]
                        cliente.nombre = datos['nombrecliente']
                        cliente.domicilio = datos['direccioncliente']
                        cliente.tipo = int(datos['tipoclienteid'])
                        cliente.telefono = datos['telefonocliente']
                        cliente.email = datos['emailcliente']
                        # cliente.save()
                    else:
                        cliente = Cliente(identificacion=datos['ruccliente'],
                                          nombre=datos['nombrecliente'],
                                          domicilio=datos['direccioncliente'],
                                          tipo=int(datos['tipoclienteid']),
                                          telefono=datos['telefonocliente'],
                                          email=datos['emailcliente'])
                        cliente.save()
                        if cliente.tipo == TIPO_CLIENTE_CORPORATIVO:
                            cliente.ruc = cliente.identificacion
                            cliente.save()

                    # Crear Factura
                    factura = Factura(sesioncaja=sesioncaja,
                                      cliente=cliente,
                                      cajero=cajero,
                                      numero=datos['numerofactura'],
                                      fecha_vencimiento=convertir_fecha(datos['fechafactura']).date(),
                                      bruto=float(datos['bruto']),
                                      descuento=float(datos['descuento']),
                                      subtotal=float(datos['subtotal']),
                                      iva=float(datos['iva']),
                                      total=float(datos['total']),
                                      notaventa=True if cliente.identificacion == "9999999999" else False,
                                      valida=True,
                                      pagado=0,
                                      valorpagado=float(datos['pagado']),
                                      cambio=float(datos['cambio']),
                                      observaciones=datos['observacionesfactura'])
                    factura.save()
                    # si es en efectivo, generar pago al instante
                    if formadepago_efectivo:
                        pago = Pago(factura=factura,
                                    fecha=datetime.now().date(),
                                    valor=factura.total,
                                    observaciones='')
                        pago.save()
                        pagoefectivo = PagoEfectivo(pago=pago)
                        pagoefectivo.save()
                        factura.save()  # recalcula campo pagado y cancelada

                    # Actualizar Inventario Real
                    if Area.objects.exists():
                        if Area.objects.filter(es_principal=True):
                            area = Area.objects.filter(es_principal=True)[0]
                        else:
                            area = Area.objects.all()[0]
                    else:
                        area = Area(nombre='Matriz', es_principal=True)
                        area.save()

                    for item in datos['productos']:
                        if int(item['id']):
                            producto = None
                            servicio = None
                            paquete = None

                            if item['tipoproducto'] == 'PRODUCTO':
                                producto = Producto.objects.get(pk=int(item['id']))

                            elif item['tipoproducto'] == 'SERVICIO':
                                servicio = Servicio.objects.get(pk=int(item['id']))

                            else:
                                paquete = Paquete.objects.get(pk=int(item['id']))

                            colaborador = None
                            if item['colaborador_id']:
                                colaborador = Colaborador.objects.get(pk=int(item['colaborador_id']))

                            detallefactura = DetalleFactura(factura=factura,
                                                            producto=producto,
                                                            servicio=servicio,
                                                            paquete=paquete,
                                                            colaborador=colaborador,
                                                            cantidad=float(item['cantidad']),
                                                            precio=float(item['precio']),
                                                            valor_bruto=float(item['valorbruto']),
                                                            porciento_descuento=float(item['porcientodescuento']),
                                                            valor_descuento=float(item['valordescuento']),
                                                            valor=float(item['valorneto']))
                            detallefactura.save()

                            # Actualizar Inventario si es producto
                            if producto:
                                producto.actualizar_inventario_salida(detallefactura, area)

                            # Actualizar Inventario si el paquete contiene productos a consumir
                            if paquete:
                                for pp in paquete.mis_productos():
                                    pp.producto.actualizar_inventario_salida(detallefactura, area)

                    # Asignacion de la factura a la solicitud q la origino
                    if orden:
                        orden.factura_asignada = factura
                        orden.fecha_asignada = datetime.now().date()
                        orden.save()

                    salva_auditoria(request, factura, ACCION_ADICIONAR)

                    # FPDF Factura
                    pdfname = get_pdf_factura(factura, empresaid, request.user.username)
                    return ok_json(data={'es_efectivo': '1' if formadepago_efectivo else '0',
                                         'cliente_id': cliente.id,
                                         'urlimpresion': '/'.join([MEDIA_URL, 'documentos', 'userreports',
                                                                  request.user.username, pdfname])})

            except ErrorVentas as ex:
                return bad_json(mensaje=str(ex))
            except Exception as ex:
                return bad_json(mensaje=str(ex))

        if action == 'datoscliente':
            cliente = None

            if 'idc' in request.POST and int(request.POST['idc']) > 0:
                cliente = Cliente.objects.get(pk=int(request.POST['idc']))
                if not cliente.identificacion:
                    diff_lenght_clienteid = 10 - len(str(cliente.id))
                    cliente.identificacion = str(cliente.id) + '1'.zfill(diff_lenght_clienteid)
                    cliente.save()

            if 'identificacion' in request.POST['identificacion'] and request.POST['identificacion']:
                if Cliente.objects.filter(identificacion=request.POST['identificacion']).exists():
                    cliente = Cliente.objects.filter(identificacion=request.POST['identificacion'])[0]

            if cliente:

                if cliente.tipo == TIPO_CLIENTE_NORMAL:
                    tipo = 1
                    ruc = cliente.identificacion
                elif cliente.tipo == TIPO_CLIENTE_CORPORATIVO:
                    tipo = 2
                    if not cliente.ruc and cliente.identificacion:
                        cliente.ruc = cliente.identificacion
                        cliente.save()
                    ruc = cliente.ruc
                else:
                    tipo = 3
                    ruc = cliente.identificacion

                return ok_json(data={"identificacion": ruc,
                                     "nombre": cliente.nombre,
                                     "tipo": tipo,
                                     "telefono": cliente.mi_telefono(),
                                     "email": cliente.email,
                                     "facturas_vencidas": cliente.cantidad_facturas_vencidas(),
                                     "direccion": cliente.domicilio})
            else:
                return bad_json(error=1)

        if action == 'rangoprecio_producto':
            try:
                producto = Producto.objects.get(pk=request.POST['pid'])
                cantidad = float(request.POST['cantidad'])
                precioprod = producto.get_precio_by_rangoprecio(cantidad)
                return ok_json(data={"precio": precioprod})
            except:
                return bad_json(error=1)

        return bad_json(error=0)

    else:
        if 'action' in request.GET:
            action = request.GET['action']

            if action == 'ultimonumerofactura':
                try:
                    numero = 1
                    sc = SesionCaja.objects.get(pk=request.GET['scid'])
                    if sc.factura_set.exists():
                        ultimafactura = sc.factura_set.latest('id')
                        numero = int(ultimafactura.numero) + 1
                    return ok_json(data={"numero": numero})
                except Exception:
                    return bad_json(error=1)

            if action == 'ordenes':
                try:
                    clienteid = None
                    if 'c' in request.GET and int(request.GET['c']) > 0:
                        clienteid = int(request.GET['c'])
                    ordenes = OrdenServicio.objects.filter(factura_asignada=None)
                    if clienteid:
                        ordenes = ordenes.filter(cliente__id=clienteid)
                    data['ordenes'] = ordenes
                    data['clientes'] = Cliente.objects.filter(ordenservicio__isnull=False).distinct()
                    return render_to_response("ventas/ordenes.html", data)
                except Exception as ex:
                    pass

            if action == 'detalle_orden':
                try:
                    data['orden'] = orden = OrdenServicio.objects.get(pk=request.GET['ordenid'])
                    data['detalles'] = orden.ordenserviciodetalle_set.all()
                    return render_to_response('ordenes/detalles.html', data)
                except Exception as ex:
                    pass

            return HttpResponseRedirect(url_back(request, mensaje_excepcion(ex.args[0])))

        else:

            if 'oid' in request.GET:
                data['orden'] = orden = OrdenServicio.objects.get(pk=int(request.GET['oid']))
                data['orden_detalles'] = orden.ordenserviciodetalle_set.all()

            data['colaboradores'] = Colaborador.objects.all()
            data['lista_items_ventas'] = [x for x in range(10)]

            productos = Producto.objects.filter(activo=True, precio__gt=0,
                                                inventarioreal__isnull=False,
                                                inventarioreal__cantidad__gt=0).distinct()[:10]

            servicios = Servicio.objects.filter(activo=True, precio__gt=0)[:10]

            paquetes = Paquete.objects.filter(activo=True)

            data['lista_items'] = list(chain(productos, servicios, paquetes))

            return render_to_response("ventas/view.html", data)
