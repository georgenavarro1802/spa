import json
import random
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response

from inv.forms import CambioClaveForm, VideoForm
from inv.funciones import url_back, mensaje_excepcion, generar_nombre, ok_json, bad_json
from inv.funciones_estadisticas import (valor_total_cif_compras, cantidad_formas_pago, cantidad_facturas_anuladas,
                                        valores_ventas_total, cantidad_facturas_total, cantidad_compras_total,
                                        pagos_total, cantidad_pagos_total, cantidad_facturas_por_cancelar,
                                        valor_inventario_con_existencia, cantidad_inventario_con_existencia,
                                        valor_facturas_por_cancelar, cantidad_clientes, cantidad_vendedores,
                                        cantidad_proveedores, cantidad_usuarios, cantidad_productos,
                                        cantidad_categorias, cantidad_inventario_agotado,
                                        cantidad_inventario_bajo_minimo, cantidad_solicitudes_asignadas,
                                        cantidad_solicitudes_pendientes_clientes,
                                        cantidad_solicitudes_pendientes_vendedores)
from inv.models import *
from spa.settings import (NOMBRE_INSTITUCION, ADMINISTRADOR_GROUP_ID, VENDEDOR_GROUP_ID, CLIENTES_GROUP_ID, IVA,
                          CAJAS_GROUP_ID, COLABORADOR_GROUP_ID, DEFAULT_PASSWORD)


class ErrorSolicitud(Exception):
    def __init__(self, valor):
        self.valor = valor

    def __str__(self):
        return "Error " + str(self.valor)


def convertir_fecha(s):
    try:
        return datetime(int(s[-4:]), int(s[3:5]), int(s[:2]))
    except:
        return datetime.now()


def addUserData(request, data):
    data['usuario'] = request.user
    data['currenttime'] = datetime.now()
    data['nombreinstitucion'] = NOMBRE_INSTITUCION
    data['iva'] = IVA
    data['hoy'] = datetime.now().date()

    if not 'empresa' in request.session:
        request.session['empresa'] = Empresa.objects.filter().all()[0]
    data['empresa'] = request.session['empresa']

    data['remoteaddr'] = request.META['REMOTE_ADDR']
    data['es_administrador'] = ADMINISTRADOR_GROUP_ID in [x.id for x in request.user.groups.all()]
    data['es_vendedor'] = VENDEDOR_GROUP_ID in [x.id for x in request.user.groups.all()]
    data['es_colaborador'] = COLABORADOR_GROUP_ID in [x.id for x in request.user.groups.all()]
    data['es_cliente'] = CLIENTES_GROUP_ID in [x.id for x in request.user.groups.all()]
    data['es_cajero'] = CAJAS_GROUP_ID in [x.id for x in request.user.groups.all()] and request.user.cajero_set.exists()


@login_required(redirect_field_name='ret', login_url='/login')
def index(request):
    global ex
    data = {'title': 'Bienvenidos - ' + NOMBRE_INSTITUCION}
    addUserData(request, data)
    data['hoy'] = datetime.now().date()
    es_cliente = data['es_cliente']
    es_colaborador = data['es_colaborador']
    if es_colaborador:
        return HttpResponseRedirect('/panelcolaborador')
    if es_cliente:
        return HttpResponseRedirect('/panelclientes')
    if request.method == 'POST':
        if 'action' in request.POST:
            return bad_json(error=0)

    else:
        if 'action' in request.GET:
            action = request.GET['action']
            if action == 'buscaproductos':
                try:
                    inventarios = None
                    if request.GET['tipoid'] != '':
                        data['tipoprod'] = tipoprod = TipoProducto.objects.get(pk=request.GET['tipoid'])
                        inventarios = tipoprod.productos_con_existencias()
                    data['productos_existencias'] = inventarios
                    data['iva'] = IVA
                    return render_to_response("solicitudes/buscaproductos.html", data)
                except Exception as ex:
                    pass

            return HttpResponseRedirect(url_back(request, mensaje_excepcion(ex.args[0])))

        else:
            if 'info' in request.GET:
                data['info'] = request.GET['info']

            # Dashboard estadistico (Para los administradores del sistema)
            # ventas
            data['valores_ventas_total'] = valores_ventas_total()
            data['cantidad_facturas_total'] = cantidad_facturas_total()
            # compras
            data['valor_total_cif_compras'] = valor_total_cif_compras()
            data['cantidad_compras_total'] = cantidad_compras_total()
            # pagos
            data['pagos_total'] = pagos_total()
            data['cantidad_pagos_total'] = cantidad_pagos_total()
            # inventarios
            data['valor_inventario_con_existencia'] = valor_inventario_con_existencia()
            data['cantidad_inventario_con_existencia'] = cantidad_inventario_con_existencia()
            # cobros pendientes
            data['valor_facturas_por_cancelar'] = valor_facturas_por_cancelar()
            data['cantidad_facturas_por_cancelar'] = cantidad_facturas_por_cancelar()
            # 2da Tabla estadistica
            data['cantidad_clientes'] = cantidad_clientes()
            data['cantidad_vendedores'] = cantidad_vendedores()
            data['cantidad_proveedores'] = cantidad_proveedores()
            data['cantidad_inventario_agotado'] = cantidad_inventario_agotado()
            data['cantidad_inventario_bajo_minimo'] = cantidad_inventario_bajo_minimo()
            # Graficos
            data['clientes_mas_compran'] = Cliente.objects.filter(factura__isnull=False,
                                                                  factura__valida=True).distinct().annotate(
                cantidadventas=Count('factura__id')).distinct().order_by('-cantidadventas')[:5]
            data['productos_mas_vendidos'] = Producto.objects.filter(detallefactura__isnull=False).annotate(
                cantidadventas=Count('detallefactura__id')).distinct().order_by('-cantidadventas')[:5]
            # Tablas - Ultimas ventas y compras
            data['ultimas_ventas'] = Factura.objects.filter(valida=True)[:5]
            data['ultimas_compras'] = IngresoProducto.objects.all()[:5]
            # Otras Tablas - Resumen y Ultimas auditorias
            data['cantidad_productos'] = cantidad_productos()
            data['cantidad_categorias'] = cantidad_categorias()
            data['cantidad_usuarios'] = cantidad_usuarios()
            data['cantidad_facturas_anuladas'] = cantidad_facturas_anuladas()
            data['cantidad_formas_pago'] = cantidad_formas_pago()
            data['ultimas_auditorias'] = AudiUsuarioTabla.objects.all()[:5]
            # Solicitudes de compras (usuarios Clientes o Vendedores)
            data['cantidad_solicitudes_pendientes_clientes'] = cantidad_solicitudes_pendientes_clientes()
            data['cantidad_solicitudes_pendientes_vendedores'] = cantidad_solicitudes_pendientes_vendedores()
            data['cantidad_solicitudes_asignadas'] = cantidad_solicitudes_asignadas()
            data['tipos_productos'] = TipoProducto.objects.all().order_by('orden')
            data['tipos_documentos'] = TipoDocumento.objects.all()
            return render_to_response("panelbs.html", data)


