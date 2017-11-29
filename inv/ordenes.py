import json
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models.query_utils import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

from inv.forms import ServicioFuturoForm
from inv.funciones import salva_auditoria, MiPaginador, url_back, mensaje_excepcion, bad_json, ok_json
from inv.models import (OrdenServicio, Cliente, TipoProducto, TipoDocumento, TipoServicio,
                        Colaborador, Producto, Servicio, OrdenServicioDetalle, ServicioFuturo)
from inv.views import addUserData
from spa.settings import ACCION_ADICIONAR, ACCION_ELIMINAR, TIPO_CLIENTE_NORMAL, TIPO_CLIENTE_CORPORATIVO


class ErrorOrdenServicio(Exception):

    def __init__(self, valor):
        self.valor = valor

    def __str__(self):
        return "Error {}".format(self.valor)


@login_required(redirect_field_name='ret', login_url='/login')
def view(request):
    ex = None
    data = {'title': u'Ordenes de Servicio'}
    addUserData(request, data)
    if not data['es_colaborador']:
        return bad_json(mensaje=u"El usuario no pertenece al grupo de colaboradores")
    if not Colaborador.objects.filter(usuario__username=request.user).exists():
        return bad_json(mensaje=u"El usuario no es colaborador")
    colaborador = Colaborador.objects.filter(usuario__username=request.user)[0]

    if request.method == 'POST':
        action = request.POST['action']
        if action == 'delete':
            orden = OrdenServicio.objects.get(pk=request.POST['id'])
            try:
                with transaction.atomic():
                    salva_auditoria(request, orden, ACCION_ELIMINAR)
                    orden.delete()
                    return ok_json()

            except Exception:
                return bad_json(error=3)

        elif action == 'datoscliente':
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
                                     "direccion": cliente.domicilio})
            else:
                return bad_json(error=1)

        elif action == 'generar':
            try:
                with transaction.atomic():

                    datos = json.loads(request.POST['items'])
                    items = json.loads(request.POST['productos'])

                    if Cliente.objects.filter(identificacion=datos['ruccliente']).exists():
                        cliente = Cliente.objects.filter(identificacion=datos['ruccliente'])[0]
                        cliente.nombre = datos['nombrecliente']
                        cliente.domicilio = datos['direccioncliente']
                        cliente.tipo = int(datos['tipoclienteid'])
                        cliente.telefono = datos['telefonocliente']
                        cliente.email = datos['emailcliente']
                        cliente.save()
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

                    # Crear Orden de Servicio
                    orden = OrdenServicio(cliente=cliente,
                                          colaborador=colaborador,
                                          fecha=fechaactual,
                                          subtotal=float(datos['subtotal']),
                                          iva=float(datos['iva']),
                                          total=float(datos['total']),
                                          observaciones=datos['observacionesfactura'])
                    orden.save()

                    for item in items:
                        producto = None
                        servicio = None
                        if item['tipoproducto'] == 'PRODUCTO':
                            producto = Producto.objects.filter(codigo=item['codproducto'])[0]
                        else:
                            servicio = Servicio.objects.filter(codigo=item['codproducto'])[0]
                        detalleorden = OrdenServicioDetalle(orden=orden,
                                                            servicio=servicio,
                                                            producto=producto,
                                                            cantidad=float(item['cantidad']),
                                                            precio=float(item['pvpproducto']),
                                                            valor=float(item['valor']))
                        detalleorden.save()

                    salva_auditoria(request, orden, ACCION_ADICIONAR)
                    return ok_json(data={"orden": orden.repr_id(), "cliente": orden.cliente.nombre})

            except ErrorOrdenServicio:
                return bad_json(error=2)
            except Exception:
                return bad_json(error=1)

        elif action == 'add_serviciofuturo':
            orden = OrdenServicio.objects.get(pk=request.POST['id'])
            f = ServicioFuturoForm(request.POST)
            if f.is_valid():
                try:
                    with transaction.atomic():
                        if f.cleaned_data['fecha'] < datetime.now().date():
                            return bad_json(mensaje="La fecha no puede ser menor al dia de hoy")
                        serviciofuturo = ServicioFuturo(orden=orden,
                                                        cliente=orden.cliente,
                                                        servicio=f.cleaned_data['servicio'],
                                                        fecha=f.cleaned_data['fecha'])
                        serviciofuturo.save()
                        salva_auditoria(request, serviciofuturo, ACCION_ADICIONAR)
                        return ok_json()

                except Exception:
                    return bad_json(error=1)
            else:
                return bad_json(error=1)

        if action == 'delete_serviciofuturo':
            serviciofuturo = ServicioFuturo.objects.get(pk=request.POST['id'])
            try:
                with transaction.atomic():
                    salva_auditoria(request, serviciofuturo, ACCION_ELIMINAR)
                    serviciofuturo.delete()
                    return ok_json()
            except Exception:
                return bad_json(error=1)

        return bad_json(error=0)

    else:
        if 'action' in request.GET:
            action = request.GET['action']
            if action == 'add':
                try:
                    data['title'] = u'Crear Orden de Servicio'
                    data['tipos_productos'] = TipoProducto.objects.all()
                    data['tipos_servicios'] = TipoServicio.objects.all()
                    data['tipos_documentos'] = TipoDocumento.objects.all()
                    return render_to_response("ordenes/add.html", data)
                except Exception as ex:
                    pass

            elif action == 'delete':
                try:
                    data['title'] = u'Eliminar orden de servicio'
                    data['orden'] = OrdenServicio.objects.get(pk=request.GET['id'])
                    return render_to_response("ordenes/delete.html", data)
                except Exception as ex:
                    pass

            elif action == 'detalle_orden':
                try:
                    data['orden'] = orden = OrdenServicio.objects.get(pk=request.GET['id'])
                    data['detalles'] = orden.ordenserviciodetalle_set.all()
                    return render_to_response('ordenes/detalles.html', data)
                except Exception as ex:
                    pass

            if action == 'buscaproductos':
                try:
                    inventarios = None
                    tipoprod = None
                    if 'tipoid' in request.GET and request.GET['tipoid'] != '':
                        tipoprod = TipoProducto.objects.get(pk=request.GET['tipoid'])
                        inventarios = tipoprod.productos_con_existencias()
                    data['productos'] = inventarios
                    data['tipoprod'] = tipoprod
                    data['tipocliente'] = int(request.GET['tipoclienteid'])
                    return render_to_response("ordenes/buscaproductos.html", data)
                except Exception as ex:
                    pass

            if action == 'buscaservicios':
                try:
                    servicios = None
                    tiposerv = None
                    if 'tipoid' in request.GET and request.GET['tipoid'] != '':
                        tiposerv = TipoServicio.objects.get(pk=request.GET['tipoid'])
                        servicios = tiposerv.servicio_set.filter(activo=True)
                    data['servicios'] = servicios
                    data['tiposerv'] = tiposerv
                    data['tipocliente'] = int(request.GET['tipoclienteid'])
                    return render_to_response("ordenes/buscaproductos.html", data)
                except Exception as ex:
                    pass

            if action == 'serviciosfuturos':
                try:
                    data['orden'] = orden = OrdenServicio.objects.get(pk=request.GET['id'])
                    data['servicios_futuros'] = orden.serviciofuturo_set.all()
                    data['cantidad_servicios_futuros'] = orden.serviciofuturo_set.count()
                    return render_to_response("ordenes/serviciosfuturos.html", data)
                except Exception as ex:
                    pass

            if action == 'add_serviciofuturo':
                try:
                    data['title'] = u'Adicionar Servicio Futuro'
                    data['orden'] = orden = OrdenServicio.objects.get(pk=request.GET['id'])
                    form = ServicioFuturoForm()
                    form.for_serviciofuturo(orden)
                    data['form'] = form
                    return render_to_response('ordenes/add_serviciofuturo.html', data)
                except Exception as ex:
                    pass

            elif action == 'delete_serviciofuturo':
                try:
                    data['title'] = u'Eliminar servicio futuro'
                    data['servicio_futuro'] = servicio_futuro = ServicioFuturo.objects.get(pk=request.GET['id'])
                    data['orden'] = servicio_futuro.orden
                    return render_to_response("ordenes/delete_serviciofuturo.html", data)
                except Exception as ex:
                    pass

            return HttpResponseRedirect(url_back(request, mensaje_excepcion(ex.args[0])))

        else:

            search = None
            clienteid = None

            if 's' in request.GET:
                search = request.GET['s']

            if 'c' in request.GET and int(request.GET['c']) > 0:
                clienteid = int(request.GET['c'])

            if search:
                ordenes = OrdenServicio.objects.filter(Q(cliente__nombre__icontains=search),
                                                       Q(factura__numero__icontains=search),
                                                       colaborador=colaborador).distinct()
            elif clienteid:
                ordenes = OrdenServicio.objects.filter(cliente__id=clienteid, colaborador=colaborador)
            else:
                ordenes = OrdenServicio.objects.filter(colaborador=colaborador)

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
            data['search'] = search if search else ""
            data['ordenes'] = page.object_list
            data['clienteid'] = clienteid if clienteid else ""
            data['clientes'] = Cliente.objects.filter(ordenservicio__colaborador__usuario=request.user).distinct()
            return render_to_response("ordenes/view.html", data)