def login_user(request):
    if request.method == 'POST':
        user = authenticate(username=request.POST['user'], password=request.POST['pass'])
        if user is not None:
            if not user.is_active:
                return HttpResponseRedirect("/login?ret=" + request.POST['ret'] + "&error=3")
            else:
                login(request, user)
                return HttpResponseRedirect(request.POST['ret'])
        else:
            return HttpResponseRedirect("/login?ret=" + request.POST['ret'] + "&error=1")
    else:
        ret = '/'
        if 'ret' in request.GET:
            ret = request.GET['ret']
        data = {"title": "Login",
                "return_url": ret,
                "background": random.randint(1, 9),
                "error": request.GET['error'] if 'error' in request.GET else "",
                "errorp": request.GET['errorp'] if 'errorp' in request.GET else "",
                'request': request}
        addUserData(request, data)
        return render_to_response("login.html", data)


def logout_user(request):
    logout(request)
    return HttpResponseRedirect("/")


@login_required(redirect_field_name='ret', login_url='/login')
def passwd(request):
    if request.method == 'POST':
        if 'action' in request.POST:
            action = request.POST['action']
            if action == 'changepass':
                try:
                    f = CambioClaveForm(request.POST)
                    if f.is_valid():
                        with transaction.atomic():
                            if f.cleaned_data['nueva'] == DEFAULT_PASSWORD:
                                return HttpResponse(json.dumps({"result": "bad", "mensaje": "No puede usar la clave por defecto."}), mimetype="application/json")
                            data = {}
                            addUserData(request, data)
                            usuario = data['usuario']
                            if usuario.check_password(f.cleaned_data['anterior']):
                                usuario.set_password(f.cleaned_data['nueva'])
                                usuario.save()
                                return ok_json()
                            return bad_json(mensaje=u"Clave anterior no coincide.")
                    else:
                        raise Exception

                except Exception:
                    return bad_json(mensaje=u"No se pudo cambiar la clave.")

        return bad_json(error=0)
    else:
        try:
            data = {}
            addUserData(request, data)
            data['title'] = u'Cambio de clave'
            data['form'] = CambioClaveForm()
            return render_to_response("changepassbs.html", data, request)
        except Exception:
            return HttpResponseRedirect('/')


@login_required(redirect_field_name='ret', login_url='/login')
def get_data(request):
    try:
        m = request.GET['model']
        if 'q' in request.GET:
            q = request.GET['q']
            if ':' in m:
                sp = m.split(':')
                model = eval(sp[0])
                query = model.flexbox_query(q)
                for n in range(1, len(sp)):
                    query = eval('query.filter(%s)' % (sp[n]))
            else:
                model = eval(request.GET['model'])
                query = model.flexbox_query(q)
        else:
            model = eval(request.GET['model'])
            query = model.flexbox_query('')

        data = {"results": [{"id": x.id, "name": x.flexbox_repr(), "alias": x.flexbox_alias()} for x in query]}
        return HttpResponse(json.dumps(data), content_type='application/json')

    except Exception:
        return bad_json(error=1)


@login_required(redirect_field_name='ret', login_url='/login')
def subir_video(request):
    data = {'title': 'Subir video instructivo', 'form': VideoForm()}
    addUserData(request, data)
    if request.method == 'POST':
        f = VideoForm(request.POST, request.FILES)
        if f.is_valid():
            try:
                with transaction.atomic():
                    video = Video()
                    video.descripcion = f.cleaned_data['descripcion']
                    newfile = request.FILES['video']
                    newfile._name = generar_nombre("video_", newfile._name)
                    video.file = newfile
                    video.save()
                return HttpResponse(json.dumps({"result": "ok"}), content_type="application/json")
            except Exception:
                return HttpResponse(json.dumps({"result": "bad"}), content_type="application/json")
        return HttpResponseRedirect('/')
    return render_to_response("subir_video.html", data)
